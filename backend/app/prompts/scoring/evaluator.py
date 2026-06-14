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

META_OUTPUT_PATTERNS = (
    "tidak ada tweet",
    "no tweet",
    "sesuai request",
    "sesuai permintaan",
    "request menggunakan",
    "hashtags allowed",
    "hashtag no",
    "quality criteria",
    "output exactly",
    "include_hashtags",
)


def _extract_mapping(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(key).strip(): str(item).strip() for key, item in value.items() if str(key).strip() and str(item).strip()}
    return {}


def _keyword_overlap_score(text: str, phrases: list[str]) -> float:
    if not phrases:
        return 1.0
    hits = 0
    for phrase in phrases:
        normalized = phrase.lower().strip()
        if not normalized:
            continue
        if normalized in text:
            hits += 1
            continue
        phrase_keywords = [word for word in normalized.split() if len(word) >= 4]
        if phrase_keywords and sum(1 for word in phrase_keywords if word in text) >= min(2, len(phrase_keywords)):
            hits += 1
    return hits / max(len(phrases), 1)


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
    bad_examples = extract_list(getattr(example, "bad_examples", []))
    must_include = extract_list(getattr(example, "must_include", []))
    desired_structure = str(getattr(example, "desired_structure", "") or "")
    hook_style = str(getattr(example, "hook_style", "") or "")
    content_goal = str(getattr(example, "content_goal", "") or "")
    scoring_rubric = _extract_mapping(getattr(example, "scoring_rubric", {}))
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

    guidance_penalty = 1.0
    combined_text = " ".join(tweets).lower()

    bad_example_overlap = _keyword_overlap_score(combined_text, bad_examples)
    if bad_examples and bad_example_overlap >= 0.45:
        criteria_notes.append("The draft resembles the bad examples more than it should.")
        guidance_penalty -= min(0.18 * bad_example_overlap, 0.22)

    must_include_overlap = _keyword_overlap_score(combined_text, must_include)
    if must_include and must_include_overlap < 0.5:
        criteria_notes.append("The draft misses too many ideas from the must_include guidance.")
        guidance_penalty -= min(0.12 * (1.0 - must_include_overlap), 0.14)

    if desired_structure:
        desired_lower = desired_structure.lower()
        if "zero hashtags" in desired_lower and "#" in combined_text:
            criteria_notes.append("The draft breaks the desired structure by using hashtags when the structure says not to.")
            guidance_penalty -= 0.08
        if "standalone" in desired_lower and any(tweet.lower().startswith(("1/", "2/", "3/")) for tweet in tweets):
            criteria_notes.append("The draft breaks the desired structure by looking like a thread instead of standalone posts.")
            guidance_penalty -= 0.08

    if hook_style and hook < 0.72:
        criteria_notes.append("The opening does not yet match the requested hook style strongly enough.")
        guidance_penalty -= 0.04

    if content_goal:
        goal_overlap = _keyword_overlap_score(combined_text, [content_goal])
        if goal_overlap < 0.34:
            criteria_notes.append("The draft does not fully serve the stated content goal.")
            guidance_penalty -= 0.06

    if scoring_rubric:
        rubric_text = " ".join(f"{key} {value}".lower() for key, value in scoring_rubric.items())
        if "specific" in rubric_text and reference_fit < 0.4:
            criteria_notes.append("The draft falls short of the specificity bar in the scoring rubric.")
            guidance_penalty -= 0.05
        if "audience" in rubric_text and relevance < 0.5:
            criteria_notes.append("The draft falls short of the audience-fit bar in the scoring rubric.")
            guidance_penalty -= 0.05
        if "clarity" in rubric_text and clarity < 0.75:
            criteria_notes.append("The draft falls short of the clarity bar in the scoring rubric.")
            guidance_penalty -= 0.04

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
    if any(pattern in combined_text for pattern in META_OUTPUT_PATTERNS):
        overall_score = round(overall_score * 0.6, 4)
        criteria_notes.append("The draft leaks internal instructions or placeholder text instead of acting like a real post.")

    overall_score = round(overall_score * max(guidance_penalty, 0.55), 4)

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
