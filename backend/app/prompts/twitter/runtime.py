from __future__ import annotations

from .artifacts import load_legacy_optimized_system_prompt, load_optimized_style_prompt
from .files import compose_system_prompt, load_generation_prompt_files, load_rewrite_prompt_files
from .render import build_rewrite_user_prompt, build_user_prompt


def build_default_system_prompt() -> str:
    prompt_files = load_generation_prompt_files()
    return compose_system_prompt(
        base_system_prompt=prompt_files["system"],
        style_prompt=prompt_files["style"],
        examples_prompt=prompt_files["examples"],
    )


def build_system_prompt(*, style_override: str | None = None) -> str:
    prompt_files = load_generation_prompt_files()
    if style_override is not None:
        return compose_system_prompt(
            base_system_prompt=prompt_files["system"],
            style_prompt=style_override,
            examples_prompt=prompt_files["examples"],
        )

    optimized_style = load_optimized_style_prompt()
    if optimized_style:
        return compose_system_prompt(
            base_system_prompt=prompt_files["system"],
            style_prompt=optimized_style,
            examples_prompt=prompt_files["examples"],
        )

    legacy_system_prompt = load_legacy_optimized_system_prompt()
    if legacy_system_prompt:
        return legacy_system_prompt

    return compose_system_prompt(
        base_system_prompt=prompt_files["system"],
        style_prompt=prompt_files["style"],
        examples_prompt=prompt_files["examples"],
    )


def build_default_style_prompt() -> str:
    return load_generation_prompt_files()["style"]


def build_rewrite_system_prompt() -> str:
    return load_rewrite_prompt_files()["system"]


__all__ = [
    "build_default_style_prompt",
    "build_default_system_prompt",
    "build_rewrite_system_prompt",
    "build_rewrite_user_prompt",
    "build_system_prompt",
    "build_user_prompt",
]
