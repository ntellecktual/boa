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
from .models import AudioFile, Document  # Updated to ensure Document model is imported
from .models import DevopsItem, PortfolioItem, ResumeDocument, Document, AudioFile
from .process_notebook import (handle_uploaded_file, process_notebook,
                               process_notebook_and_create_audio)

# Set up logging
logger = logging.getLogger(__name__)

# Thread-safe dictionary for progress and logs
progress_data_lock = threading.Lock()  # Use a lock for thread-safe updates
progress_data = {}
log_data = {}


def uploadit(request):
    uploaded_files = AudioFile.objects.filter(user=request.user)
    context = {
        'uploaded_files': uploaded_files,
        'welcome_title': "Welcome to Thenumerix",
        'description': "Upload Jupyter Notebooks. Convert them to audio. Watch them come to life as videos. All in one place."
    }
    items = [
    ("🧾 User Upload", "You upload a Jupyter notebook file (.ipynb) using our secure Django-powered form."),
    ("💾 File Storage", "The uploaded file is saved on the server, checked for duplicates, and assigned to your user account."),
    ("📖 Notebook Parsing", "We extract markdown headers, text, and code blocks from your notebook using nbformat."),
    ("🔊 Audio Generation", "Each section is converted into an MP3 using Google Text-to-Speech (gTTS) and saved in a structured folder."),
    ("🎞️ Video Rendering", "Each MP3 is combined with a looped background video, synchronized text overlays, and a logo using MoviePy."),
    ("📝 Synchronized Text", "Text is chunked into natural sentences and aligned to the audio duration for clear, readable display."),
    ("📈 Progress Tracking", "While the upload and processing runs, logs and progress percentages are tracked and updated in real-time."),
    ("📂 Dashboard + Download", "After completion, your files appear in your personal dashboard where you can play, download, or delete them.")
]
    return render(request, 'boaapp/uploadit.html', {'items': items, 'page_id': 'uploadit'})


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


def handle_audio_creation(file_path, file_name, request, document_reference):
    global progress_data, log_data
    audio_files = list(process_notebook_and_create_audio(file_path))
    total_files = len(audio_files)

    log_data[file_name] = []  # Initialize log storage
    progress_data[file_name] = {'progress': 0}  # Initialize progress

    audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
    os.makedirs(audio_dir, exist_ok=True)

    generated_audio_names = []

    if total_files == 0:
        log_data[file_name].append("No audio files to process.")
        return []

    for idx, audio_file in enumerate(audio_files):
        title = audio_file.get('title')
        if not title:
            continue

        audio_file_path = os.path.join(audio_dir, title + '.mp3')
        if os.path.exists(audio_file_path):
            log_data[file_name].append(f"Audio already exists at {audio_file_path}")
        else:
            log_data[file_name].append(f"Audio file missing: {audio_file_path}")

        AudioFile.objects.create(
            title=title,
            name=title,
            file=os.path.join('audio', title + '.mp3'),
            user=request.user,
            document=document_reference
        )

        generated_audio_names.append(title + '.mp3')
        progress_percentage = int((idx + 1) / total_files * 100)
        progress_data[file_name]['progress'] = progress_percentage
        time.sleep(0.5)

    return generated_audio_names



@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Check for duplicate file before saving
            existing_file_path = os.path.join(settings.MEDIA_ROOT, 'documents', request.FILES['uploaded_file'].name)
            if os.path.exists(existing_file_path):
                messages.error(request, "A file with this name already exists. Please rename your file or upload a different one.")
                return redirect('upload_document')

            file_path = handle_uploaded_file(request.FILES['uploaded_file'])
            document = form.save(commit=False)
            document.user = request.user
            document.save()

            file_name = document.uploaded_file.name
            cleaned_file_name = file_name.split('/')[-1]

            audio_file_names = handle_audio_creation(file_path, file_name, request, document)

            return render(request, 'boaapp/upload_success.html', {
                'file_name': cleaned_file_name,
                'audio_names': audio_file_names,
         'page_id': 'uploadit'
            })
    else:
        form = DocumentForm()
        documents_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
        existing_files = os.listdir(documents_dir) if os.path.exists(documents_dir) else []

    return render(request, 'boaapp/upload.html', {
        'form': form,
        'existing_filenames': json.dumps(existing_files),
         'page_id': 'uploadit'
    })


@login_required
def upload_progress_page(request, file_name):
    # Render the upload progress page without progress updates
    return render(request, 'boaapp/upload_progress.html', {
        'file_name': file_name,
         'page_id': 'uploadit'
    })


def upload_success(request):
    """Render upload success page with processed audio file names."""
    audio_file_names = request.POST.getlist('audio_file_names', [])

    cleaned_file_names = [
        re.sub(r'^[0-9]+__', '', file_name).replace('_',
                                                    ' ').replace('.mp3', '')
        for file_name in audio_file_names
    ]

    joined_file_names = ', '.join(cleaned_file_names)

    return render(request, 'boaapp/upload_success.html', {
        'file_name': joined_file_names,
         'page_id': 'uploadit'
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
    portfolio_items = PortfolioItem.objects.prefetch_related(
        'scrolling_images').all()
    devops_items = DevopsItem.objects.prefetch_related(
        'scrolling_images').all()
    return render(request, 'boaapp/portfolio_showcase.html', {
        'portfolio_items': portfolio_items,
        'devops_items': devops_items,
    })


def project_pages(request):
    portfolio_items = PortfolioItem.objects.all()
    devops_items = DevopsItem.objects.all()
    return render(request, 'boaapp/project_pages.html', {
        'portfolio_items': portfolio_items,
        'devops_items': devops_items,
    })


def data_start(request):
    return render(request, 'boaapp/data_start.html')


def data_project(request):
    return render(request, 'boaapp/data_project.html')


def live_demos(request):
    return render(request, 'boaapp/live_demos.html')


def skills_section(request):
    return render(request, 'boaapp/skills_section.html')


def display_resume(request):
    try:
        resume = ResumeDocument.objects.latest('id')
    except ResumeDocument.DoesNotExist:
        return render(request, 'boaapp/resume.html', {'error': 'No resume document found'})

    return render(request, 'boaapp/resume.html', {'resume': resume})


def process_audio_and_create_videos(audio_dir, video_dir, logo_path, background_path):
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


@login_required
def dashboard(request):
    all_documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

# Filter only documents that still exist on disk
    documents = [doc for doc in all_documents if os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file)))]


    # Count all audio files
    all_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio')
    total_audio = len(os.listdir(all_audio_path)) if os.path.exists(all_audio_path) else 0

    # Show only latest doc if audio folder was empty when starting
    latest_doc = documents[0] if documents else None
    latest_only = True

    if total_audio > 0:
        latest_only = False  # Don't limit if audio files already exist

    context = {
        'document_count': len(documents),
        'audio_file_count': total_audio,
        'latest_doc': documents[0] if documents else None,
        'all_docs': documents,
        'latest_only': latest_only,
    }


    return render(request, 'boaapp/dashboard.html', {
    **context,
    'page_id': 'uploadit'
})

    
@login_required
def delete_orphaned_files(request):
    deleted = 0
    for doc in Document.objects.all():
        ipynb_path = os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))
        audio_files = AudioFile.objects.filter(document=doc)

        audio_exists = any(os.path.exists(os.path.join(settings.MEDIA_ROOT, str(audio.file))) for audio in audio_files)
        doc_exists = os.path.exists(ipynb_path)

        if not audio_exists or not doc_exists:
            for audio in audio_files:
                file_path = os.path.join(settings.MEDIA_ROOT, str(audio.file))
                if os.path.exists(file_path):
                    os.remove(file_path)
                audio.delete()
            if os.path.exists(ipynb_path):
                os.remove(ipynb_path)
            doc.delete()
            deleted += 1
    return JsonResponse({'deleted': deleted})

@login_required
def delete_all_files(request):
    for doc in Document.objects.all():
        ipynb_path = os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))
        if os.path.exists(ipynb_path):
            os.remove(ipynb_path)
        doc.delete()

    for audio in AudioFile.objects.all():
        audio_path = os.path.join(settings.MEDIA_ROOT, str(audio.file))
        if os.path.exists(audio_path):
            os.remove(audio_path)
        audio.delete()

    return JsonResponse({'status': 'All files deleted'})

@login_required
def delete_ipynb_files(request):
    deleted = 0
    for doc in Document.objects.all():
        ipynb_path = os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))
        if os.path.exists(ipynb_path):
            os.remove(ipynb_path)
            deleted += 1
    return JsonResponse({'deleted_ipynb_files': deleted})