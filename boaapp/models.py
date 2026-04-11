# boaapp/models.py

import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.pk} by {self.user.username}"

class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='audio_files')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='audio/') # Path relative to MEDIA_ROOT
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True) # For section index, etc.
    name = models.CharField(max_length=255, blank=True) # Store original filename or derived name

    def __str__(self):
        return self.title


class VideoFile(models.Model):
    audio_file = models.OneToOneField(AudioFile, on_delete=models.CASCADE, related_name='video_file')
    video_file_path = models.CharField(max_length=500) # Store relative path to video
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Video for {self.audio_file.title}"


class ScrollingImage(models.Model):
    image = models.ImageField(upload_to='scrolling_images/')
    caption = models.CharField(
        max_length=255, blank=True, null=True)  # Optional caption

    def __str__(self):
        return self.caption if self.caption else "Scrolling Image"


class PortfolioVideo(models.Model):
    # Optional title for each video
    title = models.CharField(max_length=255, blank=True)
    # Path to store the video files
    video_file = models.FileField(upload_to='portfolio/videos/')

    def __str__(self):
        return self.title or self.video_file.name  # Return video name if title is empty


class PortfolioItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    project_url = models.URLField(blank=True, null=True)
    companylogo = models.ImageField(
        upload_to='portfolio/', blank=True, null=True)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    ppt_file = models.FileField(
        upload_to='portfolio_ppts/', blank=True, null=True)
    scrolling_images = models.ManyToManyField(ScrollingImage, blank=True)

    # Add ManyToManyField for multiple videos
    videos = models.ManyToManyField(
        PortfolioVideo, blank=True, related_name='portfolio_items')

    def __str__(self):
        return self.title


class DevopsItem(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    link = models.URLField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='portfolio/', blank=True, null=True)
    img = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    vid = models.FileField(upload_to='portfolio/videos/',
                           blank=True, null=True)
    ppt = models.FileField(upload_to='portfolio_ppts/', blank=True, null=True)
    scrolling_images = models.ManyToManyField(ScrollingImage, blank=True)

    def __str__(self):
        return self.name


class ResumeDocument(models.Model):  # Renamed to avoid conflict
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='resume/')

    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Placeholders for future content structure for the 3-step process
    # learn_content = models.TextField(blank=True, help_text="Content for the 'Learn' step.")
    # create_instructions = models.TextField(blank=True, help_text="Instructions for the 'Create' step.")
    # teach_guidelines = models.TextField(blank=True, help_text="Guidelines for the 'Teach' step.")

    def __str__(self):
        return self.title


def course_section_learn_path(instance, filename):
    # Sanitize course title for directory name
    course_title_sanitized = "".join(c if c.isalnum() or c in " _-" else "" for c in instance.course.title).rstrip()
    return f'courses/{course_title_sanitized}/learn_step/section_{instance.order}/{filename}'

class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, help_text="Order in which the section appears in the course.")
    learn_content_file = models.FileField(upload_to=course_section_learn_path, blank=True, null=True, help_text="e.g., .ipynb, .md, .pdf for the 'Learn' step.")
    description = models.TextField(blank=True, help_text="Brief overview of this section.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Section {self.order}: {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    # Progress tracking for the "Learn" step
    completed_learn_sections = models.ManyToManyField(CourseSection, blank=True, related_name='completed_by_enrollments')
    # Progress tracking for "Create" and "Teach" steps
    create_step_completed = models.BooleanField(default=False)
    teach_step_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course') # Ensures a user can enroll in a course only once

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    def all_learn_sections_completed(self):
        """Checks if all 'learn' sections for the course are marked as completed."""
        total_learn_sections = self.course.sections.count()
        if total_learn_sections == 0: 
            return True 
        return self.completed_learn_sections.count() >= total_learn_sections


# ==========================================================================
# Quiz / Assessment Models
# ==========================================================================

class Quiz(models.Model):
    course_section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    generated_by = models.CharField(max_length=50, default='ai', choices=[('ai', 'AI Generated'), ('manual', 'Manual')])
    difficulty = models.CharField(max_length=20, default='intermediate', choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'quizzes'

    def __str__(self):
        return f"Quiz: {self.title}"


class QuizQuestion(models.Model):
    QUESTION_TYPES = [('mcq', 'Multiple Choice'), ('code', 'Code Challenge'), ('short', 'Short Answer')]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    options = models.JSONField(null=True, blank=True, help_text='List of options for MCQ')
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    answers = models.JSONField(default=dict, help_text='Map of question_id -> user_answer')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}/{self.total_questions}"


# ==========================================================================
# RAG Chatbot Models
# ==========================================================================

class ChatConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    title = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class ChatMessage(models.Model):
    ROLES = [('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLES)
    content = models.TextField()
    sources = models.JSONField(null=True, blank=True, help_text='RAG source references')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"


# ==========================================================================
# Learning Analytics Models
# ==========================================================================

class LearningEvent(models.Model):
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('video_watch', 'Video Watch'),
        ('audio_listen', 'Audio Listen'),
        ('code_run', 'Code Run'),
        ('chat_message', 'Chat Message'),
        ('section_complete', 'Section Complete'),
        ('course_enroll', 'Course Enroll'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_events')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'event_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.event_type} at {self.created_at}"


# ==========================================================================
# AI Thumbnail Model
# ==========================================================================

class CourseThumbnail(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='thumbnail')
    image = models.ImageField(upload_to='thumbnails/')
    prompt_used = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thumbnail for {self.document}"


# ==========================================================================
# Translation Model
# ==========================================================================

class TranslatedContent(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10, help_text='e.g., es, fr, de, ja')
    language_name = models.CharField(max_length=50)
    translated_sections = models.JSONField(default=list, help_text='List of translated section dicts')
    audio_files_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'language_code')

    def __str__(self):
        return f"{self.document} - {self.language_name}"


# ==========================================================================
# GitHub Webhook Model
# ==========================================================================

class WebhookConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhook_configs')
    repo_full_name = models.CharField(max_length=255, help_text='e.g., owner/repo')
    branch = models.CharField(max_length=100, default='main')
    notebook_path = models.CharField(max_length=500, blank=True, help_text='Path to .ipynb in repo')
    auto_pipeline = models.BooleanField(default=True, help_text='Auto-run full pipeline on push')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook: {self.repo_full_name} ({self.branch})"


# ==========================================================================
# Pipeline Run Tracking
# ==========================================================================

class PipelineRun(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('audio', 'Generating Audio'),
        ('video', 'Generating Videos'),
        ('quiz', 'Generating Quizzes'),
        ('thumbnail', 'Generating Thumbnail'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pipeline_runs')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pipeline_runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_pct = models.PositiveIntegerField(default=0)
    current_step = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pipeline: {self.document} - {self.status} ({self.progress_pct}%)"


# ==========================================================================
# Code Review Model
# ==========================================================================

class CodeReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_reviews')
    code = models.TextField()
    language = models.CharField(max_length=30, default='python')
    review_result = models.JSONField(default=dict, help_text='AI review findings')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} at {self.created_at}"
