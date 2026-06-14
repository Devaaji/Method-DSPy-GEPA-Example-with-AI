from __future__ import annotations

import re
from typing import Any


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


def extract_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []
