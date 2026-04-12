# c:\Users\Kieth\Documents\Repositories\thenumerix\Belonging.Opportunity.Acceptance\boa\boaapp\process_notebook.py
import asyncio
import logging
import os
import re

import edge_tts
import markdown
import nbformat
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Microsoft Azure Neural TTS — free, no API key, natural expressive voice
TTS_VOICE = "en-US-AriaNeural"  # Warm, engaging female voice ideal for educational content


async def _tts_async(text: str, output_file: str, voice: str) -> None:
    """Async call to edge-tts; saves MP3 directly to output_file."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def _tts_clean_for_speech(text: str) -> str:
    """
    Strips markdown/code symbols so the neural voice reads naturally.
    Converts Python operators to spoken equivalents.
    """
    if not text:
        return ""
    # Remove markdown heading markers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*\n]+)\*{1,3}', r'\1', text)
    # Remove inline code backticks but keep the text
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    # Remove markdown links, keep label
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^-{3,}\s*$', '', text, flags=re.MULTILINE)
    # Make Python operators speakable
    text = text.replace('!=', ' is not equal to ')
    text = text.replace('==', ' equals ')
    text = text.replace('>=', ' greater than or equal to ')
    text = text.replace('<=', ' less than or equal to ')
    text = text.replace('->', ' to ')
    text = text.replace('=>', ' giving ')
    text = text.replace('()', '')
    # Clean residual symbols
    text = re.sub(r'[\[\]{}]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _add_speech_pacing(text):
    """
    Adds natural pauses and pacing cues for the TTS engine.
    Neural voices like AriaNeural interpret punctuation as pause signals:
    - Period/question mark → longer pause
    - Comma → short pause
    - Ellipsis → medium reflective pause
    - Paragraph break → natural topic pause
    """
    if not text:
        return text
    # Ensure paragraph breaks become spoken pauses (ellipsis + period)
    text = re.sub(r'\n\n+', '. ... ', text)
    # Single newlines become sentence-level pauses
    text = re.sub(r'\n', '. ', text)
    # Ensure proper spacing after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    # Add a brief pause before introducing a new concept (after colons)
    text = re.sub(r':\s*', ': ... ', text)
    # Clean up multiple spaces and dots
    text = re.sub(r'\.\s*\.\s*\.\s*\.+', '... ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _rewrite_with_llm(section_title, cells, notebook_title=""):
    """
    Uses an LLM (Claude or GPT-4o) to rewrite notebook section content into
    a polished, engaging educational narration script suitable for TTS.

    Falls back to None if no API key is configured or the call fails,
    letting the caller use the basic TTS cleaning approach instead.
    """
    from django.conf import settings as django_settings
    api_key = django_settings.ANTHROPIC_API_KEY
    openai_key = django_settings.OPENAI_API_KEY
    use_llm = django_settings.USE_LLM

    if not use_llm:
        logger.info(f"USE_LLM=False — skipping LLM narration for '{section_title}'")
        return None

    if not api_key and not openai_key:
        logger.info("No LLM API key configured — using basic TTS cleaning fallback.")
        return None

    # Build context from cells
    cell_descriptions = []
    for cell in cells:
        if cell['type'] == 'markdown':
            cell_descriptions.append(f"[Markdown]\n{cell['content']}")
        elif cell['type'] == 'code':
            cell_descriptions.append(f"[Code]\n{cell['content']}")
    raw_content = "\n\n".join(cell_descriptions)

    prompt = (
        "You are a professional educational course narrator. Rewrite the following "
        "notebook section into a smooth, engaging narration script that will be read "
        "aloud by a text-to-speech engine.\n\n"
        f"Notebook: {notebook_title}\n"
        f"Section: {section_title}\n\n"
        f"Raw content from the notebook:\n{raw_content}\n\n"
        "Rules:\n"
        "- Write in a warm, conversational teaching style — as if explaining to a "
        "student one-on-one.\n"
        "- Do NOT read or recite any code. Instead, explain WHAT the code does, "
        "WHY it is written that way, and what the output or result means.\n"
        "- If code outputs or results are shown, briefly describe what they reveal "
        "or demonstrate.\n"
        "- Use natural transitions between concepts.\n"
        "- Write in short, clear sentences. Each sentence should convey one idea.\n"
        "- Use proper punctuation to create natural pauses: periods for full stops, "
        "commas for brief pauses, and ellipses for reflective moments.\n"
        "- Between major ideas or paragraphs, add a sentence break so the listener "
        "has time to absorb each point.\n"
        "- Read at the pace of a patient teacher, not a rushed lecturer.\n"
        "- Avoid markdown formatting, symbols, or anything that would not sound right "
        "when spoken aloud.\n"
        "- Keep the narration concise but thorough — aim for 2-4 paragraphs.\n"
        "- Start directly with the content — no 'Welcome to' or 'In this section' "
        "filler.\n"
        "- Do not include any stage directions or notes like [pause] or (narrator).\n\n"
        "Return ONLY the narration text, nothing else."
    )

    try:
        if api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            narration = response.content[0].text.strip()
            logger.info(f"LLM narration generated for '{section_title}' ({len(narration)} chars)")
            return narration
        elif openai_key:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": "You are a professional educational course narrator."},
                    {"role": "user", "content": prompt},
                ],
            )
            narration = response.choices[0].message.content.strip()
            logger.info(f"LLM narration generated for '{section_title}' ({len(narration)} chars)")
            return narration
    except Exception as e:
        logger.warning(f"LLM narration failed for '{section_title}': {e}. Using fallback.")
        return None


def _extract_cell_output(cell):
    """
    Extracts stored output text from a notebook code cell.
    Returns the combined text/plain output, or empty string if none.
    """
    output_parts = []
    for output in cell.get('outputs', []):
        otype = output.get('output_type', '')
        if otype == 'stream':
            output_parts.append(output.get('text', ''))
        elif otype in ('execute_result', 'display_data'):
            data = output.get('data', {})
            if 'text/plain' in data:
                output_parts.append(data['text/plain'])
        elif otype == 'error':
            # Skip tracebacks — not useful for narration video
            pass
    return '\n'.join(output_parts).strip()


def _try_execute_notebook(nb, file_path):
    """
    Executes the notebook in-memory to populate cell outputs.
    Returns the executed notebook, or the original if execution fails.
    """
    try:
        import nbclient
        client = nbclient.NotebookClient(
            nb, timeout=120, kernel_name='python3',
            resources={'metadata': {'path': os.path.dirname(file_path) or '.'}}
        )
        client.execute()
        logger.info("Notebook executed successfully to populate outputs.")
        return nb
    except Exception as e:
        logger.warning(f"Could not execute notebook for outputs: {e}")
        return nb


def process_notebook(file_path=None, notebook_json_str=None):
    """
    Processes notebook content into sections based on H1, H2, H3 headers.
    Accepts either a file path (legacy) or a raw JSON string (DB-stored).
    Returns a list of sections, each with a 'title' and a list of 'cells'.
    """
    try:
        if notebook_json_str:
            import io
            nb_content = nbformat.read(io.StringIO(notebook_json_str), as_version=4)
            notebook_basename = "Notebook"
        elif file_path:
            with open(file_path, encoding='utf-8') as f:
                nb_content = nbformat.read(f, as_version=4)
            notebook_basename = os.path.splitext(os.path.basename(file_path))[0]
        else:
            logger.error("process_notebook called with no file_path or notebook_json_str")
            return []

        # Check if any code cells have stored outputs; if not, try executing
        has_outputs = any(
            cell.cell_type == 'code' and cell.get('outputs', [])
            for cell in nb_content.cells
        )
        if not has_outputs:
            logger.info("No stored outputs found — attempting notebook execution.")
            nb_content = _try_execute_notebook(nb_content, file_path)

        sections = []
        current_section_cells = []
        current_title = notebook_basename

        for cell_index, cell in enumerate(nb_content.cells):
            is_header = False
            header_text = None

            if cell.cell_type == 'markdown':
                content = cell['source'].strip()
                if content:
                    lines = content.split('\n')
                    first_line = lines[0].strip()
                    # Check for H1, H2, H3
                    match = re.match(r'^(#{1,3})\s+(.*)', first_line) # Regex to find headers
                    if match:
                        is_header = True
                        header_text = match.group(2).strip() # Extract header text

                        # Finalize previous section if it had cells
                        if current_section_cells:
                            sections.append({
                                "title": current_title,
                                "cells": current_section_cells
                            })
                            logger.debug(f"Finalized section '{current_title}' with {len(current_section_cells)} cells.")

                        # Start new section
                        current_title = header_text # Update the current title
                        current_section_cells = [] # Reset cells
                        # Add the header cell itself to the new section
                        current_section_cells.append({"type": "markdown", "content": content})
                        logger.debug(f"Starting new section '{current_title}' at cell index {cell_index}.")

                    else: # Not a header, add to current section
                        current_section_cells.append({"type": "markdown", "content": content})
            elif cell.cell_type == 'code':
                 # Add code cell to the current section
                 content = cell['source'].strip()
                 if content: # Only add if there's actual code
                     output = _extract_cell_output(cell)
                     current_section_cells.append({"type": "code", "content": content, "output": output})


        # After the loop, add the last collected section
        if current_section_cells:
            sections.append({
                "title": current_title,
                "cells": current_section_cells
            })
            logger.debug(f"Finalized last section '{current_title}' with {len(current_section_cells)} cells.")

        logger.info(f"Processed notebook '{os.path.basename(file_path)}', found {len(sections)} sections.")
        if not sections:
             logger.warning(f"No sections generated for {file_path}. Check notebook structure.")
        return sections

    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        return []
    except Exception as e:
        logger.error(f'Error processing notebook into sections: {str(e)}', exc_info=True)
        return []


def _run_tts(clean_text, output_file, voice):
    """
    Runs edge-tts async call, handling event loop edge cases.
    Returns True if the file was written with non-zero size, False otherwise.
    """
    def _do_tts():
        try:
            asyncio.run(_tts_async(clean_text, output_file, voice))
            return True
        except RuntimeError:
            # Event loop already running — create a fresh one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_tts_async(clean_text, output_file, voice))
                return True
            finally:
                loop.close()

    _do_tts()
    # Verify the file was actually written with audio data
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        return True
    return False


def generate_audio_for_block(text, voice=TTS_VOICE, pre_cleaned=False):
    """
    Generates natural-sounding narration using Microsoft edge-tts neural voice.
    Returns audio bytes on success, or None on failure.
    Retries up to 3 times with exponential backoff on transient failure.
    """
    import tempfile
    import time as _time

    if not text or not text.strip():
        logger.warning("Skipped empty content for audio generation")
        return None

    if pre_cleaned:
        clean = _add_speech_pacing(text)
    else:
        clean = _add_speech_pacing(_tts_clean_for_speech(text))
    if not clean:
        logger.warning("Empty text after cleaning for audio generation")
        return None

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        logger.info(f"Generating neural TTS ({voice}) attempt {attempt}/{max_retries}")
        tmp_path = None
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.mp3')
            os.close(tmp_fd)

            if _run_tts(clean, tmp_path, voice):
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                if audio_bytes:
                    logger.info(f"Audio generated: {len(audio_bytes)} bytes")
                    return audio_bytes
                else:
                    logger.warning(f"TTS produced 0-byte file on attempt {attempt}")
            else:
                logger.warning(f"TTS produced 0-byte file on attempt {attempt}")
        except Exception as e:
            logger.warning(f"TTS attempt {attempt} failed: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        if attempt < max_retries:
            delay = 2 ** attempt  # 2s, 4s backoff
            logger.info(f"Retrying TTS in {delay}s...")
            _time.sleep(delay)

    logger.error(f"Failed to generate TTS after {max_retries} attempts")
    return None

def sanitize_title_for_filename(title):
    """Sanitizes a title string to be safe for filenames."""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*#]', '', title)
    # Replace spaces and multiple underscores/hyphens with a single underscore
    sanitized = re.sub(r'[\s_\-]+', '_', sanitized)
    # Limit length if necessary (e.g., 100 chars)
    return sanitized.strip('_')[:100]

def process_notebook_and_create_audio(file_path=None, notebook_json_str=None, notebook_title="Notebook"):
    """
    Processes notebook into sections based on headers, generates one audio per section.
    Accepts either a file_path (legacy) or notebook_json_str (DB-stored content).
    Returns a list of dicts containing audio bytes (not file paths).
    """
    sections = process_notebook(file_path=file_path, notebook_json_str=notebook_json_str)
    audio_files_info = []
    total_sections = len(sections)

    if not sections:
        logger.warning("No sections found in notebook")
        return []

    try:
        notebook_name_sanitized = sanitize_title_for_filename(notebook_title)

        for section_index, section_data in enumerate(sections):
            section_title = section_data['title']
            section_cells = section_data['cells']
            sanitized_section_title_for_file = sanitize_title_for_filename(section_title)

            tts_content_parts = []
            original_content_parts = []

            for cell in section_cells:
                if cell['type'] == 'code':
                    original_content_parts.append(f"```python\n{cell['content']}\n```")
                    output = cell.get('output', '')
                    if output:
                        original_content_parts.append(f">>>output\n{output}\n<<<")
                else:
                    original_content_parts.append(cell['content'])

                if cell['type'] == 'markdown':
                    try:
                        html = markdown.markdown(cell['content'], extensions=['extra', 'sane_lists'])
                        soup = BeautifulSoup(html, "html.parser")
                        cleaned_text = ' '.join(soup.get_text(separator=' ', strip=True).split())
                        if cleaned_text:
                            tts_content_parts.append(cleaned_text)
                    except Exception as md_err:
                        logger.error(f"Error processing markdown cell within section '{section_title}': {md_err}")
                        tts_content_parts.append("Error processing content.")

            notebook_display_title = notebook_title.replace('_', ' ').replace('-', ' ')
            narration = _rewrite_with_llm(section_title, section_cells, notebook_display_title)

            is_llm_narration = False
            if narration:
                tts_content = narration
                is_llm_narration = True
            else:
                tts_content = ' '.join(tts_content_parts)

            if not narration and section_index < total_sections - 1 and tts_content:
                tts_content = f"{section_title}. {tts_content}"

            is_final_great_job = False
            if section_index == (total_sections - 1) and tts_content:
                logger.info(f"Overriding TTS content for last section '{section_title}'")
                is_final_great_job = "great job" in section_title.lower()
                tts_content = "Thank you for learning with thenumerix!"

            if is_final_great_job:
                audio_filename_base = "THANKYOU"
            else:
                audio_filename_base = f'{section_index:02d}_{sanitized_section_title_for_file}'[:150]
            audio_filename = f'{audio_filename_base}.mp3'

            if tts_content and tts_content.strip():
                audio_bytes = generate_audio_for_block(tts_content, pre_cleaned=is_llm_narration)
                if audio_bytes:
                    audio_files_info.append({
                        'title': section_title,
                        'name': audio_filename,
                        'audio_data': audio_bytes,
                        'section_index': section_index,
                        'original_content': "\n\n---\n\n".join(original_content_parts),
                        'block_type': 'section'
                    })
                else:
                    logger.warning(f"Skipping audio info for section '{section_title}' due to TTS failure.")
            else:
                logger.warning(f"Skipping audio generation for section '{section_title}' due to empty content.")

        logger.info(f'✅ Audio generation complete for {len(audio_files_info)} sections.')
        return audio_files_info

    except Exception as e:
        logger.error(f'❌ Error processing notebook sections or creating audio: {str(e)}', exc_info=True)
        return []
