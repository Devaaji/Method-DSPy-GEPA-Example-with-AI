from __future__ import annotations

import re


def score_clarity(tweets: list[str]) -> tuple[float, list[str]]:
    notes: list[str] = []
    if not tweets:
        return 0.0, ["No tweet drafts were produced."]

    per_tweet_scores: list[float] = []
    for tweet in tweets:
        words = re.findall(r"\b\w+\b", tweet)
        word_count = len(words)
        sentence_parts = [part for part in re.split(r"[.!?]+", tweet) if part.strip()]
        avg_sentence_words = word_count / max(len(sentence_parts), 1)

        concise_score = 1.0 if 10 <= word_count <= 40 else 0.72 if word_count <= 55 else 0.45
        readability_score = 1.0 if 8 <= avg_sentence_words <= 20 else 0.78 if avg_sentence_words <= 28 else 0.52
        structure_score = 1.0 if any(char in tweet for char in ".:;!?") else 0.82
        per_tweet_scores.append((0.45 * concise_score) + (0.35 * readability_score) + (0.20 * structure_score))

    score = round(sum(per_tweet_scores) / len(per_tweet_scores), 4)
    if score < 0.72:
        notes.append("The draft could be clearer or easier to skim.")
    return score, notes
