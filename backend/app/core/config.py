from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.providers.types import ProviderName, SUPPORTED_PROVIDERS


class Settings(BaseSettings):
    app_name: str = "Multi-Provider Twitter SSE DSPy GEPA Demo"
    app_env: str = "development"

    frontend_url: str = "http://localhost:3001"
    ai_provider: ProviderName = Field(default="gemini", alias="AI_PROVIDER")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        alias="GEMINI_BASE_URL",
    )
    gemini_model: str = Field(default="gemini-3.5-flash", alias="GEMINI_MODEL")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    ollama_api_key: str = Field(default="ollama", alias="OLLAMA_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434/v1", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", alias="OLLAMA_MODEL")

    request_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def provider_model(self, provider: ProviderName | None = None) -> str:
        active_provider = provider or self.ai_provider
        return getattr(self, f"{active_provider}_model")

    def provider_base_url(self, provider: ProviderName | None = None) -> str:
        active_provider = provider or self.ai_provider
        return getattr(self, f"{active_provider}_base_url")

    def provider_api_key(self, provider: ProviderName | None = None) -> str:
        active_provider = provider or self.ai_provider
        return getattr(self, f"{active_provider}_api_key")

    def supported_providers(self) -> tuple[ProviderName, ...]:
        return SUPPORTED_PROVIDERS


@lru_cache
def get_settings() -> Settings:
    return Settings()
