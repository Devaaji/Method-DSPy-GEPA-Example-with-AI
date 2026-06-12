from collections.abc import Generator

from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings
from app.models.twitter import TwitterGenerateRequest
from app.prompts.twitter_prompt import build_system_prompt, build_user_prompt
from app.services.kimi_client import KimiClient


class TwitterContentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.kimi = KimiClient(settings)

    def stream_generate(self, payload: TwitterGenerateRequest) -> Generator[str, None, None]:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(payload)},
        ]

        yield from self.kimi.stream_chat(messages)
