from __future__ import annotations


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
    formatting_penalties = 0

    if not include_hashtags and any("#" in tweet for tweet in tweets):
        hashtag_score = 0.0

    for tweet in tweets:
        normalized = tweet.strip()
        if normalized.startswith('"') and normalized.endswith('"'):
            formatting_penalties += 1
        if normalized.lower().startswith(("1/", "2/", "3/")):
            formatting_penalties += 1

    formatting_score = max(0.0, 1.0 - (formatting_penalties / max(len(tweets), 1)))

    if length_score < 1.0:
        notes.append("Some drafts exceed the requested character limit.")
    if hashtag_score < 1.0:
        notes.append("Some drafts use more than two hashtags.")
    if count_gap:
        notes.append(f"The output returned {len(tweets)} draft(s) even though {expected_count} was requested.")
    if not include_hashtags and any("#" in tweet for tweet in tweets):
        notes.append("Hashtags appear even though they were disabled.")
    if formatting_score < 1.0:
        notes.append("Some drafts use awkward wrapper formatting such as quoted tweets or thread-style numbering.")

    score = (0.35 * length_score) + (0.25 * hashtag_score) + (0.25 * count_score) + (0.15 * formatting_score)
    return round(score, 4), notes
