from app.core.config import Settings
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.providers.ollama import OllamaProvider
from app.providers.types import ProviderName


def create_provider(settings: Settings, requested_provider: ProviderName | None = None):
    provider_name = requested_provider or settings.ai_provider

    if provider_name == "gemini":
        return GeminiProvider(settings)
    if provider_name == "groq":
        return GroqProvider(settings)
    if provider_name == "ollama":
        return OllamaProvider(settings)

    raise ValueError(f"Unsupported provider: {provider_name}")
