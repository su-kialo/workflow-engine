"""Background worker module."""

from workflow_engine.worker.celery_app import celery_app

__all__ = ["celery_app"]
