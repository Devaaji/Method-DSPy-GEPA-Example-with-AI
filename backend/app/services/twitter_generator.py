from collections.abc import Generator
import re

from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.twitter import TwitterGenerateRequest
from app.prompts.twitter_prompt import (
    build_rewrite_system_prompt,
    build_rewrite_user_prompt,
    build_system_prompt,
    build_user_prompt,
    get_prompt_metadata,
)
from app.providers.factory import create_provider
from app.services.twitter_cleaner import sanitize_twitter_output
from app.services.twitter_reaction_writer import build_reaction_tweets, is_indonesian_reaction_brief

logger = get_logger(__name__)


class TwitterContentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def build_provider(self, payload: TwitterGenerateRequest):
        return create_provider(self.settings, payload.provider)

    def _stream_text(self, text: str) -> Generator[str, None, None]:
        for match in re.finditer(r"\S+\s*", text):
            yield match.group(0)

    def _generate_with_editor_pass(self, payload: TwitterGenerateRequest, provider) -> Generator[str, None, None]:
        draft_messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(payload)},
        ]
        logger.info("editor_pass_started provider=%s model=%s", provider.provider_name, provider.model)
        draft_text = provider.complete_chat(draft_messages).strip()
        logger.info("editor_pass_draft_ready chars=%s", len(draft_text))

        rewrite_messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_rewrite_system_prompt()},
            {"role": "user", "content": build_rewrite_user_prompt(payload, draft_text)},
        ]
        rewritten_text = provider.complete_chat(rewrite_messages).strip()
        cleaned_text = sanitize_twitter_output(
            rewritten_text or draft_text,
            expected_count=payload.count,
            include_hashtags=payload.include_hashtags,
        )
        final_text = cleaned_text or rewritten_text or draft_text
        logger.info(
            "editor_pass_finished draft_chars=%s rewritten_chars=%s final_chars=%s",
            len(draft_text),
            len(rewritten_text),
            len(final_text),
        )
        yield from self._stream_text(final_text)

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
        if is_indonesian_reaction_brief(payload):
            logger.info("reaction_writer_selected topic=%r", payload.topic[:100])
            yield from self._stream_text(build_reaction_tweets(payload))
            return

        if getattr(active_provider, "provider_name", "") == "ollama":
            yield from self._generate_with_editor_pass(payload, active_provider)
            return

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(payload)},
        ]

        yield from active_provider.stream_chat(messages)
