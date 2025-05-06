import os
import logging
from celery import shared_task
from django.conf import settings
import re
from django.contrib.auth import get_user_model
from pathlib import Path

# Import the functions that do the actual work
from .process_notebook import process_notebook_and_create_audio
from .create_video import create_video_parallel
from .models import Document, AudioFile
from .utils import _get_video_paths, _get_random_background

logger = logging.getLogger(__name__)
User = get_user_model() # Get the User model

# --- create_audio_files_task remains the same ---
@shared_task(bind=True) # bind=True gives access to self (the task instance)
def create_audio_files_task(self, document_pk, user_id):
    """
    Celery task to process a notebook and create audio files.
    """
    logger.info(f"Celery Task Started: create_audio_files_task for Document PK {document_pk}, User ID {user_id}")
    try:
        document = Document.objects.get(pk=document_pk)
        user = User.objects.get(pk=user_id)
        # Use pathlib for consistency
        notebook_file_path = Path(settings.MEDIA_ROOT) / document.uploaded_file.name

        if not notebook_file_path.exists():
            logger.error(f"Notebook file not found for Document PK {document_pk}: {notebook_file_path}")
            return {'status': 'FAILED', 'error': 'Notebook file not found'}

        # --- Replicate logic from handle_audio_creation ---
        # Assuming process_notebook_and_create_audio expects a string path
        audio_files_info = process_notebook_and_create_audio(str(notebook_file_path))
        total_files_to_create = len(audio_files_info)
        logger.info(f"Found {total_files_to_create} blocks to process for audio.")

        if total_files_to_create == 0:
            logger.warning(f"No audio files generated for Document PK {document_pk}.")
            return {'status': 'COMPLETE', 'audio_pks': []}

        generated_audio_db_pks = []
        for idx, audio_info in enumerate(audio_files_info):
            self.update_state(state='PROGRESS', meta={
                'current': idx + 1,
                'total': total_files_to_create,
                'status_message': f"Creating audio for: {audio_info['title']}"
            })

            title = audio_info['title']
            relative_path = audio_info['relative_path']
            full_path = audio_info['full_path'] # Assuming this is absolute
            section_index = audio_info['section_index']
            original_content = audio_info['original_content']
            block_type = audio_info['block_type']

            # Use Path for checking existence
            if not Path(full_path).exists():
                logger.warning(f"Audio file missing after generation: {full_path}. Skipping DB entry.")
                continue

            try:
                audio_file_obj = AudioFile.objects.create(
                    title=title,
                    # Use Pathlib to get basename safely
                    name=Path(relative_path).name,
                    file=relative_path, # Store relative path
                    user=user,
                    document=document,
                    metadata={
                        'section_index': section_index,
                        'block_type': block_type,
                        'original_content': original_content
                    }
                )
                generated_audio_db_pks.append(audio_file_obj.pk)
                logger.debug(f"AudioFile record created: {title} (PK: {audio_file_obj.pk})")
            except Exception as e:
                 logger.error(f"Error creating AudioFile record for {title}: {e}", exc_info=True) # Add exc_info
                 # Optionally: Clean up the generated audio file if DB save fails
                 # try: Path(full_path).unlink() except OSError: pass

        logger.info(f"Finished audio creation task for Document PK {document_pk}. Created {len(generated_audio_db_pks)} files.")
        return {'status': 'COMPLETE', 'audio_pks': generated_audio_db_pks}

    except Document.DoesNotExist:
        logger.error(f"Document PK {document_pk} not found for audio creation task.")
        return {'status': 'FAILED', 'error': 'Document not found'}
    except User.DoesNotExist:
         logger.error(f"User PK {user_id} not found for audio creation task.")
         return {'status': 'FAILED', 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Error in create_audio_files_task for Document PK {document_pk}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}

@shared_task(bind=True)
def create_single_video_task(self, audio_file_pk):
    """
    Celery task to create a single video file.
    Uses utility functions for path generation and background selection.
    """
    logger.info(f"Celery Task Started: create_single_video_task for AudioFile PK {audio_file_pk}")
    try:
        audio_file_obj = AudioFile.objects.get(pk=audio_file_pk)
        # --- Get and Clean Notebook Title ---
        cleaned_notebook_title = "Untitled" # Default title
        try:
            document = audio_file_obj.document
            if document and document.uploaded_file and document.uploaded_file.name:
                notebook_path = Path(document.uploaded_file.name)
                stem = notebook_path.stem # Filename without extension
                # Remove leading digits/hyphens/underscores, replace others with space
                cleaned_notebook_title = re.sub(r'^\d+[\s_-]+', '', stem).replace('-', ' ').replace('_', ' ')
                logger.debug(f"Cleaned notebook title: '{cleaned_notebook_title}' from '{notebook_path.name}'")
        except Exception as title_err:
            logger.warning(f"Could not determine cleaned notebook title for Audio PK {audio_file_pk}: {title_err}")
        # --- End Get and Clean Notebook Title ---
        # --- Get metadata ---
        metadata = audio_file_obj.metadata or {} # Ensure metadata is a dict
        section_index = metadata.get('section_index')
        block_type = metadata.get('block_type', 'markdown')
        original_content = metadata.get('original_content', '')
        section_title = audio_file_obj.title

        if section_index is None or original_content is None: # Check original_content too
            logger.error(f"Missing metadata (section_index or original_content) for AudioFile PK {audio_file_pk}.")
            return {'status': 'FAILED', 'error': 'Missing metadata'}

        section_tuple = (section_title, original_content, block_type)

        # --- Use _get_video_paths from utils.py ---
        video_output_dir_abs_str, output_path_str, sync_file_str = _get_video_paths(audio_file_obj)

        # Check if paths were determined successfully
        if not all([video_output_dir_abs_str, output_path_str, sync_file_str]):
            logger.error(f"Failed to determine video paths for AudioFile PK {audio_file_pk}. Check previous warnings.")
            # The specific reason should have been logged by _get_video_paths
            return {'status': 'FAILED', 'error': 'Could not determine video paths'}

        # Convert string paths back to Path objects if needed, or use strings directly
        video_output_dir_abs = Path(video_output_dir_abs_str)
        output_path = Path(output_path_str)
        sync_file = Path(sync_file_str)
        # --- End using _get_video_paths ---

        # Get absolute audio path
        audio_path_abs = Path(settings.MEDIA_ROOT) / audio_file_obj.file.name
        if not audio_path_abs.exists():
             logger.error(f"Audio file not found for PK {audio_file_pk}: {audio_path_abs}")
             return {'status': 'FAILED', 'error': 'Audio file not found'}

        # Ensure output directory exists
        video_output_dir_abs.mkdir(parents=True, exist_ok=True)

        # --- Get asset paths ---
        # Ensure STATICFILES_DIRS[0] is the correct place for your static assets
        logo_path = Path(settings.STATICFILES_DIRS[0]) / 'css' / 'img' / 'logo.png'
        default_background_path_str = str(Path(settings.BASE_DIR) / 'video' / 'background.mp4')

        # --- Use _get_random_background from utils.py ---
        background_path_str = _get_random_background(default_background_path_str)
        background_path = Path(background_path_str) # Convert to Path object
        # --- End using _get_random_background ---

        # Check asset existence
        logo_path_abs_str = str(logo_path) if logo_path.exists() else None
        if not logo_path_abs_str:
             logger.warning(f"Logo file not found at {logo_path}, proceeding without logo.")

        if not background_path.exists():
             logger.error(f"Selected background video not found: {background_path}")
             # Decide if you want to fail or try the default again
             default_bg_path_obj = Path(default_background_path_str)
             if default_bg_path_obj.exists():
                 logger.warning(f"Falling back to default background: {default_bg_path_obj}")
                 background_path = default_bg_path_obj
             else:
                 logger.error(f"Default background video also not found: {default_bg_path_obj}")
                 return {'status': 'FAILED', 'error': 'Background video not found'}

        font_styles = {
            "font": "Inter", "font_size": 36, "text_color": "white",
            "code_font": "Courier-New", "code_font_size": 32, "code_text_color": "#F0F0F0"
        }

        self.update_state(state='PROGRESS', meta={'status_message': f"Rendering video for: {audio_file_obj.title}"})

        # Call the video creation function (ensure it accepts Path objects or convert back to strings)
        create_video_parallel(
            section=section_tuple,
            audio_file=str(audio_path_abs),
            output_file=str(output_path),
            logo_path=logo_path_abs_str, # Pass the string path or None
            background_path=str(background_path),
            text_sync_file=str(sync_file),
            font_styles=font_styles,
            notebook_title=cleaned_notebook_title # Pass the cleaned title
        )

        logger.info(f"Finished video creation task for AudioFile PK {audio_file_pk}.")

        # Calculate relative path for the result using pathlib
        try:
            relative_video_path = output_path.relative_to(settings.MEDIA_ROOT).as_posix()
        except ValueError:
             logger.warning(f"Could not make video path relative to MEDIA_ROOT: {output_path}")
             relative_video_path = str(output_path) # Fallback to absolute path string

        # Optionally store video path in metadata
        # audio_file_obj.metadata['video_path'] = relative_video_path
        # audio_file_obj.save(update_fields=['metadata'])

        return {'status': 'COMPLETE', 'video_path': relative_video_path}

    except AudioFile.DoesNotExist:
        logger.error(f"AudioFile PK {audio_file_pk} not found for video creation task.")
        return {'status': 'FAILED', 'error': 'AudioFile not found'}
    except Exception as e:
        logger.error(f"Error in create_single_video_task for AudioFile PK {audio_file_pk}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}
