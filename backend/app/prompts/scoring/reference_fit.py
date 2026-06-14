from __future__ import annotations

import re


def score_reference_alignment(tweets: list[str], reference_posts: list[str]) -> tuple[float, list[str]]:
    if not tweets or not reference_posts:
        return 0.75, []

    combined_text = " ".join(tweets).lower()
    reference_text = " ".join(reference_posts).lower()
    keywords = [word for word in re.findall(r"\b[a-zA-Z]{5,}\b", reference_text)][:12]
    if not keywords:
        return 0.75, []

    hits = sum(1 for word in keywords if word in combined_text)
    score = hits / len(keywords)
    notes: list[str] = []
    if score < 0.3:
        notes.append("The draft does not yet reflect the level of specificity shown in the reference posts.")
    return round(max(score, 0.0), 4), notes
