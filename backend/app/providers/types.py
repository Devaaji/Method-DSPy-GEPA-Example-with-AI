from typing import Literal

ProviderName = Literal["gemini", "groq", "ollama"]

SUPPORTED_PROVIDERS: tuple[ProviderName, ...] = ("gemini", "groq", "ollama")
