from __future__ import annotations

from collections.abc import Generator
from time import perf_counter

from openai import APIConnectionError, APIError, APIStatusError, APITimeoutError, OpenAI, RateLimitError
from openai.types.chat import ChatCompletionMessageParam

from app.core.logging import get_logger
from app.providers.errors import ProviderError

logger = get_logger(__name__)


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        provider_name: str,
        display_name: str,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: int,
    ):
        if not api_key:
            raise ValueError(f"{display_name} API key is missing. Add it to backend/.env first.")

        self.provider_name = provider_name
        self.display_name = display_name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_seconds,
        )

    def stream_chat(self, messages: list[ChatCompletionMessageParam]) -> Generator[str, None, None]:
        request_started_at = perf_counter()
        logger.info(
            "provider_request_started provider=%s base_url=%s model=%s message_count=%s",
            self.provider_name,
            self.base_url,
            self.model,
            len(messages),
        )
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
        except RateLimitError as exc:
            raise self._normalize_status_error(exc) from exc
        except APIStatusError as exc:
            raise self._normalize_status_error(exc) from exc
        except APIConnectionError as exc:
            raise self._normalize_connection_error(exc) from exc
        except APITimeoutError as exc:
            raise ProviderError(f"{self.display_name} request timed out. Please try again.") from exc
        except APIError as exc:
            logger.warning(
                "provider_api_error provider=%s model=%s error=%s",
                self.provider_name,
                self.model,
                exc,
            )
            raise ProviderError(f"{self.display_name} API request failed. Please try again in a moment.") from exc

        first_chunk_logged = False
        for chunk in stream:
            if not chunk.choices:
                continue

            if not first_chunk_logged:
                logger.info(
                    "provider_first_chunk provider=%s model=%s latency_ms=%d",
                    self.provider_name,
                    self.model,
                    int((perf_counter() - request_started_at) * 1000),
                )
                first_chunk_logged = True

            delta = chunk.choices[0].delta
            token = getattr(delta, "content", None)
            if token:
                yield token

    def describe(self) -> dict[str, str]:
        return {
            "provider": self.provider_name,
            "provider_label": self.display_name,
            "model": self.model,
            "base_url": self.base_url,
        }

    def _normalize_connection_error(self, exc: APIConnectionError) -> ProviderError:
        if self.provider_name == "ollama":
            return ProviderError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running and the model is available locally."
            )
        return ProviderError(f"Could not connect to {self.display_name}. Please try again in a moment.")

    def _normalize_status_error(self, exc: APIStatusError) -> ProviderError:
        status_code = getattr(exc, "status_code", None)
        response = getattr(exc, "response", None)
        error_payload = getattr(response, "json", None)

        error_type = ""
        error_message = str(exc)

        if callable(error_payload):
            try:
                payload = error_payload()
                if isinstance(payload, dict):
                    error = payload.get("error")
                    if isinstance(error, dict):
                        error_type = str(error.get("type", "")).strip()
                        error_message = str(error.get("message", "")).strip() or error_message
            except Exception:
                pass

        normalized = error_message.lower()
        if status_code == 429 and (
            "insufficient balance" in normalized
            or "recharge your account" in normalized
            or "billing" in normalized
            or error_type == "exceeded_current_quota_error"
        ):
            return ProviderError(
                f"{self.display_name} account is out of balance or quota. "
                "Please check billing and try again."
            )

        if status_code == 429:
            return ProviderError(f"{self.display_name} rate limit reached. Please wait a moment and try again.")

        if status_code == 401:
            return ProviderError(f"{self.display_name} API key is invalid. Please check backend/.env.")

        if status_code == 403:
            return ProviderError(f"{self.display_name} request was rejected. Please check account access and plan.")

        if status_code == 404 and self.provider_name == "ollama":
            return ProviderError(
                f"Ollama model '{self.model}' was not found locally. "
                f"Run 'ollama pull {self.model}' first."
            )

        logger.warning(
            "provider_status_error provider=%s model=%s status_code=%s error_type=%s error=%s",
            self.provider_name,
            self.model,
            status_code,
            error_type or "unknown",
            error_message,
        )
        return ProviderError(f"{self.display_name} API request failed ({status_code or 'unknown status'}).")
