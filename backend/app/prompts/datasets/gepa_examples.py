from __future__ import annotations

from typing import Any

from app.prompts.datasets.gepa_english import ENGLISH_TRAIN_EXAMPLES, ENGLISH_VAL_EXAMPLES
from app.prompts.datasets.gepa_indonesian import INDONESIAN_TRAIN_EXAMPLES, INDONESIAN_VAL_EXAMPLES


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


def _reference_posts_for_example(item: dict[str, Any]) -> list[str]:
    language = str(item.get("language", "English"))
    topic = str(item.get("topic", ""))

    if language == "Indonesian":
        return [
            f"Orang biasanya salah paham soal {topic.lower()}. Yang dibutuhkan bukan lebih banyak noise, tapi satu sudut pandang yang jelas.",
            "Konten yang terasa manusiawi biasanya lahir dari observasi kecil yang spesifik, bukan kalimat motivasi yang bisa dipakai siapa saja.",
        ]

    return [
        f"Most people talk about {topic.lower()} at the level of features. Better posts zoom in on one concrete tradeoff or lesson.",
        "The strongest posts sound like an operator sharing a real observation, not a brand trying to impress everyone.",
    ]


def _quality_criteria_for_example(item: dict[str, Any]) -> list[str]:
    criteria = list(DEFAULT_QUALITY_CRITERIA)
    audience = str(item.get("audience", "")).lower()
    include_hashtags = bool(item.get("include_hashtags", True))

    if "founder" in audience or "leaders" in audience:
        criteria.append("Speak with conviction and make the implication clear for decision-makers.")
    if "developer" in audience or "engineer" in audience:
        criteria.append("Include one practical implementation detail or engineering tradeoff.")
    if not include_hashtags:
        criteria.append("Do not rely on hashtags to carry the idea.")

    return criteria


def _avoid_for_example(item: dict[str, Any]) -> list[str]:
    language = str(item.get("language", "English"))
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


def _enrich_example(item: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(item)
    enriched.setdefault("reference_posts", _reference_posts_for_example(enriched))
    enriched.setdefault("quality_criteria", _quality_criteria_for_example(enriched))
    enriched.setdefault("avoid", _avoid_for_example(enriched))
    return enriched


def _to_dspy_examples(dspy: Any, examples: list[dict[str, Any]]) -> list[Any]:
    return [
        dspy.Example(**_enrich_example(item)).with_inputs(*EXAMPLE_INPUT_FIELDS)
        for item in examples
    ]


def build_examples(dspy: Any) -> list[Any]:
    """Build a combined GEPA dataset from language-specific sources."""
    examples = [
        *ENGLISH_TRAIN_EXAMPLES,
        *ENGLISH_VAL_EXAMPLES,
        *INDONESIAN_TRAIN_EXAMPLES,
        *INDONESIAN_VAL_EXAMPLES,
    ]
    return _to_dspy_examples(dspy, examples)


def build_train_val_examples(dspy: Any) -> tuple[list[Any], list[Any]]:
    """Build a balanced train/validation split across English and Indonesian data."""
    train_examples = [*ENGLISH_TRAIN_EXAMPLES, *INDONESIAN_TRAIN_EXAMPLES]
    val_examples = [*ENGLISH_VAL_EXAMPLES, *INDONESIAN_VAL_EXAMPLES]
    trainset = _to_dspy_examples(dspy, train_examples)
    valset = _to_dspy_examples(dspy, val_examples)
    return trainset, valset
