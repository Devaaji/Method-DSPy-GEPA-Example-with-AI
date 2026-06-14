from __future__ import annotations

from typing import Any

from .avoidance import score_avoidance
from .clarity import score_clarity
from .constraints import score_constraints
from .hook import score_hook
from .naturalness import score_naturalness
from .reference_fit import score_reference_alignment
from .relevance import score_relevance
from .utils import extract_list, extract_tweets


def evaluate_twitter_output(example: Any, prediction: Any) -> dict[str, Any]:
    text = (getattr(prediction, "tweets", "") or "").strip()
    topic = str(getattr(example, "topic", ""))
    audience = str(getattr(example, "audience", ""))
    max_chars = int(getattr(example, "max_chars", 280) or 280)
    expected_count = int(getattr(example, "count", 1) or 1)
    include_hashtags = bool(getattr(example, "include_hashtags", True))
    reference_posts = extract_list(getattr(example, "reference_posts", []))
    quality_criteria = extract_list(getattr(example, "quality_criteria", []))
    avoid = extract_list(getattr(example, "avoid", []))
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
                "reference_fit": 0.0,
                "avoidance": 0.0,
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
    reference_fit, reference_notes = score_reference_alignment(tweets, reference_posts)
    avoidance, avoidance_notes = score_avoidance(tweets, avoid)

    criteria_notes: list[str] = []
    if quality_criteria:
        criteria_text = " ".join(item.lower() for item in quality_criteria)
        if "specific" in criteria_text and relevance < 0.55:
            criteria_notes.append("The draft needs more concrete specificity to match the quality criteria.")
        if "natural" in criteria_text and naturalness < 0.75:
            criteria_notes.append("The draft does not fully meet the naturalness bar described in the quality criteria.")
        if ("clear" in criteria_text or "skim" in criteria_text) and clarity < 0.72:
            criteria_notes.append("The draft falls short of the clarity bar described in the quality criteria.")
        if ("lead" in criteria_text or "hook" in criteria_text or "tension" in criteria_text) and hook < 0.7:
            criteria_notes.append("The opening does not yet meet the hook standard described in the quality criteria.")

    overall_score = round(
        (0.20 * relevance)
        + (0.18 * hook)
        + (0.16 * clarity)
        + (0.15 * naturalness)
        + (0.14 * constraint_fit)
        + (0.10 * reference_fit)
        + (0.07 * avoidance),
        4,
    )

    notes = [
        *constraint_notes,
        *relevance_notes,
        *clarity_notes,
        *hook_notes,
        *naturalness_notes,
        *reference_notes,
        *avoidance_notes,
        *criteria_notes,
    ]
    deduped_notes = list(dict.fromkeys(notes))

    return {
        "overall_score": overall_score,
        "aspect_scores": {
            "hook": hook,
            "clarity": clarity,
            "relevance": relevance,
            "naturalness": naturalness,
            "constraint_fit": constraint_fit,
            "reference_fit": reference_fit,
            "avoidance": avoidance,
        },
        "tweet_count": len(tweets),
        "tweets": tweets,
        "notes": deduped_notes,
    }
