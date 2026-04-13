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
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from nbconvert import HTMLExporter

from .forms import CustomUserCreationForm, DocumentForm, ProfileUpdateForm
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

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Event dedup — prevent the same event from being logged more than once
# per user per hour (same event_type + metadata).
# --------------------------------------------------------------------------
_EVENT_DEDUP_SECONDS = 3600  # 1 hour


def _log_learning_event(user, event_type, metadata=None):
    """Create a LearningEvent only if an identical one doesn't already exist
    within the dedup window. Returns the event or None if deduplicated."""
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(seconds=_EVENT_DEDUP_SECONDS)
    recent = LearningEvent.objects.filter(
        user=user,
        event_type=event_type,
        created_at__gte=cutoff,
    )
    # For metadata-keyed dedup, check the specific resource id
    if metadata:
        for key in ('document_id', 'quiz_id', 'conversation_id', 'language'):
            if key in metadata:
                recent = recent.filter(**{f'metadata__{key}': metadata[key]})
                break

    if recent.exists():
        return None

    return LearningEvent.objects.create(
        user=user,
        event_type=event_type,
        metadata=metadata or {},
    )

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
    """Authenticated dashboard, or public landing page for guests."""
    if request.user.is_authenticated:
        return render(request, 'boaapp/home.html')
    return render(request, 'boaapp/landing.html')


@login_required
def profile_view(request):
    """View and update user profile (name, email)."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'boaapp/profile.html', {'form': form})


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


def nfl_draft(request):
    return render(request, 'boaapp/nfl_draft.html')


def nfl_api_proxy(request, endpoint):
    """Proxy SportsData.io NFL API calls to avoid CORS issues."""
    import json
    import urllib.request

    api_key = os.environ.get('SPORTSDATA_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'API key not configured'}, status=503)

    season = request.GET.get('season', '2026')
    valid_seasons = {str(y) + s for y in range(2020, 2030) for s in ('', 'REG', 'PRE', 'POST')}
    if season not in valid_seasons:
        return JsonResponse({'error': 'Invalid season'}, status=400)

    allowed_endpoints = {
        'projections': f'https://api.sportsdata.io/v3/nfl/projections/json/PlayerSeasonProjectionStats/{season}?key={api_key}',
        'defense': f'https://api.sportsdata.io/v3/nfl/projections/json/FantasyDefenseProjectionsBySeason/{season}?key={api_key}',
        'headshots': f'https://api.sportsdata.io/v3/nfl/headshots/json/Headshots?key={api_key}',
    }

    url = allowed_endpoints.get(endpoint)
    if not url:
        return JsonResponse({'error': 'Unknown endpoint'}, status=400)

    try:
        req = urllib.request.Request(url)
        req.add_header('Ocp-Apim-Subscription-Key', api_key)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return JsonResponse(data, safe=False)
    except Exception:
        return JsonResponse({'error': 'API request failed'}, status=502)


def api_orchestration(request):
    return render(request, 'boaapp/api_orchestration.html')


def idp_demo(request):
    return render(request, 'boaapp/idp_demo.html')


def portfolio_chat_api(request):
    """Public AI-powered Q&A widget for the portfolio site.
    Uses Anthropic/OpenAI when available, falls back to keyword matching.
    Streams responses via SSE when Accept: text/event-stream is set.
    """
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

    # ── Try real LLM first ──
    system_prompt = (
        'You are the AI assistant for thenumerix.dev — a portfolio site built by a Platform Engineer / '
        'Data Engineer. The site is built with Django 5.2, PostgreSQL, Celery, Django Channels, and '
        'deployed on Render. It features 7 live interactive demos:\n'
        '- AI Process Flows (Oracle Finance & Accounting automation with AI)\n'
        '- Platform Engineering (Azure DevOps, Databricks & Entra ID pipelines — NFL partner use case)\n'
        '- MLOps Lifecycle (Model training, MLflow, blue-green deploy on AKS — MLB partner use case)\n'
        '- Streaming Architecture (Kafka, Flink, real-time event processing — Netflix-scale patterns)\n'
        '- API Orchestration (Gateway, sagas, circuit breakers, service mesh)\n'
        '- Document Processing (AI-powered OCR, extraction & validation pipelines)\n'
        '- UploadIt! (Jupyter notebook → audio lecture → video → quiz → RAG chat pipeline)\n\n'
        'Technical stack: Python, Azure (DevOps, ML, Entra ID, Databricks), Django, PostgreSQL, '
        'Kafka, Spark, Docker, Redis, Celery, HTMX, Django Ninja API (Swagger at /api/v1/docs), '
        'Sentry, structlog, allauth, GitHub Actions CI.\n\n'
        'Skills: Platform Engineering, MLOps, Data Engineering, Cloud Architecture, Full-Stack Development.\n'
        'Education: Check the Education page for degrees and certifications.\n'
        'Contact: GitHub @ntellecktual, or LinkedIn.\n\n'
        'Keep answers concise (2-4 sentences), friendly, and professional. If asked about hiring or '
        'availability, be encouraging. If asked something unrelated to the portfolio, politely redirect.'
    )

    # Try Anthropic streaming
    anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if anthropic_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=anthropic_key)

            # Check if client wants SSE streaming
            if 'text/event-stream' in request.META.get('HTTP_ACCEPT', ''):
                from django.http import StreamingHttpResponse

                def stream_response():
                    with client.messages.stream(
                        model='claude-sonnet-4-20250514',
                        max_tokens=300,
                        system=system_prompt,
                        messages=[{'role': 'user', 'content': message}],
                    ) as stream:
                        for text in stream.text_stream:
                            yield f'data: {_json.dumps({"delta": text})}\n\n'
                    yield 'data: [DONE]\n\n'

                resp = StreamingHttpResponse(stream_response(), content_type='text/event-stream')
                resp['Cache-Control'] = 'no-cache'
                resp['X-Accel-Buffering'] = 'no'
                return resp

            # Non-streaming fallback
            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=300,
                system=system_prompt,
                messages=[{'role': 'user', 'content': message}],
            )
            return JsonResponse({'reply': response.content[0].text})
        except Exception:
            pass  # Fall through to keyword matching

    # Try OpenAI
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key:
        try:
            import openai as _openai

            client = _openai.OpenAI(api_key=openai_key)

            if 'text/event-stream' in request.META.get('HTTP_ACCEPT', ''):
                from django.http import StreamingHttpResponse

                def stream_response():
                    stream = client.chat.completions.create(
                        model='gpt-4o-mini',
                        max_tokens=300,
                        stream=True,
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': message},
                        ],
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield f'data: {_json.dumps({"delta": delta})}\n\n'
                    yield 'data: [DONE]\n\n'

                resp = StreamingHttpResponse(stream_response(), content_type='text/event-stream')
                resp['Cache-Control'] = 'no-cache'
                resp['X-Accel-Buffering'] = 'no'
                return resp

            response = client.chat.completions.create(
                model='gpt-4o-mini',
                max_tokens=300,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message},
                ],
            )
            return JsonResponse({'reply': response.choices[0].message.content})
        except Exception:
            pass

    # ── Keyword fallback (zero API cost) ──
    return _keyword_chat_reply(message)


def _keyword_chat_reply(message):
    """Keyword-based fallback when no LLM API key is configured."""
    msg = message.lower()
    if any(k in msg for k in ['azure', 'cloud', 'microsoft']):
        reply = (
            'Azure is the backbone of the portfolio — Platform Engineering shows Azure DevOps '
            'pipelines, Entra ID integration, and Databricks ETL. MLOps uses Azure ML.'
        )
    elif any(k in msg for k in ['mlops', 'ml', 'machine learning', 'model']):
        reply = 'The MLOps Lifecycle demo covers model training, MLflow tracking, and blue-green deploy on AKS.'
    elif any(k in msg for k in ['data', 'pipeline', 'etl', 'databricks', 'spark']):
        reply = 'Data engineering: Databricks Spark pipelines, Delta Lake, CI/CD, plus Kafka + Flink for streaming.'
    elif any(k in msg for k in ['kafka', 'stream', 'real-time', 'event']):
        reply = 'Streaming Architecture covers Kafka event brokering, Flink processing, and CDC patterns.'
    elif any(k in msg for k in ['devops', 'cicd', 'ci/cd', 'deploy']):
        reply = 'Platform Engineering shows three CI/CD pipelines: Azure DevOps, Databricks Jobs, and Entra ID.'
    elif any(k in msg for k in ['api', 'gateway', 'orchestrat', 'microservice']):
        reply = 'API Orchestration covers gateway patterns, saga choreography, circuit breakers, and service mesh.'
    elif any(k in msg for k in ['document', 'ocr', 'extract', 'idp']):
        reply = 'Document Processing shows AI-powered OCR, data extraction, and validation pipelines.'
    elif any(k in msg for k in ['oracle', 'finance', 'accounting', 'process flow']):
        reply = 'AI Process Flows demos Oracle Finance & Accounting automation: P2P, O2C, and more.'
    elif any(k in msg for k in ['contact', 'email', 'hire', 'available', 'reach']):
        reply = 'Connect via GitHub (@ntellecktual) or LinkedIn. The portfolio demos are all live and interactive!'
    elif any(k in msg for k in ['project', 'portfolio', 'work', 'experience']):
        reply = '7 live demos spanning MLOps, streaming, CI/CD, API patterns, document processing, and AI automation.'
    elif any(k in msg for k in ['python', 'django', 'stack', 'tech']):
        reply = (
            'Built with Django 5.2, PostgreSQL, Celery, Channels, HTMX, Django Ninja (Swagger at /api/v1/docs), '
            'Sentry, structlog, allauth, and deployed on Render with GitHub Actions CI.'
        )
    elif any(k in msg for k in ['hello', 'hi', 'hey', 'greet']):
        reply = "Hey! I'm the thenumerix assistant. Ask about portfolio demos, skills, or tech stack!"
    else:
        reply = 'Ask me about Azure, MLOps, data pipelines, streaming, or any of the live demos!'
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

        # Track learning event (deduplicated)
        _log_learning_event(request.user, 'quiz_attempt', {'quiz_id': quiz.pk, 'score': score, 'total': total})

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

    # Track event (deduplicated)
    _log_learning_event(request.user, 'chat_message', {'conversation_id': conversation_id})

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

    _log_learning_event(request.user, 'code_run', {'language': language})

    return JsonResponse({'review': review_data})


# ==========================================================================
# LEARNING ANALYTICS
# ==========================================================================


@login_required
def analytics_dashboard_view(request):
    """Learning analytics dashboard."""
    import json
    from datetime import timedelta

    from django.db.models import Avg, Count, F, FloatField
    from django.db.models.functions import TruncDate, TruncHour

    user = request.user
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Activity over time (last 30 days)
    daily_activity = list(
        LearningEvent.objects.filter(user=user, created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    # Serialize dates for JS
    for row in daily_activity:
        row['date'] = row['date'].isoformat() if row['date'] else ''

    # Event type breakdown
    event_breakdown = list(
        LearningEvent.objects.filter(user=user).values('event_type').annotate(count=Count('id')).order_by('-count')
    )

    # Quiz performance
    quiz_stats = QuizAttempt.objects.filter(user=user).aggregate(
        avg_score=Avg('score'),
        total_attempts=Count('id'),
    )

    # Quiz trend (last 10 attempts)
    quiz_trend = list(
        QuizAttempt.objects.filter(user=user)
        .order_by('-completed_at')[:10]
        .values('quiz__title', 'score', 'total_questions', 'completed_at')
    )
    quiz_trend.reverse()
    for row in quiz_trend:
        row['completed_at'] = row['completed_at'].isoformat() if row['completed_at'] else ''
        row['pct'] = round(row['score'] / row['total_questions'] * 100, 1) if row['total_questions'] else 0

    # Hourly heatmap data (last 30 days)
    hourly_data = list(
        LearningEvent.objects.filter(user=user, created_at__gte=thirty_days_ago)
        .annotate(hour=TruncHour('created_at'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )
    # Build 7x24 heatmap grid (day_of_week x hour)
    heatmap = [[0] * 24 for _ in range(7)]
    for row in hourly_data:
        if row['hour']:
            heatmap[row['hour'].weekday()][row['hour'].hour] += row['count']

    # Recent activity feed
    recent_events = list(
        LearningEvent.objects.filter(user=user)
        .order_by('-created_at')[:15]
        .values('event_type', 'metadata', 'created_at')
    )
    for row in recent_events:
        row['created_at'] = row['created_at'].isoformat() if row['created_at'] else ''

    # Streak calculation
    from collections import OrderedDict
    activity_dates = set()
    for row in daily_activity:
        if row['date']:
            activity_dates.add(row['date'])
    streak = 0
    check_date = timezone.now().date()
    while check_date.isoformat() in activity_dates:
        streak += 1
        check_date -= timedelta(days=1)

    total_documents = Document.objects.filter(user=user).count()

    context = {
        'daily_activity': json.dumps(daily_activity),
        'event_breakdown': json.dumps(event_breakdown),
        'quiz_stats': quiz_stats,
        'quiz_trend': json.dumps(quiz_trend),
        'heatmap': json.dumps(heatmap),
        'recent_events': json.dumps(recent_events),
        'total_audio': AudioFile.objects.filter(user=user).count(),
        'total_events': LearningEvent.objects.filter(user=user).count(),
        'total_quizzes': quiz_stats['total_attempts'] or 0,
        'avg_quiz_score': quiz_stats['avg_score'] or 0,
        'total_documents': total_documents,
        'streak': streak,
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

    # Track event (deduplicated — one per document per hour)
    _log_learning_event(request.user, 'video_watch', {'document_id': document_pk})

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


# ==========================================================================
# LIVE API ORCHESTRATION — Real API calls with circuit breaker
# ==========================================================================


def live_api_proxy(request):
    """Call real public APIs and return actual responses with latency metrics."""
    import json
    import time
    import urllib.request
    import urllib.error

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    api_name = data.get('api', '')
    results = []

    API_CONFIGS = {
        'weather': {
            'url': 'https://api.open-meteo.com/v1/forecast?latitude=32.78&longitude=-96.80&current=temperature_2m,wind_speed_10m,relative_humidity_2m&temperature_unit=fahrenheit',
            'label': 'Open-Meteo Weather API',
            'desc': 'Real-time weather for Dallas, TX',
        },
        'countries': {
            'url': 'https://restcountries.com/v3.1/alpha/US?fields=name,capital,population,currencies,languages',
            'label': 'REST Countries API',
            'desc': 'Country metadata lookup',
        },
        'universities': {
            'url': 'https://universities.hipolabs.com/search?country=United+States&name=texas',
            'label': 'Universities API',
            'desc': 'University search — Texas institutions',
        },
        'spacex': {
            'url': 'https://api.spacexdata.com/v4/launches/latest',
            'label': 'SpaceX Launches API',
            'desc': 'Latest SpaceX launch data',
        },
        'exchange': {
            'url': 'https://open.er-api.com/v6/latest/USD',
            'label': 'Exchange Rate API',
            'desc': 'Live USD exchange rates',
        },
    }

    apis_to_call = [api_name] if api_name and api_name in API_CONFIGS else list(API_CONFIGS.keys())

    for name in apis_to_call:
        cfg = API_CONFIGS[name]
        start = time.monotonic()
        status_code = 0
        response_data = None
        error_msg = ''
        try:
            req = urllib.request.Request(cfg['url'], headers={'User-Agent': 'BOA-Portfolio/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                status_code = resp.status
                raw = resp.read().decode('utf-8')
                response_data = json.loads(raw)
        except urllib.error.HTTPError as e:
            status_code = e.code
            error_msg = str(e.reason)
        except urllib.error.URLError as e:
            status_code = 503
            error_msg = f'Connection failed: {e.reason}'
        except Exception as e:
            status_code = 500
            error_msg = str(e)

        latency_ms = round((time.monotonic() - start) * 1000)

        # Truncate large responses
        if response_data and isinstance(response_data, list) and len(response_data) > 5:
            response_data = response_data[:5]

        results.append({
            'api': name,
            'label': cfg['label'],
            'desc': cfg['desc'],
            'url': cfg['url'],
            'status': status_code,
            'latency_ms': latency_ms,
            'data': response_data,
            'error': error_msg,
            'circuit': 'closed' if status_code == 200 else 'open',
        })

    return JsonResponse({'results': results, 'timestamp': timezone.now().isoformat()})


# ==========================================================================
# AI JOB MATCH ANALYZER
# ==========================================================================


def job_match_view(request):
    """Job match analyzer page — public."""
    return render(request, 'boaapp/job_match.html', {'page_id': 'job_match'})


def job_match_api(request):
    """Analyze a job description against portfolio data using LLM."""
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    job_description = data.get('job_description', '').strip()
    if not job_description or len(job_description) < 20:
        return JsonResponse({'error': 'Please provide a job description (at least 20 characters).'}, status=400)

    # Truncate to prevent abuse
    job_description = job_description[:5000]

    # Portfolio context
    portfolio_context = """
CANDIDATE: Kieth — thenumerix
CURRENT ROLE: Senior Data Engineer / Platform Engineer

TECHNICAL SKILLS:
- Cloud: Azure (DevOps, Data Factory, Databricks, Synapse, Functions, App Service, Entra ID, Key Vault)
- Data Engineering: Python, SQL, Spark, Kafka, Flink, Airflow, dbt, Delta Lake
- MLOps: MLflow, Azure ML, model registry, feature store, drift monitoring, XGBoost, scikit-learn
- DevOps/Platform: Terraform, Docker, Kubernetes, GitHub Actions, Azure DevOps CI/CD, Helm
- Backend: Django, FastAPI, PostgreSQL, Redis, Celery, WebSockets (Django Channels)
- Frontend: HTML/CSS/JS, Bootstrap, HTMX, Chart.js
- AI/LLM: Claude API, OpenAI GPT, RAG (ChromaDB), prompt engineering, embeddings
- Streaming: Kafka, Flink, Redis Streams, event-driven architecture

PORTFOLIO HIGHLIGHTS:
- Built a full-stack Django app with Celery, WebSockets, RAG chatbot, AI quiz generation, and video pipeline
- Oracle Finance & Accounting automation (AP/AR process flows with Claude AI)
- NFL platform engineering (Azure DevOps + Databricks + Entra ID RBAC)
- MLB game prediction MLOps pipeline (XGBoost, feature store, model registry)
- Netflix-style real-time streaming architecture (Kafka + Flink + Redis)
- API orchestration with saga pattern, circuit breakers, and resilience patterns
- Intelligent Document Processing pipeline (OCR, classification, extraction, validation)
- Live code playground with Pyodide (in-browser Python) + AI code review
- System observability dashboard with real-time health monitoring

EDUCATION:
- Doctoral Studies, University of Texas at Austin
- PCAP Certified Python Programmer, Python Institute
- M.S. Data Science, Southern Methodist University
- B.S. Computer Science, UC Riverside

NOTABLE EMPLOYERS: Witherite Law Group, American Airlines, Citi, Barvin, Code Ninjas
"""

    use_llm = getattr(settings, 'USE_LLM', False)

    if use_llm:
        try:
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
            if api_key:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                msg = client.messages.create(
                    model='claude-sonnet-4-20250514',
                    max_tokens=1500,
                    messages=[{
                        'role': 'user',
                        'content': f"""Analyze this job description against the candidate's profile. Return JSON only, no markdown:

{{
  "match_score": <0-100>,
  "match_level": "<Perfect Match|Strong Match|Good Match|Partial Match|Weak Match>",
  "matching_skills": ["skill1", "skill2", ...],
  "missing_skills": ["skill1", ...],
  "talking_points": ["compelling point for interview 1", "point 2", "point 3"],
  "suggested_projects": ["project to highlight 1", "project 2"],
  "salary_insight": "<brief market insight if discernible>",
  "summary": "<2-3 sentence executive summary>"
}}

CANDIDATE PROFILE:
{portfolio_context}

JOB DESCRIPTION:
{job_description}"""
                    }],
                )
                import json as json_mod
                result_text = msg.content[0].text.strip()
                # Try to parse JSON from the response
                if result_text.startswith('{'):
                    result = json_mod.loads(result_text)
                else:
                    # Extract JSON from markdown code block
                    start = result_text.find('{')
                    end = result_text.rfind('}') + 1
                    result = json_mod.loads(result_text[start:end])
                return JsonResponse({'analysis': result})
        except Exception as e:
            logger.warning(f'LLM job match failed: {e}')

    # Dev mode / fallback: keyword-based analysis
    jd_lower = job_description.lower()
    skills_map = {
        'python': 95, 'django': 90, 'sql': 95, 'azure': 90, 'aws': 60,
        'spark': 85, 'kafka': 85, 'docker': 80, 'kubernetes': 75, 'terraform': 80,
        'data engineer': 95, 'mlops': 90, 'machine learning': 85, 'devops': 85,
        'ci/cd': 90, 'postgresql': 90, 'redis': 85, 'api': 90, 'rest': 90,
        'etl': 90, 'databricks': 90, 'airflow': 80, 'dbt': 75, 'fastapi': 80,
        'celery': 85, 'websocket': 85, 'llm': 85, 'rag': 85, 'gpt': 80,
        'javascript': 70, 'react': 40, 'java': 30, 'go': 20, 'rust': 15,
    }
    matching = []
    missing = []
    scores = []
    for skill, score in skills_map.items():
        if skill in jd_lower:
            if score >= 60:
                matching.append(skill.title())
                scores.append(score)
            else:
                missing.append(skill.title())

    avg_score = round(sum(scores) / len(scores)) if scores else 45
    match_score = min(avg_score + len(matching) * 2, 100)

    if match_score >= 85:
        level = 'Perfect Match'
    elif match_score >= 70:
        level = 'Strong Match'
    elif match_score >= 55:
        level = 'Good Match'
    elif match_score >= 40:
        level = 'Partial Match'
    else:
        level = 'Weak Match'

    result = {
        'match_score': match_score,
        'match_level': level,
        'matching_skills': matching[:12],
        'missing_skills': missing[:5],
        'talking_points': [
            'Built production Django platform with Celery, WebSockets, RAG chatbot, and AI-powered features',
            'Hands-on Azure cloud experience across DevOps, Data Factory, Databricks, and Entra ID',
            'End-to-end MLOps pipeline with model training, registry, and monitoring',
        ],
        'suggested_projects': [
            'AI Process Flows demo — enterprise finance automation',
            'MLOps Lifecycle — live MLB prediction pipeline',
        ],
        'salary_insight': 'Market rate for matching skills: competitive with senior-level roles',
        'summary': f'Based on keyword analysis, this role is a {level.lower()} with {len(matching)} matching competencies. '
                   f'Strongest areas: cloud infrastructure, data engineering, and full-stack development.',
    }
    return JsonResponse({'analysis': result})


# ─── New Demo Views ────────────────────────────────────────────────────────────

def feature_store_view(request):
    return render(request, 'boaapp/feature_store.html')


def supply_chain_view(request):
    return render(request, 'boaapp/supply_chain.html')


def anomaly_detection_view(request):
    return render(request, 'boaapp/anomaly_detection.html')


def data_quality_view(request):
    return render(request, 'boaapp/data_quality.html')


def schema_registry_view(request):
    return render(request, 'boaapp/schema_registry.html')


def multi_agent_view(request):
    return render(request, 'boaapp/multi_agent.html')


@require_POST
def multi_agent_api(request):
    """Run a 5-agent orchestration pipeline (Planner → Researcher → Calculator → Critic → Synthesizer)."""
    import json as _json

    try:
        body = _json.loads(request.body)
    except (_json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question = body.get('question', '').strip()
    if not question or len(question) < 5:
        return JsonResponse({'error': 'Question is required.'}, status=400)

    question = question[:2000]

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are orchestrating a 5-agent AI pipeline. For the question below, provide each agent's output.
Return ONLY valid JSON with exactly these keys: planner, researcher, calculator, critic, synthesizer.
Each value should be a focused, practical paragraph (3-6 sentences) from that agent's perspective.

Agents:
- planner: Breaks the question into a structured step-by-step plan.
- researcher: Provides relevant domain knowledge, patterns, and context.
- calculator: Gives quantitative estimates, sizing, or performance math where applicable.
- critic: Identifies risks, edge cases, or gaps in the plan.
- synthesizer: Writes the final integrated recommendation.

QUESTION: {question}

Respond with JSON only, no markdown fences."""
            msg = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=1800,
                messages=[{'role': 'user', 'content': prompt}],
            )
            raw = msg.content[0].text.strip()
            start = raw.find('{')
            end = raw.rfind('}') + 1
            steps = _json.loads(raw[start:end])
            return JsonResponse({'steps': steps})
        except Exception as e:
            logger.warning(f'multi_agent_api LLM error: {e}')

    # Fallback: return a minimal structured response
    return JsonResponse({'steps': None})
