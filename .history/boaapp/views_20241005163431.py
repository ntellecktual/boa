import json
import logging
import os
import re
import threading
import time
from threading import Thread

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from docx import Document

from .create_video import create_video_parallel
from .forms import DocumentForm, UserRegisterForm
from .models import AudioFile  # Ensure you import your model
from .models import DevopsItem, PortfolioItem, ResumeDocument
from .process_notebook import (handle_uploaded_file, process_notebook,
                               process_notebook_and_create_audio)

# Set up logging
logger = logging.getLogger(__name__)

# Thread-safe dictionary for progress and logs
progress_data_lock = threading.Lock()  # Use a lock for thread-safe updates
progress_data = {}
log_data = {}


def home(request):
    """Render home page with all uploaded audio files."""
    uploaded_files = AudioFile.objects.all()
    context = {'uploaded_files': uploaded_files}
    return render(request, 'boaapp/home.html', context)


def boashedskin_view(request):
    return HttpResponse("Health check successful!")

def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'boaapp/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'boaapp/login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@csrf_exempt
def upload_progress(request, file_name):
    progress = progress_data.get(file_name, {'progress': 0})
    logs = "\n".join(log_data.get(file_name, []))
    return JsonResponse({
        'progress': progress.get('progress', 0),
        'logs': logs,
    })


def handle_audio_creation(file_path, file_name):
    global progress_data, log_data
    audio_files = list(process_notebook_and_create_audio(file_path))
    total_files = len(audio_files)

    log_data[file_name] = []  # Initialize log storage
    progress_data[file_name] = {'progress': 0}  # Initialize progress

    if total_files == 0:
        log_data[file_name].append("No audio files to process.")
        return []  # Return an empty list if no audio files were created

    generated_audio_names = []  # Store the names of generated audio files

    for idx, audio_file in enumerate(audio_files):
        title = audio_file.get('title')
        if title:
            audio_file_path = os.path.join('audio', title + '.mp3')
            with open(audio_file_path, 'w') as f:
                f.write(audio_file['content'])

            log_data[file_name].append(
                f"Audio content written to {audio_file_path}")

            # Collect audio file names
            generated_audio_names.append(title + '.mp3')

            # Update progress
            progress_percentage = int((idx + 1) / total_files * 100)
            progress_data[file_name]['progress'] = progress_percentage

            time.sleep(0.5)  # Simulate delay (optional)

    return generated_audio_names  # Return the list of generated audio names


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES['uploaded_file'])
            document = form.save()

            # Get the name of the uploaded file
            file_name = document.uploaded_file.name
            cleaned_file_name = file_name.split('/')[-1]
            # Call handle_audio_creation and get the generated audio file names
            audio_file_names = handle_audio_creation(file_path, file_name)

            # Pass the audio file names to the success page
            return render(request, 'boaapp/upload_success.html', {
                'file_name': cleaned_file_name,
                'audio_names': audio_file_names  # Pass the list of generated names
            })
    else:
        form = DocumentForm()
    return render(request, 'boaapp/upload.html', {'form': form})


@login_required
def upload_progress_page(request, file_name):
    # Render the upload progress page without progress updates
    return render(request, 'boaapp/upload_progress.html', {
        'file_name': file_name  # Pass the file_name to the template
    })


def upload_success(request):
    """Render upload success page with processed audio file names."""
    # Assuming audio_file_names is a list of the generated audio file names
    audio_file_names = request.POST.getlist('audio_file_names', [])

    # Process file names: remove numbers, underscores, and ".mp3"
    cleaned_file_names = [
        re.sub(r'^[0-9]+__', '', file_name).replace('_',
                                                    ' ').replace('.mp3', '')
        for file_name in audio_file_names
    ]

    # Join names with a comma or any desired separator
    joined_file_names = ', '.join(cleaned_file_names)

    return render(request, 'boaapp/upload_success.html', {
        'file_name': joined_file_names,  # Pass the cleaned names to the template
    })


def companyandme(request):
    """Render 'Company and Me' page."""
    return render(request, 'boaapp/companyandme.html')


def handle_uploaded_file(f):
    """Handle the uploaded file and save it to the media directory."""
    file_path = os.path.join(settings.MEDIA_ROOT, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def portfolio_showcase(request):
    """Render portfolio showcase with related items."""
    portfolio_items = PortfolioItem.objects.prefetch_related(
        'scrolling_images').all()
    devops_items = DevopsItem.objects.prefetch_related(
        'scrolling_images').all()
    return render(request, 'boaapp/portfolio_showcase.html', {
        'portfolio_items': portfolio_items,
        'devops_items': devops_items,
    })


def project_pages(request):
    """Render project pages with portfolio and devops items."""
    portfolio_items = PortfolioItem.objects.all()
    devops_items = DevopsItem.objects.all()
    return render(request, 'boaapp/project_pages.html', {
        'portfolio_items': portfolio_items,
        'devops_items': devops_items,
    })


def data_start(request):
    """Render the data start page."""
    return render(request, 'boaapp/data_start.html')


def data_project(request):
    """Render the data project page."""
    return render(request, 'boaapp/data_project.html')


def live_demos(request):
    """Render the live demos page."""
    return render(request, 'boaapp/live_demos.html')


def skills_section(request):
    """Render the skills section page."""
    return render(request, 'boaapp/skills_section.html')


def display_resume(request):
    """Display the latest resume document."""
    try:
        resume = ResumeDocument.objects.latest('id')
    except ResumeDocument.DoesNotExist:
        return render(request, 'boaapp/resume.html', {'error': 'No resume document found'})

    return render(request, 'boaapp/resume.html', {'resume': resume})


def process_audio_and_create_videos(audio_dir, video_dir, logo_path, background_path):
    """Process audio files to create videos."""
    audio_files = sorted([os.path.join(audio_dir, file)
                         for file in os.listdir(audio_dir) if file.endswith('.mp3')])

    for audio_file in audio_files:
        section = process_notebook(audio_file)  # Adjust as needed
        output_file = os.path.join(
            video_dir, f"{os.path.basename(audio_file).replace('.mp3', '.mp4')}")
        text_sync_file = os.path.join(
            video_dir, f"{os.path.basename(audio_file).replace('.mp3', '.json')}")

        create_video_parallel(section, audio_file, output_file,
                              logo_path, background_path, text_sync_file)

    logger.info("Video creation complete.")
