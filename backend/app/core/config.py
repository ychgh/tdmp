"""Application configuration settings."""

from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Application
    app_name: str = "Test Data Management Platform"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Chroma DB
    chroma_persist_directory: str = "./chroma_data"
    chroma_collection_name: str = "knowledge_base"

    # Redis (for event pipeline)
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
