from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MediQuery V2"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Qdrant
    QDRANT_URL: str = "http://localhost:6335"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "mediquery_v2"

    # Voyage AI
    VOYAGE_API_KEY: str
    VOYAGE_EMBEDDING_MODEL: str = "voyage-4-lite"
    EMBEDDING_DIMENSION: int = 1024
    VOYAGE_RERANK_MODEL: str = "rerank-2.5"

    # Claude
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-haiku-4-5-20251001"
    CLAUDE_MAX_TOKENS: int = 1500

    # RAG
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200
    TOP_K_DENSE: int = 10
    TOP_K_SPARSE: int = 10
    TOP_K_RERANK: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
