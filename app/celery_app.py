# app/celery_app.py
from celery import Celery
import os

BROKER_URL = os.getenv("BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

default_config = 'app.celeryconfig'

celery_app.config_from_object(default_config)

celery_app.conf.update(task_track_started=True, task_serializer="json")

# celery_app.autodiscover_tasks(['app.email_utils'])