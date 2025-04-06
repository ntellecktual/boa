# boaapp/models.py

import os

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    uploaded_file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uploaded_file.name


class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # ✅ Added user tracking
    title = models.CharField(max_length=100, default="Untitled")
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='audio/')
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey("Document", on_delete=models.CASCADE, null=True, related_name="audio_files")
    def __str__(self):
        return f"{self.name} - {self.title}"


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
