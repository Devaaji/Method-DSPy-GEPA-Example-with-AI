"""DSPy program definitions for Twitter content generation.

This file is intentionally separated from the runtime SSE service.
DSPy + GEPA is mainly for optimizing prompt/program quality offline.
The SSE endpoint uses the optimized prompt artifact if it exists, then streams
with the selected OpenAI-compatible provider client.
"""

from __future__ import annotations
from typing import Any

try:
    import dspy as _dspy
except Exception:  # pragma: no cover - dspy may be installed later by user
    _dspy = None

dspy: Any = _dspy


if dspy is not None:
    class GenerateTwitterPosts(dspy.Signature):
        """Generate concise, high-quality X/Twitter posts from a topic and constraints."""

        topic = dspy.InputField(desc="The content topic or brief.")
        tone = dspy.InputField(desc="Desired tone: professional, casual, bold, friendly, or educational.")
        audience = dspy.InputField(desc="The target reader group.")
        language = dspy.InputField(desc="Output language.")
        count = dspy.InputField(desc="Number of tweet drafts to create.")
        max_chars = dspy.InputField(desc="Maximum characters per tweet.")
        include_hashtags = dspy.InputField(desc="Whether hashtags are allowed.")
        tweets = dspy.OutputField(desc="Final tweet drafts only, numbered one per line.")


    class TwitterContentProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate = dspy.ChainOfThought(GenerateTwitterPosts)

        def forward(
            self,
            topic: str,
            tone: str,
            audience: str,
            language: str,
            count: int,
            max_chars: int,
            include_hashtags: bool,
        ):
            return self.generate(
                topic=topic,
                tone=tone,
                audience=audience,
                language=language,
                count=str(count),
                max_chars=str(max_chars),
                include_hashtags=str(include_hashtags),
            )


def twitter_quality_metric(example, prediction, trace=None) -> float:
    """Simple metric for GEPA compile examples.

    GEPA needs a metric. This one checks practical Twitter constraints:
    - non-empty result
    - each line is not too long
    - relevant topic words appear
    - not too many hashtags

    You should replace this with a stronger evaluator for production, e.g.
    brand score, engagement score, duplicate detector, safety check, etc.
    """
    text = getattr(prediction, "tweets", "") or ""
    max_chars = int(getattr(example, "max_chars", 280) or 280)
    topic = str(getattr(example, "topic", ""))
    topic_keywords = [word.lower() for word in topic.split() if len(word) > 4][:5]

    if not text.strip():
        return 0.0

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return 0.0

    length_score = sum(1 for line in lines if len(line) <= max_chars) / len(lines)
    hashtag_score = sum(1 for line in lines if line.count("#") <= 2) / len(lines)

    lower_text = text.lower()
    relevance_score = 0.5
    if topic_keywords:
        relevance_score = sum(1 for word in topic_keywords if word in lower_text) / len(topic_keywords)

    return round((0.45 * length_score) + (0.35 * hashtag_score) + (0.20 * relevance_score), 4)
