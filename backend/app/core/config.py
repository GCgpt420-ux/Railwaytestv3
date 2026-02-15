from pydantic_settings import BaseSettings
from pydantic import AliasChoices, Field, field_validator
from typing import List


class Settings(BaseSettings):
    # Application Metadata
    APP_NAME: str = "TutorPAES API"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://mvp:mvp@localhost:5432/mvp_db",
        validation_alias=AliasChoices(
            # Railway commonly provides one or more of these.
            "DATABASE_URL",
            "DATABASE_PRIVATE_URL",
            "POSTGRES_URL",
            "POSTGRESQL_URL",
        ),
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str):
        if not isinstance(value, str):
            return value
        url = value.strip()
        if not url:
            return url

        # Railway/Heroku-style URLs often come as `postgres://` or `postgresql://`.
        # SQLAlchemy + psycopg v3 expects `postgresql+psycopg://`.
        if url.startswith("postgresql+psycopg://"):
            return url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # JWT Authentication
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # Demo Data (Seeds)
    DEMO_EMAIL: str = "demo@example.com"
    DEMO_PASSWORD: str = "demo123"
    PAES_CODE: str = "PAES"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # DB bootstrap (dev only)
    # If true, the app will run Base.metadata.create_all() on startup.
    # Prefer Alembic in production to avoid schema drift.
    AUTO_CREATE_TABLES: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
