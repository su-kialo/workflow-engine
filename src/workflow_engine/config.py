"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://workflow:workflow_secret@localhost:5432/workflow_engine"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # AWS SES
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    ses_sender_email: str = "noreply@example.com"

    # Admin Session
    admin_session_secret: str = "admin-secret-key-change-in-production"
    admin_username: str = "admin"
    admin_password_hash: str = ""

    # Application
    debug: bool = False
    log_level: str = "INFO"

    @property
    def celery_broker_url(self) -> str:
        """Return Redis URL for Celery broker."""
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        """Return Redis URL for Celery result backend."""
        return self.redis_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
