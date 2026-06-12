from __future__ import annotations

import json
from pathlib import Path

from app.models.twitter import TwitterGenerateRequest

PROMPTS_DIR = Path(__file__).resolve().parent
OPTIMIZED_PROMPT_FILE = PROMPTS_DIR / "optimized_prompt.json"

DEFAULT_SYSTEM_PROMPT = """
You are a senior social media strategist who writes concise, high-signal posts for X/Twitter.
Write content that feels human, specific, useful, and not generic.
Avoid clickbait, exaggerated claims, spammy hashtags, and vague AI buzzwords.
Return only the final tweet drafts. Do not include analysis.
""".strip()

DEFAULT_TWITTER_RULES = """
Rules:
- Each tweet must be under the requested character limit.
- Make every tweet standalone.
- Use clear formatting and line breaks only when useful.
- Do not mention that you are an AI.
- Do not use more than 2 hashtags per tweet.
- Avoid emojis unless the tone naturally fits.
""".strip()


def load_optimized_prompt() -> str | None:
    """Load a GEPA/DSPy optimized prompt if optimize_gepa.py has produced one."""
    if not OPTIMIZED_PROMPT_FILE.exists():
        return None

    try:
        data = json.loads(OPTIMIZED_PROMPT_FILE.read_text(encoding="utf-8"))
        prompt = data.get("system_prompt")
        if isinstance(prompt, str) and prompt.strip():
            return prompt.strip()
    except Exception:
        return None

    return None


def build_system_prompt() -> str:
    optimized_prompt = load_optimized_prompt()

    if optimized_prompt:
        return optimized_prompt

    return f"{DEFAULT_SYSTEM_PROMPT}\n\n{DEFAULT_TWITTER_RULES}"


def build_user_prompt(payload: TwitterGenerateRequest) -> str:
    hashtag_instruction = (
        "Include hashtags only if they help discoverability. Maximum 2 hashtags per tweet."
        if payload.include_hashtags
        else "Do not include hashtags."
    )

    return f"""
Generate {payload.count} X/Twitter post drafts.

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

Output format:
Tweet 1: ...
Tweet 2: ...
Tweet 3: ...

Only return the tweet drafts. Do not explain your reasoning.
""".strip()
