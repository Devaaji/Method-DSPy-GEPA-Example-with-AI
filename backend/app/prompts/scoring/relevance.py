from __future__ import annotations

import re


def score_relevance(tweets: list[str], topic: str, audience: str) -> tuple[float, list[str]]:
    combined_text = " ".join(tweets).lower()
    topic_keywords = [word.lower() for word in re.findall(r"\b\w+\b", topic) if len(word) > 4][:6]
    audience_keywords = [word.lower() for word in re.findall(r"\b\w+\b", audience) if len(word) > 4][:4]

    notes: list[str] = []
    if not topic_keywords:
        return 0.6, notes

    topic_hits = sum(1 for word in topic_keywords if word in combined_text)
    audience_hits = sum(1 for word in audience_keywords if word in combined_text) if audience_keywords else 0
    topic_score = topic_hits / len(topic_keywords)
    audience_score = audience_hits / len(audience_keywords) if audience_keywords else 0.6

    if topic_score < 0.45:
        notes.append("The draft does not strongly reflect the requested topic.")
    if audience_keywords and audience_score < 0.35:
        notes.append("The draft could speak more directly to the target audience.")

    score = (0.75 * topic_score) + (0.25 * audience_score)
    return round(score, 4), notes
