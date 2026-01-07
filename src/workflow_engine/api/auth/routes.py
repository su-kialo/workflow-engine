"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext

from workflow_engine.api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from workflow_engine.api.auth.schemas import (
    RefreshTokenRequest,
    TokenRequest,
    TokenResponse,
)
from workflow_engine.config import get_settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


@router.post("/token", response_model=TokenResponse)
async def login(request: TokenRequest) -> TokenResponse:
    """Authenticate and get access tokens.

    This is a simple implementation that validates against
    environment-configured credentials. In production, this
    should validate against a user database.
    """
    settings = get_settings()

    # Simple validation against configured admin credentials
    # In production, this would query a users table
    if request.username != settings.admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # If password hash is configured, verify it
    if settings.admin_password_hash:
        if not verify_password(request.password, settings.admin_password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

    # Create tokens
    token_data = {"sub": request.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh an access token using a refresh token."""
    payload = verify_token(request.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Create new tokens
    token_data = {"sub": payload.get("sub")}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/hash-password")
async def hash_password(password: str) -> dict:
    """Utility endpoint to generate a password hash.

    Only available in debug mode.
    """
    settings = get_settings()
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    return {"hash": get_password_hash(password)}
