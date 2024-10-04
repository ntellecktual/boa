from boaapp import views as boaapp_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('upload/progress/', boaapp_views.upload_progress, name='upload_progress'),
    path('admin/', admin.site.urls),
    path('register/', boaapp_views.register, name='register'),
    path('login/', boaapp_views.login_view, name='login'),
    path('logout/', boaapp_views.logout_view, name='logout'),
    path('', boaapp_views.home, name='home'),
    path('upload/', boaapp_views.upload_document, name='upload_document'),
    path('upload/success/', boaapp_views.upload_success, name='upload_success'),
    path('portfolio_showcase/', boaapp_views.portfolio_showcase,
         name='portfolio_showcase'),
    path('project_pages/', boaapp_views.project_pages, name='project_pages'),
    path('resume/', boaapp_views.display_resume, name='resume'),
    path('companyandme/', boaapp_views.companyandme, name='companyandme'),
    path('data_start/', boaapp_views.data_start, name='data_start'),
    path('data_project/', boaapp_views.data_project, name='data_project'),
    path('live_demos/', boaapp_views.live_demos, name='live_demos'),
    path('skills/', boaapp_views.skills_section, name='skills_section'),
    path('upload/progress/<str:file_name>/', boaapp_views.upload_progress,
         name='upload_progress')
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
