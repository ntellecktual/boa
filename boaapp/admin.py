from django.contrib import admin

from .models import (DevopsItem, PortfolioItem, PortfolioVideo, ResumeDocument,
                     ScrollingImage)

admin.site.register(ResumeDocument)


@admin.register(ScrollingImage)
class ScrollingImageAdmin(admin.ModelAdmin):
    list_display = ['caption']


class PortfolioVideoInline(admin.TabularInline):
    model = PortfolioItem.videos.through
    extra = 1  # Number of empty forms in the inline


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    # Allows you to select multiple images in admin
    filter_horizontal = ('scrolling_images',)
    inlines = [PortfolioVideoInline]
    exclude = ('videos',)  # Exclude this field to avoid displaying it twice


@admin.register(DevopsItem)
class DevopsItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'details']
    # Allows you to select multiple images
    filter_horizontal = ('scrolling_images',)


@admin.register(PortfolioVideo)
class PortfolioVideoAdmin(admin.ModelAdmin):
    pass
