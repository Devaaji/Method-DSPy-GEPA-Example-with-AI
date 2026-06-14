"""Optional offline DSPy + GEPA prompt optimizer.

Run this only after the normal SSE app is working.
It will call your configured provider model several times, so it may consume credits.

Output:
- app/prompts/twitter/.generated/twitter_optimized_prompt.json

Runtime behavior:
- app/prompts/twitter/runtime.py automatically loads optimized style guidance if present.
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
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

try:
    import dspy
except Exception as exc:
    raise SystemExit(
        "DSPy is not installed. Run: pip install -r requirements.txt\n"
        f"Original error: {exc}"
    )

from app.prompts.twitter.dspy import TwitterStyleProgram, twitter_quality_metric
from app.prompts.scoring import evaluate_twitter_output
from app.prompts.datasets.gepa_examples import build_examples, build_train_val_examples
from app.prompts.twitter import build_default_style_prompt, build_default_system_prompt, build_system_prompt
from app.prompts.twitter.constants import OPTIMIZED_PROMPT_FILE
from app.prompts.twitter.files import load_generation_prompt_files
from app.core.config import get_settings

OUTPUT_PATH = OPTIMIZED_PROMPT_FILE


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
        "reference_posts": list(getattr(example, "reference_posts", []) or []),
        "quality_criteria": list(getattr(example, "quality_criteria", []) or []),
        "avoid": list(getattr(example, "avoid", []) or []),
        "bad_examples": list(getattr(example, "bad_examples", []) or []),
        "must_include": list(getattr(example, "must_include", []) or []),
        "scoring_rubric": dict(getattr(example, "scoring_rubric", {}) or {}),
        "desired_structure": str(getattr(example, "desired_structure", "") or ""),
        "hook_style": str(getattr(example, "hook_style", "") or ""),
        "content_goal": str(getattr(example, "content_goal", "") or ""),
    }


def evaluate_program(program: Any, dataset: list[Any]) -> tuple[float, list[dict[str, Any]]]:
    scores: list[float] = []
    previews: list[dict[str, Any]] = []

    for example in dataset:
        prediction = program(**example_inputs(example))
        evaluation = evaluate_twitter_output(example, prediction)
        score = float(evaluation["overall_score"])
        scores.append(score)
        previews.append(
            {
                "topic": getattr(example, "topic"),
                "score": score,
                "aspect_scores": evaluation["aspect_scores"],
                "notes": evaluation["notes"],
                "tweet_count": evaluation["tweet_count"],
                "tweets": (getattr(prediction, "tweets", "") or "").strip(),
            }
        )

    average = round(sum(scores) / len(scores), 4) if scores else 0.0
    return average, previews


def build_preview_comparison(
    baseline_previews: list[dict[str, Any]],
    optimized_previews: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    optimized_by_topic = {item["topic"]: item for item in optimized_previews}
    comparisons: list[dict[str, Any]] = []

    for baseline in baseline_previews:
        topic = baseline["topic"]
        optimized = optimized_by_topic.get(topic)
        if optimized is None:
            continue

        aspect_delta = {
            key: round(float(optimized["aspect_scores"].get(key, 0.0)) - float(baseline["aspect_scores"].get(key, 0.0)), 4)
            for key in baseline["aspect_scores"].keys()
        }
        improved_aspects = [key for key, delta in aspect_delta.items() if delta >= 0.03]
        weaker_aspects = [key for key, delta in aspect_delta.items() if delta <= -0.03]
        comparisons.append(
            {
                "topic": topic,
                "baseline_score": baseline["score"],
                "optimized_score": optimized["score"],
                "score_delta": round(float(optimized["score"]) - float(baseline["score"]), 4),
                "aspect_delta": aspect_delta,
                "improved_aspects": improved_aspects,
                "weaker_aspects": weaker_aspects,
                "baseline_tweets": baseline["tweets"],
                "optimized_tweets": optimized["tweets"],
                "baseline_notes": baseline["notes"],
                "optimized_notes": optimized["notes"],
            }
        )

    return comparisons


def build_runtime_prompt() -> str:
    return build_default_system_prompt()


def extract_signature_instructions(program: Any) -> str | None:
    signature = getattr(getattr(program, "generate", None), "signature", None)
    if signature is None:
        try:
            signature = getattr(program.generate.predict, "signature", None)
        except Exception:
            signature = None

    if signature is None:
        return None

    instructions = getattr(signature, "instructions", None)

    if isinstance(instructions, str):
        normalized = instructions.strip()
        return normalized or None

    return None


def build_program() -> Any:
    prompt_files = load_generation_prompt_files()
    return TwitterStyleProgram(
        seed_style=prompt_files["style"],
        base_system_prompt=prompt_files["system"],
        examples_prompt=prompt_files["examples"],
    )


def summarize_prompt_shift(
    baseline_runtime_prompt: str,
    optimized_runtime_prompt: str,
    baseline_dspy_instructions: str | None,
    optimized_dspy_instructions: str | None,
) -> list[str]:
    summary: list[str] = []

    if baseline_runtime_prompt.strip() != optimized_runtime_prompt.strip():
        summary.append("Runtime prompt changed from the built-in default to the saved optimized prompt artifact.")
    else:
        summary.append("Runtime prompt text is unchanged, so score changes come from DSPy program behavior rather than runtime prompt wording.")

    if baseline_dspy_instructions and optimized_dspy_instructions:
        if baseline_dspy_instructions.strip() != optimized_dspy_instructions.strip():
            summary.append("DSPy signature instructions changed during GEPA compile.")
        else:
            summary.append("DSPy signature instructions stayed the same in this run.")

    summary.append("Use the aspect scores and notes to judge why an output is better or worse, not just the final score delta.")
    return summary


def main():
    settings = get_settings()
    provider_name = settings.ai_provider
    api_key = settings.provider_api_key(provider_name)
    base_url = settings.provider_base_url(provider_name)
    model = settings.provider_model(provider_name)
    max_metric_calls = int(os.getenv("GEPA_MAX_METRIC_CALLS", "20"))
    dspy_num_threads = int(os.getenv("DSPY_NUM_THREADS", "1"))

    if not api_key:
        raise SystemExit(
            f"{provider_name.upper()}_API_KEY is missing for the selected provider. "
            "Add it to backend/.env first."
        )

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
    # GEPA can evaluate candidates in parallel internally. For local Ollama runs,
    # a single thread is more stable and avoids thread-pool shutdown issues.
    dspy.settings.configure(lm=lm, num_threads=dspy_num_threads)

    dataset = build_examples(dspy)
    trainset, valset = build_train_val_examples(dspy)

    # GEPA is an offline optimizer. Keep max_metric_calls low for this demo.
    # Increase it when you have a better metric + more examples.
    optimizer = dspy.GEPA(
        metric=twitter_quality_metric,
        max_metric_calls=max_metric_calls,
        reflection_lm=lm,
    )

    print(f"==> Provider: {provider_name}")
    print(f"==> Provider base URL: {base_url}")
    print(f"==> Runtime model env: {model}")
    print(f"==> DSPy model route: {dspy_model}")
    print(f"==> DSPy num threads: {dspy_num_threads}")
    print(f"==> Max metric calls: {max_metric_calls}")
    print(f"==> Train examples: {len(trainset)} | Validation examples: {len(valset)}")
    print("==> Running baseline preview...")
    baseline_program = build_program()
    baseline_score, baseline_previews = evaluate_program(baseline_program, valset)
    print(f"==> Baseline validation score: {baseline_score}")
    print("==> Running DSPy GEPA optimization...")
    optimized_program = optimizer.compile(
        student=build_program(),
        trainset=trainset,
        valset=valset,
    )
    optimized_score, optimized_previews = evaluate_program(optimized_program, valset)
    print(f"==> Optimized validation score: {optimized_score}")
    comparisons = build_preview_comparison(baseline_previews, optimized_previews)
    baseline_style_prompt = build_default_style_prompt()
    optimized_style_prompt = extract_signature_instructions(optimized_program) or baseline_style_prompt
    baseline_runtime_prompt = build_runtime_prompt()
    optimized_runtime_prompt = build_system_prompt(style_override=optimized_style_prompt)
    baseline_dspy_instructions = extract_signature_instructions(baseline_program)
    optimized_dspy_instructions = optimized_style_prompt
    prompt_change_summary = summarize_prompt_shift(
        baseline_runtime_prompt,
        optimized_runtime_prompt,
        baseline_dspy_instructions,
        optimized_dspy_instructions,
    )

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
        "score_delta": round(optimized_score - baseline_score, 4),
        "score_weights": {
            "relevance": 0.20,
            "hook": 0.18,
            "clarity": 0.16,
            "naturalness": 0.15,
            "constraint_fit": 0.14,
            "reference_fit": 0.10,
            "avoidance": 0.07,
        },
        "system_prompt": optimized_runtime_prompt,
        "style_prompt": optimized_style_prompt,
        "prompt_versions": {
            "baseline_runtime_prompt": baseline_runtime_prompt,
            "optimized_runtime_prompt": optimized_runtime_prompt,
            "baseline_style_prompt": baseline_style_prompt,
            "optimized_style_prompt": optimized_style_prompt,
            "baseline_dspy_instructions": baseline_dspy_instructions,
            "optimized_dspy_instructions": optimized_dspy_instructions,
        },
        "prompt_change_summary": prompt_change_summary,
        "dataset_topics": [getattr(example, "topic") for example in dataset],
        "baseline_preview": baseline_previews,
        "optimized_preview": optimized_previews,
        "comparison_preview": comparisons,
        "how_to_use": [
            "Runtime will automatically load the optimized style prompt through app/prompts/twitter/runtime.py.",
            "Check backend logs for prompt_selected mode=optimized to confirm it is active.",
            "Compare baseline_preview and optimized_preview to study how GEPA changed outputs.",
            "Replace the starter dataset with your own examples to make optimization meaningful.",
        ],
        "note": "This artifact is educational: DSPy optimizes only the style layer, while runtime composes system + examples + style into a stable prompt.",
        "how_to_judge": [
            "Check baseline_runtime_prompt vs optimized_runtime_prompt to see what text the app used before and after optimization.",
            "Check baseline_style_prompt vs optimized_style_prompt to see exactly how GEPA changed the style layer.",
            "Check baseline_dspy_instructions vs optimized_dspy_instructions to see whether GEPA changed the DSPy style instructions.",
            "If optimized_validation_score is higher, the new version performed better on the validation examples in this run.",
            "Read aspect scores and notes to understand whether the gain comes from hook, clarity, relevance, naturalness, or constraint fit.",
            "Check whether reference_fit and avoidance improved, because those now capture style guidance from the dataset.",
            "A prompt can score lower overall even if one aspect improved, so judge by both total score and aspect-level tradeoffs.",
        ],
        "scoring_guide": {
            "hook": "How strong the opening angle is for grabbing attention.",
            "clarity": "How easy the draft is to read and skim quickly.",
            "relevance": "How well the draft stays on-topic and speaks to the audience.",
            "naturalness": "How human and non-generic the wording feels.",
            "constraint_fit": "How well the draft obeys tweet length and hashtag rules.",
            "reference_fit": "How closely the draft matches the specificity and voice shown in the dataset reference posts.",
            "avoidance": "How well the draft avoids banned patterns like hype, filler, or overused formatting.",
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
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
