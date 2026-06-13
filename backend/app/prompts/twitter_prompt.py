from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.twitter import TwitterGenerateRequest

PROMPTS_DIR = Path(__file__).resolve().parent
OPTIMIZED_PROMPT_FILE = PROMPTS_DIR / "optimized_prompt.json"

DEFAULT_SYSTEM_PROMPT = """
You are a senior social media strategist who writes concise, high-signal posts for X/Twitter.
Write content that feels human, specific, useful, and non-generic.
Lead with one sharp idea, tension, lesson, or contrarian observation.
Make each draft feel written for the stated audience, not for everyone.
Avoid clickbait, exaggerated claims, spammy hashtags, vague AI buzzwords, and generic marketing language.
Return only the final tweet drafts. Do not include analysis.
""".strip()

DEFAULT_TWITTER_RULES = """
Rules:
- Output exactly the requested number of drafts. No more, no less.
- Each tweet must be under the requested character limit.
- Make every tweet standalone.
- Each tweet should contain one concrete takeaway, opinion, or insight.
- Mention the audience context or pain point when it helps relevance.
- Use clear formatting and line breaks only when useful.
- Do not mention that you are an AI.
- Do not use more than 2 hashtags per tweet.
- Avoid emojis unless the tone naturally fits.
""".strip()


def build_default_system_prompt() -> str:
    return f"{DEFAULT_SYSTEM_PROMPT}\n\n{DEFAULT_TWITTER_RULES}"


def load_optimized_prompt_data() -> dict[str, Any] | None:
    """Load the GEPA/DSPy optimization artifact if it exists and is valid."""
    if not OPTIMIZED_PROMPT_FILE.exists():
        return None

    try:
        data = json.loads(OPTIMIZED_PROMPT_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            prompt = data.get("system_prompt")
            if isinstance(prompt, str) and prompt.strip():
                return data
    except Exception:
        return None

    return None


def should_use_optimized_prompt(artifact: dict[str, Any] | None) -> bool:
    if artifact is None:
        return False

    score_delta = artifact.get("score_delta")
    if isinstance(score_delta, (int, float)):
        return float(score_delta) > 0.0

    return True


def load_optimized_prompt() -> str | None:
    artifact = load_optimized_prompt_data()
    if not should_use_optimized_prompt(artifact):
        return None
    if artifact is None:
        return None

    prompt = artifact.get("system_prompt")
    if isinstance(prompt, str) and prompt.strip():
        return prompt.strip()

    return None


def get_prompt_metadata() -> dict[str, str]:
    artifact = load_optimized_prompt_data()
    if artifact is None:
        return {"prompt_mode": "default", "prompt_source": "built_in"}

    if not should_use_optimized_prompt(artifact):
        return {
            "prompt_mode": "default",
            "prompt_source": "built_in",
            "prompt_fallback_reason": "optimized_artifact_has_no_score_gain",
        }

    source = artifact.get("source")
    generated_at = artifact.get("generated_at")
    model = artifact.get("model")

    return {
        "prompt_mode": "optimized",
        "prompt_source": str(source or "optimized_prompt.json"),
        "prompt_generated_at": str(generated_at or "unknown"),
        "prompt_model": str(model or "unknown"),
    }


def build_system_prompt() -> str:
    optimized_prompt = load_optimized_prompt()

    if optimized_prompt:
        return optimized_prompt

    return build_default_system_prompt()


def build_user_prompt(payload: TwitterGenerateRequest) -> str:
    hashtag_instruction = (
        "Include hashtags only if they help discoverability. Maximum 2 hashtags per tweet."
        if payload.include_hashtags
        else "Do not include hashtags."
    )
    draft_noun = "draft" if payload.count == 1 else "drafts"
    output_format = (
        "Output format:\nTweet 1: ..."
        if payload.count == 1
        else "Output format:\nTweet 1: ...\nTweet 2: ...\nTweet 3: ..."
    )

    return f"""
Generate {payload.count} X/Twitter post {draft_noun}.

Topic:
{payload.topic}

Audience:
{payload.audience}

Tone:
{payload.tone}

Language:
{payload.language}

Character limit:
Maximum {payload.max_chars} characters per tweet.

Hashtag instruction:
{hashtag_instruction}

Quality requirements:
- Write exactly {payload.count} draft(s).
- Start with a clear hook, tension, or concrete insight.
- Make the draft feel relevant to {payload.audience}.
- Avoid generic lines like "unlock the power", "game-changing", or "revolutionary".
- Make each draft useful enough that a real person could post it without editing.

{output_format}

Only return the tweet drafts. Do not explain your reasoning.
""".strip()
