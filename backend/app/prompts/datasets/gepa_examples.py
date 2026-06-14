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
)


def build_examples(dspy: Any) -> list[Any]:
    """Build a combined GEPA dataset from language-specific sources."""
    examples = [
        *ENGLISH_TRAIN_EXAMPLES,
        *ENGLISH_VAL_EXAMPLES,
        *INDONESIAN_TRAIN_EXAMPLES,
        *INDONESIAN_VAL_EXAMPLES,
    ]
    return [
        dspy.Example(**item).with_inputs(*EXAMPLE_INPUT_FIELDS)
        for item in examples
    ]


def build_train_val_examples(dspy: Any) -> tuple[list[Any], list[Any]]:
    """Build a balanced train/validation split across English and Indonesian data."""
    train_examples = [*ENGLISH_TRAIN_EXAMPLES, *INDONESIAN_TRAIN_EXAMPLES]
    val_examples = [*ENGLISH_VAL_EXAMPLES, *INDONESIAN_VAL_EXAMPLES]
    trainset = [
        dspy.Example(**item).with_inputs(*EXAMPLE_INPUT_FIELDS)
        for item in train_examples
    ]
    valset = [
        dspy.Example(**item).with_inputs(*EXAMPLE_INPUT_FIELDS)
        for item in val_examples
    ]
    return trainset, valset
