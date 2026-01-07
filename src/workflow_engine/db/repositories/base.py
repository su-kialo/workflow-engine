"""Base repository with common CRUD operations."""

from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workflow_engine.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common database operations."""

    def __init__(self, session: AsyncSession, model_class: type[ModelType]):
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get a record by its ID."""
        return await self._session.get(self._model_class, id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Get all records with pagination."""
        stmt = select(self._model_class).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        await self._session.merge(obj)
        await self._session.flush()
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        await self._session.delete(obj)
        await self._session.flush()
