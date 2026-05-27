from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"
    chroma_path: str = "db/chroma"
    knowledge_path: str = "db/knowledge"
    opik_api_key: str | None = None
    opik_workspace: str | None = None
    opik_project_name: str = "cinema-chatbot"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
