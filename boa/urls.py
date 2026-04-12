from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from boaapp import views as boaapp_views
from boaapp.api import api as ninja_api

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    # Health check (DB, cache, storage)
    path('health/', boaapp_views.health_check, name='health_check'),
    # Django Ninja API (Swagger at /api/docs, health at /api/v1/health)
    path('api/v1/', ninja_api.urls),
    # Social Auth (allauth)
    path('accounts/', include('allauth.urls')),
    # Auth
    path('register/', boaapp_views.register, name='register'),
    path('login/', boaapp_views.login_view, name='login'),
    path('accounts/login/', boaapp_views.login_view, name='accounts_login'),
    path('logout/', boaapp_views.logout_view, name='logout'),
    path('', boaapp_views.home_view, name='home'),
    path('profile/', boaapp_views.profile_view, name='profile'),
    # Dashboard
    path('dashboard/', boaapp_views.dashboard, name='dashboard'),
    path('dashboard/delete_orphaned/', boaapp_views.delete_orphaned_files, name='delete_orphaned_files'),
    path('dashboard/delete_all/', boaapp_views.delete_all_files, name='delete_all_files'),
    # Upload & Processing
    path('uploadit/', boaapp_views.uploadit, name='uploadit'),
    path('upload/', boaapp_views.upload_document, name='upload_document'),
    path('task_status/<str:task_id>/', boaapp_views.check_task_status, name='check_task_status'),
    path('audio/<int:audio_file_pk>/stream/', boaapp_views.serve_audio, name='serve_audio'),
    path('video/<int:audio_file_pk>/download/', boaapp_views.download_video, name='download_video'),
    path('generate_video/<int:audio_file_pk>/', boaapp_views.generate_video, name='generate_video'),
    path('generate_all_videos/', boaapp_views.generate_all_videos, name='generate_all_videos'),
    # One-Click Pipeline
    path('pipeline/<int:document_pk>/', boaapp_views.run_full_pipeline, name='run_pipeline'),
    path('api/pipeline/<int:run_id>/status/', boaapp_views.pipeline_status_api, name='pipeline_status'),
    # Quizzes
    path('quizzes/<int:document_pk>/', boaapp_views.quiz_list_view, name='quiz_list'),
    path('quizzes/<int:document_pk>/generate/', boaapp_views.generate_quiz_view, name='generate_quizzes'),
    path('quiz/<int:quiz_pk>/', boaapp_views.quiz_take_view, name='quiz_take'),
    # RAG Chatbot
    path('chat/', boaapp_views.chat_view, name='chat'),
    path('chat/<int:document_pk>/', boaapp_views.chat_view, name='chat_document'),
    path('api/chat/', boaapp_views.chat_api, name='chat_api'),
    # Code Playground
    path('playground/', boaapp_views.code_playground_view, name='code_playground'),
    path('api/code-review/', boaapp_views.code_review_api, name='code_review'),
    # Analytics
    path('analytics/', boaapp_views.analytics_dashboard_view, name='analytics'),
    # Chaptered Video Player
    path('player/<int:document_pk>/', boaapp_views.chaptered_player_view, name='chaptered_player'),
    # Translation
    path('translate/<int:document_pk>/', boaapp_views.translate_document_view, name='translate_document'),
    # Voice Settings
    path('voice-settings/', boaapp_views.voice_settings_view, name='voice_settings'),
    # GitHub Webhooks
    path('webhooks/github/', boaapp_views.github_webhook, name='github_webhook'),
    path('webhooks/config/', boaapp_views.webhook_config_view, name='webhook_config'),
    # Learning Paths
    path('learning-path/', boaapp_views.learning_path_view, name='learning_path'),
    # Courses
    path('courses/', boaapp_views.course_list_view, name='course_list'),
    path('courses/<int:course_id>/', boaapp_views.course_detail_view, name='course_detail'),
    path('courses/<int:course_id>/enroll/', boaapp_views.enroll_course_view, name='enroll_course'),
    path(
        'courses/section/<int:section_id>/mark_learned/',
        boaapp_views.mark_section_learned_view,
        name='mark_section_learned',
    ),
    # Portfolio & Showcase
    path('portfolio_showcase/', boaapp_views.portfolio_showcase, name='portfolio_showcase'),
    path('education_details/', boaapp_views.education_details_view, name='education_details'),
    # AI Process Flows Demo
    path('process_flows/', boaapp_views.process_flows, name='process_flows'),
    # Resume & Skills
    path('data_start/', boaapp_views.data_start, name='data_start'),
    path('data_project/', boaapp_views.data_project, name='data_project'),
    path('live_demos/', boaapp_views.live_demos, name='live_demos'),
    # Demo Showcase Pages
    path('platform_engineering/', boaapp_views.platform_engineering, name='platform_engineering'),
    path('mlops_lifecycle/', boaapp_views.mlops_lifecycle, name='mlops_lifecycle'),
    path('streaming_architecture/', boaapp_views.streaming_architecture, name='streaming_architecture'),
    path('nfl_draft/', boaapp_views.nfl_draft, name='nfl_draft'),
    path('api_orchestration/', boaapp_views.api_orchestration, name='api_orchestration'),
    path('idp_demo/', boaapp_views.idp_demo, name='idp_demo'),
    path('api/portfolio-chat/', boaapp_views.portfolio_chat_api, name='portfolio_chat_api'),
    # Live API Orchestration
    path('api/live-apis/', boaapp_views.live_api_proxy, name='live_api_proxy'),
    # AI Job Match Analyzer
    path('job_match/', boaapp_views.job_match_view, name='job_match'),
    path('api/job-match/', boaapp_views.job_match_api, name='job_match_api'),
    # System Observability
    path('observability/', boaapp_views.system_observability_view, name='system_observability'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
