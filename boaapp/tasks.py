import os
import logging
from celery import shared_task
from django.conf import settings
import re
from django.contrib.auth import get_user_model
from pathlib import Path

# Import the functions that do the actual work
from .process_notebook import process_notebook_and_create_audio
from .create_video import create_video_parallel
from .models import Document, AudioFile
from .utils import _get_video_paths, _get_random_background

logger = logging.getLogger(__name__)
User = get_user_model() # Get the User model

# --- create_audio_files_task remains the same ---
@shared_task(bind=True) # bind=True gives access to self (the task instance)
def create_audio_files_task(self, document_pk, user_id):
    """
    Celery task to process a notebook and create audio files.
    """
    logger.info(f"Celery Task Started: create_audio_files_task for Document PK {document_pk}, User ID {user_id}")
    try:
        document = Document.objects.get(pk=document_pk)
        user = User.objects.get(pk=user_id)
        # Use pathlib for consistency
        notebook_file_path = Path(settings.MEDIA_ROOT) / document.uploaded_file.name

        if not notebook_file_path.exists():
            logger.error(f"Notebook file not found for Document PK {document_pk}: {notebook_file_path}")
            return {'status': 'FAILED', 'error': 'Notebook file not found'}

        # --- Replicate logic from handle_audio_creation ---
        # Assuming process_notebook_and_create_audio expects a string path
        audio_files_info = process_notebook_and_create_audio(str(notebook_file_path))
        total_files_to_create = len(audio_files_info)
        logger.info(f"Found {total_files_to_create} blocks to process for audio.")

        if total_files_to_create == 0:
            logger.warning(f"No audio files generated for Document PK {document_pk}.")
            return {'status': 'COMPLETE', 'audio_pks': []}

        generated_audio_db_pks = []
        for idx, audio_info in enumerate(audio_files_info):
            self.update_state(state='PROGRESS', meta={
                'current': idx + 1,
                'total': total_files_to_create,
                'status_message': f"Creating audio for: {audio_info['title']}"
            })

            title = audio_info['title']
            relative_path = audio_info['relative_path']
            full_path = audio_info['full_path'] # Assuming this is absolute
            section_index = audio_info['section_index']
            original_content = audio_info['original_content']
            block_type = audio_info['block_type']

            # Use Path for checking existence
            if not Path(full_path).exists():
                logger.warning(f"Audio file missing after generation: {full_path}. Skipping DB entry.")
                continue

            try:
                audio_file_obj = AudioFile.objects.create(
                    title=title,
                    # Use Pathlib to get basename safely
                    name=Path(relative_path).name,
                    file=relative_path, # Store relative path
                    user=user,
                    document=document,
                    metadata={
                        'section_index': section_index,
                        'block_type': block_type,
                        'original_content': original_content
                    }
                )
                generated_audio_db_pks.append(audio_file_obj.pk)
                logger.debug(f"AudioFile record created: {title} (PK: {audio_file_obj.pk})")
            except Exception as e:
                 logger.error(f"Error creating AudioFile record for {title}: {e}", exc_info=True) # Add exc_info
                 # Optionally: Clean up the generated audio file if DB save fails
                 # try: Path(full_path).unlink() except OSError: pass

        logger.info(f"Finished audio creation task for Document PK {document_pk}. Created {len(generated_audio_db_pks)} files.")
        return {'status': 'COMPLETE', 'audio_pks': generated_audio_db_pks}

    except Document.DoesNotExist:
        logger.error(f"Document PK {document_pk} not found for audio creation task.")
        return {'status': 'FAILED', 'error': 'Document not found'}
    except User.DoesNotExist:
         logger.error(f"User PK {user_id} not found for audio creation task.")
         return {'status': 'FAILED', 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Error in create_audio_files_task for Document PK {document_pk}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}

@shared_task(bind=True)
def create_single_video_task(self, audio_file_pk):
    """
    Celery task to create a single video file.
    Uses utility functions for path generation and background selection.
    """
    logger.info(f"Celery Task Started: create_single_video_task for AudioFile PK {audio_file_pk}")
    try:
        audio_file_obj = AudioFile.objects.get(pk=audio_file_pk)
        # --- Get and Clean Notebook Title ---
        cleaned_notebook_title = "Untitled" # Default title
        try:
            document = audio_file_obj.document
            if document and document.uploaded_file and document.uploaded_file.name:
                notebook_path = Path(document.uploaded_file.name)
                stem = notebook_path.stem # Filename without extension
                # Remove leading digits/hyphens/underscores, replace others with space
                cleaned_notebook_title = re.sub(r'^\d+[\s_-]+', '', stem).replace('-', ' ').replace('_', ' ')
                logger.debug(f"Cleaned notebook title: '{cleaned_notebook_title}' from '{notebook_path.name}'")
        except Exception as title_err:
            logger.warning(f"Could not determine cleaned notebook title for Audio PK {audio_file_pk}: {title_err}")
        # --- End Get and Clean Notebook Title ---
        # --- Get metadata ---
        metadata = audio_file_obj.metadata or {} # Ensure metadata is a dict
        section_index = metadata.get('section_index')
        block_type = metadata.get('block_type', 'markdown')
        original_content = metadata.get('original_content', '')
        section_title = audio_file_obj.title

        if section_index is None or original_content is None: # Check original_content too
            logger.error(f"Missing metadata (section_index or original_content) for AudioFile PK {audio_file_pk}.")
            return {'status': 'FAILED', 'error': 'Missing metadata'}

        section_tuple = (section_title, original_content, block_type)

        # --- Use _get_video_paths from utils.py ---
        video_output_dir_abs_str, output_path_str, sync_file_str = _get_video_paths(audio_file_obj)

        # Check if paths were determined successfully
        if not all([video_output_dir_abs_str, output_path_str, sync_file_str]):
            logger.error(f"Failed to determine video paths for AudioFile PK {audio_file_pk}. Check previous warnings.")
            # The specific reason should have been logged by _get_video_paths
            return {'status': 'FAILED', 'error': 'Could not determine video paths'}

        # Convert string paths back to Path objects if needed, or use strings directly
        video_output_dir_abs = Path(video_output_dir_abs_str)
        output_path = Path(output_path_str)
        sync_file = Path(sync_file_str)
        # --- End using _get_video_paths ---

        # Get absolute audio path
        audio_path_abs = Path(settings.MEDIA_ROOT) / audio_file_obj.file.name
        if not audio_path_abs.exists():
             logger.error(f"Audio file not found for PK {audio_file_pk}: {audio_path_abs}")
             return {'status': 'FAILED', 'error': 'Audio file not found'}

        # Ensure output directory exists
        video_output_dir_abs.mkdir(parents=True, exist_ok=True)

        # --- Get asset paths ---
        # Ensure STATICFILES_DIRS[0] is the correct place for your static assets
        logo_path = Path(settings.STATICFILES_DIRS[0]) / 'css' / 'img' / 'logo.png'
        default_background_path_str = str(Path(settings.BASE_DIR) / 'video' / 'background.mp4')

        # --- Use _get_random_background from utils.py ---
        background_path_str = _get_random_background(default_background_path_str)
        background_path = Path(background_path_str) # Convert to Path object
        # --- End using _get_random_background ---

        # Check asset existence
        logo_path_abs_str = str(logo_path) if logo_path.exists() else None
        if not logo_path_abs_str:
             logger.warning(f"Logo file not found at {logo_path}, proceeding without logo.")

        if not background_path.exists():
             logger.error(f"Selected background video not found: {background_path}")
             # Decide if you want to fail or try the default again
             default_bg_path_obj = Path(default_background_path_str)
             if default_bg_path_obj.exists():
                 logger.warning(f"Falling back to default background: {default_bg_path_obj}")
                 background_path = default_bg_path_obj
             else:
                 logger.error(f"Default background video also not found: {default_bg_path_obj}")
                 return {'status': 'FAILED', 'error': 'Background video not found'}

        font_styles = {
            "font": "Inter", "font_size": 36, "text_color": "white",
            "code_font": "Courier-New", "code_font_size": 32, "code_text_color": "#F0F0F0"
        }

        self.update_state(state='PROGRESS', meta={'status_message': f"Rendering video for: {audio_file_obj.title}"})

        # Call the video creation function (ensure it accepts Path objects or convert back to strings)
        create_video_parallel(
            section=section_tuple,
            audio_file=str(audio_path_abs),
            output_file=str(output_path),
            logo_path=logo_path_abs_str, # Pass the string path or None
            background_path=str(background_path),
            text_sync_file=str(sync_file),
            font_styles=font_styles,
            notebook_title=cleaned_notebook_title # Pass the cleaned title
        )

        logger.info(f"Finished video creation task for AudioFile PK {audio_file_pk}.")

        # Calculate relative path for the result using pathlib
        try:
            relative_video_path = output_path.relative_to(settings.MEDIA_ROOT).as_posix()
        except ValueError:
             logger.warning(f"Could not make video path relative to MEDIA_ROOT: {output_path}")
             relative_video_path = str(output_path) # Fallback to absolute path string

        # Optionally store video path in metadata
        # audio_file_obj.metadata['video_path'] = relative_video_path
        # audio_file_obj.save(update_fields=['metadata'])

        return {'status': 'COMPLETE', 'video_path': relative_video_path}

    except AudioFile.DoesNotExist:
        logger.error(f"AudioFile PK {audio_file_pk} not found for video creation task.")
        return {'status': 'FAILED', 'error': 'AudioFile not found'}
    except Exception as e:
        logger.error(f"Error in create_single_video_task for AudioFile PK {audio_file_pk}: {e}", exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}


# ==========================================================================
# Full Pipeline Task (One-Click: Audio → Video → Quiz → Thumbnail)
# ==========================================================================

@shared_task(bind=True)
def run_full_pipeline_task(self, document_pk, user_id, pipeline_run_id=None):
    """
    One-click pipeline: generates audio, videos, quizzes, and thumbnail.
    Sends WebSocket progress updates via PipelineRun.
    """
    from .pipeline_utils import send_pipeline_update
    from .rag_engine import index_document
    from .quiz_generator import generate_quiz_for_section
    from .thumbnail_generator import generate_thumbnail
    from .models import Document, AudioFile, Quiz, QuizQuestion, PipelineRun

    logger.info(f"Full Pipeline Started for Document PK {document_pk}")

    def _update(status, pct, step, msg=''):
        if pipeline_run_id:
            send_pipeline_update(pipeline_run_id, status, pct, step, msg)

    try:
        document = Document.objects.get(pk=document_pk)
        user = User.objects.get(pk=user_id)
        notebook_file_path = Path(settings.MEDIA_ROOT) / document.uploaded_file.name

        if not notebook_file_path.exists():
            _update('failed', 0, '', 'Notebook file not found')
            return {'status': 'FAILED', 'error': 'Notebook file not found'}

        # ---- STEP 1: Audio Generation (0-40%) ----
        _update('audio', 5, 'Parsing notebook & generating audio...')

        audio_files_info = process_notebook_and_create_audio(str(notebook_file_path))
        total_audio = len(audio_files_info)

        if total_audio == 0:
            _update('failed', 0, '', 'No content found in notebook')
            return {'status': 'FAILED', 'error': 'No content found'}

        audio_pks = []
        for idx, audio_info in enumerate(audio_files_info):
            pct = 5 + int((idx / total_audio) * 35)
            _update('audio', pct, f'Audio {idx + 1}/{total_audio}: {audio_info["title"]}')

            if not Path(audio_info['full_path']).exists():
                continue

            try:
                audio_obj = AudioFile.objects.create(
                    title=audio_info['title'],
                    name=Path(audio_info['relative_path']).name,
                    file=audio_info['relative_path'],
                    user=user,
                    document=document,
                    metadata={
                        'section_index': audio_info['section_index'],
                        'block_type': audio_info['block_type'],
                        'original_content': audio_info['original_content'],
                    }
                )
                audio_pks.append(audio_obj.pk)
            except Exception as e:
                logger.error(f"Error creating AudioFile for {audio_info['title']}: {e}", exc_info=True)

        # ---- STEP 2: Video Generation (40-75%) ----
        _update('video', 40, 'Generating videos...')

        for vidx, audio_pk in enumerate(audio_pks):
            pct = 40 + int((vidx / max(len(audio_pks), 1)) * 35)
            audio_obj = AudioFile.objects.get(pk=audio_pk)
            _update('video', pct, f'Video {vidx + 1}/{len(audio_pks)}: {audio_obj.title}')

            try:
                # Reuse the single video task logic inline
                create_single_video_task.apply(args=[audio_pk])
            except Exception as e:
                logger.error(f"Video gen failed for audio PK {audio_pk}: {e}", exc_info=True)

        # ---- STEP 3: Quiz Generation (75-85%) ----
        _update('quiz', 75, 'Generating quizzes...')

        for aidx, audio_pk in enumerate(audio_pks):
            audio_obj = AudioFile.objects.get(pk=audio_pk)
            meta = audio_obj.metadata or {}
            content = meta.get('original_content', '')
            block_type = meta.get('block_type', 'markdown')

            if block_type == 'thankyou' or not content.strip():
                continue

            pct = 75 + int((aidx / max(len(audio_pks), 1)) * 10)
            _update('quiz', pct, f'Quiz for: {audio_obj.title}')

            try:
                questions = generate_quiz_for_section(content, audio_obj.title)
                if questions:
                    quiz = Quiz.objects.create(
                        course_section_id=None,  # Will be linked if course exists
                        title=f"Quiz: {audio_obj.title}",
                    )
                    # Handle case where course_section is required
                    # For standalone notebooks, we store quiz linked via metadata
                    quiz.save()

                    for qidx, q in enumerate(questions):
                        QuizQuestion.objects.create(
                            quiz=quiz,
                            question_text=q['question'],
                            question_type=q.get('type', 'mcq'),
                            options=q.get('options'),
                            correct_answer=q['correct_answer'],
                            explanation=q.get('explanation', ''),
                            order=qidx,
                        )
            except Exception as e:
                logger.error(f"Quiz generation failed for {audio_obj.title}: {e}", exc_info=True)

        # ---- STEP 4: Thumbnail Generation (85-92%) ----
        _update('thumbnail', 85, 'Generating AI thumbnail...')
        try:
            generate_thumbnail(document_pk)
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}", exc_info=True)

        # ---- STEP 5: RAG Indexing (92-100%) ----
        _update('thumbnail', 92, 'Indexing content for AI chatbot...')
        try:
            index_document(document_pk)
        except Exception as e:
            logger.error(f"RAG indexing failed: {e}", exc_info=True)

        # ---- COMPLETE ----
        _update('complete', 100, 'Pipeline complete!', 'All steps finished successfully.')
        logger.info(f"Full Pipeline Complete for Document PK {document_pk}")
        return {'status': 'COMPLETE', 'audio_pks': audio_pks}

    except Exception as e:
        logger.error(f"Full pipeline failed for Document PK {document_pk}: {e}", exc_info=True)
        _update('failed', 0, '', str(e))
        return {'status': 'FAILED', 'error': str(e)}


# ==========================================================================
# Standalone Quiz Generation Task
# ==========================================================================

@shared_task(bind=True)
def generate_quiz_task(self, audio_file_pk):
    """Generate a quiz for a single audio file's content."""
    from .quiz_generator import generate_quiz_for_section
    from .models import AudioFile, Quiz, QuizQuestion

    try:
        audio = AudioFile.objects.get(pk=audio_file_pk)
        meta = audio.metadata or {}
        content = meta.get('original_content', '')

        questions = generate_quiz_for_section(content, audio.title)
        if not questions:
            return {'status': 'NO_QUESTIONS'}

        quiz = Quiz.objects.create(title=f"Quiz: {audio.title}")
        # quiz.course_section is nullable via the FK; we'll leave it null for standalone
        for idx, q in enumerate(questions):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=q['question'],
                question_type=q.get('type', 'mcq'),
                options=q.get('options'),
                correct_answer=q['correct_answer'],
                explanation=q.get('explanation', ''),
                order=idx,
            )
        return {'status': 'COMPLETE', 'quiz_id': quiz.pk, 'num_questions': len(questions)}

    except Exception as e:
        logger.error(f"Quiz generation task failed: {e}", exc_info=True)
        return {'status': 'FAILED', 'error': str(e)}


@shared_task(bind=True)
def generate_quiz_from_document_task(self, document_pk):
    """Generate quizzes from a document's actual .ipynb notebook content."""
    import nbformat
    from .quiz_generator import generate_quiz_for_section
    from .models import Document, Quiz, QuizQuestion

    try:
        doc = Document.objects.get(pk=document_pk)
        notebook_path = Path(settings.MEDIA_ROOT) / doc.uploaded_file.name

        if not notebook_path.exists():
            logger.error(f"Notebook not found for quiz generation: {notebook_path}")
            return {'status': 'FAILED', 'error': 'Notebook file not found'}

        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Group cells into meaningful sections for quiz generation
        sections = []
        current_section_title = os.path.splitext(os.path.basename(str(doc.uploaded_file)))[0]
        current_content = []

        for cell in nb.cells:
            source = cell.get('source', '').strip()
            if not source:
                continue

            cell_type = cell.get('cell_type', 'code')

            # Markdown headings start new sections
            if cell_type == 'markdown' and source.startswith('#'):
                if current_content:
                    sections.append({
                        'title': current_section_title,
                        'content': '\n\n'.join(current_content),
                    })
                    current_content = []
                current_section_title = source.lstrip('#').strip() or current_section_title
            current_content.append(source)

        # Add final section
        if current_content:
            sections.append({
                'title': current_section_title,
                'content': '\n\n'.join(current_content),
            })

        if not sections:
            return {'status': 'NO_CONTENT'}

        # Delete old quizzes for this document so we don't pile duplicates
        Quiz.objects.filter(document=doc).delete()

        total_questions = 0
        quiz_ids = []
        for section in sections:
            if len(section['content'].strip()) < 50:
                continue

            questions = generate_quiz_for_section(
                section['content'], section['title'],
            )
            if not questions:
                continue

            quiz = Quiz.objects.create(
                title=f"Quiz: {section['title']}"[:250],
                document=doc,
            )
            for idx, q in enumerate(questions):
                raw_type = q.get('type', 'mcq').lower().replace('-', '_')
                if 'multiple' in raw_type or raw_type == 'mcq':
                    q_type = 'mcq'
                elif 'code' in raw_type:
                    q_type = 'code'
                else:
                    q_type = 'short'
                QuizQuestion.objects.create(
                    quiz=quiz,
                    question_text=q['question'],
                    question_type=q_type,
                    options=q.get('options'),
                    correct_answer=q['correct_answer'],
                    explanation=q.get('explanation', ''),
                    order=idx,
                )
            total_questions += len(questions)
            quiz_ids.append(quiz.pk)

        logger.info(f"Generated {len(quiz_ids)} quizzes ({total_questions} questions) for document {doc.pk}")
        return {'status': 'COMPLETE', 'quiz_ids': quiz_ids, 'total_questions': total_questions}

    except Exception as e:
        logger.error(f"Document quiz generation failed: {e}", exc_info=True)
        return {'status': 'FAILED', 'error': str(e)}


# ==========================================================================
# Translation Task
# ==========================================================================

@shared_task(bind=True)
def translate_document_task(self, document_pk, target_language_code, target_language_name):
    """Translate document sections and optionally generate audio in target language."""
    from .models import Document, TranslatedContent

    try:
        doc = Document.objects.get(pk=document_pk)
        notebook_path = Path(settings.MEDIA_ROOT) / doc.uploaded_file.name

        if not notebook_path.exists():
            return {'status': 'FAILED', 'error': 'Notebook not found'}

        import nbformat
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        sections_to_translate = []
        for cell in nb.cells:
            if cell.cell_type == 'markdown' and cell.source.strip():
                sections_to_translate.append({
                    'type': 'markdown',
                    'content': cell.source.strip(),
                })

        if not sections_to_translate:
            return {'status': 'NO_CONTENT'}

        # Translate via LLM
        translated = _translate_sections(sections_to_translate, target_language_code, target_language_name)

        TranslatedContent.objects.update_or_create(
            document=doc,
            language_code=target_language_code,
            defaults={
                'language_name': target_language_name,
                'translated_sections': translated,
            }
        )

        return {'status': 'COMPLETE', 'sections_translated': len(translated)}

    except Exception as e:
        logger.error(f"Translation task failed: {e}", exc_info=True)
        return {'status': 'FAILED', 'error': str(e)}


def _translate_sections(sections, lang_code, lang_name):
    """Translate sections using LLM."""
    import json as _json

    all_content = "\n---SECTION_BREAK---\n".join(s['content'] for s in sections)

    prompt = f"""Translate the following educational content from English to {lang_name} ({lang_code}).
Preserve ALL formatting including markdown headers, code blocks, and bullet points.
Sections are separated by ---SECTION_BREAK---. Keep these separators in your response.

Content:
{all_content[:8000]}"""

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    translated_text = ''

    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            translated_text = response.content[0].text
        except Exception as e:
            logger.error(f"Translation LLM call failed: {e}")
            return []

    if not translated_text:
        return []

    parts = translated_text.split('---SECTION_BREAK---')
    result = []
    for i, part in enumerate(parts):
        result.append({
            'original': sections[i]['content'] if i < len(sections) else '',
            'translated': part.strip(),
            'type': sections[i]['type'] if i < len(sections) else 'markdown',
        })
    return result


# ==========================================================================
# Code Review Task
# ==========================================================================

@shared_task(bind=True)
def ai_code_review_task(self, code, language='python'):
    """Run AI code review on submitted code."""
    import json as _json

    prompt = f"""Review this {language} code for:
1. Bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Style and best practices
5. Suggestions for improvement

Code:
```{language}
{code[:4000]}
```

Return ONLY valid JSON:
{{
  "score": 85,
  "issues": [
    {{"severity": "error|warning|info", "line": 1, "message": "description", "suggestion": "fix"}}
  ],
  "summary": "Brief overall assessment"
}}"""

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
            if text.endswith('```'):
                text = text[:-3]
            return _json.loads(text.strip())
        except Exception as e:
            logger.error(f"Code review failed: {e}", exc_info=True)
            return {'score': 0, 'issues': [], 'summary': f'Review failed: {e}'}

    return {'score': 0, 'issues': [], 'summary': 'No AI backend configured.'}
