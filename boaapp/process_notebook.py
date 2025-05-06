# c:\Users\Kieth\Documents\Repositories\thenumerix\Belonging.Opportunity.Acceptance\boa\boaapp\process_notebook.py
import json
import os
import re # Import re
import nbformat
from gtts import gTTS
from django.conf import settings
import logging
import markdown
from bs4 import BeautifulSoup
import io # For in-memory audio data
from pydub import AudioSegment # For combining audio and adding silence

logger = logging.getLogger(__name__) # Set up logger for this module

# --- Keep process_notebook, handle_uploaded_file, sanitize_title_for_filename functions as they are ---

def process_notebook(file_path):
    """
    Processes notebook content into sections based on H1, H2, H3 headers.
    Returns a list of sections, each with a 'title' and a list of 'cells'
    (each cell being {'type': 'markdown'/'code', 'content': ...}).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb_content = nbformat.read(f, as_version=4)

        sections = []
        current_section_cells = []
        # Default title for content before the first header
        notebook_basename = os.path.splitext(os.path.basename(file_path))[0]
        current_title = notebook_basename # Use notebook name as default initial title

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
                     current_section_cells.append({"type": "code", "content": content})


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


def generate_audio_for_block(text, output_file):
    """
    Generates audio from text using gTTS.
    If the text starts with a header (#, ##, ###), it reads the cleaned header,
    adds a 1-second pause, and then reads the rest of the text.
    """
    if not text or not text.strip():
        logger.warning(f"Skipped empty content for {output_file}")
        return False

    # Define the header pattern
    header_pattern = r'^(#{1,3})\s*(.*)' # Capture '#' count and the header text
    match = re.match(header_pattern, text)

    if match:
        # --- Header Detected ---
        header_hashes, header_text_full = match.groups()
        # Find where the header text ends (first newline after header)
        first_newline_index = text.find('\n')
        if first_newline_index != -1:
            header_line = text[:first_newline_index].strip() # The full line including hashes
            body_text = text[first_newline_index:].strip() # The rest of the content
        else:
            # Block contains only the header line
            header_line = text.strip()
            body_text = ""

        # Clean the header line for speech (remove hashes)
        header_speech_text = re.sub(r'^#{1,3}\s*', '', header_line).strip()

        logger.info(f"Header detected: '{header_speech_text}'. Adding 1s pause for {os.path.basename(output_file)}.")

        try:
            # 1. Generate audio for header
            header_audio_fp = io.BytesIO()
            tts_header = gTTS(text=header_speech_text, lang='en')
            tts_header.write_to_fp(header_audio_fp)
            header_audio_fp.seek(0)
            header_segment = AudioSegment.from_file(header_audio_fp, format="mp3")

            # 2. Create 1 second of silence
            silence_segment = AudioSegment.silent(duration=1000) # duration in milliseconds

            # 3. Generate audio for body (if exists and not just whitespace)
            if body_text and body_text.strip():
                body_audio_fp = io.BytesIO()
                tts_body = gTTS(text=body_text, lang='en')
                tts_body.write_to_fp(body_audio_fp)
                body_audio_fp.seek(0)
                body_segment = AudioSegment.from_file(body_audio_fp, format="mp3")
                # Combine: header + silence + body
                combined_audio = header_segment + silence_segment + body_segment
            else:
                # Combine: header + silence (no body)
                combined_audio = header_segment + silence_segment

            # 4. Export combined audio
            combined_audio.export(output_file, format="mp3")
            logger.info(f'Audio content with pause written to {output_file}')
            return True

        except Exception as e:
            logger.error(f"Failed to generate TTS with pause for {output_file}: {e}", exc_info=True)
            return False
    else:
        # --- No Header Detected - Generate Normally ---
        logger.debug(f"No header detected. Generating audio normally for: {os.path.basename(output_file)}")
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_file)
            logger.info(f'Audio content written to {output_file}')
            return True
        except Exception as e:
            logger.error(f"Failed to generate TTS for {output_file}: {e}", exc_info=True)
            return False


def handle_uploaded_file(f):
    """Saves uploaded file to the 'documents' media directory."""
    # Consider adding unique identifiers to filenames to prevent overwrites if needed
    # e.g., using uuid: import uuid; unique_id = uuid.uuid4().hex[:8]; filename = f"{unique_id}_{f.name}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents') # Save directly to documents
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logger.info(f"Uploaded file saved to: {file_path}")
    return file_path

def sanitize_title_for_filename(title):
    """Sanitizes a title string to be safe for filenames."""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*#]', '', title)
    # Replace spaces and multiple underscores/hyphens with a single underscore
    sanitized = re.sub(r'[\s_\-]+', '_', sanitized)
    # Limit length if necessary (e.g., 100 chars)
    return sanitized.strip('_')[:100]

def process_notebook_and_create_audio(file_path):
    """
    Processes notebook into sections based on headers, generates one audio file per section,
    and preprocesses the combined section text for TTS.
    Returns a list of dictionaries containing info about generated audio files.
    """
    sections = process_notebook(file_path)
    audio_files_info = []
    total_sections = len(sections)

    if not sections:
        logger.warning(f"No sections found in notebook: {file_path}")
        return []

    try:
        base_audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
        os.makedirs(base_audio_dir, exist_ok=True)
        notebook_filename = os.path.basename(file_path)
        notebook_name_sanitized = sanitize_title_for_filename(os.path.splitext(notebook_filename)[0])
        notebook_audio_dir = os.path.join(base_audio_dir, notebook_name_sanitized)
        os.makedirs(notebook_audio_dir, exist_ok=True)
        logger.info(f"Audio directory for notebook: {notebook_audio_dir}")

        for section_index, section_data in enumerate(sections):
            section_title = section_data['title']
            section_cells = section_data['cells']
            sanitized_section_title_for_file = sanitize_title_for_filename(section_title)

            # --- Combine and Prepare Text for TTS for the entire section ---
            tts_content_parts = []
            original_content_parts = [] # Store original content for video if needed

            for cell in section_cells:
                original_content_parts.append(cell['content']) # Store raw cell content
                if cell['type'] == 'markdown':
                    try:
                        # Process markdown: Convert to HTML then extract text
                        html = markdown.markdown(cell['content'], extensions=['extra', 'sane_lists'])
                        soup = BeautifulSoup(html, "html.parser")
                        # Get text, replace multiple whitespace chars with single space
                        cleaned_text = ' '.join(soup.get_text(separator=' ', strip=True).split())
                        if cleaned_text:
                            tts_content_parts.append(cleaned_text)
                    except Exception as md_err:
                        logger.error(f"Error processing markdown cell within section '{section_title}': {md_err}")
                        tts_content_parts.append("Error processing content.")
                elif cell['type'] == 'code':
                    # Announce code blocks but don't include code content in TTS
                    tts_content_parts.append("Code block.")

            # Join the processed parts for the final TTS input for this section
            # Use newline as separator for potentially better phrasing by TTS
            tts_content = '\n'.join(tts_content_parts)

            # --- Last Section Override ---
            is_final_great_job = False # Flag for filename change
            # Apply override to the TTS content of the very last section
            if section_index == (total_sections - 1) and tts_content:
                 logger.info(f"Overriding TTS content for last section '{section_title}'")
                 # Check if the original title suggests it's the intended final slide
                 is_final_great_job = "great job" in section_title.lower()
                 tts_content = "Thank you for learning with thenumerix!"

            # --- Determine Audio Filename using section index and SANITIZED section title ---
            # Special case for the final "Thank You" audio file
            if is_final_great_job: # Check the flag set during override check
                audio_filename_base = "THANKYOU" # Use specific name
            else:
                audio_filename_base = f'{section_index:02d}_{sanitized_section_title_for_file}'[:150] # Limit length
            audio_filename = f'{audio_filename_base}.mp3'
            audio_file_path = os.path.join(notebook_audio_dir, audio_filename)
            audio_file_relative_path = os.path.join('audio', notebook_name_sanitized, audio_filename).replace('\\', '/')

            # --- Generate Audio for the section ---
            if tts_content and tts_content.strip():
                # Call the updated function to generate audio (handles pause)
                if generate_audio_for_block(tts_content, audio_file_path):
                    audio_files_info.append({
                        'title': section_title, # The actual header text for display
                        'name': audio_filename, # The generated filename
                        'relative_path': audio_file_relative_path,
                        'full_path': audio_file_path,
                        'section_index': section_index, # Index of the section (0-based)
                        # Store combined original content for video
                        'original_content': "\n\n---\n\n".join(original_content_parts), # Combine original cell content
                        'block_type': 'section' # Indicate this represents a whole section
                    })
                else:
                     logger.warning(f"Skipping audio info for section '{section_title}' due to TTS failure.")
            else:
                 logger.warning(f"Skipping audio generation for section '{section_title}' due to empty/whitespace TTS content after processing.")

        logger.info(f'✅ Audio generation complete for {len(audio_files_info)} sections from {file_path}.')
        return audio_files_info

    except Exception as e:
        logger.error(f'❌ Error processing notebook sections or creating audio: {str(e)}', exc_info=True)
        return []
