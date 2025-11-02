from celery import Celery

from core.config import settings


celery_app = Celery(
    "celery_app",
    broker_url=settings.app.celery_broker_url,
    result_backend=settings.app.celery_result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
celery_app.conf.task_create_missing_queues = True

import app.v1.tasks