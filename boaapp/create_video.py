import json
import os
os.environ["IMAGEMAGICK_BINARY"] = "C:\\Users\\Kieth\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import (
    AudioFileClip, ColorClip, CompositeVideoClip,
    ImageClip, TextClip, VideoFileClip
)
from .process_notebook import process_notebook
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

def to_camel_case(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    parts = re.split(r'[\s_\-]+', base)
    return ''.join(p.capitalize() for p in parts)

def find_latest_notebook(media_dir='boa/boa/media'):
    notebooks = [
        os.path.join(media_dir, f)
        for f in os.listdir(media_dir)
        if f.endswith('.ipynb')
    ]
    if not notebooks:
        raise FileNotFoundError("No .ipynb notebooks found in media directory.")
    return max(notebooks, key=os.path.getctime)

def get_audio_files(media_dir='boa/boa/media/audio'):
    if not os.path.exists(media_dir):
        raise FileNotFoundError("Audio directory not found.")
    return sorted([
        os.path.join(media_dir, f)
        for f in os.listdir(media_dir)
        if f.endswith('.mp3') and f.lower() != 'great_job!.mp3'
    ])

def create_video_parallel(section, audio_file, output_file, logo_path, background_path, text_sync_file,
                          font_styles, typewriter_effect=True):
    title, code = section
    try:
        print(f'Processing section: {title}')
        is_great_job = 'great job' in title.lower()

        audio = AudioFileClip(audio_file)
        bg_clip_raw = VideoFileClip(background_path).resize((1080, 1920))
        loops = int(audio.duration // bg_clip_raw.duration) + 1
        bg_clip = bg_clip_raw.loop(n=loops).subclip(0, audio.duration)

        dimming = ColorClip(size=bg_clip.size, color=[0, 0, 0]).set_duration(audio.duration).set_opacity(0.7)

        clips = [bg_clip, dimming]

        if is_great_job:
            # Great Job visual override
            logo = (ImageClip(logo_path, transparent=True)
                    .set_duration(audio.duration)
                    .resize(height=600)
                    .set_position("center"))

            text_clip = (TextClip("Thank you for learning with the numerix",
                                  fontsize=72, font="Arial-Bold", color="white",
                                  method="caption", size=(1000, None))
                         .set_duration(audio.duration)
                         .set_position(("center", 250)))

            clips += [logo, text_clip]
        else:
            # Logo in upper-right with 10px margins
            logo = (ImageClip(logo_path, transparent=True)
                    .set_duration(audio.duration)
                    .resize(height=100)
                    .margin(top=10, right=10, opacity=0)
                    .set_position(("right", "top")))

            # Split text into 4-word chunks
            words = code.split()
            chunk_size = 4
            chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            chunk_duration = audio.duration / max(1, len(chunks))

            font = font_styles.get("font", "Arial-Bold")
            font_size = font_styles.get("font_size", 36)
            text_color = font_styles.get("text_color", "white")

            text_sync_data = []
            word_clips = []

            for i, chunk in enumerate(chunks):
                start = i * chunk_duration
                end = start + chunk_duration
                clip = (TextClip(chunk, fontsize=font_size, color=text_color, font=font, size=(1000, None), method='caption')
                        .set_position(("center", 250))  # <-- same position as great job text
                        .set_start(start)
                        .set_end(end))
                word_clips.append(clip)
                text_sync_data.append({
                    "text": chunk,
                    "start_time": start,
                    "end_time": end
                })

            clips += [logo] + word_clips

            with open(text_sync_file, 'w') as f:
                json.dump(text_sync_data, f, indent=4)

        final_video = CompositeVideoClip(clips).set_duration(audio.duration).set_audio(audio)
        final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)

        print(f"✅ Finished video: {output_file}")

    except Exception as e:
        print(f"❌ Error creating video for {output_file}: {e}")
        raise e

    finally:
        audio.close()
        bg_clip_raw.close()
        bg_clip.close()
        if 'final_video' in locals():
            final_video.close()


if __name__ == "__main__":
    start_time = time.time()
    try:
        notebook_path = find_latest_notebook()
        print(f"📓 Using latest notebook: {notebook_path}")

        sections = process_notebook(notebook_path)
        print(f"✂️ Extracted {len(sections)} sections.")

        audio_files = get_audio_files()
        print(f"🔉 Found {len(audio_files)} .mp3 files.")

        if len(sections) != len(audio_files):
            print("⚠️ Warning: Mismatch between sections and audio files.")

        # New: subfolder for videos
        camel_folder = to_camel_case(notebook_path)
        video_dir = os.path.join('boa', 'boaapp', 'media', 'video', camel_folder)
        os.makedirs(video_dir, exist_ok=True)

        logo_path = os.path.join('boa', 'boaapp', 'static', 'logo.png')
        background_path = os.path.join('boa', 'video', 'background.mp4')
        font_styles = {"font": "Arial-Bold", "font_size": 36, "text_color": "white"}

        batch_size = os.cpu_count() or 6
        for batch_start in range(0, len(sections), batch_size):
            batch_sections = sections[batch_start:batch_start + batch_size]
            batch_audio_files = audio_files[batch_start:batch_start + batch_size]

            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = []
                for section, audio in zip(batch_sections, batch_audio_files):
                    name = os.path.splitext(os.path.basename(audio))[0]
                    output_path = os.path.join(video_dir, f"{name}.mp4")
                    sync_path = os.path.join(video_dir, f"{name}_sync.json")
                    futures.append(executor.submit(
                        create_video_parallel, section, audio, output_path,
                        logo_path, background_path, sync_path,
                        font_styles, typewriter_effect=True
                    ))

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"❌ Error in batch: {e}")

        print(f"✅ All videos created in {time.time() - start_time:.2f} seconds.")

    except Exception as e:
        print(f"🚫 Setup failed: {e}")
