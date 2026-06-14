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
