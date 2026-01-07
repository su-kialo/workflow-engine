"""Database enums."""

import enum


class RequestType(str, enum.Enum):
    """Types of requests that can be processed."""

    GDPR_DATA_REQUEST = "GDPR_DATA_REQUEST"


class RequestStatus(str, enum.Enum):
    """Status of a request."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_RESPONSE = "AWAITING_RESPONSE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
