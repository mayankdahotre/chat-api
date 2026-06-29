from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str = "gpt-4.1"
    azure_openai_api_version: str = "2025-04-01-preview"

    @property
    def app_storage_db(self) -> Path:
        return DATA_DIR / "app_storage.db"

    @property
    def finance_db(self) -> Path:
        return DATA_DIR / "finance_data.db"

    @property
    def marketing_db(self) -> Path:
        return DATA_DIR / "marketing_data.db"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.azure_openai_api_key and self.azure_openai_endpoint)

    default_session_id: str = "default"


@lru_cache
def get_settings() -> Settings:
    return Settings()
