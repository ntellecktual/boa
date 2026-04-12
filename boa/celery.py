# c:\Users\Kieth\Documents\Repositories\thenumerix\Belonging.Opportunity.Acceptance\boa\boa\celery.py
import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boa.settings')

# Create the Celery application instance
# 'boa' is the name of your main project package
app = Celery('boa')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# Celery will automatically discover tasks in files named 'tasks.py'
# within your Django apps (like 'boaapp').
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# Optional: Example task for testing
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
