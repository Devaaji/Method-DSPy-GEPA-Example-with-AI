from __future__ import annotations

import re


def _keywords(text: str, *, min_len: int, limit: int) -> list[str]:
    return [word.lower() for word in re.findall(r"\b\w+\b", text) if len(word) >= min_len][:limit]


def score_relevance(tweets: list[str], topic: str, audience: str) -> tuple[float, list[str]]:
    combined_text = " ".join(tweets).lower()
    topic_keywords = _keywords(topic, min_len=4, limit=8)
    audience_keywords = _keywords(audience, min_len=4, limit=5)
    topic_phrases = [part.strip().lower() for part in re.split(r"[,:;]| and | dan ", topic) if len(part.strip()) >= 10][:3]

    notes: list[str] = []
    if not topic_keywords:
        return 0.6, notes

    topic_hits = sum(1 for word in topic_keywords if word in combined_text)
    audience_hits = sum(1 for word in audience_keywords if word in combined_text) if audience_keywords else 0
    topic_score = topic_hits / len(topic_keywords)
    audience_score = audience_hits / len(audience_keywords) if audience_keywords else 0.6
    phrase_hits = sum(1 for phrase in topic_phrases if phrase and phrase in combined_text)
    phrase_score = phrase_hits / len(topic_phrases) if topic_phrases else topic_score

    if topic_score < 0.45 and phrase_score < 0.34:
        notes.append("The draft does not strongly reflect the requested topic.")
    if audience_keywords and audience_score < 0.35:
        notes.append("The draft could speak more directly to the target audience.")

    score = (0.60 * topic_score) + (0.15 * phrase_score) + (0.25 * audience_score)
    return round(score, 4), notes
