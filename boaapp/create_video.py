import json
import os
from decouple import config

os.environ["IMAGEMAGICK_BINARY"] = config('IMAGEMAGICK_BINARY', default='magick')
import time
import re
import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import (
    AudioFileClip, ColorClip, CompositeVideoClip,
    ImageClip, TextClip, VideoFileClip
)
from PIL import Image

logger = logging.getLogger(__name__)


def split_into_sentences(text):
    """Splits text into sentences based on punctuation followed by space."""
    if not text: return []
    # Corrected regex to handle HTML entities if they appear
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def clean_header_hashes(text):
    """Removes leading #, ##, ### and subsequent space from text."""
    if not text: return ""
    return re.sub(r'^#{1,3}\s*', '', text).strip()


def render_code_panel_image(code_text, target_size=(1080, 1920)):
    """
    Renders code as a VS Code-style dark panel on a transparent full-frame RGBA image.
    Returns a PIL Image suitable for conversion to a MoviePy ImageClip via numpy.
    """
    from PIL import Image as PILImage, ImageDraw, ImageFont as PILFont

    W, H = target_size
    img = PILImage.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad_x = 45
    panel_top = 175
    panel_right = W - pad_x
    panel_width = panel_right - pad_x
    header_h = 46
    font_size = 27
    lnum_size = 23

    # Try to load a system monospace font; fall back gracefully
    font_candidates = [
        r"C:\Windows\Fonts\courbd.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    code_font = lnum_font = None
    for fp in font_candidates:
        try:
            code_font = PILFont.truetype(fp, font_size)
            lnum_font = PILFont.truetype(fp, lnum_size)
            break
        except (IOError, OSError):
            continue
    if code_font is None:
        code_font = lnum_font = PILFont.load_default()

    try:
        header_font = PILFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
    except (IOError, OSError):
        header_font = lnum_font

    # Prepare lines: expand tabs, truncate long lines
    max_chars = 48
    raw_lines = code_text.replace('\t', '    ').split('\n')
    display_lines = []
    for raw in raw_lines:
        display_lines.append(raw[:max_chars - 1] + '\u2026' if len(raw) > max_chars else raw)

    line_height = font_size + 12
    max_visible = (H - panel_top - header_h - 40) // line_height
    visible_lines = display_lines[:max_visible]
    truncated = len(display_lines) > max_visible

    panel_height = min(len(visible_lines) * line_height + header_h + 24, H - panel_top - 30)

    # Panel background (#1E1E1E — VS Code dark)
    draw.rounded_rectangle(
        [pad_x, panel_top, panel_right, panel_top + panel_height],
        radius=14, fill=(30, 30, 30, 248)
    )
    # Header bar (#2D2D2D)
    draw.rounded_rectangle(
        [pad_x, panel_top, panel_right, panel_top + header_h],
        radius=14, fill=(45, 45, 45, 255)
    )
    # Flatten header bottom corners
    draw.rectangle(
        [pad_x, panel_top + header_h // 2, panel_right, panel_top + header_h],
        fill=(45, 45, 45, 255)
    )

    # macOS traffic-light dots
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = pad_x + 18 + i * 26
        cy = panel_top + header_h // 2
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Header filename label
    draw.text(
        (pad_x + panel_width // 2, panel_top + header_h // 2),
        "script.py", fill=(160, 160, 160), font=header_font, anchor="mm"
    )

    # Line number gutter
    lnum_col_w = 52
    sep_x = pad_x + lnum_col_w + 6
    draw.line([(sep_x, panel_top + header_h), (sep_x, panel_top + panel_height)],
              fill=(55, 55, 55), width=1)

    code_x = sep_x + 12
    for i, line in enumerate(visible_lines):
        y = panel_top + header_h + 10 + i * line_height
        if y + line_height > panel_top + panel_height:
            break
        draw.text(
            (sep_x - 8, y + (font_size - lnum_size) // 2),
            str(i + 1), fill=(80, 80, 80), font=lnum_font, anchor="ra"
        )
        draw.text((code_x, y), line, fill=(212, 212, 212), font=code_font)

    if truncated:
        extra = len(display_lines) - max_visible
        draw.text(
            (pad_x + panel_width // 2, panel_top + panel_height - 22),
            f"\u2026 {extra} more line{'s' if extra != 1 else ''}",
            fill=(100, 100, 100), font=lnum_font, anchor="mm"
        )

    return img


def _parse_section_sub_blocks(content):
    """
    Parses combined section content into a list of sub-blocks.
    Detects fenced code blocks (```python ... ```), output blocks (>>>output...<<<),
    and plain text.
    Returns list of dicts: [{'type': 'code'|'text'|'output', 'content': str, 'weight': int}]
    """
    blocks = []
    # Split on fenced code blocks and output blocks, keeping delimiters
    parts = re.split(
        r'(```(?:python)?\s*\n.*?\n```|>>>output\n.*?\n<<<)',
        content, flags=re.DOTALL
    )

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check if this part is a fenced code block
        code_match = re.match(r'^```(?:python)?\s*\n(.*?)\n```$', part, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            if code:
                blocks.append({
                    'type': 'code',
                    'content': code,
                    'weight': max(2, len(code.split('\n'))),
                })
            continue

        # Check if this part is an output block
        output_match = re.match(r'^>>>output\n(.*?)\n<<<$', part, re.DOTALL)
        if output_match:
            output = output_match.group(1).strip()
            if output:
                blocks.append({
                    'type': 'output',
                    'content': output,
                    'weight': max(1, len(output.split('\n'))),
                })
            continue

        # Plain text
        cleaned = re.sub(r'\n?-{3,}\n?', '\n', part).strip()
        cleaned = re.sub(r'^#{1,6}\s*', '', cleaned, flags=re.MULTILINE).strip()
        if cleaned:
            blocks.append({
                'type': 'text',
                'content': cleaned,
                'weight': max(1, len(split_into_sentences(cleaned))),
            })

    return blocks


def _render_code_panel_inline(code_text, frame_width, pad_x, start_y, text_font, frame_img):
    """
    Draws a VS Code-style dark code panel directly onto an existing Pillow RGBA image
    at the given Y offset.  Returns the updated cursor_y (bottom of the panel).
    """
    from PIL import ImageDraw, ImageFont as PILFont

    draw = ImageDraw.Draw(frame_img)

    panel_left = pad_x
    panel_right = frame_width - pad_x
    panel_width = panel_right - panel_left
    header_h = 38
    font_size = 24
    lnum_size = 20

    # Load monospace font
    code_font = lnum_font = None
    for fp in [r"C:\Windows\Fonts\courbd.ttf", r"C:\Windows\Fonts\cour.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
        try:
            code_font = PILFont.truetype(fp, font_size)
            lnum_font = PILFont.truetype(fp, lnum_size)
            break
        except (IOError, OSError):
            continue
    if code_font is None:
        code_font = lnum_font = PILFont.load_default()

    try:
        header_font = PILFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
    except (IOError, OSError):
        header_font = lnum_font

    # Prepare code lines
    max_chars = 46
    raw_lines = code_text.replace('\t', '    ').split('\n')
    display_lines = []
    for raw in raw_lines:
        display_lines.append(raw[:max_chars - 1] + '\u2026' if len(raw) > max_chars else raw)

    line_height = font_size + 10
    max_visible = min(len(display_lines), 18)  # Cap at 18 lines for inline panels
    visible_lines = display_lines[:max_visible]
    truncated = len(display_lines) > max_visible

    panel_height = len(visible_lines) * line_height + header_h + 20
    panel_bottom = start_y + panel_height

    # Panel background (#1E1E1E)
    draw.rounded_rectangle(
        [panel_left, start_y, panel_right, panel_bottom],
        radius=12, fill=(30, 30, 30, 248)
    )
    # Header bar (#2D2D2D)
    draw.rounded_rectangle(
        [panel_left, start_y, panel_right, start_y + header_h],
        radius=12, fill=(45, 45, 45, 255)
    )
    draw.rectangle(
        [panel_left, start_y + header_h // 2, panel_right, start_y + header_h],
        fill=(45, 45, 45, 255)
    )

    # Traffic-light dots
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = panel_left + 16 + i * 22
        cy = start_y + header_h // 2
        r = 6
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Header label
    draw.text(
        (panel_left + panel_width // 2, start_y + header_h // 2),
        "script.py", fill=(160, 160, 160), font=header_font, anchor="mm"
    )

    # Line number gutter
    lnum_col_w = 44
    sep_x = panel_left + lnum_col_w + 4
    draw.line([(sep_x, start_y + header_h), (sep_x, panel_bottom)],
              fill=(55, 55, 55), width=1)

    code_x = sep_x + 10
    for i, line in enumerate(visible_lines):
        y = start_y + header_h + 8 + i * line_height
        draw.text(
            (sep_x - 6, y + (font_size - lnum_size) // 2),
            str(i + 1), fill=(80, 80, 80), font=lnum_font, anchor="ra"
        )
        draw.text((code_x, y), line, fill=(212, 212, 212), font=code_font)

    if truncated:
        extra = len(display_lines) - max_visible
        draw.text(
            (panel_left + panel_width // 2, panel_bottom - 16),
            f"\u2026 {extra} more line{'s' if extra != 1 else ''}",
            fill=(100, 100, 100), font=lnum_font, anchor="mm"
        )

    return panel_bottom


def _render_output_inline(output_text, frame_width, pad_x, start_y, frame_img):
    """
    Draws a console-style output panel directly onto an existing Pillow RGBA image
    at the given Y offset.  Dark green-tinted background with monospace white/green text.
    Returns the updated cursor_y (bottom of the panel).
    """
    from PIL import ImageDraw, ImageFont as PILFont

    draw = ImageDraw.Draw(frame_img)

    panel_left = pad_x
    panel_right = frame_width - pad_x
    panel_width = panel_right - panel_left
    header_h = 32
    font_size = 22
    label_size = 16

    # Load monospace font
    out_font = label_font = None
    for fp in [r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
        try:
            out_font = PILFont.truetype(fp, font_size)
            label_font = PILFont.truetype(fp, label_size)
            break
        except (IOError, OSError):
            continue
    if out_font is None:
        out_font = label_font = PILFont.load_default()

    # Prepare output lines
    max_chars = 46
    raw_lines = output_text.replace('\t', '    ').split('\n')
    display_lines = []
    for raw in raw_lines:
        display_lines.append(raw[:max_chars - 1] + '\u2026' if len(raw) > max_chars else raw)

    line_height = font_size + 8
    max_visible = min(len(display_lines), 12)  # Cap at 12 lines for output panels
    visible_lines = display_lines[:max_visible]
    truncated = len(display_lines) > max_visible

    panel_height = len(visible_lines) * line_height + header_h + 16
    panel_bottom = start_y + panel_height

    # Panel background — dark with slight green tint (#0D1A0D)
    draw.rounded_rectangle(
        [panel_left, start_y, panel_right, panel_bottom],
        radius=10, fill=(13, 26, 13, 245)
    )
    # Header bar (#1A2E1A)
    draw.rounded_rectangle(
        [panel_left, start_y, panel_right, start_y + header_h],
        radius=10, fill=(26, 46, 26, 255)
    )
    draw.rectangle(
        [panel_left, start_y + header_h // 2, panel_right, start_y + header_h],
        fill=(26, 46, 26, 255)
    )

    # Label: "Output"
    draw.text(
        (panel_left + 14, start_y + header_h // 2),
        "\u25b6 Output", fill=(80, 200, 80), font=label_font, anchor="lm"
    )

    # Output lines — green-tinted monospace text
    text_x = panel_left + 14
    for i, line in enumerate(visible_lines):
        y = start_y + header_h + 6 + i * line_height
        if y + line_height > panel_bottom - 8:
            break
        draw.text((text_x, y), line, fill=(160, 230, 160), font=out_font)

    if truncated:
        extra = len(display_lines) - max_visible
        draw.text(
            (panel_left + panel_width // 2, panel_bottom - 12),
            f"\u2026 {extra} more line{'s' if extra != 1 else ''}",
            fill=(80, 140, 80), font=label_font, anchor="mm"
        )

    return panel_bottom


def create_video_parallel(section, audio_file, output_file, logo_path, background_path, text_sync_file,
                          font_styles, notebook_title=None):
    """Creates a video segment with text overlays synchronized approximately."""
    # --- Unpack section tuple (now includes block_type) ---
    if len(section) == 3:
        title, content, block_type = section
    else:
        logger.warning("Received section tuple without block_type, defaulting to markdown.")
        title, content = section
        block_type = 'markdown' # Assume markdown if block_type is missing
    # --- End Unpack ---

    clips = []
    audio_clip = None
    bg_clip_raw = None
    bg_clip_resized = None
    bg_clip_looped = None
    dimming_clip = None
    logo_clip_main = None
    logo_clip_final = None
    title_text_clip = None
    text_clips = [] # Clips generated in loops (markdown/code)
    final_video = None
    target_size = (1080, 1920)

    try:
        # --- Pillow Compatibility Checks ---
        if not hasattr(Image, 'Resampling'): Image.Resampling = Image
        if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.Resampling.LANCZOS
        # --- End Checks ---

        logger.info(f"Starting video creation for: {os.path.basename(output_file)}")
        logger.debug(f"  Block Type: {block_type}")

        # --- Load Audio ---
        if not os.path.exists(audio_file): raise FileNotFoundError(f"Audio file not found: {audio_file}")
        audio_clip = AudioFileClip(audio_file)
        audio_duration = audio_clip.duration
        if audio_duration <= 0: raise ValueError(f"Audio file has zero or negative duration: {audio_file}")

        # --- Load Background ---
        if not os.path.exists(background_path): raise FileNotFoundError(f"Background video not found: {background_path}")
        bg_clip_raw = VideoFileClip(background_path)
        if bg_clip_raw.duration <= 0: raise ValueError(f"Background video has zero or negative duration: {background_path}")

        logger.debug(f"Resizing background to {target_size}")
        bg_clip_resized = bg_clip_raw.resize(target_size)
        loops = int(audio_duration // bg_clip_resized.duration) + 1
        bg_clip_looped = bg_clip_resized.loop(n=loops).set_duration(audio_duration)
        clips.append(bg_clip_looped) # Add background first

        # --- Dimming Overlay ---
        dimming_clip = ColorClip(size=target_size, color=(0, 0, 0), ismask=False)
        dimming_clip = dimming_clip.set_duration(audio_duration).set_opacity(0.7)
        clips.append(dimming_clip) # Add dimming overlay

        # --- Prepare Logo ---
        logo_clip_main = None # Initialize
        logo_height = 100
        logo_margin_top = 20
        logo_margin_right = 20
        logo_actual_width = 0 # Initialize width
        if logo_path: # Check if a path was provided (existence checked in tasks.py)
            try:
                logo_clip_main = (ImageClip(logo_path, transparent=True)
                                 .set_duration(audio_duration)
                                 .resize(height=logo_height)
                                 .margin(top=logo_margin_top, right=logo_margin_right, opacity=0)
                                 .set_position(("right", "top")))
                logo_actual_width = logo_clip_main.w # Get width after potential margin effects
            except Exception as logo_err:
                 logger.warning(f"Could not load or process logo '{logo_path}': {logo_err}. Skipping logo.")
                 logo_clip_main = None # Explicitly set to None on error
        else:
            logger.info("No logo path provided or logo not found. Skipping logo.")
            logo_clip_main = None # Explicitly set to None if path invalid

        # --- Prepare Notebook Title Text (if logo exists and not 'Thank You') ---
        title_text_clip = None # Initialize
        # Check if it's the special slide based on the ORIGINAL title from the section tuple
        is_thank_you_slide_by_title = "great job" in title.lower()

        if logo_clip_main and notebook_title and not is_thank_you_slide_by_title:
            title_text_clip_instance = None # Temp instance before positioning
            try:
                title_fontsize = 24
                # Vertically center roughly with logo
                title_y_pos = logo_margin_top + (logo_height // 2) - (title_fontsize // 2)

                # Create the clip first to get its width
                title_text_clip_instance = TextClip(notebook_title,
                                          fontsize=title_fontsize,
                                          font=font_styles.get("font", "Inter"),
                                          color=font_styles.get("text_color", "white"),
                                          method="label", # Use label for better size control
                                          align='East') # Align text to the right edge of its box

                # Calculate position for the LEFT edge of the title clip
                title_padding = 10 # Pixels between title and logo
                title_x_pos_left_edge = target_size[0] - logo_margin_right - logo_actual_width - title_padding - title_text_clip_instance.w

                # Apply duration and position
                title_text_clip = title_text_clip_instance.set_duration(audio_duration).set_position((title_x_pos_left_edge, title_y_pos))

            except Exception as title_clip_err:
                 logger.warning(f"Could not create notebook title text clip: {title_clip_err}")
                 title_text_clip = None # Ensure it's None on error

        # --- Prepare Text Clips & Handle Slide Type ---
        # Use the flag derived from the original title
        if is_thank_you_slide_by_title:
             # --- Special "Thank You" Slide Logic with Fades ---
             logger.info(f"Detected 'Thank You' slide for {output_file}")
             thank_you_text = "Thank you for learning\nwith thenumerix!"
             text_clip_ty = (TextClip(thank_you_text, # Use different variable name
                                  fontsize=72, font=font_styles.get("font", "Inter"),
                                  color=font_styles.get("text_color", "white"),
                                  method="caption", size=(target_size[0] - 100, None), align='center')
                         .set_duration(audio_duration) # Set full duration initially
                         .set_position(("center", "center"))) # Center vertically too

             # --- Fixed Timing Logic ---
             text_display_duration = 3.0
             logo_display_duration = 3.0

             # Set text clip to display for the fixed duration
             text_clip_timed = text_clip_ty.set_start(0).set_duration(text_display_duration)
             clips.append(text_clip_timed) # Add timed text clip

             logo_clip_final = None # Initialize
             if logo_path: # Check if logo path exists
                 try:
                     # Create the large centered logo
                     logo_clip_final = (ImageClip(logo_path, transparent=True)
                                     .resize(height=600)
                                     .set_position("center"))

                     # Set logo clip to start after text and display for its fixed duration
                     logo_start_time = text_display_duration
                     logo_clip_timed = logo_clip_final.set_start(logo_start_time).set_duration(logo_display_duration)
                     clips.append(logo_clip_timed) # Add timed logo clip
                     logger.debug("Added large centered logo for 'Thank You' slide.")
                 except Exception as final_logo_err:
                      logger.warning(f"Could not create final centered logo: {final_logo_err}")
                      logo_clip_final = None # Explicitly set to None on error
             # --- End Special "Thank You" Slide Logic ---

        elif block_type == 'code':
            # --- Code Block Handling (VS Code-style Pillow panel) ---
            logger.info(f"Processing as Code Block for {output_file}")
            if logo_clip_main: clips.append(logo_clip_main)
            if title_text_clip: clips.append(title_text_clip)

            code_content_cleaned = clean_header_hashes(content)
            try:
                code_img = render_code_panel_image(code_content_cleaned, target_size)
                code_arr = np.array(code_img)
                clip = (ImageClip(code_arr, ismask=False)
                        .set_position((0, 0))
                        .set_duration(audio_duration))
                text_clips.append(clip)
                # Sync data uses original content for potential future use
                text_sync_data = [{"text": content, "start_time": 0.0, "end_time": round(audio_duration, 2)}]
                try:
                    with open(text_sync_file, 'w', encoding='utf-8') as f:
                        json.dump(text_sync_data, f, indent=4, ensure_ascii=False)
                    logger.debug(f"📝 Synced text JSON saved for code block: {text_sync_file}")
                except Exception as jerr:
                    logger.warning(f"⚠️ Failed to write sync JSON for code block '{text_sync_file}': {jerr}")

            except Exception as text_clip_err:
                 logger.error(f"Failed to create code panel for {output_file}: {text_clip_err}", exc_info=True)
            # --- End Code Block Handling ---

        else: # Default: Markdown / Section Block
            # --- Section Processing with Code Panel Detection ---
            logger.info(f"Processing as Section Block for {output_file}")
            if logo_clip_main: clips.append(logo_clip_main)
            if title_text_clip: clips.append(title_text_clip)

            # Large section heading above the text content
            try:
                sec_heading = (
                    TextClip(
                        clean_header_hashes(title),
                        fontsize=52, font=font_styles.get("font", "Inter"),
                        color="white", method='label', align='center',
                        stroke_color='black', stroke_width=1,
                    )
                    .set_position(("center", 115))
                    .set_duration(audio_duration)
                )
                text_clips.append(sec_heading)
            except Exception as sh_err:
                logger.warning(f"Could not create section heading: {sh_err}")

            # Parse content into sub-blocks (text vs code)
            sub_blocks = _parse_section_sub_blocks(content)
            text_sync_data = []

            if sub_blocks:
                font = font_styles.get("font", "Inter")
                font_size = font_styles.get("font_size", 36)
                text_color = font_styles.get("text_color", "white")

                # --- Build a single composite frame with ALL content stacked vertically ---
                from PIL import Image as PILImage, ImageDraw, ImageFont as PILFont
                W, H = target_size
                frame_img = PILImage.new('RGBA', (W, H), (0, 0, 0, 0))

                # Load text fonts for Pillow rendering
                text_font = None
                for fp in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf",
                           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
                    try:
                        text_font = PILFont.truetype(fp, font_size)
                        break
                    except (IOError, OSError):
                        continue
                if text_font is None:
                    text_font = PILFont.load_default()

                pad_x = 50
                cursor_y = 190  # Start below the section heading
                max_text_width = W - (pad_x * 2)

                for bi, block in enumerate(sub_blocks):
                    if cursor_y >= H - 60:
                        break  # Stop if we've run out of vertical space

                    if block['type'] == 'code':
                        # Render a VS Code-style code panel directly onto the frame
                        code_mini = _render_code_panel_inline(
                            block['content'], W, pad_x, cursor_y, text_font, frame_img
                        )
                        cursor_y = code_mini  # Updated cursor position
                        cursor_y += 10  # Small gap before output (if any)

                    elif block['type'] == 'output':
                        # Render console-style output panel below the code
                        output_bottom = _render_output_inline(
                            block['content'], W, pad_x, cursor_y, frame_img
                        )
                        cursor_y = output_bottom
                        cursor_y += 20  # Gap after output

                    else:
                        # Render wrapped text lines onto the frame
                        draw = ImageDraw.Draw(frame_img)
                        # Word-wrap the text
                        words = block['content'].split()
                        lines = []
                        current_line = ""
                        for word in words:
                            test_line = f"{current_line} {word}".strip()
                            bbox = draw.textbbox((0, 0), test_line, font=text_font)
                            if bbox[2] - bbox[0] <= max_text_width:
                                current_line = test_line
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = word
                        if current_line:
                            lines.append(current_line)

                        line_h = font_size + 10
                        for line in lines:
                            if cursor_y + line_h > H - 40:
                                break
                            # Center text horizontally
                            bbox = draw.textbbox((0, 0), line, font=text_font)
                            lw = bbox[2] - bbox[0]
                            x = (W - lw) // 2
                            draw.text((x, cursor_y), line, fill=(255, 255, 255, 255), font=text_font)
                            cursor_y += line_h

                        cursor_y += 16  # Gap after text block

                # Convert the full frame to a single clip that stays on screen the whole time
                frame_arr = np.array(frame_img)
                content_clip = (ImageClip(frame_arr, ismask=False)
                                .set_position((0, 0))
                                .set_duration(audio_duration))
                text_clips.append(content_clip)

                # Sync data for the entire section
                text_sync_data = [{"text": content, "start_time": 0.0, "end_time": round(audio_duration, 2)}]

                try:
                    with open(text_sync_file, 'w', encoding='utf-8') as f:
                        json.dump(text_sync_data, f, indent=4, ensure_ascii=False)
                    logger.debug(f"📝 Synced text JSON saved: {text_sync_file}")
                except Exception as jerr:
                    logger.warning(f"⚠️ Failed to write sync JSON '{text_sync_file}': {jerr}")

            else:
                 logger.warning(f"No sub-blocks to process for {output_file}")
            # --- End Normal Markdown Text Processing ---

        # Add all generated text clips from loops (markdown/code) to the main clips list
        # Note: Thank You slide text/logo were added directly to clips earlier
        clips.extend(text_clips)

        # --- Compose Final Video ---
        if not clips:
            logger.error(f"No clips generated for {output_file}, cannot compose video.")
            raise ValueError("No clips available to compose the video.")

        logger.debug(f"Composing final video for {output_file} with {len(clips)} layers.")
        # Ensure background/dimming are the base layers
        final_video = CompositeVideoClip(clips, size=target_size).set_duration(audio_duration).set_audio(audio_clip)

        # --- Write Video File ---
        logger.info(f"Writing video file: {output_file}")
        final_video.write_videofile(
            output_file,
            fps=24, codec='libx264', audio_codec='aac', preset='ultrafast',
            threads=max(1, os.cpu_count() // 2), logger='bar', # Use 'bar' for progress
            temp_audiofile=f'temp-audio-{os.path.basename(output_file)}.m4a', remove_temp=True
        )
        logger.info(f"✅ Finished video: {output_file}")

    except Exception as e:
        logger.error(f"❌ Error creating video for {output_file}: {e}", exc_info=True)
        # Re-raise the exception so the Celery task knows it failed
        raise e

    finally:
        # --- Cleanup Resources ---
        logger.debug(f"Cleaning up resources for {output_file}")
        # Ensure all potential clip variables are included
        resources_to_close = [
            audio_clip, bg_clip_raw, bg_clip_resized, bg_clip_looped,
            dimming_clip, logo_clip_main, logo_clip_final, title_text_clip
        ] + text_clips + [final_video] # Add text_clips list and final_video

        for resource in resources_to_close:
            # Check if it's a list/tuple (like text_clips) - handle elements individually
            if isinstance(resource, (list, tuple)):
                for item in resource:
                    # Check if item is not None and has a close method
                    if item and hasattr(item, 'close') and callable(item.close):
                        try:
                            item.close()
                        except Exception as close_err:
                            logger.warning(f"Error closing resource item {type(item).__name__}: {close_err}")
            # Handle single clip objects
            elif resource and hasattr(resource, 'close') and callable(resource.close):
                try:
                    resource.close()
                except Exception as close_err:
                    logger.warning(f"Error closing resource {type(resource).__name__}: {close_err}")

        # --- Temp Audio File Cleanup ---
        # Construct temp audio path based on output filename
        temp_audio_path = f'temp-audio-{os.path.basename(output_file)}.m4a'
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                logger.debug(f"Removed temporary audio file: {temp_audio_path}")
            except OSError as rm_err:
                logger.warning(f"Could not remove temporary audio file {temp_audio_path}: {rm_err}")
