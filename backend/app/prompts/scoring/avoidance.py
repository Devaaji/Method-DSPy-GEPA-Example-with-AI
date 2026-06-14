from __future__ import annotations

import re

from .constants import GENERIC_PHRASES

META_OUTPUT_PATTERNS = (
    "tidak ada tweet",
    "no tweet",
    "sesuai request",
    "sesuai permintaan",
    "request menggunakan",
    "hashtags allowed",
    "hashtag no",
    "quality criteria",
    "output exactly",
    "include_hashtags",
)


def score_avoidance(tweets: list[str], avoid: list[str]) -> tuple[float, list[str]]:
    if not tweets or not avoid:
        return 1.0, []

    combined_text = " ".join(tweets).lower()
    lowered_avoid = [item.lower() for item in avoid]
    bad_hits = 0

    for item in lowered_avoid:
        if item in combined_text:
            bad_hits += 1

    if any("emoji" in item for item in lowered_avoid):
        emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF]", combined_text))
        if emoji_count > 3:
            bad_hits += 1
    if any("hashtag" in item for item in lowered_avoid) and combined_text.count("#") > 2:
        bad_hits += 1
    if any("generic" in item or "buzzword" in item for item in lowered_avoid):
        bad_hits += sum(1 for phrase in GENERIC_PHRASES if phrase in combined_text)
    bad_hits += sum(2 for pattern in META_OUTPUT_PATTERNS if pattern in combined_text)

    penalty = min(bad_hits * 0.12, 0.72)
    score = max(1.0 - penalty, 0.0)
    notes: list[str] = []
    if score < 0.76:
        notes.append("The draft still includes patterns listed in the avoid guidance.")
    if any(pattern in combined_text for pattern in META_OUTPUT_PATTERNS):
        notes.append("The draft talks about the instructions instead of just delivering the final post.")
    return round(score, 4), notes
