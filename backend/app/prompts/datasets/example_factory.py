from __future__ import annotations

import re
from typing import Any


EXAMPLE_INPUT_FIELDS = (
    "topic",
    "tone",
    "audience",
    "language",
    "count",
    "max_chars",
    "include_hashtags",
    "reference_posts",
    "quality_criteria",
    "avoid",
    "bad_examples",
    "desired_structure",
    "hook_style",
    "must_include",
    "content_goal",
    "scoring_rubric",
)

DEFAULT_QUALITY_CRITERIA = [
    "Lead with one clear idea or tension.",
    "Make the post specific enough to feel earned, not generic.",
    "Sound natural and human for the target audience.",
    "Keep the draft concise and easy to skim.",
]

DEFAULT_AVOID = [
    "generic marketing hype",
    "too many hashtags",
    "too many emojis",
    "robotic phrasing",
    "vague claims without a concrete point",
]


def _topic_keywords(topic: str, *, limit: int = 3) -> list[str]:
    return [word for word in re.findall(r"\b\w+\b", topic) if len(word) >= 5][:limit]


def _default_reference_posts(language: str, topic: str) -> list[str]:
    if language == "Indonesian":
        return [
            f"Orang biasanya salah paham soal {topic.lower()}. Yang dibutuhkan bukan lebih banyak noise, tapi satu sudut pandang yang jelas.",
            "Konten yang terasa manusiawi biasanya lahir dari observasi kecil yang spesifik, bukan kalimat motivasi yang bisa dipakai siapa saja.",
        ]

    return [
        f"Most people talk about {topic.lower()} at the level of features. Better posts zoom in on one concrete tradeoff or lesson.",
        "The strongest posts sound like an operator sharing a real observation, not a brand trying to impress everyone.",
    ]


def _default_quality_criteria(language: str, audience: str, include_hashtags: bool) -> list[str]:
    criteria = list(DEFAULT_QUALITY_CRITERIA)
    audience_lower = audience.lower()

    if language == "Indonesian":
        criteria[2] = "Sound natural and human in everyday Indonesian for the target audience."
    if "founder" in audience_lower or "leaders" in audience_lower:
        criteria.append("Speak with conviction and make the implication clear for decision-makers.")
    if "developer" in audience_lower or "engineer" in audience_lower:
        criteria.append("Include one practical implementation detail or engineering tradeoff.")
    if not include_hashtags:
        criteria.append("Do not rely on hashtags to carry the idea.")

    return criteria


def _default_avoid(language: str) -> list[str]:
    avoid = list(DEFAULT_AVOID)

    if language == "Indonesian":
        avoid.extend(
            [
                "terlalu normatif",
                "terlalu menggurui",
                "bahasa iklan yang berlebihan",
            ]
        )
    else:
        avoid.extend(
            [
                "buzzwords like game-changing or revolutionary",
                "salesy CTA at the end",
                "thread-style filler that adds no new point",
            ]
        )

    return avoid


def _default_bad_examples(language: str, topic: str, include_hashtags: bool) -> list[str]:
    if language == "Indonesian":
        hashtag_tail = " #AI #Tips #Growth" if include_hashtags else ""
        return [
            f"Konten tentang {topic.lower()} itu penting banget untuk semua orang{hashtag_tail}",
            "Tidak ada tweet, sesuai request menggunakan hashtag NO.",
            "Kalau mau sukses, konsisten adalah kunci dan jangan menyerah.",
        ]

    hashtag_tail = " #AI #Marketing #Growth" if include_hashtags else ""
    return [
        f"{topic} is very important for everyone and changes everything{hashtag_tail}",
        "No tweet. Hashtags disabled.",
        "Success comes from consistency, mindset, and always believing in yourself.",
    ]


def _default_desired_structure(count: int, include_hashtags: bool) -> str:
    base = (
        f"Return exactly {count} standalone tweet draft(s), each on its own line, with no quote marks or thread markers."
    )
    if include_hashtags:
        return f"{base} If hashtags are used, keep them natural and limited."
    return f"{base} Use zero hashtags."


def _default_hook_style(tone: str, language: str) -> str:
    tone_lower = tone.lower()
    if tone_lower in {"bold", "contrarian"}:
        return "Open with a sharp tension, disagreement, or hard-earned observation."
    if tone_lower in {"educational", "insightful"}:
        return "Open with a clear lesson, misconception, or practical takeaway."
    if tone_lower in {"reflective", "honest"}:
        return "Open with a grounded observation that feels personal but not dramatic."
    if language == "Indonesian":
        return "Open with one clear idea that feels natural in everyday Indonesian."
    return "Open with one clear idea that feels natural and specific."


def _default_must_include(topic: str, audience: str) -> list[str]:
    keywords = _topic_keywords(topic, limit=2)
    audience_keywords = _topic_keywords(audience, limit=1)
    return [*keywords, *audience_keywords]


def _default_content_goal(topic: str, audience: str) -> str:
    return f"Help {audience} understand or act on {topic} through one specific, non-generic post."


def _default_scoring_rubric(include_hashtags: bool) -> dict[str, str]:
    rubric = {
        "specificity": "The draft should sound concrete, not generic or interchangeable.",
        "audience_fit": "The draft should feel written for the stated audience.",
        "clarity": "The draft should be easy to skim and understand quickly.",
        "naturalness": "The draft should sound like a human wrote it.",
        "reference_fit": "The draft should match the specificity and realism of the reference posts.",
    }
    if include_hashtags:
        rubric["constraint_fit"] = "If hashtags are used, keep them natural and limited to two."
    else:
        rubric["constraint_fit"] = "Use zero hashtags and stay within the requested draft count."
    return rubric


def make_example(
    *,
    topic: str,
    tone: str,
    audience: str,
    language: str,
    count: int,
    max_chars: int,
    include_hashtags: bool,
    reference_posts: list[str] | None = None,
    quality_criteria: list[str] | None = None,
    avoid: list[str] | None = None,
    bad_examples: list[str] | None = None,
    desired_structure: str | None = None,
    hook_style: str | None = None,
    must_include: list[str] | None = None,
    content_goal: str | None = None,
    scoring_rubric: dict[str, str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    language_normalized = language or "English"

    return {
        "topic": topic,
        "tone": tone,
        "audience": audience,
        "language": language_normalized,
        "count": count,
        "max_chars": max_chars,
        "include_hashtags": include_hashtags,
        "reference_posts": list(reference_posts or _default_reference_posts(language_normalized, topic)),
        "quality_criteria": list(quality_criteria or _default_quality_criteria(language_normalized, audience, include_hashtags)),
        "avoid": list(avoid or _default_avoid(language_normalized)),
        "bad_examples": list(bad_examples or _default_bad_examples(language_normalized, topic, include_hashtags)),
        "desired_structure": desired_structure or _default_desired_structure(count, include_hashtags),
        "hook_style": hook_style or _default_hook_style(tone, language_normalized),
        "must_include": list(must_include or _default_must_include(topic, audience)),
        "content_goal": content_goal or _default_content_goal(topic, audience),
        "scoring_rubric": dict(scoring_rubric or _default_scoring_rubric(include_hashtags)),
        **extra,
    }


def normalize_examples(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [make_example(**item) for item in examples]


def to_dspy_examples(dspy: Any, examples: list[dict[str, Any]], *, input_fields: tuple[str, ...] = EXAMPLE_INPUT_FIELDS) -> list[Any]:
    return [
        dspy.Example(**make_example(**item)).with_inputs(*input_fields)
        for item in examples
    ]
