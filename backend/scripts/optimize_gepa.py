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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "app" / "prompts" / "optimized_prompt.json"
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
            "count": 1,
            "max_chars": 280,
            "include_hashtags": True,
        },
        {
            "topic": "Why approval workflows matter before auto-publishing social posts",
            "tone": "educational",
            "audience": "marketing teams",
            "language": "English",
            "count": 1,
            "max_chars": 280,
            "include_hashtags": False,
        },
        {
            "topic": "Cara founder menjaga konsistensi konten tanpa kehilangan kualitas",
            "tone": "friendly",
            "audience": "founder Indonesia",
            "language": "Indonesian",
            "count": 1,
            "max_chars": 280,
            "include_hashtags": True,
        },
        {
            "topic": "Building realtime AI streaming UI with FastAPI and Next.js",
            "tone": "bold",
            "audience": "software developers",
            "language": "English",
            "count": 1,
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


def resolve_dspy_model_name(model: str) -> str:
    return model if "/" in model else f"openai/{model}"


def example_inputs(example: Any) -> dict[str, Any]:
    return {
        "topic": getattr(example, "topic"),
        "tone": getattr(example, "tone"),
        "audience": getattr(example, "audience"),
        "language": getattr(example, "language"),
        "count": int(getattr(example, "count")),
        "max_chars": int(getattr(example, "max_chars")),
        "include_hashtags": bool(getattr(example, "include_hashtags")),
    }


def evaluate_program(program: Any, dataset: list[Any]) -> tuple[float, list[dict[str, Any]]]:
    scores: list[float] = []
    previews: list[dict[str, Any]] = []

    for example in dataset:
        prediction = program(**example_inputs(example))
        score = twitter_quality_metric(example, prediction)
        scores.append(score)
        previews.append(
            {
                "topic": getattr(example, "topic"),
                "score": score,
                "tweets": (getattr(prediction, "tweets", "") or "").strip(),
            }
        )

    average = round(sum(scores) / len(scores), 4) if scores else 0.0
    return average, previews


def build_runtime_prompt() -> str:
    return """
You are an optimized X/Twitter content generator for founders, marketers, and software builders.
Prioritize specificity, usefulness, and clarity. Write natural posts that sound human, not generic.
For every request, produce the requested number of standalone tweet drafts.
Keep each draft under the requested character limit.
Use the requested tone and language.
If hashtags are enabled, use at most two and only when useful.
Return only final tweet drafts. Do not include reasoning or commentary.
""".strip()


def main():
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.getenv("KIMI_MODEL", "openai/gpt-oss-120b")

    if not api_key:
        raise SystemExit("KIMI_API_KEY is missing. Add it to backend/.env first.")

    dspy_model = resolve_dspy_model_name(model)

    # DSPy uses LiteLLM-style provider strings. For OpenAI-compatible providers,
    # we pass the provider route via api_base.
    lm = dspy.LM(
        model=dspy_model,
        api_key=api_key,
        api_base=base_url,
        temperature=0.7,
        max_tokens=900,
    )
    dspy.settings.configure(lm=lm)

    dataset = build_examples()
    trainset = dataset[:3]
    valset = dataset[3:]

    # GEPA is an offline optimizer. Keep max_metric_calls low for this demo.
    # Increase it when you have a better metric + more examples.
    optimizer = dspy.GEPA(
        metric=twitter_quality_metric,
        max_metric_calls=20,
        reflection_lm=lm,
    )

    print(f"==> Provider base URL: {base_url}")
    print(f"==> Runtime model env: {model}")
    print(f"==> DSPy model route: {dspy_model}")
    print(f"==> Train examples: {len(trainset)} | Validation examples: {len(valset)}")
    print("==> Running baseline preview...")
    baseline_score, baseline_previews = evaluate_program(TwitterContentProgram(), valset)
    print(f"==> Baseline validation score: {baseline_score}")
    print("==> Running DSPy GEPA optimization...")
    optimized_program = optimizer.compile(
        student=TwitterContentProgram(),
        trainset=trainset,
        valset=valset,
    )
    optimized_score, optimized_previews = evaluate_program(optimized_program, valset)
    print(f"==> Optimized validation score: {optimized_score}")

    artifact = {
        "source": "DSPy GEPA optimization",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "dspy_model": dspy_model,
        "base_url": base_url,
        "trainset_size": len(trainset),
        "valset_size": len(valset),
        "baseline_validation_score": baseline_score,
        "optimized_validation_score": optimized_score,
        "system_prompt": build_runtime_prompt(),
        "dataset_topics": [getattr(example, "topic") for example in dataset],
        "baseline_preview": baseline_previews,
        "optimized_preview": optimized_previews,
        "how_to_use": [
            "Runtime will automatically load this file through app/prompts/twitter_prompt.py.",
            "Check backend logs for prompt_selected mode=optimized to confirm it is active.",
            "Compare baseline_preview and optimized_preview to study how GEPA changed outputs.",
            "Replace the starter dataset with your own examples to make optimization meaningful.",
        ],
        "note": "This artifact is educational: DSPy optimizes the program internally, while runtime still consumes a stable prompt artifact.",
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            artifact,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"==> Saved optimized prompt artifact to {OUTPUT_PATH}")
    print("==> Done.")


if __name__ == "__main__":
    main()
