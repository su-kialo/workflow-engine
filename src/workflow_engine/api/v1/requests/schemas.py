"""Request API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from workflow_engine.db.models.enums import RequestStatus, RequestType


class ClientBase(BaseModel):
    """Base client schema."""

    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    notes: str | None = None


class ClientCreate(ClientBase):
    """Schema for creating a client."""

    pass


class ClientResponse(ClientBase):
    """Schema for client response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RequestBase(BaseModel):
    """Base request schema."""

    type: RequestType
    target_name: str
    target_email: str
    target_responsible_name: str | None = None


class RequestCreate(RequestBase):
    """Schema for creating a request."""

    client_id: int


class RequestCreateWithClient(RequestBase):
    """Schema for creating a request with a new client."""

    client: ClientCreate


class RequestResponse(RequestBase):
    """Schema for request response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    status: RequestStatus
    created_at: datetime
    finished_at: datetime | None = None
    last_response_at: datetime | None = None


class RequestDetailResponse(RequestResponse):
    """Schema for detailed request response with client info."""

    client: ClientResponse


class RequestStateResponse(BaseModel):
    """Schema for request state response."""

    request_id: int
    current_state: dict[str, Any]
    status: RequestStatus


class RequestListResponse(BaseModel):
    """Schema for paginated request list."""

    items: list[RequestResponse]
    total: int
    page: int
    page_size: int
