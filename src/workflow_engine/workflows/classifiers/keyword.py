"""Keyword-based classifier implementation."""

from typing import Generic, TypeVar

from workflow_engine.workflows.base.event import BaseEventType
from workflow_engine.workflows.classifiers.base import AbstractClassifier

E = TypeVar("E", bound=BaseEventType)


class KeywordClassifier(AbstractClassifier[E], Generic[E]):
    """Simple keyword-based classifier.

    Maps keywords or phrases to event types. Useful for simple
    classification tasks where specific words indicate intent.

    Example:
        classifier = KeywordClassifier({
            "approved": ApprovalEvent.APPROVED,
            "rejected": ApprovalEvent.REJECTED,
            "more information": ApprovalEvent.INFO_REQUESTED,
        })
    """

    def __init__(
        self,
        keyword_map: dict[str, E],
        case_sensitive: bool = False,
    ):
        """Initialize the keyword classifier.

        Args:
            keyword_map: Dictionary mapping keywords/phrases to event types.
                         Keywords are checked in order, first match wins.
            case_sensitive: Whether to perform case-sensitive matching.
                           Defaults to False.
        """
        self._keyword_map = keyword_map
        self._case_sensitive = case_sensitive

    def classify(self, content: str) -> E | None:
        """Classify content by searching for keywords.

        Args:
            content: Email body text to classify

        Returns:
            The event type for the first matching keyword, or None
        """
        search_content = content if self._case_sensitive else content.lower()

        for keyword, event_type in self._keyword_map.items():
            search_keyword = keyword if self._case_sensitive else keyword.lower()
            if search_keyword in search_content:
                return event_type

        return None
