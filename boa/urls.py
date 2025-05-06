from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from boaapp import views as boaapp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', boaapp_views.register, name='register'),
    path('login/', boaapp_views.login_view, name='login'),
    path('accounts/login/', boaapp_views.login_view, name='login'),
    path('logout/', boaapp_views.logout_view, name='logout'),
    path('', boaapp_views.login_view, name='home'),
    path('uploadit!', boaapp_views.uploadit, name='uploadit!'),
    path('upload/', boaapp_views.upload_document, name='upload_document'),
    path('portfolio_showcase/', boaapp_views.portfolio_showcase,
         name='portfolio_showcase'),
    path('technical_showcase/', boaapp_views.technical_showcase_view, name='project_pages'), # Changed path and view, kept URL name
    path('resume/', boaapp_views.display_resume, name='resume'),
    path('companyandme/', boaapp_views.companyandme, name='companyandme'),
    path('task_status/<str:task_id>/', boaapp_views.check_task_status, name='check_task_status'),
    path('data_start/', boaapp_views.data_start, name='data_start'),
    path('data_project/', boaapp_views.data_project, name='data_project'),
    path('live_demos/', boaapp_views.live_demos, name='live_demos'),
    path('skills/', boaapp_views.skills_section, name='skills_section'),
    path('boashedskin', boaapp_views.boashedskin_view, name='boashedskin'),
    path('education_details/', boaapp_views.education_details_view, name='education_details'), # New URL for education
    path('dashboard/', boaapp_views.dashboard, name='dashboard'),
     path('dashboard/delete_orphaned/', boaapp_views.delete_orphaned_files, name='delete_orphaned_files'),
     path('dashboard/delete_all/', boaapp_views.delete_all_files, name='delete_all_files'),
    path('generate_video/<int:audio_file_pk>/', boaapp_views.generate_video, name='generate_video'),
    path('generate_all_videos/', boaapp_views.generate_all_videos, name='generate_all_videos'),


]

urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
