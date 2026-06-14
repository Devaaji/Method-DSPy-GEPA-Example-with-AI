from __future__ import annotations

from pathlib import Path

from .constants import GENERATION_DIR, OUTPUT_EXAMPLES_PREAMBLE, REWRITE_DIR


def load_prompt_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Missing prompt file: {path}")
    return path.read_text(encoding="utf-8").strip()


def load_generation_prompt_files() -> dict[str, str]:
    return {
        "system": load_prompt_file(GENERATION_DIR / "system.md"),
        "style": load_prompt_file(GENERATION_DIR / "style.md"),
        "examples": load_prompt_file(GENERATION_DIR / "examples.md"),
        "user": load_prompt_file(GENERATION_DIR / "user.md"),
    }


def load_rewrite_prompt_files() -> dict[str, str]:
    return {
        "system": load_prompt_file(REWRITE_DIR / "system.md"),
        "user": load_prompt_file(REWRITE_DIR / "user.md"),
    }


def compose_system_prompt(
    *,
    base_system_prompt: str,
    style_prompt: str | None = None,
    examples_prompt: str | None = None,
) -> str:
    parts = [base_system_prompt.strip()]
    examples = str(examples_prompt or "").strip()
    style = str(style_prompt or "").strip()

    if examples:
        parts.append(f"{OUTPUT_EXAMPLES_PREAMBLE}\n\nEXAMPLES:\n{examples}")
    if style:
        parts.append(f"STYLE GUIDANCE:\n{style}")

    return "\n\n".join(part for part in parts if part).strip()
