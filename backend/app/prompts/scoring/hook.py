from __future__ import annotations

import re

from .constants import HOOK_WORDS


def score_hook(tweets: list[str]) -> tuple[float, list[str]]:
    notes: list[str] = []
    if not tweets:
        return 0.0, ["No tweet drafts were produced."]

    hook_scores: list[float] = []
    for tweet in tweets:
        opening = " ".join(re.findall(r"\b\w+\b", tweet.lower())[:12])
        question_bonus = 1.0 if "?" in tweet else 0.72
        pattern_bonus = 1.0 if any(word in opening for word in HOOK_WORDS) else 0.68
        number_bonus = 1.0 if re.search(r"\b\d+\b", tweet) else 0.76
        contrast_bonus = 1.0 if any(token in tweet.lower() for token in ("but", "instead", "without", "before")) else 0.74
        hook_scores.append((0.35 * pattern_bonus) + (0.25 * question_bonus) + (0.20 * number_bonus) + (0.20 * contrast_bonus))

    score = round(sum(hook_scores) / len(hook_scores), 4)
    if score < 0.7:
        notes.append("The opening could use a stronger hook.")
    return score, notes
