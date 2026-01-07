"""Base event type for workflows."""

from enum import Enum
from typing import TypeVar


class BaseEventType(Enum):
    """Base class for workflow-specific event types.

    Each workflow should define its own event type enum that inherits from this class.
    """

    pass


# Type variable for generic event types
EventType = TypeVar("EventType", bound=BaseEventType)
