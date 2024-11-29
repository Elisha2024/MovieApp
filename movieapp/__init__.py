from __future__ import absolute_import, unicode_literals

# Ensure Celery is always imported when Django starts up.
from .celery import app as celery_app

__all__ = ('celery_app',)
