"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from workflow_engine.api.auth.jwt import verify_token
from workflow_engine.db.session import get_session

security = HTTPBearer()


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """Validate JWT token and return the current user.

    Args:
        credentials: The HTTP Bearer credentials

    Returns:
        The decoded token payload

    Raises:
        HTTPException: If the token is invalid
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Type aliases for cleaner dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]
