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
        """Write final X/Twitter drafts that feel specific, human, and audience-aware.

        Follow the requested topic, tone, audience, language, and count exactly.
        Treat the reference posts as style anchors for specificity and voice, not as text to copy.
        Follow the quality criteria closely and avoid anything listed in the avoid section.
        Every draft must stay under max_chars and stand on its own.
        If include_hashtags is false, output zero hashtags.
        If include_hashtags is true, use at most two hashtags and only if they feel natural.
        Avoid generic marketing advice, vague motivational lines, filler, and robotic phrasing.
        Return final tweet drafts only. No explanations, no notes, no extra text.
        """

        topic = dspy.InputField(desc="The content topic or brief.")
        tone = dspy.InputField(desc="Desired tone: professional, casual, bold, friendly, or educational.")
        audience = dspy.InputField(desc="The target reader group.")
        language = dspy.InputField(desc="Output language.")
        count = dspy.InputField(desc="Number of tweet drafts to create.")
        max_chars = dspy.InputField(desc="Maximum characters per tweet.")
        include_hashtags = dspy.InputField(desc="Hashtag rule. If false, use zero hashtags. If true, use at most two natural hashtags.")
        reference_posts = dspy.InputField(desc="Style anchors showing the desired specificity, framing, and voice. Learn from them, but do not copy them.")
        quality_criteria = dspy.InputField(desc="Checklist of what a strong output must do. Satisfy these criteria directly.")
        avoid = dspy.InputField(desc="Phrases, patterns, and mistakes that must not appear in the output.")
        tweets = dspy.OutputField(desc="Final tweet drafts only, numbered one per line, with no commentary.")


    class TwitterContentProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate = dspy.Predict(GenerateTwitterPosts)

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
            hashtag_rule = (
                "Hashtags allowed: NO. Use zero hashtags in every draft."
                if not include_hashtags
                else "Hashtags allowed: YES. Use at most two hashtags and only when they feel natural."
            )
            quality_header = (
                "Quality criteria:\n"
                + "\n".join(f"- {item}" for item in quality_criteria)
                + "\n- Make the draft concrete enough that it would not fit every topic."
                + "\n- Mention the audience pain point, decision, trade-off, or use case when helpful."
            )
            avoid_header = (
                "Avoid:\n"
                + "\n".join(f"- {item}" for item in avoid)
                + "\n- generic advice that could apply to any post"
                + "\n- filler openings that restate the topic without insight"
            )
            reference_header = (
                "Reference posts:\n"
                + "\n".join(f"- {item}" for item in reference_posts)
                + "\nUse these as style anchors for specificity and realism. Do not copy wording."
            )
            return self.generate(
                topic=topic,
                tone=tone,
                audience=audience,
                language=language,
                count=str(count),
                max_chars=str(max_chars),
                include_hashtags=hashtag_rule,
                reference_posts=reference_header,
                quality_criteria=quality_header,
                avoid=avoid_header,
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
