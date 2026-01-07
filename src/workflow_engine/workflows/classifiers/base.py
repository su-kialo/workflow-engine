"""Abstract classifier interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from workflow_engine.workflows.base.event import BaseEventType

E = TypeVar("E", bound=BaseEventType)


class AbstractClassifier(ABC, Generic[E]):
    """Abstract interface for email content classifiers.

    Classifiers analyze email content and determine the appropriate
    event type for the workflow state machine.

    Implementations can use:
    - Simple keyword matching
    - Regular expressions
    - LLM-based classification
    """

    @abstractmethod
    def classify(self, content: str) -> E | None:
        """Classify email content into an event type.

        Args:
            content: Email body text to classify

        Returns:
            EventType if classification successful, None if unable to classify
        """
        pass

    async def classify_async(self, content: str) -> E | None:
        """Async version for classifiers that need async operations.

        Default implementation calls the sync version.
        Override this method for LLM-based or API-based classifiers.

        Args:
            content: Email body text to classify

        Returns:
            EventType if classification successful, None if unable to classify
        """
        return self.classify(content)
