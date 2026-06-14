from __future__ import annotations

import json
from typing import Any

from .constants import LEGACY_OPTIMIZED_PROMPT_FILE, OPTIMIZED_PROMPT_FILE


def _artifact_candidates():
    yield OPTIMIZED_PROMPT_FILE
    yield LEGACY_OPTIMIZED_PROMPT_FILE


def load_optimized_prompt_data() -> dict[str, Any] | None:
    for path in _artifact_candidates():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            continue

    return None


def should_use_optimized_prompt(artifact: dict[str, Any] | None) -> bool:
    if artifact is None:
        return False

    score_delta = artifact.get("score_delta")
    if isinstance(score_delta, (int, float)):
        return float(score_delta) > 0.0

    return True


def load_optimized_style_prompt() -> str | None:
    artifact = load_optimized_prompt_data()
    if not should_use_optimized_prompt(artifact) or artifact is None:
        return None

    prompt_versions = artifact.get("prompt_versions")
    if isinstance(prompt_versions, dict):
        style_prompt = prompt_versions.get("optimized_style_prompt")
        if isinstance(style_prompt, str) and style_prompt.strip():
            return style_prompt.strip()

    style_prompt = artifact.get("style_prompt")
    if isinstance(style_prompt, str) and style_prompt.strip():
        return style_prompt.strip()

    return None


def load_legacy_optimized_system_prompt() -> str | None:
    artifact = load_optimized_prompt_data()
    if not should_use_optimized_prompt(artifact) or artifact is None:
        return None

    system_prompt = artifact.get("system_prompt")
    if isinstance(system_prompt, str) and system_prompt.strip():
        return system_prompt.strip()

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
    artifact_path = artifact.get("artifact_path")
    generated_at = artifact.get("generated_at")
    model = artifact.get("model")

    return {
        "prompt_mode": "optimized",
        "prompt_source": str(artifact_path or source or OPTIMIZED_PROMPT_FILE.name),
        "prompt_generated_at": str(generated_at or "unknown"),
        "prompt_model": str(model or "unknown"),
    }
