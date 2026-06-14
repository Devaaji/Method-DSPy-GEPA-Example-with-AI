from __future__ import annotations

import re


def score_reference_alignment(tweets: list[str], reference_posts: list[str]) -> tuple[float, list[str]]:
    if not tweets or not reference_posts:
        return 0.75, []

    combined_text = " ".join(tweets).lower()
    reference_text = " ".join(reference_posts).lower()
    keywords = [word for word in re.findall(r"\b\w{5,}\b", reference_text)][:16]
    phrases = [part.strip() for part in re.split(r"[.!?]", reference_text) if len(part.strip()) >= 24][:4]
    if not keywords:
        return 0.75, []

    hits = sum(1 for word in keywords if word in combined_text)
    phrase_hits = 0
    for phrase in phrases:
        phrase_keywords = [word for word in re.findall(r"\b\w{5,}\b", phrase)[:6]]
        if phrase_keywords and sum(1 for word in phrase_keywords if word in combined_text) >= 2:
            phrase_hits += 1

    keyword_score = hits / len(keywords)
    phrase_score = phrase_hits / len(phrases) if phrases else keyword_score
    score = (0.7 * keyword_score) + (0.3 * phrase_score)
    notes: list[str] = []
    if score < 0.3:
        notes.append("The draft does not yet reflect the level of specificity shown in the reference posts.")
    return round(max(score, 0.0), 4), notes
