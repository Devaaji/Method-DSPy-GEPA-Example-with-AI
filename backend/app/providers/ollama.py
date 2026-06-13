from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            provider_name="ollama",
            display_name="Ollama",
            api_key=settings.ollama_api_key,
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
