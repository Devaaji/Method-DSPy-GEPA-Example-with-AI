from __future__ import annotations

from typing import Any

from app.prompts.datasets.example_factory import EXAMPLE_INPUT_FIELDS, make_example, to_dspy_examples
from app.prompts.datasets.gepa_english import ENGLISH_TRAIN_EXAMPLES, ENGLISH_VAL_EXAMPLES
from app.prompts.datasets.gepa_indonesian import INDONESIAN_TRAIN_EXAMPLES, INDONESIAN_VAL_EXAMPLES

def _enrich_example(item: dict[str, Any]) -> dict[str, Any]:
    return make_example(**item)


def build_examples(dspy: Any) -> list[Any]:
    """Build a combined GEPA dataset from language-specific sources."""
    examples = [
        *ENGLISH_TRAIN_EXAMPLES,
        *ENGLISH_VAL_EXAMPLES,
        *INDONESIAN_TRAIN_EXAMPLES,
        *INDONESIAN_VAL_EXAMPLES,
    ]
    return to_dspy_examples(dspy, examples, input_fields=EXAMPLE_INPUT_FIELDS)


def build_train_val_examples(dspy: Any) -> tuple[list[Any], list[Any]]:
    """Build a balanced train/validation split across English and Indonesian data."""
    train_examples = [*ENGLISH_TRAIN_EXAMPLES, *INDONESIAN_TRAIN_EXAMPLES]
    val_examples = [*ENGLISH_VAL_EXAMPLES, *INDONESIAN_VAL_EXAMPLES]
    trainset = to_dspy_examples(dspy, train_examples, input_fields=EXAMPLE_INPUT_FIELDS)
    valset = to_dspy_examples(dspy, val_examples, input_fields=EXAMPLE_INPUT_FIELDS)
    return trainset, valset
