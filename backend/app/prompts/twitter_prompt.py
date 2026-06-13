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

TECH_TOPIC_KEYWORDS = (
    "ai",
    "startup",
    "saas",
    "software",
    "developer",
    "developers",
    "coding",
    "code",
    "programming",
    "api",
    "fastapi",
    "next.js",
    "nextjs",
    "cloud",
    "automation",
    "product",
    "tech",
    "teknologi",
)


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


def topic_is_tech_related(topic: str) -> bool:
    normalized = topic.lower()
    return any(keyword in normalized for keyword in TECH_TOPIC_KEYWORDS)


def build_topic_angle_instruction(payload: TwitterGenerateRequest) -> str:
    if topic_is_tech_related(payload.topic):
        if payload.audience:
            return f"Make the draft relevant to {payload.audience} without sounding forced."
        return "If the topic is tech-related, keep it useful and grounded without forcing a niche persona."

    return (
        "Do not mention startup, software, SaaS, product, AI, app, founder, or developer angles unless the topic itself clearly talks about them."
    )


def build_language_style_instruction(payload: TwitterGenerateRequest) -> str:
    if payload.language == "Indonesian":
        return (
            "Use natural everyday Indonesian like a real person posting on X. "
            "Prefer short, direct, conversational sentences. Avoid stiff formal wording."
        )
    return "Use natural everyday English like a real person posting on X."


def build_audience_section(payload: TwitterGenerateRequest) -> str:
    if topic_is_tech_related(payload.topic) and payload.audience:
        return f"Audience:\n{payload.audience}"

    if payload.language == "Indonesian":
        return (
            "Audience:\n"
            "Pembaca X pada umumnya. Fokus utama tetap ke topik asli dan cara ngomong yang natural."
        )

    return (
        "Audience:\n"
        "General X readers. Keep the focus on the original topic rather than a niche audience angle."
    )


def build_tone_section(payload: TwitterGenerateRequest) -> str:
    if payload.tone:
        return f"Tone:\n{payload.tone}"

    if payload.language == "Indonesian":
        return "Tone:\nnatural, conversational, and human"

    return "Tone:\nnatural, conversational, and human"


def build_user_prompt(payload: TwitterGenerateRequest) -> str:
    hashtag_instruction = "Do not include hashtags."
    if payload.include_hashtags:
        hashtag_instruction = (
            "Prefer no hashtags. Only add up to 2 hashtags if they feel genuinely natural."
            if not topic_is_tech_related(payload.topic)
            else "Include hashtags only if they help discoverability. Maximum 2 hashtags per tweet."
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

{build_audience_section(payload)}

{build_tone_section(payload)}

Language:
{payload.language}

Character limit:
Maximum {payload.max_chars} characters per tweet.

Hashtag instruction:
{hashtag_instruction}

Quality requirements:
- Write exactly {payload.count} draft(s).
- Start with a clear hook, tension, or concrete insight.
- {build_topic_angle_instruction(payload)}
- Keep the core topic intact. Do not force it into startup, SaaS, crypto, AI, or software angles unless the topic itself is about that.
- If the topic is a reaction, opinion, or public statement, write it as a natural reaction or opinion.
- {build_language_style_instruction(payload)}
- Avoid generic lines like "unlock the power", "game-changing", or "revolutionary".
- Avoid corporate jargon, motivational fluff, or awkward metaphors.
- Make each draft useful enough that a real person could post it without editing.

{output_format}

Only return the tweet drafts. Do not explain your reasoning.
""".strip()


def build_rewrite_system_prompt() -> str:
    return """
You are a sharp social media editor.
Rewrite drafts so they sound like a real human wrote them.
Keep the original topic and intent.
Do not force startup, AI, crypto, or software angles into unrelated topics.
Avoid corporate jargon, generic inspiration, weird metaphors, and cheesy phrasing.
Return only the final tweet drafts in the requested format.
""".strip()


def build_rewrite_user_prompt(payload: TwitterGenerateRequest, draft_text: str) -> str:
    hashtag_instruction = "Remove all hashtags."
    if payload.include_hashtags:
        hashtag_instruction = (
            "Prefer no hashtags. Keep at most 1 hashtag only if it feels genuinely natural."
            if not topic_is_tech_related(payload.topic)
            else "Keep at most 2 hashtags only if they genuinely help."
        )
    return f"""
Rewrite the draft below so it sounds natural and postable.

Original topic:
{payload.topic}

{build_audience_section(payload)}

{build_tone_section(payload)}

Language:
{payload.language}

Requirements:
- Return exactly {payload.count} draft(s), nothing else.
- Keep the meaning close to the topic. Do not invent a new angle.
- If the topic is not about technology, do not turn it into a tech lesson.
- Write like a person reacting or sharing a thought, not like a seminar, press release, or LinkedIn guru.
- {build_topic_angle_instruction(payload)}
- {build_language_style_instruction(payload)}
- Mirror the vibe of the original brief when useful. If the brief sounds spontaneous, keep that spontaneous feel.
- Keep each draft under {payload.max_chars} characters.
- {hashtag_instruction}
- No intro, no explanation, no quotation marks around the full tweet unless truly needed.
- Avoid words like "implementasi", "inovasi", "optimalisasi", "ekosistem", or other stiff consultant language unless the original topic truly needs them.
- Avoid emojis unless the original brief clearly calls for them.

Good style target:
Tweet 1: Jujur, kalimat itu kedengeran simpel, tapi makin dipikir malah bikin miris.
Tweet 2: Yang aneh bukan cuma ucapannya, tapi cara mikir di baliknya.
Tweet 3: Agak kocak kedengerannya, tapi kalau dipikir pelan-pelan justru bikin nggak tenang.

Bad style to avoid:
Tweet 1: Aplikasi startup dan teknologi desentralisasi mengajarkan kita tentang implementasi kebijakan.
Tweet 2: Inovasi digital menjadi refleksi ekosistem yang perlu dioptimalkan.

Draft to rewrite:
{draft_text}
""".strip()
