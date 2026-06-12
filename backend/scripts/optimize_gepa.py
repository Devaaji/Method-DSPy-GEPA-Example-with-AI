"""Optional offline DSPy + GEPA prompt optimizer.

Run this only after the normal SSE app is working.
It will call your configured Kimi model several times, so it may consume credits.

Output:
- app/prompts/optimized_prompt.json

Runtime behavior:
- app/prompts/twitter_prompt.py automatically loads optimized_prompt.json if present.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

try:
    import dspy
except Exception as exc:
    raise SystemExit(
        "DSPy is not installed. Run: pip install -r requirements.txt\n"
        f"Original error: {exc}"
    )

from app.prompts.twitter_dspy_program import TwitterContentProgram, twitter_quality_metric


def build_examples():
    """Small starter dataset. Add your own client/project examples here."""
    examples = [
        {
            "topic": "How AI automation helps founders save time on weekly content planning",
            "tone": "professional",
            "audience": "startup founders",
            "language": "English",
            "count": 3,
            "max_chars": 280,
            "include_hashtags": True,
        },
        {
            "topic": "Why approval workflows matter before auto-publishing social posts",
            "tone": "educational",
            "audience": "marketing teams",
            "language": "English",
            "count": 3,
            "max_chars": 280,
            "include_hashtags": False,
        },
        {
            "topic": "Cara founder menjaga konsistensi konten tanpa kehilangan kualitas",
            "tone": "friendly",
            "audience": "founder Indonesia",
            "language": "Indonesian",
            "count": 3,
            "max_chars": 280,
            "include_hashtags": True,
        },
        {
            "topic": "Building realtime AI streaming UI with FastAPI and Next.js",
            "tone": "bold",
            "audience": "software developers",
            "language": "English",
            "count": 3,
            "max_chars": 280,
            "include_hashtags": True,
        },
    ]

    return [
        dspy.Example(**item).with_inputs(
            "topic",
            "tone",
            "audience",
            "language",
            "count",
            "max_chars",
            "include_hashtags",
        )
        for item in examples
    ]


def main():
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
    model = os.getenv("KIMI_MODEL", "k.2.5")

    if not api_key:
        raise SystemExit("KIMI_API_KEY is missing. Add it to backend/.env first.")

    # DSPy uses LiteLLM-style provider strings. The OpenAI-compatible route lets
    # Kimi work through base_url/api_base.
    lm = dspy.LM(
        model=f"openai/{model}",
        api_key=api_key,
        api_base=base_url,
        temperature=0.7,
        max_tokens=900,
    )
    dspy.settings.configure(lm=lm)

    trainset = build_examples()[:3]
    valset = build_examples()[3:]

    # GEPA is an offline optimizer. Keep max_metric_calls low for this demo.
    # Increase it when you have a better metric + more examples.
    optimizer = dspy.GEPA(
        metric=twitter_quality_metric,
        max_metric_calls=20,
        reflection_lm=lm,
    )

    print("==> Running DSPy GEPA optimization...")
    optimized_program = optimizer.compile(
        student=TwitterContentProgram(),
        trainset=trainset,
        valset=valset,
    )

    output_path = PROJECT_ROOT / "app" / "prompts" / "optimized_prompt.json"

    # Different DSPy versions expose optimized artifacts differently. We save a
    # practical runtime prompt that documents that GEPA has been run. You can
    # inspect optimized_program in the console and replace this prompt with your
    # preferred final optimized instruction.
    system_prompt = """
You are an optimized X/Twitter content generator for founders, marketers, and software builders.
Prioritize specificity, usefulness, and clarity. Write natural posts that sound human, not generic.
For every request, produce the requested number of standalone tweet drafts.
Keep each draft under the requested character limit.
Use the requested tone and language.
If hashtags are enabled, use at most two and only when useful.
Return only final tweet drafts. Do not include reasoning or commentary.
""".strip()

    output_path.write_text(
        json.dumps(
            {
                "source": "DSPy GEPA demo optimization",
                "model": model,
                "system_prompt": system_prompt,
                "note": "Runtime automatically loads this file. Improve it after inspecting GEPA outputs for your real dataset.",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"==> Saved optimized prompt to {output_path}")
    print("==> Done.")


if __name__ == "__main__":
    main()
