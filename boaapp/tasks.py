import logging
import os
import re
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import AudioFile, Document
from .process_notebook import process_notebook_and_create_audio

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True)
def create_audio_files_task(self, document_pk, user_id):
    """
    Celery task to process a notebook and create audio files.
    Reads notebook JSON from DB, generates audio bytes, stores in AudioFile.audio_data.
    """
    logger.info(f'Celery Task Started: create_audio_files_task for Document PK {document_pk}, User ID {user_id}')
    try:
        document = Document.objects.get(pk=document_pk)
        user = User.objects.get(pk=user_id)

        notebook_json = document.notebook_json
        if not notebook_json:
            logger.error(f'No notebook JSON stored for Document PK {document_pk}')
            return {'status': 'FAILED', 'error': 'No notebook content stored'}

        notebook_title = document.original_filename
        if notebook_title:
            notebook_title = os.path.splitext(notebook_title)[0]
        else:
            notebook_title = 'Notebook'

        audio_files_info = process_notebook_and_create_audio(
            notebook_json_str=notebook_json,
            notebook_title=notebook_title,
        )
        total_files_to_create = len(audio_files_info)
        logger.info(f'Found {total_files_to_create} blocks to process for audio.')

        if total_files_to_create == 0:
            logger.warning(f'No audio files generated for Document PK {document_pk}.')
            return {'status': 'COMPLETE', 'audio_pks': []}

        generated_audio_db_pks = []
        for idx, audio_info in enumerate(audio_files_info):
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx + 1,
                    'total': total_files_to_create,
                    'status_message': f'Creating audio for: {audio_info["title"]}',
                },
            )

            try:
                audio_file_obj = AudioFile.objects.create(
                    title=audio_info['title'],
                    name=audio_info['name'],
                    audio_data=audio_info['audio_data'],
                    user=user,
                    document=document,
                    metadata={
                        'section_index': audio_info['section_index'],
                        'block_type': audio_info['block_type'],
                        'original_content': audio_info['original_content'],
                    },
                )
                generated_audio_db_pks.append(audio_file_obj.pk)
                logger.debug(f'AudioFile record created: {audio_info["title"]} (PK: {audio_file_obj.pk})')
            except Exception as e:
                logger.error(f'Error creating AudioFile record for {audio_info["title"]}: {e}', exc_info=True)

        logger.info(
            f'Finished audio creation task for Document PK {document_pk}. Created {len(generated_audio_db_pks)} files.'
        )
        return {'status': 'COMPLETE', 'audio_pks': generated_audio_db_pks}

    except Document.DoesNotExist:
        logger.error(f'Document PK {document_pk} not found for audio creation task.')
        return {'status': 'FAILED', 'error': 'Document not found'}
    except User.DoesNotExist:
        logger.error(f'User PK {user_id} not found for audio creation task.')
        return {'status': 'FAILED', 'error': 'User not found'}
    except Exception as e:
        logger.error(f'Error in create_audio_files_task for Document PK {document_pk}: {e}', exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}


@shared_task(bind=True)
def create_single_video_task(self, audio_file_pk):
    """
    Celery task to create a single video file from DB-stored audio.
    Writes audio to a temp file, generates video to a temp file, returns video bytes.
    """
    import tempfile

    from .create_video import create_video_parallel
    from .utils import _get_random_background

    logger.info(f'Celery Task Started: create_single_video_task for AudioFile PK {audio_file_pk}')
    try:
        audio_file_obj = AudioFile.objects.get(pk=audio_file_pk)

        if not audio_file_obj.audio_data:
            logger.error(f'No audio data stored for AudioFile PK {audio_file_pk}')
            return {'status': 'FAILED', 'error': 'No audio data stored'}

        # Get notebook title
        cleaned_notebook_title = 'Untitled'
        try:
            document = audio_file_obj.document
            if document and document.original_filename:
                stem = os.path.splitext(document.original_filename)[0]
                cleaned_notebook_title = re.sub(r'^\d+[\s_-]+', '', stem).replace('-', ' ').replace('_', ' ')
        except Exception as title_err:
            logger.warning(f'Could not determine cleaned notebook title for Audio PK {audio_file_pk}: {title_err}')

        metadata = audio_file_obj.metadata or {}
        section_index = metadata.get('section_index')
        block_type = metadata.get('block_type', 'markdown')
        original_content = metadata.get('original_content', '')
        section_title = audio_file_obj.title

        if section_index is None or original_content is None:
            logger.error(f'Missing metadata for AudioFile PK {audio_file_pk}.')
            return {'status': 'FAILED', 'error': 'Missing metadata'}

        section_tuple = (section_title, original_content, block_type)

        # Write audio bytes to temp file
        tmp_audio_fd, tmp_audio_path = tempfile.mkstemp(suffix='.mp3')
        tmp_video_fd, tmp_video_path = tempfile.mkstemp(suffix='.mp4')
        tmp_sync_fd, tmp_sync_path = tempfile.mkstemp(suffix='.json')
        os.close(tmp_audio_fd)
        os.close(tmp_video_fd)
        os.close(tmp_sync_fd)

        try:
            with open(tmp_audio_path, 'wb') as f:
                f.write(bytes(audio_file_obj.audio_data))

            logo_path = Path(settings.STATICFILES_DIRS[0]) / 'css' / 'img' / 'logo.png'
            logo_path_str = str(logo_path) if logo_path.exists() else None
            default_bg = str(Path(settings.BASE_DIR) / 'video' / 'background.mp4')
            background_path_str = _get_random_background(default_bg)

            font_styles = {
                'font': 'Inter',
                'font_size': 36,
                'text_color': 'white',
                'code_font': 'Courier-New',
                'code_font_size': 32,
                'code_text_color': '#F0F0F0',
            }

            self.update_state(state='PROGRESS', meta={'status_message': f'Rendering video for: {audio_file_obj.title}'})

            create_video_parallel(
                section=section_tuple,
                audio_file=tmp_audio_path,
                output_file=tmp_video_path,
                logo_path=logo_path_str,
                background_path=background_path_str,
                text_sync_file=tmp_sync_path,
                font_styles=font_styles,
                notebook_title=cleaned_notebook_title,
            )

            with open(tmp_video_path, 'rb') as f:
                video_bytes = f.read()

            logger.info(f'Finished video creation for AudioFile PK {audio_file_pk}. Size: {len(video_bytes)} bytes')
            return {'status': 'COMPLETE', 'video_bytes': video_bytes}

        finally:
            for p in [tmp_audio_path, tmp_video_path, tmp_sync_path]:
                try:
                    os.remove(p)
                except OSError:
                    pass

    except AudioFile.DoesNotExist:
        logger.error(f'AudioFile PK {audio_file_pk} not found for video creation task.')
        return {'status': 'FAILED', 'error': 'AudioFile not found'}
    except Exception as e:
        logger.error(f'Error in create_single_video_task for AudioFile PK {audio_file_pk}: {e}', exc_info=True)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        return {'status': 'FAILED', 'error': str(e)}


# ==========================================================================
# Full Pipeline Task (One-Click: Audio → Video → Quiz → Thumbnail)
# ==========================================================================


@shared_task(bind=True)
def run_full_pipeline_task(self, document_pk, user_id, pipeline_run_id=None):
    """
    One-click pipeline: generates audio, quizzes, and thumbnail.
    Audio bytes stored in DB. Video generation is on-demand (not part of pipeline).
    """
    from .models import AudioFile, Document, Quiz, QuizQuestion
    from .pipeline_utils import send_pipeline_update
    from .quiz_generator import generate_quiz_for_section
    from .rag_engine import index_document
    from .thumbnail_generator import generate_thumbnail

    logger.info(f'Full Pipeline Started for Document PK {document_pk}')

    def _update(status, pct, step, msg=''):
        if pipeline_run_id:
            send_pipeline_update(pipeline_run_id, status, pct, step, msg)

    try:
        document = Document.objects.get(pk=document_pk)
        user = User.objects.get(pk=user_id)

        notebook_json = document.notebook_json
        if not notebook_json:
            _update('failed', 0, '', 'No notebook content stored')
            return {'status': 'FAILED', 'error': 'No notebook content stored'}

        notebook_title = document.original_filename
        if notebook_title:
            notebook_title = os.path.splitext(notebook_title)[0]
        else:
            notebook_title = 'Notebook'

        # ---- STEP 1: Audio Generation (0-50%) ----
        _update('audio', 5, 'Parsing notebook & generating audio...')

        audio_files_info = process_notebook_and_create_audio(
            notebook_json_str=notebook_json,
            notebook_title=notebook_title,
        )
        total_audio = len(audio_files_info)

        if total_audio == 0:
            _update('failed', 0, '', 'No content found in notebook')
            return {'status': 'FAILED', 'error': 'No content found'}

        audio_pks = []
        for idx, audio_info in enumerate(audio_files_info):
            pct = 5 + int((idx / total_audio) * 45)
            _update('audio', pct, f'Audio {idx + 1}/{total_audio}: {audio_info["title"]}')

            try:
                audio_obj = AudioFile.objects.create(
                    title=audio_info['title'],
                    name=audio_info['name'],
                    audio_data=audio_info['audio_data'],
                    user=user,
                    document=document,
                    metadata={
                        'section_index': audio_info['section_index'],
                        'block_type': audio_info['block_type'],
                        'original_content': audio_info['original_content'],
                    },
                )
                audio_pks.append(audio_obj.pk)
            except Exception as e:
                logger.error(f'Error creating AudioFile for {audio_info["title"]}: {e}', exc_info=True)

        # ---- STEP 2: Quiz Generation (50-75%) ----
        _update('quiz', 50, 'Generating quizzes...')

        for aidx, audio_pk in enumerate(audio_pks):
            audio_obj = AudioFile.objects.get(pk=audio_pk)
            meta = audio_obj.metadata or {}
            content = meta.get('original_content', '')
            block_type = meta.get('block_type', 'markdown')

            if block_type == 'thankyou' or not content.strip():
                continue

            pct = 50 + int((aidx / max(len(audio_pks), 1)) * 25)
            _update('quiz', pct, f'Quiz for: {audio_obj.title}')

            try:
                questions = generate_quiz_for_section(content, audio_obj.title)
                if questions:
                    quiz = Quiz.objects.create(
                        course_section_id=None,
                        title=f'Quiz: {audio_obj.title}',
                    )
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
                logger.error(f'Quiz generation failed for {audio_obj.title}: {e}', exc_info=True)

        # ---- STEP 3: Thumbnail Generation (75-85%) ----
        _update('thumbnail', 75, 'Generating AI thumbnail...')
        try:
            generate_thumbnail(document_pk)
        except Exception as e:
            logger.error(f'Thumbnail generation failed: {e}', exc_info=True)

        # ---- STEP 4: RAG Indexing (85-100%) ----
        _update('thumbnail', 85, 'Indexing content for AI chatbot...')
        try:
            index_document(document_pk)
        except Exception as e:
            logger.error(f'RAG indexing failed: {e}', exc_info=True)

        # ---- COMPLETE ----
        _update('complete', 100, 'Pipeline complete!', 'All steps finished successfully.')
        logger.info(f'Full Pipeline Complete for Document PK {document_pk}')
        return {'status': 'COMPLETE', 'audio_pks': audio_pks}

    except Exception as e:
        logger.error(f'Full pipeline failed for Document PK {document_pk}: {e}', exc_info=True)
        _update('failed', 0, '', str(e))
        return {'status': 'FAILED', 'error': str(e)}


# ==========================================================================
# Standalone Quiz Generation Task
# ==========================================================================


@shared_task(bind=True)
def generate_quiz_task(self, audio_file_pk):
    """Generate a quiz for a single audio file's content."""
    from .models import AudioFile, Quiz, QuizQuestion
    from .quiz_generator import generate_quiz_for_section

    try:
        audio = AudioFile.objects.get(pk=audio_file_pk)
        meta = audio.metadata or {}
        content = meta.get('original_content', '')

        questions = generate_quiz_for_section(content, audio.title)
        if not questions:
            return {'status': 'NO_QUESTIONS'}

        quiz = Quiz.objects.create(title=f'Quiz: {audio.title}')
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
        logger.error(f'Quiz generation task failed: {e}', exc_info=True)
        return {'status': 'FAILED', 'error': str(e)}


@shared_task(bind=True)
def generate_quiz_from_document_task(self, document_pk):
    """Generate quizzes from a document's stored notebook JSON content."""
    import io

    import nbformat

    from .models import Document, Quiz, QuizQuestion
    from .quiz_generator import generate_quiz_for_section

    try:
        doc = Document.objects.get(pk=document_pk)

        if not doc.notebook_json:
            logger.error(f'No notebook JSON stored for Document PK {document_pk}')
            return {'status': 'FAILED', 'error': 'No notebook content stored'}

        nb = nbformat.read(io.StringIO(doc.notebook_json), as_version=4)

        sections = []
        current_section_title = os.path.splitext(doc.original_filename or 'Notebook')[0]
        current_content = []

        for cell in nb.cells:
            source = cell.get('source', '').strip()
            if not source:
                continue

            cell_type = cell.get('cell_type', 'code')

            # Markdown headings start new sections
            if cell_type == 'markdown' and source.startswith('#'):
                if current_content:
                    sections.append(
                        {
                            'title': current_section_title,
                            'content': '\n\n'.join(current_content),
                        }
                    )
                    current_content = []
                current_section_title = source.lstrip('#').strip() or current_section_title
            current_content.append(source)

        # Add final section
        if current_content:
            sections.append(
                {
                    'title': current_section_title,
                    'content': '\n\n'.join(current_content),
                }
            )

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
                section['content'],
                section['title'],
            )
            if not questions:
                continue

            quiz = Quiz.objects.create(
                title=f'Quiz: {section["title"]}'[:250],
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

        logger.info(f'Generated {len(quiz_ids)} quizzes ({total_questions} questions) for document {doc.pk}')
        return {'status': 'COMPLETE', 'quiz_ids': quiz_ids, 'total_questions': total_questions}

    except Exception as e:
        logger.error(f'Document quiz generation failed: {e}', exc_info=True)
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

        if not doc.notebook_json:
            return {'status': 'FAILED', 'error': 'No notebook content stored'}

        import io

        import nbformat

        nb = nbformat.read(io.StringIO(doc.notebook_json), as_version=4)

        sections_to_translate = []
        for cell in nb.cells:
            if cell.cell_type == 'markdown' and cell.source.strip():
                sections_to_translate.append(
                    {
                        'type': 'markdown',
                        'content': cell.source.strip(),
                    }
                )

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
            },
        )

        return {'status': 'COMPLETE', 'sections_translated': len(translated)}

    except Exception as e:
        logger.error(f'Translation task failed: {e}', exc_info=True)
        return {'status': 'FAILED', 'error': str(e)}


def _translate_sections(sections, lang_code, lang_name):
    """Translate sections using LLM."""

    all_content = '\n---SECTION_BREAK---\n'.join(s['content'] for s in sections)

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
                model='claude-sonnet-4-20250514',
                max_tokens=4096,
                messages=[{'role': 'user', 'content': prompt}],
            )
            translated_text = response.content[0].text
        except Exception as e:
            logger.error(f'Translation LLM call failed: {e}')
            return []

    if not translated_text:
        return []

    parts = translated_text.split('---SECTION_BREAK---')
    result = []
    for i, part in enumerate(parts):
        result.append(
            {
                'original': sections[i]['content'] if i < len(sections) else '',
                'translated': part.strip(),
                'type': sections[i]['type'] if i < len(sections) else 'markdown',
            }
        )
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
                model='claude-sonnet-4-20250514',
                max_tokens=2048,
                messages=[{'role': 'user', 'content': prompt}],
            )
            text = response.content[0].text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
            if text.endswith('```'):
                text = text[:-3]
            return _json.loads(text.strip())
        except Exception as e:
            logger.error(f'Code review failed: {e}', exc_info=True)
            return {'score': 0, 'issues': [], 'summary': f'Review failed: {e}'}

    return {'score': 0, 'issues': [], 'summary': 'No AI backend configured.'}
