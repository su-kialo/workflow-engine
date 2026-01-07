"""Email utilities."""

from workflow_engine.email.base import (
    AbstractEmailProvider,
    EmailMessage,
    SendEmailRequest,
)
from workflow_engine.email.ses import SESEmailProvider

__all__ = [
    "AbstractEmailProvider",
    "EmailMessage",
    "SendEmailRequest",
    "SESEmailProvider",
]
