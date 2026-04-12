from django.contrib import admin

from .models import (
    AudioFile,
    ChatConversation,
    CodeReview,
    Course,
    CourseSection,
    CourseThumbnail,
    Document,
    Enrollment,
    LearningEvent,
    PipelineRun,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    TranslatedContent,
    VideoFile,
    WebhookConfig,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uploaded_file', 'uploaded_at')
    list_filter = ('user', 'uploaded_at')
    search_fields = ('user__username', 'uploaded_file')

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'document', 'created_at', 'name')
    list_filter = ('user', 'created_at', 'document__user') # Example of filtering by related model field
    search_fields = ('title', 'name', 'user__username', 'document__uploaded_file')

@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'audio_file', 'created_at')
    list_filter = ('created_at', 'audio_file__user')
    search_fields = ('title', 'audio_file__title')

class CourseSectionInline(admin.TabularInline): # Or admin.StackedInline
    model = CourseSection
    extra = 1 # Number of empty forms to display
    fields = ('order', 'title', 'description', 'learn_content_file')
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('instructor', 'created_at')
    inlines = [CourseSectionInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'create_step_completed', 'teach_step_completed')
    search_fields = ('user__username', 'course__title')
    list_filter = ('course', 'enrolled_at', 'create_step_completed', 'teach_step_completed')
    filter_horizontal = ('completed_learn_sections',) # For easier management of ManyToMany

# Optionally register CourseSection separately if you want a dedicated admin page for it too
# @admin.register(CourseSection)
# class CourseSectionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'order')
#     list_filter = ('course',)
#     search_fields = ('title', 'course__title')


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'document', 'course_section', 'difficulty', 'created_at')
    list_filter = ('difficulty', 'generated_by')
    inlines = [QuizQuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'total_questions', 'completed_at')
    list_filter = ('quiz', 'completed_at')


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'title', 'created_at')


@admin.register(LearningEvent)
class LearningEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'created_at')
    list_filter = ('event_type', 'created_at')


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'status', 'progress_pct', 'started_at', 'completed_at')
    list_filter = ('status',)


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'repo_full_name', 'branch', 'is_active')


@admin.register(TranslatedContent)
class TranslatedContentAdmin(admin.ModelAdmin):
    list_display = ('document', 'language_name', 'language_code', 'created_at')


@admin.register(CourseThumbnail)
class CourseThumbnailAdmin(admin.ModelAdmin):
    list_display = ('document', 'generated_at')


@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'created_at')
