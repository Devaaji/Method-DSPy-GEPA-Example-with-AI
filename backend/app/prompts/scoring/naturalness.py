from __future__ import annotations

import re

from .constants import GENERIC_PHRASES


def score_naturalness(tweets: list[str]) -> tuple[float, list[str]]:
    notes: list[str] = []
    if not tweets:
        return 0.0, ["No tweet drafts were produced."]

    combined_text = " ".join(tweets).lower()
    generic_hits = sum(1 for phrase in GENERIC_PHRASES if phrase in combined_text)
    emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF]", combined_text))
    exclamation_count = combined_text.count("!")
    repeated_word_penalty = 0

    words = re.findall(r"\b[a-zA-Z]{4,}\b", combined_text)
    if words:
        unique_ratio = len(set(words)) / len(words)
        repeated_word_penalty = 1 if unique_ratio < 0.55 else 0
    else:
        unique_ratio = 1.0

    score = 1.0
    score -= min(generic_hits * 0.12, 0.36)
    score -= 0.08 if emoji_count > 3 else 0.0
    score -= 0.08 if exclamation_count > 2 else 0.0
    score -= 0.1 if repeated_word_penalty else 0.0
    score -= 0.08 if unique_ratio < 0.45 else 0.0
    score = max(score, 0.0)

    if generic_hits:
        notes.append("The draft uses generic marketing phrasing.")
    if unique_ratio < 0.45:
        notes.append("The wording feels repetitive.")

    return round(score, 4), notes
