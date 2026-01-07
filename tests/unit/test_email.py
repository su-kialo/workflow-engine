"""Tests for email utilities."""

import pytest

from workflow_engine.email.base import EmailMessage, SendEmailRequest
from workflow_engine.email.sender import EmailSender


class TestEmailSender:
    """Tests for EmailSender utility functions."""

    def test_format_subject_with_request_id(self):
        """Test formatting subject with request ID."""
        sender = EmailSender(provider=None)  # Provider not needed for this test
        result = sender.format_subject_with_request_id("Test Subject", 123)
        assert result == "[REQ-123] Test Subject"

    def test_format_subject_with_large_id(self):
        """Test formatting subject with large request ID."""
        sender = EmailSender(provider=None)
        result = sender.format_subject_with_request_id("Subject", 999999)
        assert result == "[REQ-999999] Subject"

    def test_extract_request_id(self):
        """Test extracting request ID from subject."""
        result = EmailSender.extract_request_id("[REQ-123] Test Subject")
        assert result == 123

    def test_extract_request_id_large_number(self):
        """Test extracting large request ID."""
        result = EmailSender.extract_request_id("[REQ-999999] Subject")
        assert result == 999999

    def test_extract_request_id_middle_of_subject(self):
        """Test extracting request ID from middle of subject."""
        result = EmailSender.extract_request_id("Re: [REQ-456] Original Subject")
        assert result == 456

    def test_extract_request_id_no_match(self):
        """Test extracting from subject without request ID."""
        result = EmailSender.extract_request_id("Regular Subject Line")
        assert result is None

    def test_extract_request_id_invalid_format(self):
        """Test extracting from malformed request ID."""
        result = EmailSender.extract_request_id("[REQ-abc] Invalid")
        assert result is None

    def test_extract_request_id_partial_match(self):
        """Test extracting from partial match."""
        result = EmailSender.extract_request_id("[REQ-] No Number")
        assert result is None


class TestEmailMessage:
    """Tests for EmailMessage dataclass."""

    def test_email_message_creation(self):
        """Test creating an EmailMessage."""
        msg = EmailMessage(
            message_id="test-123",
            from_address="sender@example.com",
            to_addresses=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body",
        )
        assert msg.message_id == "test-123"
        assert msg.from_address == "sender@example.com"
        assert msg.to_addresses == ["recipient@example.com"]
        assert msg.subject == "Test Subject"
        assert msg.body_text == "Test body"
        assert msg.body_html is None
        assert msg.headers == {}

    def test_email_message_with_html(self):
        """Test creating an EmailMessage with HTML body."""
        msg = EmailMessage(
            message_id="test-123",
            from_address="sender@example.com",
            to_addresses=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
        )
        assert msg.body_html == "<p>Test body</p>"

    def test_email_message_multiple_recipients(self):
        """Test creating an EmailMessage with multiple recipients."""
        msg = EmailMessage(
            message_id="test-123",
            from_address="sender@example.com",
            to_addresses=["a@example.com", "b@example.com", "c@example.com"],
            subject="Test Subject",
            body_text="Test body",
        )
        assert len(msg.to_addresses) == 3


class TestSendEmailRequest:
    """Tests for SendEmailRequest dataclass."""

    def test_send_email_request_minimal(self):
        """Test creating a minimal SendEmailRequest."""
        req = SendEmailRequest(
            to_addresses=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body",
        )
        assert req.to_addresses == ["recipient@example.com"]
        assert req.from_address is None
        assert req.reply_to is None
        assert req.body_html is None

    def test_send_email_request_full(self):
        """Test creating a full SendEmailRequest."""
        req = SendEmailRequest(
            to_addresses=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            from_address="sender@example.com",
            reply_to="reply@example.com",
        )
        assert req.from_address == "sender@example.com"
        assert req.reply_to == "reply@example.com"
        assert req.body_html == "<p>Test body</p>"
