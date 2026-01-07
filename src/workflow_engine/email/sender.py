"""High-level email sending service."""

import re

from workflow_engine.email.base import AbstractEmailProvider, SendEmailRequest


class EmailSender:
    """High-level service for sending workflow emails.

    Provides convenience methods for common email operations
    and handles request ID embedding in subjects.
    """

    REQUEST_ID_PATTERN = re.compile(r"\[REQ-(\d+)\]")

    def __init__(self, provider: AbstractEmailProvider):
        """Initialize the email sender.

        Args:
            provider: The email provider to use for sending
        """
        self._provider = provider

    def format_subject_with_request_id(self, subject: str, request_id: int) -> str:
        """Format a subject line with the request ID prefix.

        Args:
            subject: The original subject line
            request_id: The request ID to embed

        Returns:
            Subject with [REQ-{id}] prefix
        """
        return f"[REQ-{request_id}] {subject}"

    @classmethod
    def extract_request_id(cls, subject: str) -> int | None:
        """Extract the request ID from a subject line.

        Args:
            subject: The email subject

        Returns:
            The request ID if found, None otherwise
        """
        match = cls.REQUEST_ID_PATTERN.search(subject)
        if match:
            return int(match.group(1))
        return None

    async def send_workflow_email(
        self,
        request_id: int,
        to_addresses: list[str],
        subject: str,
        body_text: str,
        body_html: str | None = None,
        from_address: str | None = None,
    ) -> str:
        """Send an email for a workflow request.

        Automatically embeds the request ID in the subject.

        Args:
            request_id: The workflow request ID
            to_addresses: Recipients
            subject: Email subject (will be prefixed with request ID)
            body_text: Plain text body
            body_html: Optional HTML body
            from_address: Optional sender address

        Returns:
            Message ID from the provider
        """
        formatted_subject = self.format_subject_with_request_id(subject, request_id)

        request = SendEmailRequest(
            to_addresses=to_addresses,
            subject=formatted_subject,
            body_text=body_text,
            body_html=body_html,
            from_address=from_address,
        )

        return await self._provider.send_email(request)

    async def send_email(self, request: SendEmailRequest) -> str:
        """Send an email directly.

        Args:
            request: The email request

        Returns:
            Message ID from the provider
        """
        return await self._provider.send_email(request)
