from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movieapp.settings')

app = Celery('movieapp')

# Configure Celery to use settings from Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
