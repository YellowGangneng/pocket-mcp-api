"""Pydantic settings for the Pocket MCP Server Store API."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Pocket MCP Server Store API", description="Display name for API docs.")
    environment: Literal["local", "development", "production", "test"] = Field(default="local")
    version: str = Field(default="0.1.0", description="Semantic version of the service.")
    docs_url: str = Field(default="/docs", description="FastAPI Swagger UI endpoint.")
    redoc_url: str | None = Field(default="/redoc", description="ReDoc documentation endpoint.")
    api_prefix: str = Field(default="/api", description="Base path for all API routes.")

    database_url: str = Field(
        default="postgresql+asyncpg://pocket:pocket@localhost:5432/pocket",
        description="Async SQLAlchemy database URL.",
    )
    sqlalchemy_echo: bool = Field(default=False, description="Enable SQLAlchemy SQL echo for debugging.")
    run_migrations_on_startup: bool = Field(
        default=True,
        description="Run SQLAlchemy metadata create_all on startup (useful for local dev).",
    )
    
    # CORS 설정
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        description="Allowed CORS origins for frontend applications.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a singleton settings instance."""

    return Settings()
