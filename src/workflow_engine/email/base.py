"""Abstract email provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmailMessage:
    """Represents an email message."""

    message_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    body_text: str
    body_html: str | None = None
    received_at: datetime | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class SendEmailRequest:
    """Request to send an email."""

    to_addresses: list[str]
    subject: str
    body_text: str
    body_html: str | None = None
    from_address: str | None = None  # Uses default if not specified
    reply_to: str | None = None


class AbstractEmailProvider(ABC):
    """Abstract interface for email providers.

    Implementations can use AWS SES, SendGrid, SMTP, etc.
    """

    @abstractmethod
    async def send_email(self, request: SendEmailRequest) -> str:
        """Send an email.

        Args:
            request: The email to send

        Returns:
            Message ID from the provider
        """
        pass

    @abstractmethod
    async def receive_emails(self, mailbox: str | None = None) -> list[EmailMessage]:
        """Fetch new emails from the inbox.

        Args:
            mailbox: Optional mailbox/folder identifier

        Returns:
            List of new email messages
        """
        pass

    @abstractmethod
    async def mark_processed(self, message_id: str) -> None:
        """Mark an email as processed.

        This could mean moving it to a processed folder,
        deleting it, or flagging it depending on the provider.

        Args:
            message_id: The message ID to mark as processed
        """
        pass
