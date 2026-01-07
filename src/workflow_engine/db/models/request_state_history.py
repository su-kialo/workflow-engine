"""Request state history model."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from workflow_engine.db.base import Base

if TYPE_CHECKING:
    from workflow_engine.db.models.request import Request


class RequestStateHistory(Base):
    """Stores the state machine state history for a request."""

    __tablename__ = "request_state_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    request_state_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    request: Mapped["Request"] = relationship("Request", back_populates="state_history")
