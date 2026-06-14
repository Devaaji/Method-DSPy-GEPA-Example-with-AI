"""DSPy program definitions for Twitter content generation.

This optimizer mirrors the production prompt architecture:
- `system.md` stays fixed
- `examples.md` stays fixed
- `user.md` stays fixed
- GEPA evolves only `style.md`
"""

from __future__ import annotations

from typing import Any

from app.models.twitter import TwitterGenerateRequest
from app.prompts.scoring import evaluate_twitter_output

from .files import compose_system_prompt
from .render import build_user_prompt

try:
    import dspy as _dspy
except Exception:  # pragma: no cover - dspy may be installed later by user
    _dspy = None

dspy: Any = _dspy


if dspy is not None:
    def build_style_guided_signature(seed_style: str):
        return dspy.Signature(
            {
                "fixed_system": (
                    str,
                    dspy.InputField(
                        desc="Locked system prompt and examples block used in production.",
                    ),
                ),
                "user_message": (
                    str,
                    dspy.InputField(
                        desc="Formatted user prompt derived from the current Twitter request.",
                    ),
                ),
                "tweets": (
                    str,
                    dspy.OutputField(
                        desc="Final tweet drafts only, numbered when requested, with no commentary.",
                    ),
                ),
            },
            instructions=seed_style,
        )


    class TwitterStyleProgram(dspy.Module):
        def __init__(
            self,
            *,
            seed_style: str,
            base_system_prompt: str,
            examples_prompt: str,
        ):
            super().__init__()
            self.generate = dspy.Predict(build_style_guided_signature(seed_style))
            self._base_system_prompt = base_system_prompt
            self._examples_prompt = examples_prompt

        def forward(
            self,
            *,
            topic: str,
            tone: str,
            audience: str,
            language: str,
            count: int,
            max_chars: int,
            include_hashtags: bool,
            **_: Any,
        ):
            payload = TwitterGenerateRequest(
                topic=topic,
                tone=tone,
                audience=audience,
                language=language,
                count=int(count),
                max_chars=int(max_chars),
                include_hashtags=bool(include_hashtags),
            )
            style = str(self.generate.signature.instructions or "").strip()
            fixed_system = compose_system_prompt(
                base_system_prompt=self._base_system_prompt,
                style_prompt=style,
                examples_prompt=self._examples_prompt,
            )

            return self.generate(
                fixed_system=fixed_system,
                user_message=build_user_prompt(payload),
            )


def twitter_quality_metric(example, prediction, trace=None, pred_name=None, pred_trace=None) -> float:
    result = evaluate_twitter_output(example, prediction)
    return float(result["overall_score"])
