"""Client repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workflow_engine.db.models.client import Client
from workflow_engine.db.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Repository for Client operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Client)

    async def get_by_email(self, email: str) -> Client | None:
        """Get a client by email address."""
        stmt = select(Client).where(Client.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
