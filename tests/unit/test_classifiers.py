"""Tests for classifier functionality."""

from enum import Enum

import pytest

from workflow_engine.workflows.base.event import BaseEventType
from workflow_engine.workflows.classifiers.keyword import KeywordClassifier


class ClassifierEventType(BaseEventType):
    """Event types for classifier tests."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    INFO_REQUESTED = "INFO_REQUESTED"
    UNKNOWN = "UNKNOWN"


class TestKeywordClassifier:
    """Tests for KeywordClassifier."""

    @pytest.fixture
    def keyword_map(self):
        """Create a keyword map for testing."""
        return {
            "approved": ClassifierEventType.APPROVED,
            "accepted": ClassifierEventType.APPROVED,
            "rejected": ClassifierEventType.REJECTED,
            "denied": ClassifierEventType.REJECTED,
            "more information": ClassifierEventType.INFO_REQUESTED,
            "please provide": ClassifierEventType.INFO_REQUESTED,
        }

    @pytest.fixture
    def classifier(self, keyword_map):
        """Create a classifier instance."""
        return KeywordClassifier(keyword_map)

    def test_classify_approved(self, classifier):
        """Test classifying approved content."""
        content = "Your request has been approved. Thank you."
        result = classifier.classify(content)
        assert result == ClassifierEventType.APPROVED

    def test_classify_rejected(self, classifier):
        """Test classifying rejected content."""
        content = "Unfortunately, your request has been rejected."
        result = classifier.classify(content)
        assert result == ClassifierEventType.REJECTED

    def test_classify_info_requested(self, classifier):
        """Test classifying info request content."""
        content = "We need more information to process your request."
        result = classifier.classify(content)
        assert result == ClassifierEventType.INFO_REQUESTED

    def test_classify_no_match(self, classifier):
        """Test classifying content with no matching keywords."""
        content = "Thank you for contacting us. We will respond soon."
        result = classifier.classify(content)
        assert result is None

    def test_case_insensitive(self, classifier):
        """Test case-insensitive matching."""
        content = "Your request has been APPROVED!"
        result = classifier.classify(content)
        assert result == ClassifierEventType.APPROVED

    def test_case_sensitive(self, keyword_map):
        """Test case-sensitive matching."""

        # Lowercase should match
        result1 = classifier.classify("Request approved")
        assert result1 == ClassifierEventType.APPROVED

        
        # Uppercase should not match when case-sensitive
        result2 = classifier.classify("Request APPROVED")
        assert result2 is None

    def test_first_match_wins(self, classifier):
        """Test that first matching keyword wins."""
        content = "Request approved but we need more information"
        result = classifier.classify(content)
        # "approved" comes before "more information" in the keyword map
        assert result == ClassifierEventType.APPROVED

    def test_phrase_matching(self, classifier):
        """Test matching multi-word phrases."""
        content = "Could you please provide additional documentation?"
        result = classifier.classify(content)
        assert result == ClassifierEventType.INFO_REQUESTED

    def test_async_classify(self, classifier):
        """Test async classification method."""
        import asyncio

        content = "Your request has been approved."
        result = asyncio.run(classifier.classify_async(content))
        assert result == ClassifierEventType.APPROVED

    def test_empty_content(self, classifier):
        """Test classifying empty content."""
        result = classifier.classify("")
        assert result is None

    def test_whitespace_content(self, classifier):
        """Test classifying whitespace-only content."""
        result = classifier.classify("   \n\t  ")
        assert result is None
