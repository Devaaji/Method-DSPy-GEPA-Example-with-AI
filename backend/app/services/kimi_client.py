from collections.abc import Generator

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings


class KimiClient:
    def __init__(self, settings: Settings):
        if not settings.kimi_api_key:
            raise ValueError("KIMI_API_KEY is missing. Add it to backend/.env first.")

        self.settings = settings
        self.client = OpenAI(
            api_key=settings.kimi_api_key,
            base_url=settings.kimi_base_url,
            timeout=settings.request_timeout_seconds,
        )

    def stream_chat(self, messages: list[ChatCompletionMessageParam]) -> Generator[str, None, None]:
        """Stream tokens from Kimi's OpenAI-compatible Chat Completions API."""
        stream = self.client.chat.completions.create(
            model=self.settings.kimi_model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            token = getattr(delta, "content", None)

            if token:
                yield token
