from app.core.config import Settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class GeminiProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            provider_name="gemini",
            display_name="Gemini",
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            model=settings.gemini_model,
            timeout_seconds=settings.request_timeout_seconds,
        )
