from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            provider_name="groq",
            display_name="Groq",
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            model=settings.groq_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
