import logging
import nbformat
from nbconvert import HTMLExporter # Add this import
import os

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

from .forms import DocumentForm, UserRegisterForm, CustomUserCreationForm
from .models import Document, AudioFile, VideoFile, Course, Enrollment, CourseSection, PortfolioItem, DevopsItem, ResumeDocument
from .tasks import create_audio_files_task, create_single_video_task
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

# boaapp/views.py (Add this function)
def witheritelaw_view(request):
    """Render the Witheritelaw Automation Engineer profile page."""
    context = {
        'page_title': 'Automation Engineer Profile: Witheritelaw',
        'job_title': 'Automation Engineer',
        'company_name': 'Witheritelaw',
        # You can add more context variables here if needed,
        # but the main content will be in the template.
    }
    return render(request, 'boaapp/witheritelaw.html', context)


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
            return redirect('course_list') # Redirect to the course list page
    else:
        # GET request
        form = CustomUserCreationForm()
        # --- Debugging ---
        print("--- Register View (GET) ---")
        print(f"Form type: {type(form)}")
        print(f"Form fields: {form.fields.keys()}") # See which fields the form object thinks it has
        print(f"Form is bound: {form.is_bound}")
        print("--------------------------")
        logger.info(f"Rendering registration form. Fields: {list(form.fields.keys())}") # Also log it
        # --- End Debugging ---
    return render(request, 'boaapp/register.html', {'form': form})

def login_view(request):
    """Handle user login using Django's AuthenticationForm."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) # Pass request to the form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}.")
                # Redirect to the intended page or dashboard
                next_url = request.POST.get('next') # Handle redirection if 'next' parameter exists
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard') # Default redirect
            else:
                # This case should ideally not happen if form.is_valid() and authenticate works
                # but good to handle defensively.
                messages.error(request, "Authentication failed unexpectedly.")
        else:
            # Form is invalid (e.g., wrong password, inactive user)
            # The form itself will contain the error messages.
            messages.error(request, "Invalid username or password.")
    else: # GET request
        form = AuthenticationForm()

    # Pass the form to the template for both GET and failed POST requests
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

            # --- Trigger Audio Creation Task (Explicit Connection Test) ---
            logger.info(f"Triggering Celery task create_audio_files_task for document PK {document.pk} using explicit connection")
            try:
                # Get broker URL from settings (already verified it's correct)
                broker_url = settings.CELERY_BROKER_URL
                logger.debug(f"Using broker URL for explicit connection: {broker_url}")

                # Create a connection explicitly using the broker URL
                # The 'with' statement ensures the connection is closed
                with Connection(broker_url) as conn:
                    logger.debug(f"Explicit Kombu connection established: {conn}")
                    # Send the task and get the AsyncResult
                    async_result = create_audio_files_task.apply_async(
                        args=[document.pk, request.user.pk],
                        connection=conn # Pass the connection object
                    )
                task_id = async_result.id # Get the task ID
                logger.info(f"Task sent successfully using explicit connection. Task ID: {task_id}")
                redirect_url = f"{redirect('dashboard').url}?audio_task_id={task_id}" # Append task ID to dashboard URL

            except ConnectionRefusedError as e_conn_refused:
                logger.error(f"Connection refused even with explicit Kombu connection: {e_conn_refused}", exc_info=True)
                messages.error(request, "Failed to connect to the background task queue (Connection Refused). Please ensure Redis is running and accessible.")
                # Optionally delete the document record if queuing fails?
                # document.delete()
                return redirect('dashboard') # Redirect on failure
            except Exception as e_send: # Catch other potential errors during task sending
                 logger.error(f"Error sending task with explicit connection: {e_send}", exc_info=True)
                 messages.error(request, f"Failed to queue background task: {e_send}")
                 # Optionally delete the document record if queuing fails?
                 # document.delete()
                 return redirect('dashboard') # Redirect on failure
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

def companyandme(request):
    """Render 'Company and Me' page."""
    return render(request, 'boaapp/companyandme.html')

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

def technical_showcase_view(request):
    # You can pass context here if this page needs more dynamic data later
    context = {} 
    return render(request, 'boaapp/technical_showcase.html', context)

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
            video_url = os.path.join(settings.MEDIA_URL, os.path.relpath(video_path_abs, settings.MEDIA_ROOT)) if video_exists else None

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
    """Triggers the background task to generate a single video."""
    audio_file = get_object_or_404(AudioFile, pk=audio_file_pk, user=request.user)
    logger.info(f"User {request.user.username} initiated video generation for AudioFile PK {audio_file_pk}")

    # --- Trigger Video Creation Task (Explicit Connection Test) ---
    logger.info(f"Triggering Celery task create_single_video_task for AudioFile PK {audio_file_pk} using explicit connection")
    try:
        # Get broker URL from settings
        broker_url = settings.CELERY_BROKER_URL
        logger.debug(f"Using broker URL for explicit connection: {broker_url}")

        # Create a connection explicitly using the broker URL
        with Connection(broker_url) as conn:
            logger.debug(f"Explicit Kombu connection established: {conn}")
            # Send the task using apply_async and the explicit connection
            create_single_video_task.apply_async(
                args=[audio_file_pk],
                connection=conn # Pass the connection object
            )
        logger.info("Video generation task sent successfully using explicit connection.")
        messages.success(request, f"Video generation started for '{audio_file.title}'. It will appear on the dashboard when ready.")

    except ConnectionRefusedError as e_conn_refused:
        logger.error(f"Connection refused when sending video task with explicit Kombu connection: {e_conn_refused}", exc_info=True)
        messages.error(request, "Failed to connect to the background task queue (Connection Refused). Please ensure Redis is running and accessible.")
    except Exception as e_send:
         logger.error(f"Error sending video task with explicit connection: {e_send}", exc_info=True)
         messages.error(request, f"Failed to queue video generation task: {e_send}")
    # --- End Explicit Connection Test ---

    return redirect('dashboard') # Redirect back to dashboard regardless of success/failure queuing

@login_required
def generate_all_videos(request):
    """Triggers video generation tasks for all audio files for the user."""
    user_audio_files = AudioFile.objects.filter(user=request.user)
    triggered_count = 0
    skipped_count = 0

    logger.info(f"Starting 'generate_all_videos' task trigger for user {request.user.username}")

    for audio_file in user_audio_files:
        # Optional: Check if video already exists before triggering
        _, video_path_abs, _ = _get_video_paths(audio_file)
        if video_path_abs and os.path.exists(video_path_abs):
            logger.debug(f"Skipping video task for AudioFile PK {audio_file.pk}, video already exists.")
            skipped_count += 1
            continue

        # Trigger task for each audio file
        create_single_video_task.delay(audio_file.pk)
        triggered_count += 1

    message = f"Triggered {triggered_count} video generation tasks. Skipped {skipped_count} (already exist)."
    messages.info(request, message + " Please refresh the dashboard shortly to see progress.")
    return redirect('dashboard')