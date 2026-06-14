from __future__ import annotations

from string import Formatter
from typing import Any

from app.models.twitter import TwitterGenerateRequest

from .constants import TECH_TOPIC_KEYWORDS


def safe_format(template: str, values: dict[str, Any]) -> str:
    formatter = Formatter()
    keys = {
        field_name
        for _, field_name, _, _ in formatter.parse(template)
        if field_name
    }
    missing = sorted(key for key in keys if key not in values)
    if missing:
        missing_str = ", ".join(missing)
        raise KeyError(f"Missing template values for twitter prompt: {missing_str}")
    return template.format_map(values).strip()


def topic_is_tech_related(topic: str) -> bool:
    normalized = topic.lower()
    return any(keyword in normalized for keyword in TECH_TOPIC_KEYWORDS)


def build_topic_angle_instruction(payload: TwitterGenerateRequest) -> str:
    if topic_is_tech_related(payload.topic):
        if payload.audience:
            return f"Make the draft relevant to {payload.audience} without sounding forced."
        return "If the topic is tech-related, keep it useful and grounded without forcing a niche persona."

    return (
        "Do not mention startup, software, SaaS, product, AI, app, founder, or developer angles unless the topic itself clearly talks about them."
    )


def build_language_style_instruction(payload: TwitterGenerateRequest) -> str:
    if payload.language == "Indonesian":
        return (
            "Use natural everyday Indonesian like a real person posting on X. "
            "Prefer short, direct, conversational sentences. Avoid stiff formal wording."
        )
    return "Use natural everyday English like a real person posting on X."


def build_audience_section(payload: TwitterGenerateRequest) -> str:
    if topic_is_tech_related(payload.topic) and payload.audience:
        return f"Audience:\n{payload.audience}"

    if payload.language == "Indonesian":
        return (
            "Audience:\n"
            "Pembaca X pada umumnya. Fokus utama tetap ke topik asli dan cara ngomong yang natural."
        )

    return (
        "Audience:\n"
        "General X readers. Keep the focus on the original topic rather than a niche audience angle."
    )


def build_tone_section(payload: TwitterGenerateRequest) -> str:
    if payload.tone:
        return f"Tone:\n{payload.tone}"

    if payload.language == "Indonesian":
        return "Tone:\nnatural, conversational, and human"

    return "Tone:\nnatural, conversational, and human"
