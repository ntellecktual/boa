import logging
import nbformat
from nbconvert import HTMLExporter # Add this import
import os
import threading

from django.conf import settings
from django.db import transaction
from django.contrib import messages
from kombu import Connection
from celery.result import AsyncResult
from celery import current_app
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm

from .forms import DocumentForm, CustomUserCreationForm
from .models import (
    Document, AudioFile, VideoFile, Course, Enrollment, CourseSection,
    PortfolioItem, DevopsItem, ResumeDocument,
    Quiz, QuizQuestion, QuizAttempt, ChatConversation, ChatMessage,
    LearningEvent, CourseThumbnail, TranslatedContent, WebhookConfig,
    PipelineRun, CodeReview,
)
from .tasks import create_audio_files_task, create_single_video_task, run_full_pipeline_task
from .utils import _get_video_paths, _get_random_background
from .process_notebook import handle_uploaded_file

# Set up logging
logger = logging.getLogger(__name__)

def render_notebook_to_html(filepath):
    """Converts a Jupyter Notebook file (.ipynb) to HTML."""
    if not os.path.exists(filepath):
        logger.error(f"Notebook file not found: {filepath}")
        return f"<p>Error: Notebook file not found at {filepath}</p>"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Configure the HTML exporter
        html_exporter = HTMLExporter()

        # --- Template Selection ---
        # 'basic' is very minimal.
        # 'classic' or 'lab' provide richer styling but might have more external dependencies (like fonts).
        html_exporter.template_name = 'basic' # Current setting
        # html_exporter.template_name = 'classic' 
        # html_exporter.template_name = 'lab'

        # --- Content Exclusion ---
        # Exclude the "In [1]:", "Out [1]:" prompts
        html_exporter.exclude_output_prompt = True
        # Set to True if you want to hide the code input cells by default
        html_exporter.exclude_input = False 

        # --- Embedding Resources (More Advanced) ---
        # html_exporter.embed_images = True # To embed images directly in HTML (can increase HTML size)

        (body, resources) = html_exporter.from_notebook_node(nb) # Corrected method name
        
        # --- Advanced: Embedding CSS (if needed and available in resources) ---
        # if resources.get('inlining', {}).get('css'):
        #     css_to_embed = "\n".join(resources['inlining']['css'])
        #     body = f"<style>{css_to_embed}</style>\n{body}"
        return body

    except nbformat.validator.NotebookValidationError as e_nb_invalid:
        logger.error(f"Invalid notebook format for {filepath}: {e_nb_invalid}", exc_info=True)
        return f"<p>Error: Invalid Jupyter Notebook format: {e_nb_invalid}</p>"
    except Exception as e:
        logger.error(f"Error rendering notebook {filepath}: {e}", exc_info=True)
        return f"<p>Error rendering notebook: {e}</p>"


def course_list_view(request):
    courses = Course.objects.all().order_by('updated_at') # Changed to order by updated_at ascending
    user_enrollments_ids = []
    if request.user.is_authenticated:
        user_enrollments_ids = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    
    return render(request, 'boaapp/course_list.html', {'courses': courses, 'user_enrollments_ids': user_enrollments_ids})

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    sections = course.sections.all().order_by('order') # CourseSection.Meta.ordering handles this too
    
    is_enrolled = False
    completed_learn_sections_ids = []
    current_step_number = 0
    current_step_name = "Not Enrolled"
    current_step_description = "Enroll in the course to begin your journey."
    enrollment = None

    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        is_enrolled = True
        completed_learn_sections_ids = list(enrollment.completed_learn_sections.values_list('id', flat=True))

        # Determine current step
        if not enrollment.all_learn_sections_completed():
            current_step_number = 1
            current_step_name = "Step 1: Learning"
            current_step_description = "Focus on understanding the core concepts and materials provided in the sections below."
        elif not enrollment.create_step_completed:
            current_step_number = 2
            current_step_name = "Step 2: Creating"
            current_step_description = "Apply what you've learned! It's time to build/create the project."
        elif not enrollment.teach_step_completed:
            current_step_number = 3
            current_step_name = "Step 3: Teaching"
            current_step_description = "Solidify your understanding by preparing to teach this topic to others."
        else:
            current_step_name = "Course Completed!"
            current_step_description = "Congratulations on completing all steps of this course!"

    except Enrollment.DoesNotExist:
        is_enrolled = False

    # Prepare sections data, including rendered HTML for notebooks
    sections_data = []
    for section in sections:
        section_info = {
            'section': section,
            'is_completed': section.id in completed_learn_sections_ids,
            'learn_content_html': None # Placeholder for rendered HTML
        }
        if section.learn_content_file and section.learn_content_file.name.lower().endswith('.ipynb'):
             # Construct absolute path to the file
             file_path = os.path.join(settings.MEDIA_ROOT, section.learn_content_file.name)
             section_info['learn_content_html'] = render_notebook_to_html(file_path)
        sections_data.append(section_info)


    context = {
        'course': course,
        'sections_data': sections_data, # Pass the processed sections data
        'is_enrolled': is_enrolled,
        'completed_learn_sections_ids': completed_learn_sections_ids,
        'current_step_name': current_step_name,
        'current_step_description': current_step_description,
        'page_id': 'course-detail' 
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
    return redirect('course_list') # Should not be reached via GET directly typically

@login_required
def mark_section_learned_view(request, section_id):
    section = get_object_or_404(CourseSection, pk=section_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=section.course)
    enrollment.completed_learn_sections.add(section)
    messages.success(request, f"Section '{section.title}' marked as learned!")
    return redirect('course_detail', course_id=section.course.id)


def uploadit(request):
    uploaded_files = []
    if request.user.is_authenticated: # Check login status
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
    return render(request, 'boaapp/uploadit.html', {'items': items, 'page_id': 'uploadit', **context})


def boashedskin_view(request):
    return HttpResponse("Health check successful!")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Save the user and get the user object
            username = form.cleaned_data.get('username')
            login(request, user) # Log the new user in automatically
            messages.success(request, f'Account created for {username}! Welcome to the courses.')
            return redirect('home') # Redirect to home dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'boaapp/register.html', {'form': form})

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
                messages.info(request, f"Welcome back, {username}.")
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Authentication failed unexpectedly.")
        else:
            messages.error(request, "Invalid username or password.")
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

            # --- Duplicate Check Logic ---
            try:
                # Ensure nbformat is imported: import nbformat
                # Ensure os is imported: import os
                uploaded_file.seek(0) # Rewind file pointer before reading
                uploaded_nb = nbformat.read(uploaded_file, as_version=4)
                uploaded_title_original = None # Store original case for message
                uploaded_title_lower = None

                # Find the first H1 header in the uploaded notebook
                for cell in uploaded_nb.cells:
                    if cell.cell_type == 'markdown':
                        lines = [line.strip() for line in cell['source'].split('\n') if line.strip()]
                        if lines and lines[0].startswith('# '):
                            uploaded_title_original = lines[0][2:].strip()
                            uploaded_title_lower = uploaded_title_original.lower()
                            break # Found first H1

                # Fallback to filename if no H1 found
                if not uploaded_title_lower:
                     uploaded_title_original = os.path.splitext(original_filename)[0]
                     uploaded_title_lower = uploaded_title_original.lower()

                uploaded_file.seek(0) # Rewind again before potential save or further processing

                # Check against titles derived from existing documents for this user
                existing_docs = Document.objects.filter(user=request.user)
                for doc in existing_docs:
                    try:
                        # Construct path to existing notebook
                        existing_doc_path = os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))
                        if os.path.exists(existing_doc_path):
                            with open(existing_doc_path, 'r', encoding='utf-8') as f_existing:
                                existing_nb = nbformat.read(f_existing, as_version=4)
                                existing_title_original = None
                                existing_title_lower = None

                                # Find first H1 in existing notebook
                                for cell_existing in existing_nb.cells:
                                    if cell_existing.cell_type == 'markdown':
                                        lines_existing = [line.strip() for line in cell_existing['source'].split('\n') if line.strip()]
                                        if lines_existing and lines_existing[0].startswith('# '):
                                            existing_title_original = lines_existing[0][2:].strip()
                                            existing_title_lower = existing_title_original.lower()
                                            break # Found first H1

                                # Fallback for existing notebook title
                                if not existing_title_lower:
                                    existing_title_original = os.path.splitext(os.path.basename(str(doc.uploaded_file)))[0]
                                    existing_title_lower = existing_title_original.lower()

                                # Perform the duplicate check (case-insensitive, excluding "great job!")
                                if uploaded_title_lower == existing_title_lower and uploaded_title_lower != "great job!":
                                     logger.warning(f"Duplicate title detected for user {request.user.username}: '{uploaded_title_original}' matches existing document PK {doc.pk}")
                                     messages.error(request, f"A notebook with the same title ('{uploaded_title_original}') already exists. Please rename the notebook's first H1 header or upload a different file.")
                                     return redirect('upload_document') # Stop processing and redirect

                                break # Move to the next existing document after checking the first H1

                    except Exception as e_read_existing:
                        # Log error reading existing file but continue checking others
                        logger.warning(f"Could not read or parse existing document {doc.uploaded_file} (PK: {doc.pk}) for title check: {e_read_existing}")
                        continue # Skip this document check

            except nbformat.validator.NotebookValidationError as e_nb_invalid:
                 logger.error(f"Invalid notebook format uploaded by user {request.user.username}: {original_filename}. Error: {e_nb_invalid}", exc_info=True)
                 messages.error(request, "The uploaded file is not a valid Jupyter Notebook. Please check the file format.")
                 return redirect('upload_document')
            except Exception as e_read_upload:
                logger.error(f"Failed to read uploaded notebook content for title check: {original_filename}. Error: {e_read_upload}", exc_info=True)
                messages.error(request, "Failed to read notebook content. Please upload a valid .ipynb file.")
                return redirect('upload_document')
            # --- End Duplicate Check Logic ---


            # Save Document model instance first
            document = form.save(commit=False)
            document.user = request.user
            document.save() # Save to get a PK

            # Handle file saving using the uploaded_file variable
            saved_file_path = handle_uploaded_file(uploaded_file)
            # Ensure the path saved is relative to MEDIA_ROOT
            relative_path = os.path.relpath(saved_file_path, settings.MEDIA_ROOT)
            # Replace backslashes with forward slashes for consistency if needed
            document.uploaded_file.name = relative_path.replace('\\', '/')
            document.save(update_fields=['uploaded_file'])

            # --- Trigger Audio Creation Task ---
            logger.info(f"Triggering Celery task create_audio_files_task for document PK {document.pk}")
            try:
                if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
                    # Eager mode: run synchronously, no broker connection needed
                    logger.info("Running task in eager mode (synchronous)")
                    async_result = create_audio_files_task.apply_async(
                        args=[document.pk, request.user.pk]
                    )
                else:
                    # Production mode: use explicit connection to broker
                    broker_url = settings.CELERY_BROKER_URL
                    logger.debug(f"Using broker URL for explicit connection: {broker_url}")
                    with Connection(broker_url) as conn:
                        logger.debug(f"Explicit Kombu connection established: {conn}")
                        async_result = create_audio_files_task.apply_async(
                            args=[document.pk, request.user.pk],
                            connection=conn
                        )
                task_id = async_result.id
                logger.info(f"Task sent successfully. Task ID: {task_id}")
                redirect_url = f"{redirect('dashboard').url}?audio_task_id={task_id}"

            except ConnectionRefusedError as e_conn_refused:
                logger.error(f"Connection refused: {e_conn_refused}", exc_info=True)
                messages.error(request, "Failed to connect to the background task queue (Connection Refused). Please ensure Redis is running and accessible.")
                return redirect('dashboard')
            except Exception as e_send:
                 logger.error(f"Error sending task: {e_send}", exc_info=True)
                 messages.error(request, f"Failed to queue background task: {e_send}")
                 return redirect('dashboard')
            # --- End Task Triggering ---

            messages.success(request, f"Notebook '{original_filename}' uploaded successfully. Audio generation started in the background.")
            # Redirect to dashboard with task ID
            return redirect(redirect_url)
        # else: If form is not valid, it will fall through to render the form again
    else: # GET request
        form = DocumentForm()

    return render(request, 'boaapp/upload.html', {
        'form': form,
        'page_id': 'uploadit'
    })


def check_task_status(request, task_id):
    """Checks the status of a Celery task."""
    app = current_app._get_current_object()
    task_result = AsyncResult(task_id, app=app)
    status = task_result.status
    result = None

    if task_result.failed():
        status = 'FAILURE' # Standardize failure status
        try:
            # Try to get the exception message if available
            result = str(task_result.info) if task_result.info else 'Task failed without specific error info.'
        except Exception:
            result = 'Could not retrieve failure reason.'
        logger.warning(f"Task {task_id} failed. Info: {result}")
    elif status == 'SUCCESS':
        try:
            # Get the actual result returned by the task
            result = task_result.get(timeout=1.0) # Short timeout
        except Exception as e:
            logger.warning(f"Could not retrieve result for successful task {task_id}: {e}")
            result = 'Success, but result retrieval failed.'

    response_data = {
        'task_id': task_id,
        'status': status,
        'result': result, # Include result/error info
    }
    return JsonResponse(response_data)

def process_flows(request):
    """Render AI Process Flows demo page."""
    return render(request, 'boaapp/process_flows.html')

def portfolio_showcase(request):
    portfolio_items = PortfolioItem.objects.prefetch_related(
        'scrolling_images').all()
    devops_items = DevopsItem.objects.prefetch_related(
        'scrolling_images').all()
    return render(request, 'boaapp/portfolio_showcase.html', {
        'portfolio_items': portfolio_items,
        'devops_items': devops_items,
    })

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
        reply = ("Azure is the backbone of most of the portfolio. The Platform Engineering demo "
                 "shows Azure DevOps pipelines, Entra ID integration, and Databricks-based ETL. "
                 "The MLOps demo uses Azure ML for model training and deployment.")
    elif any(k in msg for k in ['mlops', 'ml', 'machine learning', 'model']):
        reply = ("The MLOps Lifecycle demo walks through model training, feature stores, experiment "
                 "tracking with MLflow, and blue-green deployment on AKS. "
                 "Check it out at the Live Demos page!")
    elif any(k in msg for k in ['data', 'pipeline', 'etl', 'databricks', 'spark']):
        reply = ("Data engineering is a core focus — the Platform Engineering demo covers "
                 "Databricks Spark pipelines, Delta Lake, and CI/CD integration. "
                 "The Streaming Architecture demo shows Kafka + Flink real-time event processing.")
    elif any(k in msg for k in ['kafka', 'stream', 'real-time', 'event']):
        reply = ("The Streaming Architecture demo covers Apache Kafka event brokering, "
                 "Flink stream processing, schema registries, and CDC patterns used at Netflix-scale.")
    elif any(k in msg for k in ['devops', 'cicd', 'ci/cd', 'pipeline', 'deploy']):
        reply = ("The Platform Engineering demo shows three full CI/CD pipelines: "
                 "Azure DevOps, Databricks Jobs, and Entra ID automation — all for a casino platform use case.")
    elif any(k in msg for k in ['api', 'gateway', 'orchestrat', 'microservice']):
        reply = ("The API Orchestration demo covers API gateway patterns, saga choreography, "
                 "circuit breakers, and service mesh fundamentals.")
    elif any(k in msg for k in ['document', 'ocr', 'extract', 'idp']):
        reply = ("The Document Processing (IDP) demo shows AI-powered OCR, structured data "
                 "extraction, and validation pipelines — great for financial document automation.")
    elif any(k in msg for k in ['oracle', 'finance', 'accounting', 'process flow']):
        reply = ("The AI Process Flows demo shows Oracle Finance & Accounting automation "
                 "workflows powered by AI — procure-to-pay, order-to-cash, and more.")
    elif any(k in msg for k in ['nfl', 'mlb', 'netflix', 'sport', 'partner']):
        reply = ("The portfolio demos are built around real enterprise partner use cases: "
                 "Oracle (finance automation), NFL (Azure DevOps pipelines), "
                 "MLB (MLOps at scale), and Netflix (streaming architecture).")
    elif any(k in msg for k in ['education', 'degree', 'school', 'university', 'certif']):
        reply = ("The Education section covers degrees and certifications. "
                 "Navigate to Education in the sidebar (or Profile on the home dashboard) for the full details.")
    elif any(k in msg for k in ['contact', 'email', 'hire', 'available', 'reach']):
        reply = ("The best way to connect is via GitHub (@ntellecktual) or LinkedIn. "
                 "Feel free to explore the portfolio demos — they're all fully interactive!")
    elif any(k in msg for k in ['project', 'portfolio', 'work', 'experience']):
        reply = ("The Portfolio section showcases enterprise projects across cloud, data, and AI. "
                 "There are 7 live interactive demos spanning MLOps, streaming, CI/CD, API patterns, "
                 "document processing, and AI process automation.")
    elif any(k in msg for k in ['python', 'django', 'stack', 'tech']):
        reply = ("The site itself is built with Django 5.1, PostgreSQL, Celery + Redis, "
                 "and deployed on Render. The demos use Bootstrap 5, vanilla JS, and Font Awesome. "
                 "Python is the primary language across all backend work.")
    elif any(k in msg for k in ['upload', 'notebook', 'jupyter', 'audio', 'video']):
        reply = ("UploadIt! lets you upload Jupyter notebooks and auto-generates audio lectures, "
                 "video content with synced text, quizzes, and a RAG-powered chatbot — "
                 "all in one pipeline. Try it from the sidebar!")
    elif any(k in msg for k in ['hello', 'hi', 'hey', 'greet']):
        reply = ("Hey! I'm the thenumerix assistant. Ask me about the portfolio demos, "
                 "skills, tech stack, or anything else you see on the site!")
    elif any(k in msg for k in ['demo', 'live', 'interact']):
        reply = ("There are 7 live interactive demos: AI Process Flows, UploadIt!, Platform Engineering, "
                 "MLOps Lifecycle, Streaming Architecture, API Orchestration, and Document Processing. "
                 "Hit 'Discover' in the sidebar to explore them all!")
    else:
        reply = ("I can answer questions about the portfolio demos, tech stack, skills, and experience. "
                 "Try asking about Azure, MLOps, data pipelines, or any of the live demos!")

    return JsonResponse({'reply': reply})

@login_required
def dashboard(request):
    user_documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

    dashboard_items = []
    total_audio_count = 0

    for doc in user_documents:
        doc_data = {
            'document': doc,
            'notebook_exists': os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))),
            'audio_files': []
        }
        audio_files_for_doc = AudioFile.objects.filter(document=doc).order_by('metadata__section_index', 'pk') # Order by index
        total_audio_count += audio_files_for_doc.count()

        for audio in audio_files_for_doc:
            audio_path_abs = os.path.join(settings.MEDIA_ROOT, str(audio.file))
            video_output_dir, video_path_abs, sync_file = _get_video_paths(audio) # Use helper

            video_exists = os.path.exists(video_path_abs) if video_path_abs else False
            video_url = (settings.MEDIA_URL + os.path.relpath(video_path_abs, settings.MEDIA_ROOT).replace('\\', '/')) if video_exists else None

            doc_data['audio_files'].append({
                'audio': audio,
                'audio_exists': os.path.exists(audio_path_abs),
                'video_exists': video_exists,
                'video_url': video_url, # Pass URL for playing/linking
                'video_filename': os.path.basename(video_path_abs) if video_exists else None,
            })
        dashboard_items.append(doc_data)

    context = {
        'dashboard_items': dashboard_items,
        'document_count': user_documents.count(),
        'total_audio_count': total_audio_count,
        # 'latest_doc': latest_doc, # Remove if using dashboard_items structure
        # 'all_docs': documents, # Remove if using dashboard_items structure
        # 'latest_only': latest_only, # Remove if logic changes
        # 'displayed_count': displayed_count, # Remove if logic changes
        'page_id': 'dashboard', # Set appropriate page ID
    }

    return render(request, 'boaapp/dashboard.html', context)
  
@login_required
@transaction.atomic
def delete_orphaned_files(request):
    # This logic might need adjustment based on the new directory structure
    # (audio/notebook_name/file.mp3, video/notebook_name/file.mp4)
    deleted_docs = 0
    deleted_audio = 0
    deleted_videos = 0 # Add video deletion
    logger.info(f"Running delete_orphaned_files for user {request.user.username}")

    # Iterate through documents potentially belonging to *any* user if checking orphans globally
    # Or filter by request.user if only cleaning for the current user
    for doc in Document.objects.filter(user=request.user): # Or Document.objects.all()
        doc_exists = os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file)))
        audio_files = AudioFile.objects.filter(document=doc)
        related_files_exist = doc_exists # Start assuming doc exists

        if not audio_files.exists() and not doc_exists:
             # If no audio records AND no doc file, safe to delete the doc record
             logger.info(f"Deleting orphaned document record PK {doc.pk} (no file, no audio records).")
             doc.delete()
             deleted_docs += 1
             continue

        # Check if *any* related files (audio or video) exist on disk
        if audio_files.exists():
            related_files_exist = False # Assume no files exist until one is found
            for audio in audio_files:
                audio_path = os.path.join(settings.MEDIA_ROOT, str(audio.file))
                _, video_path, _ = _get_video_paths(audio)
                if os.path.exists(audio_path) or (video_path and os.path.exists(video_path)):
                    related_files_exist = True
                    break # Found at least one related file

        # If the notebook file is gone AND no related audio/video files exist on disk
        if not doc_exists and not related_files_exist:
            logger.info(f"Deleting document record PK {doc.pk} and associated DB audio records (notebook missing, no audio/video files found).")
            for audio in audio_files:
                # No need to delete files here as they don't exist
                audio.delete() # Delete DB record
                deleted_audio += 1 # Count deleted DB records
            doc.delete()
            deleted_docs += 1

    # Separate loop for orphaned audio/video files (where DB record exists but file doesn't)
    for audio in AudioFile.objects.filter(user=request.user): # Or AudioFile.objects.all()
         audio_path = os.path.join(settings.MEDIA_ROOT, str(audio.file))
         _, video_path, _ = _get_video_paths(audio)
         audio_exists = os.path.exists(audio_path)
         video_exists = video_path and os.path.exists(video_path)

         if not audio_exists and not video_exists:
             # If neither audio nor video file exists, delete the DB record
             logger.info(f"Deleting orphaned audio record PK {audio.pk} (no audio/video file found).")
             audio.delete()
             deleted_audio += 1

    # Add cleanup for empty directories if desired (more complex)

    return JsonResponse({'deleted_docs': deleted_docs, 'deleted_audio_records': deleted_audio})

@login_required
@transaction.atomic
def delete_all_files(request):
    # Careful with this!
    if request.method == 'POST': # Ensure it's a POST request
        logger.warning(f"User {request.user.username} initiated DELETE ALL FILES.")
        deleted_docs_count = 0
        deleted_audio_count = 0
        deleted_video_count = 0

        for doc in Document.objects.filter(user=request.user):
            ipynb_path = os.path.join(settings.MEDIA_ROOT, str(doc.uploaded_file))
            if os.path.exists(ipynb_path):
                try:
                    os.remove(ipynb_path)
                    logger.info(f"Deleted notebook file: {ipynb_path}")
                except OSError as e:
                     logger.error(f"Error deleting notebook file {ipynb_path}: {e}")
            doc.delete()
            deleted_docs_count += 1

        for audio in AudioFile.objects.filter(user=request.user):
            audio_path = os.path.join(settings.MEDIA_ROOT, str(audio.file))
            _, video_path, _ = _get_video_paths(audio)

            if os.path.exists(audio_path):
                 try:
                    os.remove(audio_path)
                    logger.info(f"Deleted audio file: {audio_path}")
                 except OSError as e:
                     logger.error(f"Error deleting audio file {audio_path}: {e}")

            if video_path and os.path.exists(video_path):
                 try:
                    os.remove(video_path)
                    logger.info(f"Deleted video file: {video_path}")
                    deleted_video_count += 1
                 except OSError as e:
                     logger.error(f"Error deleting video file {video_path}: {e}")

            # Clean up sync file too
            sync_file = video_path.replace('.mp4', '_sync.json') if video_path else None
            if sync_file and os.path.exists(sync_file):
                try:
                    os.remove(sync_file)
                except OSError as e:
                    logger.error(f"Error deleting sync file {sync_file}: {e}")


            audio.delete()
            deleted_audio_count += 1

        # Optional: Clean up empty directories in media/audio and media/video
        # ... (implementation for directory cleanup) ...

        messages.success(request, f"All your documents ({deleted_docs_count}), audio files ({deleted_audio_count}), and videos ({deleted_video_count}) have been deleted.")
        return JsonResponse({'status': 'All files deleted', 'docs': deleted_docs_count, 'audio': deleted_audio_count, 'videos': deleted_video_count})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def generate_video(request, audio_file_pk):
    """Triggers video generation for a single audio file in a background thread."""
    audio_file = get_object_or_404(AudioFile, pk=audio_file_pk, user=request.user)
    logger.info(f"User {request.user.username} initiated video generation for AudioFile PK {audio_file_pk}")

    def _gen_video(pk):
        try:
            create_single_video_task.apply(args=[pk])
        except Exception as e:
            logger.error(f"Background video gen failed for AudioFile PK {pk}: {e}")

    thread = threading.Thread(target=_gen_video, args=(audio_file_pk,), daemon=True)
    thread.start()

    messages.success(request, f"Video generation started for '{audio_file.title}'. It will appear on the dashboard when ready.")
    return redirect('dashboard')

@login_required
def generate_all_videos(request):
    """Triggers video generation tasks for all audio files for the user in a background thread."""
    user_audio_files = list(AudioFile.objects.filter(user=request.user))

    # Collect audio PKs that need videos
    audio_pks_to_generate = []
    skipped_count = 0
    for audio_file in user_audio_files:
        _, video_path_abs, _ = _get_video_paths(audio_file)
        if video_path_abs and os.path.exists(video_path_abs):
            skipped_count += 1
            continue
        audio_pks_to_generate.append(audio_file.pk)

    triggered_count = len(audio_pks_to_generate)
    logger.info(f"generate_all_videos: {triggered_count} to generate, {skipped_count} skipped for user {request.user.username}")

    # Run in background thread so the HTTP response returns immediately
    def _generate_all(pks):
        for pk in pks:
            try:
                create_single_video_task.apply(args=[pk])
            except Exception as e:
                logger.error(f"Background video gen failed for AudioFile PK {pk}: {e}")

    if audio_pks_to_generate:
        thread = threading.Thread(target=_generate_all, args=(audio_pks_to_generate,), daemon=True)
        thread.start()

    message = f"Generating {triggered_count} videos in the background. Skipped {skipped_count} (already exist)."
    messages.info(request, message + " Refresh the dashboard to see progress.")
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
        try:
            run_full_pipeline_task.apply(args=[doc_pk, user_pk, run_pk])
        except Exception as e:
            logger.error(f"Background pipeline failed for doc {doc_pk}: {e}")

    thread = threading.Thread(
        target=_run_pipeline,
        args=(document_pk, request.user.pk, pipeline_run.pk),
        daemon=True,
    )
    thread.start()

    messages.success(request, f"Full pipeline started for '{document.uploaded_file.name}'. Refresh to track progress.")
    return redirect('dashboard')


@login_required
def pipeline_status_api(request, run_id):
    """API endpoint for pipeline run status."""
    run = get_object_or_404(PipelineRun, pk=run_id, user=request.user)
    return JsonResponse({
        'id': run.pk,
        'status': run.status,
        'progress_pct': run.progress_pct,
        'current_step': run.current_step,
        'error_message': run.error_message,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
    })


# ==========================================================================
# QUIZ VIEWS
# ==========================================================================

@login_required
def quiz_list_view(request, document_pk):
    """List all quizzes for a document."""
    document = get_object_or_404(Document, pk=document_pk, user=request.user)
    quizzes = Quiz.objects.filter(document=document).order_by('-created_at')
    return render(request, 'boaapp/quiz_list.html', {
        'document': document,
        'quizzes': quizzes,
        'page_id': 'quiz',
    })


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
            results.append({
                'question': q.question_text,
                'user_answer': user_answer,
                'correct_answer': q.correct_answer,
                'is_correct': is_correct,
                'feedback': feedback,
                'explanation': q.explanation,
            })

        attempt = QuizAttempt.objects.create(
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

        return render(request, 'boaapp/quiz_results.html', {
            'quiz': quiz,
            'results': results,
            'score': score,
            'total': total,
            'percentage': round(score / total * 100) if total else 0,
            'page_id': 'quiz',
        })

    return render(request, 'boaapp/quiz_take.html', {
        'quiz': quiz,
        'questions': questions,
        'page_id': 'quiz',
    })


@login_required
def generate_quiz_view(request, document_pk):
    """Generate quizzes for a document's audio sections."""
    from .tasks import generate_quiz_from_document_task

    document = get_object_or_404(Document, pk=document_pk, user=request.user)

    generate_quiz_from_document_task.delay(document.pk)

    messages.success(request, "Quiz generation started from notebook content.")
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
        conversation = ChatConversation.objects.filter(
            user=request.user, document=document
        ).order_by('-updated_at').first()

        if not conversation:
            stem = os.path.splitext(os.path.basename(str(document.uploaded_file)))[0]
            conversation = ChatConversation.objects.create(
                user=request.user,
                document=document,
                title=f"Chat: {stem}",
            )

    chat_messages = []
    if conversation:
        chat_messages = list(conversation.messages.values('role', 'content', 'created_at'))

    return render(request, 'boaapp/chat.html', {
        'document': document,
        'conversation': conversation,
        'messages_list': chat_messages,
        'page_id': 'chat',
    })


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
    ChatMessage.objects.create(
        conversation=conversation, role='assistant', content=response_text, sources=sources
    )

    # Track event
    LearningEvent.objects.create(
        user=request.user,
        event_type='chat_message',
        metadata={'conversation_id': conversation_id},
    )

    return JsonResponse({
        'response': response_text,
        'sources': sources,
    })


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
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncDate

    user = request.user

    # Activity over time (last 30 days)
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)

    daily_activity = (
        LearningEvent.objects
        .filter(user=user, created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Event type breakdown
    event_breakdown = (
        LearningEvent.objects
        .filter(user=user)
        .values('event_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Quiz performance
    quiz_stats = QuizAttempt.objects.filter(user=user).aggregate(
        avg_score=Avg('score'),
        total_attempts=Count('id'),
    )

    # Total content consumed
    total_audio = AudioFile.objects.filter(user=user).count()
    total_videos = sum(
        1 for a in AudioFile.objects.filter(user=user)
        if _get_video_paths(a)[1] and os.path.exists(_get_video_paths(a)[1])
    )

    context = {
        'daily_activity': list(daily_activity),
        'event_breakdown': list(event_breakdown),
        'quiz_stats': quiz_stats,
        'total_audio': total_audio,
        'total_videos': total_videos,
        'total_events': LearningEvent.objects.filter(user=user).count(),
        'page_id': 'analytics',
    }

    return render(request, 'boaapp/analytics.html', context)


# ==========================================================================
# SMART CHAPTERED VIDEO PLAYER
# ==========================================================================

@login_required
def chaptered_player_view(request, document_pk):
    """Smart chaptered video player for all videos of a document."""
    document = get_object_or_404(Document, pk=document_pk, user=request.user)
    audio_files = AudioFile.objects.filter(document=document).order_by('metadata__section_index', 'pk')

    chapters = []
    for audio in audio_files:
        _, video_path_abs, sync_file = _get_video_paths(audio)
        if video_path_abs and os.path.exists(video_path_abs):
            video_url = settings.MEDIA_URL + os.path.relpath(video_path_abs, settings.MEDIA_ROOT).replace('\\', '/')
            chapters.append({
                'title': audio.title,
                'video_url': video_url,
                'audio_pk': audio.pk,
                'section_index': (audio.metadata or {}).get('section_index', 0),
            })

    # Track event
    LearningEvent.objects.create(
        user=request.user,
        event_type='video_watch',
        metadata={'document_id': document_pk},
    )

    return render(request, 'boaapp/chaptered_player.html', {
        'document': document,
        'chapters': chapters,
        'page_id': 'player',
    })


# ==========================================================================
# GITHUB WEBHOOK
# ==========================================================================

from django.views.decorators.csrf import csrf_exempt
import hashlib
import hmac


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

        expected = 'sha256=' + hmac.new(
            secret.encode(), request.body, hashlib.sha256
        ).hexdigest()
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
                logger.info(f"GitHub webhook: {len(ipynb_files)} notebooks changed in {repo_name}/{branch}")
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
            messages.success(request, f"Webhook configured for {repo}/{branch}")

        return redirect('webhook_config')

    return render(request, 'boaapp/webhook_config.html', {
        'configs': configs,
        'page_id': 'webhooks',
    })


# ==========================================================================
# TRANSLATION VIEWS
# ==========================================================================

SUPPORTED_LANGUAGES = [
    ('es', 'Spanish'), ('fr', 'French'), ('de', 'German'),
    ('ja', 'Japanese'), ('ko', 'Korean'), ('zh', 'Chinese'),
    ('pt', 'Portuguese'), ('it', 'Italian'), ('ru', 'Russian'),
    ('ar', 'Arabic'), ('hi', 'Hindi'),
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
            messages.success(request, f"Translation to {lang_name} started.")
        else:
            messages.error(request, "Invalid language selected.")

        return redirect('translate_document', document_pk=document_pk)

    existing = TranslatedContent.objects.filter(document=document)

    return render(request, 'boaapp/translate.html', {
        'document': document,
        'languages': SUPPORTED_LANGUAGES,
        'existing_translations': existing,
        'page_id': 'translate',
    })


# ==========================================================================
# VOICE CLONING VIEW
# ==========================================================================

@login_required
def voice_settings_view(request):
    """Voice settings page for TTS provider selection."""
    elevenlabs_available = bool(getattr(settings, 'ELEVENLABS_API_KEY', ''))
    return render(request, 'boaapp/voice_settings.html', {
        'elevenlabs_available': elevenlabs_available,
        'page_id': 'voice_settings',
    })


# ==========================================================================
# ADAPTIVE LEARNING
# ==========================================================================

@login_required
def learning_path_view(request):
    """AI-recommended learning path based on user activity."""
    user = request.user

    # Get user's completed content
    completed_sections = CourseSection.objects.filter(
        completed_by_enrollments__user=user
    ).values_list('id', flat=True)

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