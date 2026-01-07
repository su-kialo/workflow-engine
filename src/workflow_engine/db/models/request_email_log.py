"""Request email log model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from workflow_engine.db.base import Base

if TYPE_CHECKING:
    from workflow_engine.db.models.request import Request


class RequestEmailLog(Base):
    """Logs all emails sent and received for a request."""

    __tablename__ = "request_email_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    is_outgoing: Mapped[bool] = mapped_column(nullable=False)
    email_subject: Mapped[str] = mapped_column(String(500), nullable=False)
    email_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    # Relationships
    request: Mapped["Request"] = relationship("Request", back_populates="email_logs")
