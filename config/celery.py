from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# Initialize Celery
app = Celery("argus_celery")

# Using a string here means the worker doesn't need to serialize the configuration object to child processes
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks from installed apps' tasks.py files
app.autodiscover_tasks()
