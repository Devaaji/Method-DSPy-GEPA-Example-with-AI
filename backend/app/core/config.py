from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kimi Twitter SSE DSPy GEPA Demo"
    app_env: str = "development"

    frontend_url: str = "http://localhost:3000"

    kimi_api_key: str = Field(default="", alias="KIMI_API_KEY")
    kimi_base_url: str = Field(default="https://api.moonshot.ai/v1", alias="KIMI_BASE_URL")
    kimi_model: str = Field(default="k.2.5", alias="KIMI_MODEL")

    request_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
