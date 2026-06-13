from __future__ import annotations

import re
from typing import Any

GENERIC_PHRASES = (
    "unlock",
    "revolutionize",
    "game-changing",
    "supercharge",
    "delve into",
    "in today's fast-paced",
    "leverage ai",
    "synergy",
    "seamless",
)

HOOK_WORDS = (
    "why",
    "how",
    "stop",
    "most",
    "the truth",
    "what if",
    "lesson",
    "mistake",
    "hard truth",
)


def extract_tweets(text: str) -> list[str]:
    tweets: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^tweet\s*\d+\s*:\s*", "", line, flags=re.IGNORECASE)
        if line:
            tweets.append(line)
    return tweets


def score_constraints(
    tweets: list[str],
    max_chars: int,
    include_hashtags: bool,
    expected_count: int,
) -> tuple[float, list[str]]:
    if not tweets:
        return 0.0, ["No tweet drafts were produced."]

    notes: list[str] = []
    length_score = sum(1 for tweet in tweets if len(tweet) <= max_chars) / len(tweets)
    hashtag_score = sum(1 for tweet in tweets if tweet.count("#") <= 2) / len(tweets)
    count_gap = abs(len(tweets) - expected_count)
    count_score = 1.0 if count_gap == 0 else max(0.0, 1.0 - (count_gap / max(expected_count, 1)))

    if length_score < 1.0:
        notes.append("Some drafts exceed the requested character limit.")
    if hashtag_score < 1.0:
        notes.append("Some drafts use more than two hashtags.")
    if count_gap:
        notes.append(f"The output returned {len(tweets)} draft(s) even though {expected_count} was requested.")
    if not include_hashtags and any("#" in tweet for tweet in tweets):
        notes.append("Hashtags appear even though they were disabled.")

    score = (0.40 * length_score) + (0.25 * hashtag_score) + (0.35 * count_score)
    return round(score, 4), notes


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


def evaluate_twitter_output(example: Any, prediction: Any) -> dict[str, Any]:
    text = (getattr(prediction, "tweets", "") or "").strip()
    topic = str(getattr(example, "topic", ""))
    audience = str(getattr(example, "audience", ""))
    max_chars = int(getattr(example, "max_chars", 280) or 280)
    expected_count = int(getattr(example, "count", 1) or 1)
    include_hashtags = bool(getattr(example, "include_hashtags", True))
    tweets = extract_tweets(text)

    if not tweets:
        return {
            "overall_score": 0.0,
            "aspect_scores": {
                "hook": 0.0,
                "clarity": 0.0,
                "relevance": 0.0,
                "naturalness": 0.0,
                "constraint_fit": 0.0,
            },
            "tweet_count": 0,
            "tweets": [],
            "notes": ["No tweet drafts were produced."],
        }

    constraint_fit, constraint_notes = score_constraints(
        tweets,
        max_chars,
        include_hashtags,
        expected_count,
    )
    relevance, relevance_notes = score_relevance(tweets, topic, audience)
    clarity, clarity_notes = score_clarity(tweets)
    hook, hook_notes = score_hook(tweets)
    naturalness, naturalness_notes = score_naturalness(tweets)

    overall_score = round(
        (0.24 * relevance)
        + (0.22 * hook)
        + (0.20 * clarity)
        + (0.18 * naturalness)
        + (0.16 * constraint_fit),
        4,
    )

    notes = [
        *constraint_notes,
        *relevance_notes,
        *clarity_notes,
        *hook_notes,
        *naturalness_notes,
    ]

    # Keep notes readable and deduplicated in a stable order.
    deduped_notes = list(dict.fromkeys(notes))

    return {
        "overall_score": overall_score,
        "aspect_scores": {
            "hook": hook,
            "clarity": clarity,
            "relevance": relevance,
            "naturalness": naturalness,
            "constraint_fit": constraint_fit,
        },
        "tweet_count": len(tweets),
        "tweets": tweets,
        "notes": deduped_notes,
    }
