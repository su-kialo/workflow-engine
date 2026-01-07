"""Celery application configuration."""

from celery import Celery

from workflow_engine.config import get_settings

settings = get_settings()

celery_app = Celery(
    "workflow_engine",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "workflow_engine.worker.tasks.process_inbound_emails",
        "workflow_engine.worker.tasks.check_deadlines",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Import beat schedule
from workflow_engine.worker.scheduler import CELERYBEAT_SCHEDULE  # noqa: E402

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
