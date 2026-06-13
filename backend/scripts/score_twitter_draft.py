"""Score one manual Twitter/X draft with the same evaluator used by GEPA.

Usage:
    .venv/bin/python scripts/score_twitter_draft.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.prompts.scoring import evaluate_twitter_output


def score_example(
    *,
    topic: str,
    audience: str,
    max_chars: int,
    include_hashtags: bool,
    tweets: str,
) -> dict:
    example = SimpleNamespace(
        topic=topic,
        audience=audience,
        max_chars=max_chars,
        include_hashtags=include_hashtags,
    )
    prediction = SimpleNamespace(tweets=tweets)
    return evaluate_twitter_output(example, prediction)


def main() -> None:
    topic = "Building realtime AI streaming UI with FastAPI and Next.js"
    audience = "software developers and startup founders"

    before = """
Tweet 1: Unlock the power of AI with this revolutionary FastAPI and Next.js setup for realtime streaming. It is game-changing, seamless, and amazing for everyone building apps today! #AI #FastAPI #NextJS #Realtime
""".strip()

    after = """
Tweet 1: Most realtime AI demos feel smooth until the stream breaks under real user traffic.
Tweet 2: FastAPI handles the token stream well. Next.js makes the UI feel instant. The hard part is designing retries, loading states, and partial output that still feels trustworthy.
""".strip()

    result = {
        "topic": topic,
        "audience": audience,
        "before": {
            "tweets": before,
            "evaluation": score_example(
                topic=topic,
                audience=audience,
                max_chars=280,
                include_hashtags=True,
                tweets=before,
            ),
        },
        "after": {
            "tweets": after,
            "evaluation": score_example(
                topic=topic,
                audience=audience,
                max_chars=280,
                include_hashtags=True,
                tweets=after,
            ),
        },
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
