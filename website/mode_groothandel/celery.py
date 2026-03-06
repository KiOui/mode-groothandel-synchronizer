import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mode_groothandel.settings")

app = Celery("mode_groothandel", result_extended=True)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
