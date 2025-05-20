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
