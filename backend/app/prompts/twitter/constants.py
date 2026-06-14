from __future__ import annotations

from pathlib import Path

TWITTER_PROMPTS_DIR = Path(__file__).resolve().parent
GENERATION_DIR = TWITTER_PROMPTS_DIR / "generation"
REWRITE_DIR = TWITTER_PROMPTS_DIR / "rewrite"
GENERATED_DIR = TWITTER_PROMPTS_DIR / ".generated"
OPTIMIZED_PROMPT_FILE = GENERATED_DIR / "twitter_optimized_prompt.json"
LEGACY_OPTIMIZED_PROMPT_FILE = TWITTER_PROMPTS_DIR.parent / "optimized_prompt.json"

OUTPUT_EXAMPLES_PREAMBLE = """
OUTPUT EXAMPLES (structure guidance only):
- Use these examples only to mirror structure and pacing.
- Do not copy wording, claims, numbers, or placeholders.
- Write original content from the current brief.
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
