"""Session-based authentication for admin interface."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from passlib.context import CryptContext

from workflow_engine.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_serializer() -> URLSafeTimedSerializer:
    """Get the session serializer."""
    settings = get_settings()
    return URLSafeTimedSerializer(settings.admin_session_secret)


def create_session(response: Response, username: str) -> None:
    """Create a session cookie.

    Args:
        response: The response to set the cookie on
        username: The username to store in the session
    """
    serializer = get_serializer()
    token = serializer.dumps({"username": username})
    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400,  # 24 hours
    )


def get_session(request: Request) -> dict | None:
    """Get the session from the cookie.

    Args:
        request: The request containing the cookie

    Returns:
        The session data if valid, None otherwise
    """
    token = request.cookies.get("admin_session")
    if not token:
        return None

    serializer = get_serializer()
    try:
        data = serializer.loads(token, max_age=86400)
        return data
    except BadSignature:
        return None


def clear_session(response: Response) -> None:
    """Clear the session cookie.

    Args:
        response: The response to clear the cookie from
    """
    response.delete_cookie("admin_session")


async def require_admin_session(request: Request) -> dict:
    """Dependency that requires a valid admin session.

    Args:
        request: The incoming request

    Returns:
        The session data

    Raises:
        HTTPException: If no valid session exists
    """
    session = get_session(request)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"},
        )
    return session


def verify_admin_password(password: str) -> bool:
    """Verify the admin password.

    Args:
        password: The password to verify

    Returns:
        True if the password is valid
    """
    settings = get_settings()

    # If no password hash is configured, reject all logins
    if not settings.admin_password_hash:
        return False

    return pwd_context.verify(password, settings.admin_password_hash)


# Type alias for dependency injection
AdminSession = Annotated[dict, Depends(require_admin_session)]
