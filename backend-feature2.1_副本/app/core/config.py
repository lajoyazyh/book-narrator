from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "agent-eval-backend"
    env: str = "dev"

    cors_origins: str = "http://localhost:5173"
    cors_origin_regex: str | None = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
    database_url: str = "sqlite:///./app.db"

    # Agent service
    agent_base_url: str = "http://localhost:8000"

    # LLM-as-a-Judge / Ragas
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "pai-judge"

    # Embeddings
    openai_embedding_model: str | None = None
    openai_embedding_base_url: str | None = None
    openai_embedding_api_key: str | None = None

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()


def sync_openai_env() -> None:
    """
    Make pydantic settings visible to libraries such as Ragas/LangChain,
    because they often read directly from os.environ.
    """

    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    if settings.openai_base_url:
        os.environ["OPENAI_BASE_URL"] = settings.openai_base_url

    if settings.openai_model:
        os.environ["OPENAI_MODEL"] = settings.openai_model

    if settings.openai_embedding_api_key:
        os.environ["OPENAI_EMBEDDING_API_KEY"] = settings.openai_embedding_api_key

    if settings.openai_embedding_base_url:
        os.environ["OPENAI_EMBEDDING_BASE_URL"] = settings.openai_embedding_base_url

    if settings.openai_embedding_model:
        os.environ["OPENAI_EMBEDDING_MODEL"] = settings.openai_embedding_model


sync_openai_env()