from typing import Literal
from pydantic import BaseModel, Field

from app.providers.types import ProviderName


class TwitterGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    provider: ProviderName | None = Field(default=None)
    tone: Literal["professional", "casual", "bold", "friendly", "educational"] | None = None
    audience: str | None = Field(default=None, max_length=200)
    language: Literal["English", "Indonesian"] = "English"
    count: int = Field(default=1, ge=1, le=5)
    include_hashtags: bool = True
    max_chars: int = Field(default=280, ge=120, le=280)


class TwitterSessionResponse(BaseModel):
    session_id: str
    sse_url: str
