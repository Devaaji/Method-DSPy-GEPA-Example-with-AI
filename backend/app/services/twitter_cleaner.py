from __future__ import annotations

import re

INTRO_PATTERNS = (
    r"^here(?:'s| is)\b",
    r"^certainly\b",
    r"^sure\b",
    r"^absolutely\b",
    r"^draft\b",
    r"^x/twitter\b",
)


def _strip_intro_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    skipping_intro = True

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        normalized = line.lower().strip(" :.-")
        if skipping_intro and any(re.match(pattern, normalized) for pattern in INTRO_PATTERNS):
            continue

        skipping_intro = False
        cleaned.append(line)

    return cleaned


def _extract_candidate_tweets(text: str) -> list[str]:
    tweets: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        line = re.sub(r"^tweet\s*\d+\s*:\s*", "", line, flags=re.IGNORECASE)
        line = re.sub(r"^\d+\s*[\.\):-]\s*", "", line)
        line = line.strip().strip('"').strip("'").strip()
        if line:
            tweets.append(line)

    if tweets:
        return tweets

    compact = " ".join(part.strip() for part in text.splitlines() if part.strip()).strip()
    compact = compact.strip('"').strip("'").strip()
    return [compact] if compact else []


def _limit_hashtags(tweet: str, include_hashtags: bool) -> str:
    if not include_hashtags:
        tweet = re.sub(r"\s*#\w+", "", tweet)
        return re.sub(r"\s{2,}", " ", tweet).strip()

    hashtags = list(re.finditer(r"#\w+", tweet))
    if len(hashtags) <= 2:
        return tweet.strip()

    extra_spans = hashtags[2:]
    pieces: list[str] = []
    last_index = 0
    for match in extra_spans:
        start, end = match.span()
        pieces.append(tweet[last_index:start])
        last_index = end
    pieces.append(tweet[last_index:])
    trimmed = "".join(pieces)
    return re.sub(r"\s{2,}", " ", trimmed).strip()


def sanitize_twitter_output(
    text: str,
    *,
    expected_count: int,
    include_hashtags: bool,
) -> str:
    raw_lines = [line for line in text.splitlines()]
    cleaned_lines = _strip_intro_lines(raw_lines)
    normalized_text = "\n".join(cleaned_lines).strip()
    tweets = _extract_candidate_tweets(normalized_text)

    if not tweets:
        return ""

    tweets = tweets[:expected_count]
    final_lines: list[str] = []
    for index, tweet in enumerate(tweets, start=1):
        tweet = _limit_hashtags(tweet, include_hashtags=include_hashtags)
        tweet = re.sub(r"\s{2,}", " ", tweet).strip()
        if tweet:
            final_lines.append(f"Tweet {index}: {tweet}")

    return "\n".join(final_lines).strip()
