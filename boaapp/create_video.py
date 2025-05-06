import json
import os
os.environ["IMAGEMAGICK_BINARY"] = "C:\\Users\\Kieth\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"
import time
import re
import logging
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
    # Remove 1 to 3 '#' characters at the start, followed by optional space
    return re.sub(r'^#{1,3}\s*', '', text).strip()

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
            # --- Code Block Handling ---
            logger.info(f"Processing as Code Block for {output_file}")
            if logo_clip_main: clips.append(logo_clip_main)
            if title_text_clip: clips.append(title_text_clip)

            code_content_cleaned = clean_header_hashes(content) # Clean visual headers
            font = font_styles.get("code_font", "Courier-New")
            font_size = font_styles.get("code_font_size", 32)
            text_color = font_styles.get("code_text_color", "white")
            try:
                # Use cleaned content for the TextClip
                clip = (TextClip(code_content_cleaned, fontsize=font_size, color=text_color, font=font,
                                 method='caption', size=(target_size[0] - 100, None), align='west')
                        .set_position(("center", 250))
                        .set_duration(audio_duration))
                text_clips.append(clip) # Add to temporary list for normal clips
                # Sync data uses original content for potential future use
                text_sync_data = [{"text": content, "start_time": 0.0, "end_time": round(audio_duration, 2)}]
                # Save sync data for code block
                try:
                    with open(text_sync_file, 'w', encoding='utf-8') as f:
                        json.dump(text_sync_data, f, indent=4, ensure_ascii=False)
                    logger.debug(f"📝 Synced text JSON saved for code block: {text_sync_file}")
                except Exception as jerr:
                    logger.warning(f"⚠️ Failed to write sync JSON for code block '{text_sync_file}': {jerr}")

            except Exception as text_clip_err:
                 logger.error(f"Failed to create TextClip for code block in {output_file}: {text_clip_err}", exc_info=True)
            # --- End Code Block Handling ---

        else: # Default: Markdown Block
            # --- Normal Markdown Text Processing ---
            logger.info(f"Processing as Markdown Block for {output_file}")
            if logo_clip_main: clips.append(logo_clip_main)
            if title_text_clip: clips.append(title_text_clip)

            sentences = split_into_sentences(content)
            if sentences:
                font = font_styles.get("font", "Inter")
                font_size = font_styles.get("font_size", 36)
                text_color = font_styles.get("text_color", "white")
                text_sync_data = []
                current_time = 0.0
                num_sentences = len(sentences)
                chunk_duration = audio_duration / num_sentences if num_sentences > 0 else audio_duration

                for i, sentence in enumerate(sentences):
                    start = round(current_time, 2)
                    # Calculate end time, ensuring the last sentence fills remaining duration
                    end = round(start + chunk_duration, 2) if i < num_sentences - 1 else round(audio_duration, 2)
                    # Prevent zero or negative duration clips
                    clip_duration = max(0.01, end - start)
                    actual_end = start + clip_duration # Use calculated duration for sync data end time

                    sentence_cleaned = clean_header_hashes(sentence) # Clean visual headers
                    try:
                        # Use cleaned sentence for the TextClip
                        clip = (TextClip(sentence_cleaned, fontsize=font_size, color=text_color, font=font,
                                         method='caption', size=(target_size[0] - 100, None), align='center')
                                .set_position(("center", 250))
                                .set_start(start)
                                .set_duration(clip_duration))
                        text_clips.append(clip) # Add to temporary list for normal clips
                        # Sync data uses original sentence
                        text_sync_data.append({ "text": sentence, "start_time": start, "end_time": actual_end })
                        current_time = actual_end # Move time forward based on actual clip duration
                    except Exception as text_clip_err:
                         logger.error(f"Failed to create TextClip for sentence: '{sentence[:50]}...' in {output_file}: {text_clip_err}", exc_info=True)

                # Save sync data for markdown block
                try:
                    with open(text_sync_file, 'w', encoding='utf-8') as f:
                        json.dump(text_sync_data, f, indent=4, ensure_ascii=False)
                    logger.debug(f"📝 Synced text JSON saved for markdown block: {text_sync_file}")
                except Exception as jerr:
                    logger.warning(f"⚠️ Failed to write sync JSON for markdown block '{text_sync_file}': {jerr}")

            else:
                 logger.warning(f"No sentences to process for markdown block {output_file}")
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
