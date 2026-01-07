"""AWS SES email provider implementation."""

import email
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import aioboto3

from workflow_engine.config import get_settings
from workflow_engine.email.base import (
    AbstractEmailProvider,
    EmailMessage,
    SendEmailRequest,
)


class SESEmailProvider(AbstractEmailProvider):
    """AWS SES implementation of the email provider.

    For receiving emails, this implementation expects emails to be
    stored in S3 via SES receipt rules. The S3 bucket and prefix
    can be configured.
    """

    def __init__(
        self,
        s3_bucket: str | None = None,
        s3_prefix: str = "inbound/",
        processed_prefix: str = "processed/",
    ):
        """Initialize the SES email provider.

        Args:
            s3_bucket: S3 bucket where inbound emails are stored.
                      If None, receiving emails will not work.
            s3_prefix: Prefix for unprocessed emails in S3
            processed_prefix: Prefix to move processed emails to
        """
        self._settings = get_settings()
        self._s3_bucket = s3_bucket
        self._s3_prefix = s3_prefix
        self._processed_prefix = processed_prefix
        self._session = aioboto3.Session(
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            region_name=self._settings.aws_region,
        )

    async def send_email(self, request: SendEmailRequest) -> str:
        """Send an email via AWS SES.

        Args:
            request: The email to send

        Returns:
            Message ID from SES
        """
        from_address = request.from_address or self._settings.ses_sender_email

        async with self._session.client("ses") as ses:
            # Build email body
            body = {"Text": {"Data": request.body_text, "Charset": "UTF-8"}}
            if request.body_html:
                body["Html"] = {"Data": request.body_html, "Charset": "UTF-8"}

            # Build destination
            destination = {"ToAddresses": request.to_addresses}

            # Build message
            message = {
                "Subject": {"Data": request.subject, "Charset": "UTF-8"},
                "Body": body,
            }

            # Send email
            kwargs = {
                "Source": from_address,
                "Destination": destination,
                "Message": message,
            }

            if request.reply_to:
                kwargs["ReplyToAddresses"] = [request.reply_to]

            response = await ses.send_email(**kwargs)
            return response["MessageId"]

    async def receive_emails(self, mailbox: str | None = None) -> list[EmailMessage]:
        """Fetch new emails from S3.

        Emails are expected to be stored in S3 via SES receipt rules.

        Args:
            mailbox: Optional subfolder within the S3 prefix

        Returns:
            List of new email messages
        """
        if not self._s3_bucket:
            return []

        prefix = self._s3_prefix
        if mailbox:
            prefix = f"{prefix}{mailbox}/"

        messages = []

        async with self._session.client("s3") as s3:
            # List objects in the bucket
            response = await s3.list_objects_v2(
                Bucket=self._s3_bucket,
                Prefix=prefix,
            )

            for obj in response.get("Contents", []):
                key = obj["Key"]
                # Skip if it's just the prefix directory
                if key == prefix:
                    continue

                # Get the email content
                email_obj = await s3.get_object(
                    Bucket=self._s3_bucket,
                    Key=key,
                )
                raw_email = await email_obj["Body"].read()

                # Parse the email
                msg = email.message_from_bytes(raw_email)
                email_message = self._parse_email(msg, key)
                if email_message:
                    messages.append(email_message)

        return messages

    def _parse_email(self, msg: email.message.Message, message_id: str) -> EmailMessage | None:
        """Parse a raw email message into an EmailMessage.

        Args:
            msg: The parsed email message
            message_id: The S3 key as message ID

        Returns:
            EmailMessage or None if parsing fails
        """
        # Extract basic headers
        from_address = msg.get("From", "")
        to_addresses = msg.get("To", "").split(",")
        to_addresses = [addr.strip() for addr in to_addresses if addr.strip()]
        subject = msg.get("Subject", "")

        # Parse date
        date_str = msg.get("Date")
        received_at = None
        if date_str:
            try:
                received_at = parsedate_to_datetime(date_str)
            except (ValueError, TypeError):
                received_at = datetime.now(timezone.utc)

        # Extract body
        body_text = ""
        body_html = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode("utf-8", errors="replace")
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html = payload.decode("utf-8", errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_text = payload.decode("utf-8", errors="replace")

        # Extract headers
        headers = {key: msg.get(key, "") for key in msg.keys()}

        return EmailMessage(
            message_id=message_id,
            from_address=from_address,
            to_addresses=to_addresses,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            received_at=received_at,
            headers=headers,
        )

    async def mark_processed(self, message_id: str) -> None:
        """Move the email to the processed folder in S3.

        Args:
            message_id: The S3 key of the message
        """
        if not self._s3_bucket:
            return

        # Calculate new key
        filename = message_id.split("/")[-1]
        new_key = f"{self._processed_prefix}{filename}"

        async with self._session.client("s3") as s3:
            # Copy to processed folder
            await s3.copy_object(
                Bucket=self._s3_bucket,
                CopySource={"Bucket": self._s3_bucket, "Key": message_id},
                Key=new_key,
            )

            # Delete original
            await s3.delete_object(
                Bucket=self._s3_bucket,
                Key=message_id,
            )
