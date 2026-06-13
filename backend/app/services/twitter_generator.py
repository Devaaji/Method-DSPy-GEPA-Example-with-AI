from collections.abc import Generator

from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.twitter import TwitterGenerateRequest
from app.prompts.twitter_prompt import (
    build_system_prompt,
    build_user_prompt,
    get_prompt_metadata,
)
from app.providers.factory import create_provider

logger = get_logger(__name__)


class TwitterContentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def build_provider(self, payload: TwitterGenerateRequest):
        return create_provider(self.settings, payload.provider)

    def stream_generate(self, payload: TwitterGenerateRequest, provider=None) -> Generator[str, None, None]:
        prompt_metadata = get_prompt_metadata()
        logger.info(
            "prompt_selected mode=%s source=%s model=%s generated_at=%s",
            prompt_metadata.get("prompt_mode", "unknown"),
            prompt_metadata.get("prompt_source", "unknown"),
            prompt_metadata.get("prompt_model", "n/a"),
            prompt_metadata.get("prompt_generated_at", "n/a"),
        )
        active_provider = provider or self.build_provider(payload)
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(payload)},
        ]

        yield from active_provider.stream_chat(messages)
