"""Request model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from workflow_engine.db.base import Base
from workflow_engine.db.models.enums import RequestStatus, RequestType

if TYPE_CHECKING:
    from workflow_engine.db.models.client import Client
    from workflow_engine.db.models.request_email_log import RequestEmailLog
    from workflow_engine.db.models.request_state_history import RequestStateHistory


class Request(Base):
    """Request entity representing a workflow request."""

    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    type: Mapped[RequestType] = mapped_column(nullable=False)
    status: Mapped[RequestStatus] = mapped_column(nullable=False, default=RequestStatus.PENDING)
    target_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_responsible_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_response_at: Mapped[datetime | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True, onupdate=func.now())

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="requests")
    state_history: Mapped[list["RequestStateHistory"]] = relationship(
        "RequestStateHistory", back_populates="request", lazy="selectin"
    )
    email_logs: Mapped[list["RequestEmailLog"]] = relationship(
        "RequestEmailLog", back_populates="request", lazy="selectin"
    )
