import json
import os
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from moviepy.editor import (AudioFileClip, ColorClip, CompositeVideoClip,
                            ImageClip, TextClip, VideoFileClip)

from .process_notebook import process_notebook


def create_video_parallel(section, audio_file, output_file, logo_path, background_path, text_sync_file):
    """
    Creates a video from code text and an audio file with a dimmed background in parallel,
    synchronized with the spoken words.

    Args:
    section (tuple): Tuple containing (title, code) extracted from the notebook.
    audio_file (str): The path to the audio file.
    output_file (str): The path to save the video file.
    logo_path (str): The path to the logo image file.
    background_path (str): The path to the background video file.
    text_sync_file (str): The path to the JSON file storing text synchronization data.
    """
    title, code = section

    try:
        print(f'Processing section: {title}')
        audio = AudioFileClip(audio_file)
        bg_clip = VideoFileClip(background_path).subclip(0, audio.duration)
        dimming = ColorClip(size=bg_clip.size, color=[0, 0, 0]).set_duration(
            audio.duration).set_opacity(0.7)
        logo = ImageClip(logo_path, transparent=True).set_duration(audio.duration).set_position(
            ("right", "top")).resize(height=100).margin(right=8, top=8)

        # Split code text into words
        words = code.split()
        text_sync_data = []

        # Calculate word durations and create clips for each word
        word_clips = []
        word_durations = audio.duration / len(words)
        padding_time = 0.05  # Padding time in seconds for verification
        fontsize = 24  # Start with the original font size

        for i, word in enumerate(words):
            start_time = (word_durations * i) + padding_time
            end_time = (word_durations * (i + 1)) + padding_time

            # Create text clip
            word_clip = TextClip(
                word, fontsize=fontsize, color='white', font='Arial-Bold', size=(1080, None))

            word_clips.append(word_clip.set_position('center').set_start(start_time).set_end(end_time))
            text_sync_data.append({
                "text": word,
                "start_time": start_time,
                "end_time": end_time
            })

        # Combine all clips into final video
        video = CompositeVideoClip(
            [bg_clip, dimming, logo] + word_clips).set_duration(audio.duration).set_audio(audio)

        # Write video file
        print(f'Writing video to {output_file}')
        video.write_videofile(output_file, fps=24, codec='libx264',
                              audio_codec='aac', preset='ultrafast', threads=4)
        print(f'Video content written to {output_file}')

        # Write text synchronization data to JSON file
        with open(text_sync_file, 'w') as f:
            json.dump(text_sync_data, f, indent=4)
        print(f'Text synchronization data written to {text_sync_file}')

    except MemoryError as me:
        print(f'Memory Error creating video for {output_file}: {str(me)}')
    except Exception as e:
        print(f'Error creating video for {output_file}: {str(e)}')
        raise e  # Rethrow the exception to see the full traceback

if __name__ == "__main__":
    start_time = time.time()

    notebook_path = os.path.join('Numpy', '01-NumPy Arrays.ipynb')

    if not os.path.exists(notebook_path):
        print(f"Error: The file {notebook_path} does not exist.")
        exit(1)
    else:
        print(f"Notebook file found at: {notebook_path}")

    sections = extract_content(notebook_path)
    print(f'Extracted {len(sections)} sections from the notebook.')

    audio_dir = 'audio'
    video_dir = 'video'
    logo_path = os.path.join('static', 'logo.png')
    background_path = os.path.join('video', 'background.mp4')
    sound_file_path = os.path.join('audio', 'matrix_sound.wav')
    text_sync_file = os.path.join('video', 'text_sync.json')  # Adjust path as needed

    audio_files = sorted([os.path.join(root, file) for root, dirs, files in os.walk(
        audio_dir) for file in files if file.endswith('.mp3')])

    print(f'Found {len(audio_files)} audio files.')

    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    batch_size = 4
    for batch_start in range(0, len(sections), batch_size):
        batch_sections = sections[batch_start:batch_start + batch_size]
        batch_audio_files = audio_files[batch_start:batch_start + batch_size]

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            for section, audio in zip(batch_sections, batch_audio_files):
                title, content = section
                code = content.replace("\n", " ")
                sanitized_title = os.path.basename(audio).replace(".mp3", "")
                output_file = os.path.join(video_dir, f'{sanitized_title}.mp4')
                future = executor.submit(
                    create_video_parallel, section, audio, output_file, logo_path, background_path, text_sync_file)
                futures.append(future)

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f'Error in task: {str(e)}')

    end_time = time.time()
    duration = end_time - start_time
    print(f'Total time taken: {duration:.2f} seconds')

