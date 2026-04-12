"""
BOA — Django Ninja REST API
Auto-generates interactive Swagger docs at /api/v1/docs
"""

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


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


@api.get('/health', response=HealthOut, auth=None, tags=['System'])
def api_health(request):
    """Public health check for uptime monitors."""
    return {'status': 'ok', 'version': '1.0.0'}


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
