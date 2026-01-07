"""Authentication schemas."""

from pydantic import BaseModel


class TokenRequest(BaseModel):
    """Request for token generation."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response containing JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str
