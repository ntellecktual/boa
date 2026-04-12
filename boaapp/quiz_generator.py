"""
AI-powered quiz generation from notebook content.
Uses Claude/GPT to generate MCQ and code challenge questions.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def generate_quiz_for_section(section_content, section_title, difficulty='intermediate', num_questions=5):
    """
    Generate quiz questions from section content using an LLM.
    Returns a list of question dicts.
    """
    # --- Dev stub mode: zero API cost ---
    if not getattr(settings, 'USE_LLM', True):
        logger.info(f"USE_LLM=False — returning stub quiz for '{section_title}'")
        return [
            {
                'type': 'mcq',
                'question': f'[STUB] What is a key concept in: {section_title[:60]}?',
                'options': ['A) Option A', 'B) Option B', 'C) Option C', 'D) Option D'],
                'correct_answer': 'A) Option A',
                'explanation': 'This is a stub question generated in dev mode (USE_LLM=False).',
            },
            {
                'type': 'short',
                'question': f'[STUB] Explain the main purpose of: {section_title[:60]}.',
                'options': None,
                'correct_answer': 'Sample answer for dev mode.',
                'explanation': 'Stub — set USE_LLM=True in .env for real questions.',
            },
        ]
    system_prompt = (
        'You are an expert educator creating quiz questions for a data science/programming course. '
        'Generate high-quality assessment questions that test understanding, not just memorization.'
    )

    user_prompt = f"""Generate {num_questions} quiz questions for the following section.

Section Title: {section_title}
Difficulty: {difficulty}
Content:
{section_content[:4000]}

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "type": "mcq",
      "question": "What is...?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "B) Option 2",
      "explanation": "Brief explanation of why this is correct."
    }},
    {{
      "type": "code",
      "question": "Write a Python function that...",
      "options": null,
      "correct_answer": "def example():\\n    return 42",
      "explanation": "This tests understanding of..."
    }}
  ]
}}

Mix of question types: ~60% MCQ, ~20% code challenges, ~20% short answer.
"""

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model='claude-3-5-haiku-20241022',
                max_tokens=2048,
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_prompt}],
            )
            return _parse_quiz_response(response.content[0].text)
        except Exception as e:
            logger.error(f'Anthropic quiz generation failed: {e}', exc_info=True)

    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key:
        try:
            import openai

            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                max_tokens=2048,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
            )
            return _parse_quiz_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f'OpenAI quiz generation failed: {e}', exc_info=True)

    logger.warning('No LLM available for quiz generation')
    return []


def _parse_quiz_response(raw_text):
    """Parse LLM response into structured question list."""
    try:
        # Strip markdown code fences if present
        text = raw_text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1] if '\n' in text else text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        questions = data.get('questions', [])

        # Validate structure
        valid = []
        for q in questions:
            if 'question' in q and 'correct_answer' in q:
                valid.append(
                    {
                        'type': q.get('type', 'mcq'),
                        'question': q['question'],
                        'options': q.get('options'),
                        'correct_answer': q['correct_answer'],
                        'explanation': q.get('explanation', ''),
                    }
                )
        return valid
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f'Failed to parse quiz response: {e}')
        return []


def grade_answer(question_type, user_answer, correct_answer):
    """Grade a single answer. Returns (is_correct, feedback)."""
    if question_type == 'mcq':
        # Simple exact match for MCQ
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        return is_correct, 'Correct!' if is_correct else f'Incorrect. The correct answer is: {correct_answer}'

    elif question_type == 'code':
        # For code challenges, use LLM to evaluate
        return _grade_code_answer(user_answer, correct_answer)

    else:
        # Short answer — use fuzzy matching via LLM
        return _grade_short_answer(user_answer, correct_answer)


def _grade_code_answer(user_code, correct_code):
    """Use LLM to grade code answers."""
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '') or getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        # Fallback to simple comparison
        return user_code.strip() == correct_code.strip(), 'Manual review needed.'

    prompt = f"""Compare these two code solutions. Is the student's code functionally equivalent or correct?

Expected solution:
```
{correct_code}
```

Student's solution:
```
{user_code}
```

Reply with ONLY JSON: {{"correct": true/false, "feedback": "brief explanation"}}"""

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=getattr(settings, 'ANTHROPIC_API_KEY', ''))
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=256,
            messages=[{'role': 'user', 'content': prompt}],
        )
        result = json.loads(response.content[0].text.strip().strip('`').strip())
        return result.get('correct', False), result.get('feedback', '')
    except Exception as e:
        logger.warning(f'Code grading failed: {e}')
        return False, 'Could not auto-grade. Please review manually.'


def _grade_short_answer(user_answer, correct_answer):
    """Use fuzzy string matching for short answers."""
    # Simple containment check as baseline
    user_lower = user_answer.strip().lower()
    correct_lower = correct_answer.strip().lower()

    if user_lower == correct_lower:
        return True, 'Correct!'
    if correct_lower in user_lower or user_lower in correct_lower:
        return True, 'Correct! (partial match)'
    return False, f'Incorrect. Expected: {correct_answer}'
