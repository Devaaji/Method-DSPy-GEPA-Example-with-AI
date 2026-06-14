from __future__ import annotations

from typing import Any

from app.models.twitter import TwitterGenerateRequest

from .files import load_generation_prompt_files, load_rewrite_prompt_files
from .helpers import (
    build_audience_section,
    build_language_style_instruction,
    build_tone_section,
    build_topic_angle_instruction,
    safe_format,
    topic_is_tech_related,
)


def build_user_prompt_template() -> str:
    return load_generation_prompt_files()["user"]


def build_rewrite_user_template() -> str:
    return load_rewrite_prompt_files()["user"]


def build_generation_prompt_values(payload: TwitterGenerateRequest) -> dict[str, Any]:
    hashtag_instruction = "Do not include hashtags."
    if payload.include_hashtags:
        hashtag_instruction = (
            "Prefer no hashtags. Only add up to 2 hashtags if they feel genuinely natural."
            if not topic_is_tech_related(payload.topic)
            else "Include hashtags only if they help discoverability. Maximum 2 hashtags per tweet."
        )
    draft_noun = "draft" if payload.count == 1 else "drafts"
    output_format = (
        "Output format:\nTweet 1: ..."
        if payload.count == 1
        else "Output format:\nTweet 1: ...\nTweet 2: ...\nTweet 3: ..."
    )

    return {
        "count": payload.count,
        "draft_noun": draft_noun,
        "topic": payload.topic,
        "audience_section": build_audience_section(payload),
        "tone_section": build_tone_section(payload),
        "language": payload.language,
        "max_chars": payload.max_chars,
        "hashtag_instruction": hashtag_instruction,
        "topic_angle_instruction": build_topic_angle_instruction(payload),
        "language_style_instruction": build_language_style_instruction(payload),
        "output_format": output_format,
    }


def build_rewrite_prompt_values(payload: TwitterGenerateRequest, draft_text: str) -> dict[str, Any]:
    rewrite_hashtag_instruction = "Remove all hashtags."
    if payload.include_hashtags:
        rewrite_hashtag_instruction = (
            "Prefer no hashtags. Keep at most 1 hashtag only if it feels genuinely natural."
            if not topic_is_tech_related(payload.topic)
            else "Keep at most 2 hashtags only if they genuinely help."
        )

    return {
        "topic": payload.topic,
        "audience_section": build_audience_section(payload),
        "tone_section": build_tone_section(payload),
        "language": payload.language,
        "count": payload.count,
        "max_chars": payload.max_chars,
        "topic_angle_instruction": build_topic_angle_instruction(payload),
        "language_style_instruction": build_language_style_instruction(payload),
        "rewrite_hashtag_instruction": rewrite_hashtag_instruction,
        "draft_text": draft_text,
    }


def build_user_prompt(payload: TwitterGenerateRequest) -> str:
    return safe_format(build_user_prompt_template(), build_generation_prompt_values(payload))


def build_rewrite_user_prompt(payload: TwitterGenerateRequest, draft_text: str) -> str:
    return safe_format(build_rewrite_user_template(), build_rewrite_prompt_values(payload, draft_text))
