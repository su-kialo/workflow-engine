"""Email receiving service."""

from workflow_engine.email.base import AbstractEmailProvider, EmailMessage
from workflow_engine.email.sender import EmailSender


class EmailReceiver:
    """High-level service for receiving and processing workflow emails.

    Provides convenience methods for fetching and matching emails
    to workflow requests.
    """

    def __init__(self, provider: AbstractEmailProvider):
        """Initialize the email receiver.

        Args:
            provider: The email provider to use for receiving
        """
        self._provider = provider

    async def fetch_emails(self, mailbox: str | None = None) -> list[EmailMessage]:
        """Fetch new emails from the inbox.

        Args:
            mailbox: Optional mailbox/folder identifier

        Returns:
            List of new email messages
        """
        return await self._provider.receive_emails(mailbox)

    async def mark_processed(self, message_id: str) -> None:
        """Mark an email as processed.

        Args:
            message_id: The message ID to mark as processed
        """
        await self._provider.mark_processed(message_id)

    def match_email_to_request(self, email_message: EmailMessage) -> int | None:
        """Extract the request ID from an email.

        Args:
            email_message: The email message to match

        Returns:
            The request ID if found in the subject, None otherwise
        """
        return EmailSender.extract_request_id(email_message.subject)

    async def fetch_and_group_by_request(
        self, mailbox: str | None = None
    ) -> dict[int, list[EmailMessage]]:
        """Fetch emails and group them by request ID.

        Args:
            mailbox: Optional mailbox/folder identifier

        Returns:
            Dictionary mapping request IDs to lists of emails.
            Emails without a valid request ID are excluded.
        """
        emails = await self.fetch_emails(mailbox)
        grouped: dict[int, list[EmailMessage]] = {}

        for email_message in emails:
            request_id = self.match_email_to_request(email_message)
            if request_id is not None:
                if request_id not in grouped:
                    grouped[request_id] = []
                grouped[request_id].append(email_message)

        return grouped
