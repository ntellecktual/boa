import io
import logging
import os
import threading

import nbformat
from celery import current_app
from celery.result import AsyncResult
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from nbconvert import HTMLExporter

from .forms import CustomUserCreationForm, DocumentForm
from .models import (
    AudioFile,
    ChatConversation,
    ChatMessage,
    CodeReview,
    Course,
    CourseSection,
    DevopsItem,
    Document,
    Enrollment,
    LearningEvent,
    PipelineRun,
    PortfolioItem,
    Quiz,
    QuizAttempt,
    TranslatedContent,
    WebhookConfig,
)
from .tasks import create_audio_files_task, create_single_video_task, run_full_pipeline_task

# Set up logging
logger = logging.getLogger(__name__)


def render_notebook_to_html(notebook_json_str):
    """Converts a Jupyter Notebook JSON string to HTML."""
    if not notebook_json_str:
        return '<p>No notebook content available.</p>'
    try:
        nb = nbformat.read(io.StringIO(notebook_json_str), as_version=4)
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'basic'
        html_exporter.exclude_output_prompt = True
        html_exporter.exclude_input = False
        (body, resources) = html_exporter.from_notebook_node(nb)
        return body
    except Exception as e:
        logger.error(f'Error rendering notebook: {e}', exc_info=True)
        return f'<p>Error rendering notebook: {e}</p>'


def course_list_view(request):
    courses = Course.objects.all().order_by('updated_at')  # Changed to order by updated_at ascending
    user_enrollments_ids = []
    if request.user.is_authenticated:
        user_enrollments_ids = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)

    return render(
        request, 'boaapp/course_list.html', {'courses': courses, 'user_enrollments_ids': user_enrollments_ids}
    )


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    sections = course.sections.all().order_by('order')  # CourseSection.Meta.ordering handles this too

    is_enrolled = False
    completed_learn_sections_ids = []
    current_step_name = 'Not Enrolled'
    current_step_description = 'Enroll in the course to begin your journey.'
    enrollment = None

    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        is_enrolled = True
        completed_learn_sections_ids = list(enrollment.completed_learn_sections.values_list('id', flat=True))

        # Determine current step
        if not enrollment.all_learn_sections_completed():
            current_step_name = 'Step 1: Learning'
            current_step_description = (
                'Focus on understanding the core concepts and materials provided in the sections below.'
            )
        elif not enrollment.create_step_completed:
            current_step_name = 'Step 2: Creating'
            current_step_description = "Apply what you've learned! It's time to build/create the project."
        elif not enrollment.teach_step_completed:
            current_step_name = 'Step 3: Teaching'
            current_step_description = 'Solidify your understanding by preparing to teach this topic to others.'
        else:
            current_step_name = 'Course Completed!'
            current_step_description = 'Congratulations on completing all steps of this course!'

    except Enrollment.DoesNotExist:
        is_enrolled = False

    # Prepare sections data, including rendered HTML for notebooks
    sections_data = []
    for section in sections:
        section_info = {
            'section': section,
            'is_completed': section.id in completed_learn_sections_ids,
            'learn_content_html': None,  # Placeholder for rendered HTML
        }
        if section.learn_content_file and section.learn_content_file.name.lower().endswith('.ipynb'):
            # Construct absolute path to the file
            file_path = os.path.join(settings.MEDIA_ROOT, section.learn_content_file.name)
            section_info['learn_content_html'] = render_notebook_to_html(file_path)
        sections_data.append(section_info)

    context = {
        'course': course,
        'sections_data': sections_data,  # Pass the processed sections data
        'is_enrolled': is_enrolled,
        'completed_learn_sections_ids': completed_learn_sections_ids,
        'current_step_name': current_step_name,
        'current_step_description': current_step_description,
        'page_id': 'course-detail',
    }
    return render(request, 'boaapp/course_detail.html', context)


@login_required
def enroll_course_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        if created:
            messages.success(request, f"You have successfully enrolled in '{course.title}'.")
        else:
            messages.info(request, f"You are already enrolled in '{course.title}'.")
        return redirect('course_detail', course_id=course.id)
    return redirect('course_list')  # Should not be reached via GET directly typically


@login_required
def mark_section_learned_view(request, section_id):
    section = get_object_or_404(CourseSection, pk=section_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=section.course)
    enrollment.completed_learn_sections.add(section)
    messages.success(request, f"Section '{section.title}' marked as learned!")
    return redirect('course_detail', course_id=section.course.id)


def uploadit(request):
    uploaded_files = []
    if request.user.is_authenticated:  # Check login status
        uploaded_files = AudioFile.objects.filter(user=request.user)
    context = {
        'uploaded_files': uploaded_files,
        'welcome_title': 'Welcome to Thenumerix',
        'description': 'Upload Jupyter Notebooks. Convert them to audio. Watch them come to life as videos. All in one place.',
    }
    items = [
        ('🧾 User Upload', 'You upload a Jupyter notebook file (.ipynb) using our secure Django-powered form.'),
        (
            '💾 File Storage',
            'The uploaded file is saved on the server, checked for duplicates, and assigned to your user account.',
        ),
        (
            '📖 Notebook Parsing',
            'We extract markdown headers, text, and code blocks from your notebook using nbformat.',
        ),
        (
            '🔊 Audio Generation',
            'Each section is converted into an MP3 using Google Text-to-Speech (gTTS) and saved in a structured folder.',
        ),
        (
            '🎞️ Video Rendering',
            'Each MP3 is combined with a looped background video, synchronized text overlays, and a logo using MoviePy.',
        ),
        (
            '📝 Synchronized Text',
            'Text is chunked into natural sentences and aligned to the audio duration for clear, readable display.',
        ),
        (
            '📈 Progress Tracking',
            'While the upload and processing runs, logs and progress percentages are tracked and updated in real-time.',
        ),
        (
            '📂 Dashboard + Download',
            'After completion, your files appear in your personal dashboard where you can play, download, or delete them.',
        ),
    ]
    return render(request, 'boaapp/uploadit.html', {'items': items, 'page_id': 'uploadit', **context})


def boashedskin_view(request):
    return HttpResponse('Health check successful!')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and get the user object
            username = form.cleaned_data.get('username')
            login(request, user)  # Log the new user in automatically
            messages.success(request, f'Account created for {username}! Welcome to the courses.')
            return redirect('home')  # Redirect to home dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'boaapp/register.html', {'form': form})


def health_check(request):
    """Health endpoint — verifies DB and returns service status."""
    import time

    status = {'status': 'ok', 'checks': {}}
    http_status = 200

    # Database check
    try:
        start = time.monotonic()
        from django.db import connection

        connection.ensure_connection()
        status['checks']['db'] = {'status': 'ok', 'latency_ms': round((time.monotonic() - start) * 1000, 1)}
    except Exception as exc:
        status['checks']['db'] = {'status': 'error', 'detail': str(exc)}
        status['status'] = 'degraded'
        http_status = 500

    return JsonResponse(status, status=http_status)


def home_view(request):
    """Authenticated home dashboard, or redirect to login."""
    if request.user.is_authenticated:
        return render(request, 'boaapp/home.html')
    return redirect('login')


def login_view(request):
    """Handle user login using Django's AuthenticationForm."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome back, {username}.')
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Authentication failed unexpectedly.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'boaapp/login.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['uploaded_file']
            original_filename = uploaded_file.name

            # --- Read and validate notebook ---
            try:
                uploaded_file.seek(0)
                notebook_json_str = uploaded_file.read().decode('utf-8')
                uploaded_nb = nbformat.read(io.StringIO(notebook_json_str), as_version=4)

                # Extract title from first H1 header
                uploaded_title_original = None
                uploaded_title_lower = None
                for cell in uploaded_nb.cells:
                    if cell.cell_type == 'markdown':
                        lines = [line.strip() for line in cell['source'].split('\n') if line.strip()]
                        if lines and lines[0].startswith('# '):
                            uploaded_title_original = lines[0][2:].strip()
                            uploaded_title_lower = uploaded_title_original.lower()
                            break

                if not uploaded_title_lower:
                    uploaded_title_original = os.path.splitext(original_filename)[0]
                    uploaded_title_lower = uploaded_title_original.lower()

                # --- Duplicate Check (compare against existing DB-stored notebooks) ---
                existing_docs = Document.objects.filter(user=request.user)
                for doc in existing_docs:
                    try:
                        if not doc.notebook_json:
                            continue
                        existing_nb = nbformat.read(io.StringIO(doc.notebook_json), as_version=4)
                        existing_title_lower = None
                        for cell_existing in existing_nb.cells:
                            if cell_existing.cell_type == 'markdown':
                                lines_existing = [
                                    line.strip() for line in cell_existing['source'].split('\n') if line.strip()
                                ]
                                if lines_existing and lines_existing[0].startswith('# '):
                                    existing_title_lower = lines_existing[0][2:].strip().lower()
                                    break
                        if not existing_title_lower:
                            existing_title_lower = os.path.splitext(doc.original_filename or '')[0].lower()

                        if uploaded_title_lower == existing_title_lower and uploaded_title_lower != 'great job!':
                            logger.warning(
                                f"Duplicate title detected for user {request.user.username}: '{uploaded_title_original}'"
                            )
                            messages.error(
                                request, f"A notebook with the same title ('{uploaded_title_original}') already exists."
                            )
                            return redirect('upload_document')
                    except Exception as e_read_existing:
                        logger.warning(
                            f'Could not parse existing document PK {doc.pk} for title check: {e_read_existing}'
                        )
                        continue

            except nbformat.validator.NotebookValidationError as e_nb:
                logger.error(f'Invalid notebook format: {original_filename}. Error: {e_nb}', exc_info=True)
                messages.error(request, 'The uploaded file is not a valid Jupyter Notebook.')
                return redirect('upload_document')
            except Exception as e_read:
                logger.error(f'Failed to read notebook: {original_filename}. Error: {e_read}', exc_info=True)
                messages.error(request, 'Failed to read notebook content. Please upload a valid .ipynb file.')
                return redirect('upload_document')

            # --- Save Document with notebook JSON stored in DB ---
            document = Document(
                user=request.user,
                original_filename=original_filename,
                notebook_json=notebook_json_str,
            )
            document.save()

            # --- Trigger Audio Creation in Background Thread ---
            # In EAGER mode, apply_async runs synchronously and blocks the request.
            # Use a background thread so the user gets an immediate redirect.
            logger.info(f'Triggering audio creation for document PK {document.pk}')

            def _run_audio_generation(doc_pk, user_pk):
                """Run audio generation in a background thread."""
                from django.db import connection

                try:
                    create_audio_files_task(doc_pk, user_pk)
                    logger.info(f'Background audio generation completed for document PK {doc_pk}')
                except Exception as e:
                    logger.error(f'Background audio generation failed for document PK {doc_pk}: {e}', exc_info=True)
                finally:
                    connection.close()

            thread = threading.Thread(
                target=_run_audio_generation,
                args=[document.pk, request.user.pk],
                daemon=True,
            )
            thread.start()

            messages.success(
                request,
                f"Notebook '{original_filename}' uploaded successfully. Audio generation started — refresh the dashboard in a moment.",
            )
            return redirect('dashboard')
    else:
        form = DocumentForm()

    return render(request, 'boaapp/upload.html', {'form': form, 'page_id': 'uploadit'})


def check_task_status(request, task_id):
    """Checks the status of a Celery task."""
    app = current_app._get_current_object()
    task_result = AsyncResult(task_id, app=app)
    status = task_result.status
    result = None

    if task_result.failed():
        status = 'FAILURE'  # Standardize failure status
        try:
            # Try to get the exception message if available
            result = str(task_result.info) if task_result.info else 'Task failed without specific error info.'
        except Exception:
            result = 'Could not retrieve failure reason.'
        logger.warning(f'Task {task_id} failed. Info: {result}')
    elif status == 'SUCCESS':
        try:
            # Get the actual result returned by the task
            result = task_result.get(timeout=1.0)  # Short timeout
        except Exception as e:
            logger.warning(f'Could not retrieve result for successful task {task_id}: {e}')
            result = 'Success, but result retrieval failed.'

    response_data = {
        'task_id': task_id,
        'status': status,
        'result': result,  # Include result/error info
    }
    return JsonResponse(response_data)


def process_flows(request):
    """Render AI Process Flows demo page."""
    return render(request, 'boaapp/process_flows.html')


def portfolio_showcase(request):
    portfolio_items = PortfolioItem.objects.prefetch_related('scrolling_images').all()
    devops_items = DevopsItem.objects.prefetch_related('scrolling_images').all()
    return render(
        request,
        'boaapp/portfolio_showcase.html',
        {
            'portfolio_items': portfolio_items,
            'devops_items': devops_items,
        },
    )


def education_details_view(request):
    # You can pass context here if needed, but for static content, it's simple
    return render(request, 'boaapp/education.html')


def data_start(request):
    return render(request, 'boaapp/data_start.html')


def data_project(request):
    return render(request, 'boaapp/data_project.html')


def live_demos(request):
    return render(request, 'boaapp/live_demos.html')


def platform_engineering(request):
    return render(request, 'boaapp/platform_engineering.html')


def mlops_lifecycle(request):
    return render(request, 'boaapp/mlops_lifecycle.html')


def streaming_architecture(request):
    return render(request, 'boaapp/streaming_architecture.html')


def api_orchestration(request):
    return render(request, 'boaapp/api_orchestration.html')


def idp_demo(request):
    return render(request, 'boaapp/idp_demo.html')


def portfolio_chat_api(request):
    """Public keyword-based Q&A widget for the portfolio site."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        import json as _json

        data = _json.loads(request.body)
        message = (data.get('message') or '').strip()[:500]
    except (ValueError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not message:
        return JsonResponse({'reply': "I didn't catch that — ask me anything about the portfolio!"})

    msg = message.lower()

    # ── Skill / tech questions ──
    if any(k in msg for k in ['azure', 'cloud', 'microsoft']):
        reply = (
            'Azure is the backbone of most of the portfolio. The Platform Engineering demo '
            'shows Azure DevOps pipelines, Entra ID integration, and Databricks-based ETL. '
            'The MLOps demo uses Azure ML for model training and deployment.'
        )
    elif any(k in msg for k in ['mlops', 'ml', 'machine learning', 'model']):
        reply = (
            'The MLOps Lifecycle demo walks through model training, feature stores, experiment '
            'tracking with MLflow, and blue-green deployment on AKS. '
            'Check it out at the Live Demos page!'
        )
    elif any(k in msg for k in ['data', 'pipeline', 'etl', 'databricks', 'spark']):
        reply = (
            'Data engineering is a core focus — the Platform Engineering demo covers '
            'Databricks Spark pipelines, Delta Lake, and CI/CD integration. '
            'The Streaming Architecture demo shows Kafka + Flink real-time event processing.'
        )
    elif any(k in msg for k in ['kafka', 'stream', 'real-time', 'event']):
        reply = (
            'The Streaming Architecture demo covers Apache Kafka event brokering, '
            'Flink stream processing, schema registries, and CDC patterns used at Netflix-scale.'
        )
    elif any(k in msg for k in ['devops', 'cicd', 'ci/cd', 'pipeline', 'deploy']):
        reply = (
            'The Platform Engineering demo shows three full CI/CD pipelines: '
            'Azure DevOps, Databricks Jobs, and Entra ID automation — all for a casino platform use case.'
        )
    elif any(k in msg for k in ['api', 'gateway', 'orchestrat', 'microservice']):
        reply = (
            'The API Orchestration demo covers API gateway patterns, saga choreography, '
            'circuit breakers, and service mesh fundamentals.'
        )
    elif any(k in msg for k in ['document', 'ocr', 'extract', 'idp']):
        reply = (
            'The Document Processing (IDP) demo shows AI-powered OCR, structured data '
            'extraction, and validation pipelines — great for financial document automation.'
        )
    elif any(k in msg for k in ['oracle', 'finance', 'accounting', 'process flow']):
        reply = (
            'The AI Process Flows demo shows Oracle Finance & Accounting automation '
            'workflows powered by AI — procure-to-pay, order-to-cash, and more.'
        )
    elif any(k in msg for k in ['nfl', 'mlb', 'netflix', 'sport', 'partner']):
        reply = (
            'The portfolio demos are built around real enterprise partner use cases: '
            'Oracle (finance automation), NFL (Azure DevOps pipelines), '
            'MLB (MLOps at scale), and Netflix (streaming architecture).'
        )
    elif any(k in msg for k in ['education', 'degree', 'school', 'university', 'certif']):
        reply = (
            'The Education section covers degrees and certifications. '
            'Navigate to Education in the sidebar (or Profile on the home dashboard) for the full details.'
        )
    elif any(k in msg for k in ['contact', 'email', 'hire', 'available', 'reach']):
        reply = (
            'The best way to connect is via GitHub (@ntellecktual) or LinkedIn. '
            "Feel free to explore the portfolio demos — they're all fully interactive!"
        )
    elif any(k in msg for k in ['project', 'portfolio', 'work', 'experience']):
        reply = (
            'The Portfolio section showcases enterprise projects across cloud, data, and AI. '
            'There are 7 live interactive demos spanning MLOps, streaming, CI/CD, API patterns, '
            'document processing, and AI process automation.'
        )
    elif any(k in msg for k in ['python', 'django', 'stack', 'tech']):
        reply = (
            'The site itself is built with Django 5.1, PostgreSQL, Celery + Redis, '
            'and deployed on Render. The demos use Bootstrap 5, vanilla JS, and Font Awesome. '
            'Python is the primary language across all backend work.'
        )
    elif any(k in msg for k in ['upload', 'notebook', 'jupyter', 'audio', 'video']):
        reply = (
            'UploadIt! lets you upload Jupyter notebooks and auto-generates audio lectures, '
            'video content with synced text, quizzes, and a RAG-powered chatbot — '
            'all in one pipeline. Try it from the sidebar!'
        )
    elif any(k in msg for k in ['hello', 'hi', 'hey', 'greet']):
        reply = (
            "Hey! I'm the thenumerix assistant. Ask me about the portfolio demos, "
            'skills, tech stack, or anything else you see on the site!'
        )
    elif any(k in msg for k in ['demo', 'live', 'interact']):
        reply = (
            'There are 7 live interactive demos: AI Process Flows, UploadIt!, Platform Engineering, '
            'MLOps Lifecycle, Streaming Architecture, API Orchestration, and Document Processing. '
            "Hit 'Discover' in the sidebar to explore them all!"
        )
    else:
        reply = (
            'I can answer questions about the portfolio demos, tech stack, skills, and experience. '
            'Try asking about Azure, MLOps, data pipelines, or any of the live demos!'
        )

    return JsonResponse({'reply': reply})


@login_required
def dashboard(request):
    user_documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

    dashboard_items = []
    total_audio_count = 0

    for doc in user_documents:
        doc_data = {'document': doc, 'audio_files': []}
        audio_files_for_doc = AudioFile.objects.filter(document=doc).order_by('metadata__section_index', 'pk')
        total_audio_count += audio_files_for_doc.count()

        for audio in audio_files_for_doc:
            has_audio = bool(audio.audio_data)
            doc_data['audio_files'].append(
                {
                    'audio': audio,
                    'has_audio': has_audio,
                }
            )
        dashboard_items.append(doc_data)

    context = {
        'dashboard_items': dashboard_items,
        'document_count': user_documents.count(),
        'total_audio_count': total_audio_count,
        'page_id': 'dashboard',
    }

    return render(request, 'boaapp/dashboard.html', context)


@login_required
@transaction.atomic
def delete_orphaned_files(request):
    """Delete documents that have no associated audio files."""
    deleted_docs = 0
    deleted_audio = 0
    logger.info(f'Running delete_orphaned_files for user {request.user.username}')

    for doc in Document.objects.filter(user=request.user):
        audio_files = AudioFile.objects.filter(document=doc)
        if not audio_files.exists():
            logger.info(f'Deleting orphaned document record PK {doc.pk} (no audio records).')
            doc.delete()
            deleted_docs += 1

    # Delete audio records with no audio data
    for audio in AudioFile.objects.filter(user=request.user):
        if not audio.audio_data:
            logger.info(f'Deleting orphaned audio record PK {audio.pk} (no audio data).')
            audio.delete()
            deleted_audio += 1

    return JsonResponse({'deleted_docs': deleted_docs, 'deleted_audio_records': deleted_audio})


@login_required
@transaction.atomic
def delete_all_files(request):
    """Delete all documents and audio records for the current user."""
    if request.method == 'POST':
        logger.warning(f'User {request.user.username} initiated DELETE ALL FILES.')

        deleted_audio_count = AudioFile.objects.filter(user=request.user).count()
        AudioFile.objects.filter(user=request.user).delete()

        deleted_docs_count = Document.objects.filter(user=request.user).count()
        Document.objects.filter(user=request.user).delete()

        messages.success(
            request,
            f'All your documents ({deleted_docs_count}) and audio files ({deleted_audio_count}) have been deleted.',
        )
        return JsonResponse({'status': 'All files deleted', 'docs': deleted_docs_count, 'audio': deleted_audio_count})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def serve_audio(request, audio_file_pk):
    """Serve audio bytes from DB as an audio/mpeg stream."""
    audio_file = get_object_or_404(AudioFile, pk=audio_file_pk, user=request.user)
    if not audio_file.audio_data:
        return HttpResponse('No audio data available.', status=404)
    response = HttpResponse(bytes(audio_file.audio_data), content_type='audio/mpeg')
    response['Content-Disposition'] = f'inline; filename="{audio_file.name}"'
    return response


@login_required
def download_video(request, audio_file_pk):
    """Generate a video on-demand from DB-stored audio and stream as download."""
    audio_file = get_object_or_404(AudioFile, pk=audio_file_pk, user=request.user)
    if not audio_file.audio_data:
        messages.error(request, 'No audio data available to generate video.')
        return redirect('dashboard')

    logger.info(f'User {request.user.username} initiated on-demand video download for AudioFile PK {audio_file_pk}')

    try:
        result = create_single_video_task.apply(args=[audio_file_pk])
        task_result = result.get()

        if task_result.get('status') == 'COMPLETE' and task_result.get('video_bytes'):
            video_bytes = task_result['video_bytes']
            # Ensure video_bytes is proper bytes
            if isinstance(video_bytes, memoryview):
                video_bytes = bytes(video_bytes)
            video_filename = f'{audio_file.name.rsplit(".", 1)[0]}.mp4'
            response = HttpResponse(video_bytes, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{video_filename}"'
            return response
        else:
            error_msg = task_result.get('error', 'Unknown error')
            messages.error(request, f'Video generation failed: {error_msg}')
            return redirect('dashboard')
    except Exception as e:
        logger.error(f'Video download failed for AudioFile PK {audio_file_pk}: {e}', exc_info=True)
        messages.error(request, f'Video generation failed: {e}')
        return redirect('dashboard')


@login_required
def generate_video(request, audio_file_pk):
    """Triggers on-demand video download for a single audio file."""
    return download_video(request, audio_file_pk)


@login_required
def generate_all_videos(request):
    """Redirect to dashboard — batch video generation not supported in DB-storage mode."""
    messages.info(request, 'Videos are now generated on-demand. Click the download button next to any audio file.')
    return redirect('dashboard')


# ==========================================================================
# ONE-CLICK FULL PIPELINE
# ==========================================================================


@login_required
def run_full_pipeline(request, document_pk):
    """Start the full pipeline: audio → video → quiz → thumbnail → RAG index."""
    document = get_object_or_404(Document, pk=document_pk, user=request.user)

    # Create pipeline run for tracking
    pipeline_run = PipelineRun.objects.create(
        user=request.user,
        document=document,
        status='pending',
        current_step='Initializing...',
    )

    # Run in background thread so the response returns immediately
    def _run_pipeline(doc_pk, user_pk, run_pk):
        from django.db import connection

        try:
            run_full_pipeline_task.apply(args=[doc_pk, user_pk, run_pk])
        except Exception as e:
            logger.error(f'Background pipeline failed for doc {doc_pk}: {e}')
        finally:
            connection.close()

    thread = threading.Thread(
        target=_run_pipeline,
        args=(document_pk, request.user.pk, pipeline_run.pk),
        daemon=True,
    )
    thread.start()

    messages.success(
        request, f"Full pipeline started for '{document.original_filename or 'Notebook'}'. Refresh to track progress."
    )
    return redirect('dashboard')


@login_required
def pipeline_status_api(request, run_id):
    """API endpoint for pipeline run status."""
    run = get_object_or_404(PipelineRun, pk=run_id, user=request.user)
    return JsonResponse(
        {
            'id': run.pk,
            'status': run.status,
            'progress_pct': run.progress_pct,
            'current_step': run.current_step,
            'error_message': run.error_message,
            'started_at': run.started_at.isoformat() if run.started_at else None,
            'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        }
    )


# ==========================================================================
# QUIZ VIEWS
# ==========================================================================


@login_required
def quiz_list_view(request, document_pk):
    """List all quizzes for a document."""
    document = get_object_or_404(Document, pk=document_pk, user=request.user)
    quizzes = Quiz.objects.filter(document=document).order_by('-created_at')
    return render(
        request,
        'boaapp/quiz_list.html',
        {
            'document': document,
            'quizzes': quizzes,
            'page_id': 'quiz',
        },
    )


@login_required
def quiz_take_view(request, quiz_pk):
    """Take a quiz (GET shows questions, POST submits answers)."""
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    questions = quiz.questions.all()

    if request.method == 'POST':
        from .quiz_generator import grade_answer

        answers = {}
        score = 0
        total = questions.count()
        results = []

        for q in questions:
            user_answer = request.POST.get(f'question_{q.pk}', '')
            answers[str(q.pk)] = user_answer
            is_correct, feedback = grade_answer(q.question_type, user_answer, q.correct_answer)
            if is_correct:
                score += 1
            results.append(
                {
                    'question': q.question_text,
                    'user_answer': user_answer,
                    'correct_answer': q.correct_answer,
                    'is_correct': is_correct,
                    'feedback': feedback,
                    'explanation': q.explanation,
                }
            )

        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total,
            answers=answers,
        )

        # Track learning event
        LearningEvent.objects.create(
            user=request.user,
            event_type='quiz_attempt',
            metadata={'quiz_id': quiz.pk, 'score': score, 'total': total},
        )

        return render(
            request,
            'boaapp/quiz_results.html',
            {
                'quiz': quiz,
                'results': results,
                'score': score,
                'total': total,
                'percentage': round(score / total * 100) if total else 0,
                'page_id': 'quiz',
            },
        )

    return render(
        request,
        'boaapp/quiz_take.html',
        {
            'quiz': quiz,
            'questions': questions,
            'page_id': 'quiz',
        },
    )


@login_required
def generate_quiz_view(request, document_pk):
    """Generate quizzes for a document's audio sections."""
    from .tasks import generate_quiz_from_document_task

    document = get_object_or_404(Document, pk=document_pk, user=request.user)

    generate_quiz_from_document_task.delay(document.pk)

    messages.success(request, 'Quiz generation started from notebook content.')
    return redirect('quiz_list', document_pk=document_pk)


# ==========================================================================
# RAG CHATBOT VIEWS
# ==========================================================================


@login_required
def chat_view(request, document_pk=None):
    """Chatbot interface for a document."""
    document = None
    if document_pk:
        document = get_object_or_404(Document, pk=document_pk, user=request.user)

    # Get or create conversation
    conversation = None
    if document:
        conversation = (
            ChatConversation.objects.filter(user=request.user, document=document).order_by('-updated_at').first()
        )

        if not conversation:
            stem = os.path.splitext(document.original_filename or 'Notebook')[0]
            conversation = ChatConversation.objects.create(
                user=request.user,
                document=document,
                title=f'Chat: {stem}',
            )

    chat_messages = []
    if conversation:
        chat_messages = list(conversation.messages.values('role', 'content', 'created_at'))

    return render(
        request,
        'boaapp/chat.html',
        {
            'document': document,
            'conversation': conversation,
            'messages_list': chat_messages,
            'page_id': 'chat',
        },
    )


@login_required
def chat_api(request):
    """REST API fallback for chat (when WebSocket is unavailable)."""
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    if not message or not conversation_id:
        return JsonResponse({'error': 'Missing message or conversation_id'}, status=400)

    conversation = get_object_or_404(ChatConversation, pk=conversation_id, user=request.user)

    # Save user message
    ChatMessage.objects.create(conversation=conversation, role='user', content=message)

    # Get RAG response
    from .rag_engine import get_rag_response

    response_text, sources = get_rag_response(message, conversation.document_id)

    # Save assistant message
    ChatMessage.objects.create(conversation=conversation, role='assistant', content=response_text, sources=sources)

    # Track event
    LearningEvent.objects.create(
        user=request.user,
        event_type='chat_message',
        metadata={'conversation_id': conversation_id},
    )

    return JsonResponse(
        {
            'response': response_text,
            'sources': sources,
        }
    )


# ==========================================================================
# CODE PLAYGROUND
# ==========================================================================


@login_required
def code_playground_view(request):
    """Interactive code playground page (Pyodide-based, runs in browser)."""
    return render(request, 'boaapp/code_playground.html', {'page_id': 'playground'})


@login_required
def code_review_api(request):
    """API endpoint for AI code review."""
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    code = data.get('code', '')
    language = data.get('language', 'python')

    if not code.strip():
        return JsonResponse({'error': 'No code provided'}, status=400)

    from .tasks import ai_code_review_task

    try:
        result = ai_code_review_task.apply(args=[code, language])
        review_data = result.get()
    except Exception as e:
        review_data = {'score': 0, 'issues': [], 'summary': f'Review failed: {e}'}

    # Save review
    CodeReview.objects.create(
        user=request.user,
        code=code,
        language=language,
        review_result=review_data,
    )

    LearningEvent.objects.create(
        user=request.user,
        event_type='code_run',
        metadata={'language': language},
    )

    return JsonResponse({'review': review_data})


# ==========================================================================
# LEARNING ANALYTICS
# ==========================================================================


@login_required
def analytics_dashboard_view(request):
    """Learning analytics dashboard."""
    from django.db.models import Avg, Count
    from django.db.models.functions import TruncDate

    user = request.user

    # Activity over time (last 30 days)
    from datetime import timedelta

    thirty_days_ago = timezone.now() - timedelta(days=30)

    daily_activity = (
        LearningEvent.objects.filter(user=user, created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Event type breakdown
    event_breakdown = (
        LearningEvent.objects.filter(user=user).values('event_type').annotate(count=Count('id')).order_by('-count')
    )

    # Quiz performance
    quiz_stats = QuizAttempt.objects.filter(user=user).aggregate(
        avg_score=Avg('score'),
        total_attempts=Count('id'),
    )

    # Total content consumed
    total_audio = AudioFile.objects.filter(user=user).count()

    context = {
        'daily_activity': list(daily_activity),
        'event_breakdown': list(event_breakdown),
        'quiz_stats': quiz_stats,
        'total_audio': total_audio,
        'total_events': LearningEvent.objects.filter(user=user).count(),
        'page_id': 'analytics',
    }

    return render(request, 'boaapp/analytics.html', context)


# ==========================================================================
# SMART CHAPTERED VIDEO PLAYER
# ==========================================================================


@login_required
def chaptered_player_view(request, document_pk):
    """Smart chaptered audio player for all audio of a document."""
    document = get_object_or_404(Document, pk=document_pk, user=request.user)
    audio_files = AudioFile.objects.filter(document=document).order_by('metadata__section_index', 'pk')

    chapters = []
    for audio in audio_files:
        if audio.audio_data:
            chapters.append(
                {
                    'title': audio.title,
                    'audio_pk': audio.pk,
                    'section_index': (audio.metadata or {}).get('section_index', 0),
                }
            )

    # Track event
    LearningEvent.objects.create(
        user=request.user,
        event_type='video_watch',
        metadata={'document_id': document_pk},
    )

    return render(
        request,
        'boaapp/chaptered_player.html',
        {
            'document': document,
            'chapters': chapters,
            'page_id': 'player',
        },
    )


# ==========================================================================
# GITHUB WEBHOOK
# ==========================================================================

import hashlib
import hmac

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def github_webhook(request):
    """Handle GitHub webhook push events."""
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Verify signature
    secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', '')
    if secret:
        signature = request.headers.get('X-Hub-Signature-256', '')
        if not signature:
            return JsonResponse({'error': 'Missing signature'}, status=403)

        expected = 'sha256=' + hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return JsonResponse({'error': 'Invalid signature'}, status=403)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_type = request.headers.get('X-GitHub-Event', '')
    if event_type != 'push':
        return JsonResponse({'status': 'ignored', 'event': event_type})

    repo_name = payload.get('repository', {}).get('full_name', '')
    ref = payload.get('ref', '')
    branch = ref.split('/')[-1] if '/' in ref else ref

    # Find matching webhook configs
    configs = WebhookConfig.objects.filter(
        repo_full_name=repo_name,
        branch=branch,
        is_active=True,
    )

    triggered = 0
    for config in configs:
        if config.auto_pipeline:
            # Check if any .ipynb files were changed
            commits = payload.get('commits', [])
            changed_files = set()
            for commit in commits:
                changed_files.update(commit.get('added', []))
                changed_files.update(commit.get('modified', []))

            ipynb_files = [f for f in changed_files if f.endswith('.ipynb')]
            if ipynb_files:
                logger.info(f'GitHub webhook: {len(ipynb_files)} notebooks changed in {repo_name}/{branch}')
                triggered += 1

    return JsonResponse({'status': 'ok', 'triggered': triggered})


@login_required
def webhook_config_view(request):
    """Manage webhook configurations."""
    configs = WebhookConfig.objects.filter(user=request.user)

    if request.method == 'POST':
        repo = request.POST.get('repo_full_name', '').strip()
        branch = request.POST.get('branch', 'main').strip()
        notebook_path = request.POST.get('notebook_path', '').strip()

        if repo:
            WebhookConfig.objects.create(
                user=request.user,
                repo_full_name=repo,
                branch=branch,
                notebook_path=notebook_path,
            )
            messages.success(request, f'Webhook configured for {repo}/{branch}')

        return redirect('webhook_config')

    return render(
        request,
        'boaapp/webhook_config.html',
        {
            'configs': configs,
            'page_id': 'webhooks',
        },
    )


# ==========================================================================
# TRANSLATION VIEWS
# ==========================================================================

SUPPORTED_LANGUAGES = [
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('zh', 'Chinese'),
    ('pt', 'Portuguese'),
    ('it', 'Italian'),
    ('ru', 'Russian'),
    ('ar', 'Arabic'),
    ('hi', 'Hindi'),
]


@login_required
def translate_document_view(request, document_pk):
    """Trigger translation for a document."""
    from .tasks import translate_document_task

    document = get_object_or_404(Document, pk=document_pk, user=request.user)

    if request.method == 'POST':
        lang_code = request.POST.get('language_code', '')
        lang_name = dict(SUPPORTED_LANGUAGES).get(lang_code, '')

        if lang_code and lang_name:
            translate_document_task.delay(document_pk, lang_code, lang_name)
            messages.success(request, f'Translation to {lang_name} started.')
        else:
            messages.error(request, 'Invalid language selected.')

        return redirect('translate_document', document_pk=document_pk)

    existing = TranslatedContent.objects.filter(document=document)

    return render(
        request,
        'boaapp/translate.html',
        {
            'document': document,
            'languages': SUPPORTED_LANGUAGES,
            'existing_translations': existing,
            'page_id': 'translate',
        },
    )


# ==========================================================================
# VOICE CLONING VIEW
# ==========================================================================


@login_required
def voice_settings_view(request):
    """Voice settings page for TTS provider selection."""
    elevenlabs_available = bool(getattr(settings, 'ELEVENLABS_API_KEY', ''))
    return render(
        request,
        'boaapp/voice_settings.html',
        {
            'elevenlabs_available': elevenlabs_available,
            'page_id': 'voice_settings',
        },
    )


# ==========================================================================
# ADAPTIVE LEARNING
# ==========================================================================


@login_required
def learning_path_view(request):
    """AI-recommended learning path based on user activity."""
    user = request.user

    # Get user's completed content
    completed_sections = CourseSection.objects.filter(completed_by_enrollments__user=user).values_list('id', flat=True)

    # Get quiz performance
    quiz_attempts = QuizAttempt.objects.filter(user=user).select_related('quiz')
    weak_topics = []
    for attempt in quiz_attempts:
        if attempt.total_questions > 0 and (attempt.score / attempt.total_questions) < 0.7:
            weak_topics.append(attempt.quiz.title)

    # Recommend courses user hasn't enrolled in
    enrolled_ids = Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
    recommended_courses = Course.objects.exclude(pk__in=enrolled_ids)[:5]

    context = {
        'weak_topics': weak_topics,
        'recommended_courses': recommended_courses,
        'completed_count': len(completed_sections),
        'total_quizzes': quiz_attempts.count(),
        'page_id': 'learning_path',
    }

    return render(request, 'boaapp/learning_path.html', context)
