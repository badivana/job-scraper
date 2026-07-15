from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, AnyHttpUrl
from typing import Optional
import secrets

class Settings(BaseSettings):
    # App
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "AI Job Finder Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "RS256"
    # Supabase JWT verification
    SUPABASE_JWKS_URL: Optional[AnyHttpUrl] = None
    JWT_AUDIENCE: str = "authenticated"

    # Database
    DATABASE_URL: Optional[PostgresDsn] = None

    # Redis
    REDIS_URL: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[AnyHttpUrl] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_JWKS_URL: Optional[AnyHttpUrl] = None

    # Apify
    APIFY_API_TOKEN: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Email (SMTP)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    MAIL_FROM: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[AnyHttpUrl] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # File upload limits
    MAX_CONTENT_LENGTH: int = 5242880  # 5 MB

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()