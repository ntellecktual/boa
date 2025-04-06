import json
import os
import nbformat
from django.http import JsonResponse
from gtts import gTTS
from django.conf import settings

def process_notebook(file_path):
    """
    Extracts titles and their corresponding content from a Jupyter Notebook, including both top-level and second-level headers.

    Args:
    file_path (str): The path to the Jupyter Notebook file.

    Returns:
    list: A list of tuples, each containing the title and corresponding content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb_content = nbformat.read(f, as_version=4)

        sections = []
        current_title = None
        current_content = []

        for cell in nb_content.cells:
            if cell.cell_type == 'markdown':
                for line in cell['source'].split('\n'):
                    # Check for headers
                    if (line.startswith('# ') or line.startswith('## ')) and line[2:].strip():
                        if current_title and current_content:
                            content_text = '\n'.join(current_content).strip()
                            if content_text:
                                sections.append((current_title, content_text))
                        current_title = line.strip()  # Keep the leading # or ##
                        current_content = [line.lstrip('#').strip()]
                    elif current_title:
                        current_content.append(line)
            elif cell.cell_type == 'code' and current_title:
                current_content.append(cell['source'])

        if current_title and current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text:
                sections.append((current_title, content_text))

        return sections

    except FileNotFoundError:
        print(f'File not found: {file_path}')
        return []
    except PermissionError:
        print(f'Permission denied: {file_path}. Please check file permissions.')
        return []
    except Exception as e:
        print(f'Error extracting content from {file_path}: {str(e)}')
        return []

def text_to_speech(text, output_file):
    """
    Converts text to speech and saves it as an MP3 file.

    Args:
    text (str): The text to convert to speech.
    output_file (str): The path to save the audio file.
    """
    if not text.strip():
        print(f"Skipped empty content for {output_file}")
        return
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    print(f'Audio content written to {output_file}')

def handle_uploaded_file(f):
    """
    Handles file upload and saves it to the upload directory.

    Args:
    f (UploadedFile): The uploaded file object.

    Returns:
    str: File path of the uploaded file.
    """
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_files')

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path

def process_notebook_and_create_audio(file_path):
    """
    Processes the notebook and creates audio files for each section using text-to-speech.

    Args:
    file_path (str): The path to the Jupyter Notebook file.

    Returns:
    list: A list of audio file details.
    """
    sections = process_notebook(file_path)
    audio_files = []
    total_sections = len(sections)

    try:
        if sections:
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)

            for index, (title, content) in enumerate(sections, start=1):
                sanitized_title = title.replace(" ", "_").replace("#", "").replace("/", "_").strip()
                first_word = sanitized_title.split('_')[0]
                folder_path = os.path.join(audio_dir, first_word)

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                audio_file = os.path.join(folder_path, f'{index:02d}___{sanitized_title}.mp3')

                # Convert text to speech and save
                text_to_speech(content, audio_file)
                audio_files.append({'title': f'{index:02d}___{sanitized_title}', 'path': audio_file})

            # Save sections to JSON for record-keeping
            with open('sections.json', 'w') as f:
                json.dump(sections, f)
            print('Sections and audio files created.')

        return audio_files

    except Exception as e:
        print(f'Error processing notebook: {str(e)}')
        return []
