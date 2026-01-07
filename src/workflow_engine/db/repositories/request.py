"""Request repository."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workflow_engine.db.models.enums import RequestStatus
from workflow_engine.db.models.request import Request
from workflow_engine.db.repositories.base import BaseRepository


class RequestRepository(BaseRepository[Request]):
    """Repository for Request operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Request)

    async def get_by_client_id(
        self, client_id: int, limit: int = 100, offset: int = 0
    ) -> Sequence[Request]:
        """Get all requests for a specific client."""
        stmt = select(Request).where(Request.client_id == client_id).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(
        self, status: RequestStatus, limit: int = 100, offset: int = 0
    ) -> Sequence[Request]:
        """Get all requests with a specific status."""
        stmt = select(Request).where(Request.status == status).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_open_requests(self, limit: int = 100, offset: int = 0) -> Sequence[Request]:
        """Get all open (non-completed, non-cancelled) requests."""
        stmt = (
            select(Request)
            .where(Request.status.not_in([RequestStatus.COMPLETED, RequestStatus.CANCELLED]))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
