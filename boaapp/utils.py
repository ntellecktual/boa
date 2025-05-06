import os
import random
import logging
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)

def _get_video_paths(audio_file_instance):
    """
    Determines the expected video output directory, video file path (absolute),
    and sync file path based on the AudioFile instance and its file path.
    Handles the new audio filename format: index_SectionTitle.mp3
    Uses pathlib for more robust path handling.
    """
    try:
        # Ensure the input is treated as a relative path string
        relative_audio_path_str = str(audio_file_instance.file.name)
        relative_audio_path = Path(relative_audio_path_str)
        logger.debug(f"[_get_video_paths] Processing audio path: {relative_audio_path}")

        # Get path parts directly from the pathlib object
        parts = relative_audio_path.parts
        # Example: Path("audio/notebook/file.mp3").parts -> ('audio', 'notebook', 'file.mp3')

        # --- Define conditions using pathlib attributes ---
        # Check if the path has exactly 3 parts and is relative
        is_expected_structure = (
            len(parts) == 3 and
            not relative_audio_path.is_absolute() and
            parts[0] == 'audio' and
            relative_audio_path.suffix.lower() == '.mp3'
        )
        # --- End condition definitions ---

        if is_expected_structure:
            # Path structure is as expected
            notebook_sanitized_name = parts[1] # Second part is the notebook name
            audio_basename = relative_audio_path.stem # Filename without extension

            # Construct paths using pathlib
            relative_video_dir = Path('video') / notebook_sanitized_name
            # Combine MEDIA_ROOT and the relative video dir
            video_output_dir_abs = Path(settings.MEDIA_ROOT) / relative_video_dir

            video_filename = f"{audio_basename}.mp4"
            video_path_abs = video_output_dir_abs / video_filename

            sync_filename = f"{audio_basename}_sync.json"
            sync_file_path = video_output_dir_abs / sync_filename

            logger.debug(f"[_get_video_paths] Determined video dir: {video_output_dir_abs}, video path: {video_path_abs}, sync path: {sync_file_path}")
            # Return paths as strings if needed by downstream functions
            return str(video_output_dir_abs), str(video_path_abs), str(sync_file_path)
        else:
            # Path structure is NOT as expected - Log detailed reasons
            logger.warning(f"[_get_video_paths] Unexpected audio path structure: {relative_audio_path_str}") # Log original string
            logger.warning(f"[_get_video_paths] Path object: {relative_audio_path}")
            logger.warning(f"[_get_video_paths] Path parts found ({len(parts)}): {parts}")
            # Log specific reasons for failure
            if relative_audio_path.is_absolute():
                 logger.warning(f"[_get_video_paths] Reason: Path is absolute.")
            if len(parts) != 3:
                 logger.warning(f"[_get_video_paths] Reason: Expected 3 path parts, got {len(parts)}.")
            # Check parts length before accessing index 0
            if len(parts) == 0 or parts[0] != 'audio':
                 logger.warning(f"[_get_video_paths] Reason: First part is not 'audio' (or path is empty). Parts: {parts}")
            if relative_audio_path.suffix.lower() != '.mp3':
                 logger.warning(f"[_get_video_paths] Reason: File suffix is '{relative_audio_path.suffix}', expected '.mp3'.")

            return None, None, None

    except Exception as e:
        # Log the original path string in case of error during Path() creation
        try:
            path_str = str(audio_file_instance.file.name)
        except Exception:
            path_str = "[Could not get path string]"
        # Log the specific error along with the traceback
        logger.error(f"[_get_video_paths] Error determining video paths for audio PK {audio_file_instance.pk} (path='{path_str}'): {e}", exc_info=True)
        return None, None, None

def _get_random_background(default_bg_path):
    """Selects a random video background path."""
    background_dir = os.path.dirname(default_bg_path)
    try:
        all_files = os.listdir(background_dir)
        video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))]
        if video_files:
            chosen_file = random.choice(video_files)
            logger.info(f"Using random background: {chosen_file}")
            return os.path.join(background_dir, chosen_file)
        else:
            logger.warning(f"No video files found in background directory: {background_dir}. Using default.")
            return default_bg_path
    except FileNotFoundError:
        logger.error(f"Background directory not found: {background_dir}. Using default.")
        return default_bg_path
    except Exception as e:
        logger.error(f"Error selecting random background: {e}. Using default.")
        return default_bg_path

