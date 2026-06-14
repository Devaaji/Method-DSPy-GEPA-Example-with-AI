"""DSPy program definitions for Twitter content generation.

This file is intentionally separated from the runtime SSE service.
DSPy + GEPA is mainly for optimizing prompt/program quality offline.
The SSE endpoint uses the optimized prompt artifact if it exists, then streams
with the selected OpenAI-compatible provider client.
"""

from __future__ import annotations
from typing import Any

from app.prompts.scoring import evaluate_twitter_output

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
        reference_posts = dspy.InputField(desc="A few short reference posts that show the desired level of specificity and voice.")
        quality_criteria = dspy.InputField(desc="Quality checklist for what a strong output should do.")
        avoid = dspy.InputField(desc="Phrases, patterns, or mistakes the output should avoid.")
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
            reference_posts: list[str],
            quality_criteria: list[str],
            avoid: list[str],
        ):
            return self.generate(
                topic=topic,
                tone=tone,
                audience=audience,
                language=language,
                count=str(count),
                max_chars=str(max_chars),
                include_hashtags=str(include_hashtags),
                reference_posts="\n".join(f"- {item}" for item in reference_posts),
                quality_criteria="\n".join(f"- {item}" for item in quality_criteria),
                avoid="\n".join(f"- {item}" for item in avoid),
            )


def twitter_quality_metric(example, prediction, trace=None, pred_name=None, pred_trace=None) -> float:
    """Simple metric for GEPA compile examples.

    GEPA needs a metric. This one checks practical Twitter constraints:
    - non-empty result
    - each line is not too long
    - relevant topic words appear
    - not too many hashtags

    This signature matches newer DSPy GEPA versions that pass five arguments.

    You should replace this with a stronger evaluator for production, e.g.
    brand score, engagement score, duplicate detector, safety check, etc.
    """
    result = evaluate_twitter_output(example, prediction)
    return float(result["overall_score"])
