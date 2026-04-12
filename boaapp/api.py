"""
BOA — Django Ninja REST API
Auto-generates interactive Swagger docs at /api/v1/docs
"""

import time
from collections import defaultdict

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

api = NinjaAPI(
    title='BOA API',
    version='1.0.0',
    description='Belonging · Opportunity · Acceptance — REST API',
    auth=django_auth,
)


# --------------------------------------------------------------------------
# Rate Limiting
# --------------------------------------------------------------------------

_rate_limit_store = defaultdict(list)  # {user_id: [timestamps]}
RATE_LIMIT_RPM = 60  # requests per minute


def _check_rate_limit(user_id):
    """Simple in-memory rate limiter. Returns (allowed, remaining, reset_s)."""
    now = time.time()
    window = 60.0
    timestamps = _rate_limit_store[user_id]
    # Prune old entries
    _rate_limit_store[user_id] = [t for t in timestamps if now - t < window]
    timestamps = _rate_limit_store[user_id]
    if len(timestamps) >= RATE_LIMIT_RPM:
        oldest = timestamps[0]
        reset_s = round(window - (now - oldest))
        return False, 0, reset_s
    _rate_limit_store[user_id].append(now)
    return True, RATE_LIMIT_RPM - len(timestamps), 0


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------


class UserOut(Schema):
    id: int
    username: str
    email: str


class DocumentOut(Schema):
    id: int
    original_filename: str
    uploaded_at: str
    audio_count: int


class AudioFileOut(Schema):
    id: int
    title: str
    created_at: str
    has_audio_data: bool


class CourseOut(Schema):
    id: int
    title: str
    description: str
    section_count: int
    created_at: str


class HealthOut(Schema):
    status: str
    version: str


class SystemHealthOut(Schema):
    status: str
    version: str
    database: dict
    cache: dict
    celery: dict
    content_stats: dict
    rate_limit: dict


class RateLimitOut(Schema):
    allowed: bool
    remaining: int
    reset_seconds: int
    limit: int


class FeatureFlagOut(Schema):
    name: str
    is_enabled: bool
    description: str


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


@api.get('/health', response=HealthOut, auth=None, tags=['System'])
def api_health(request):
    """Public health check for uptime monitors."""
    return {'status': 'ok', 'version': '1.0.0'}


@api.get('/health/detailed', response=SystemHealthOut, tags=['System'])
def api_health_detailed(request):
    """Detailed system health check (authenticated)."""
    import time as t

    from django.db import connection

    # DB check
    db_ok = False
    db_ms = 0
    try:
        start = t.monotonic()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_ms = round((t.monotonic() - start) * 1000, 1)
        db_ok = True
    except Exception:
        pass

    # Cache check
    cache_ok = False
    cache_ms = 0
    try:
        from django.core.cache import cache
        start = t.monotonic()
        cache.set('_api_health', '1', 5)
        cache_ok = cache.get('_api_health') == '1'
        cache_ms = round((t.monotonic() - start) * 1000, 1)
    except Exception:
        pass

    # Celery check
    celery_ok = False
    try:
        from celery import current_app
        insp = current_app.control.inspect(timeout=2)
        workers = insp.ping() or {}
        celery_ok = len(workers) > 0
    except Exception:
        pass

    # Content stats
    from boaapp.models import AudioFile, Course, Document, LearningEvent, Quiz
    content = {
        'documents': Document.objects.count(),
        'audio_files': AudioFile.objects.count(),
        'quizzes': Quiz.objects.count(),
        'courses': Course.objects.count(),
        'events': LearningEvent.objects.count(),
    }

    # Rate limit status for caller
    allowed, remaining, reset_s = _check_rate_limit(request.user.id)

    return {
        'status': 'ok' if (db_ok and cache_ok) else 'degraded',
        'version': '1.0.0',
        'database': {'healthy': db_ok, 'latency_ms': db_ms},
        'cache': {'healthy': cache_ok, 'latency_ms': cache_ms},
        'celery': {'healthy': celery_ok},
        'content_stats': content,
        'rate_limit': {'allowed': allowed, 'remaining': remaining, 'reset_seconds': reset_s, 'limit': RATE_LIMIT_RPM},
    }


@api.get('/rate-limit', response=RateLimitOut, tags=['System'])
def api_rate_limit_status(request):
    """Check your current rate limit status."""
    allowed, remaining, reset_s = _check_rate_limit(request.user.id)
    return {
        'allowed': allowed,
        'remaining': remaining,
        'reset_seconds': reset_s,
        'limit': RATE_LIMIT_RPM,
    }


@api.get('/feature-flags', response=list[FeatureFlagOut], tags=['System'])
def api_feature_flags(request):
    """List all feature flags and their states."""
    from boaapp.models import FeatureFlag
    flags = FeatureFlag.objects.all().order_by('name')
    return [{'name': f.name, 'is_enabled': f.is_enabled, 'description': f.description} for f in flags]


@api.get('/me', response=UserOut, tags=['Auth'])
def me(request):
    """Return the currently authenticated user."""
    return request.user


@api.get('/documents', response=list[DocumentOut], tags=['Documents'])
def list_documents(request):
    """List all documents for the authenticated user."""
    from boaapp.models import Document

    docs = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    return [
        {
            'id': d.id,
            'original_filename': d.original_filename or 'untitled',
            'uploaded_at': d.uploaded_at.isoformat(),
            'audio_count': d.audio_files.count(),
        }
        for d in docs
    ]


@api.get('/documents/{document_id}/audio', response=list[AudioFileOut], tags=['Documents'])
def list_audio(request, document_id: int):
    """List audio files for a document owned by the authenticated user."""
    from boaapp.models import Document

    doc = get_object_or_404(Document, pk=document_id, user=request.user)
    return [
        {
            'id': a.id,
            'title': a.title,
            'created_at': a.created_at.isoformat(),
            'has_audio_data': bool(a.audio_data),
        }
        for a in doc.audio_files.all()
    ]


@api.get('/courses', response=list[CourseOut], tags=['Courses'])
def list_courses(request):
    """List all available courses."""
    from boaapp.models import Course

    courses = Course.objects.all().order_by('-created_at')
    return [
        {
            'id': c.id,
            'title': c.title,
            'description': c.description[:200],
            'section_count': c.sections.count(),
            'created_at': c.created_at.isoformat(),
        }
        for c in courses
    ]
