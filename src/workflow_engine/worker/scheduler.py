"""Celery Beat schedule configuration."""

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    "process-inbound-emails": {
        "task": "workflow_engine.worker.tasks.process_inbound_emails.process_inbound",
        "schedule": 60.0,  # Every 60 seconds
        "options": {"queue": "default"},
    },
    "check-deadlines": {
        "task": "workflow_engine.worker.tasks.check_deadlines.check_deadline_conditions",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "default"},
    },
}
