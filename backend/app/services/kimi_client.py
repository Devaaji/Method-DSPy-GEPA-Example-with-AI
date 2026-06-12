from collections.abc import Generator
from time import perf_counter

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


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
        request_started_at = perf_counter()
        logger.info(
            "provider_request_started base_url=%s model=%s message_count=%s",
            self.settings.kimi_base_url,
            self.settings.kimi_model,
            len(messages),
        )
        stream = self.client.chat.completions.create(
            model=self.settings.kimi_model,
            messages=messages,
            stream=True,
        )

        first_chunk_logged = False
        for chunk in stream:
            if not chunk.choices:
                continue

            if not first_chunk_logged:
                logger.info(
                    "provider_first_chunk model=%s latency_ms=%d",
                    self.settings.kimi_model,
                    int((perf_counter() - request_started_at) * 1000),
                )
                first_chunk_logged = True

            delta = chunk.choices[0].delta
            token = getattr(delta, "content", None)

            if token:
                yield token
