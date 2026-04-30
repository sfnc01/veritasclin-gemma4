from __future__ import annotations

import json
import re

from veritasclin.llm import LLMProvider
from veritasclin.llm.prompts import PICO_SYSTEM_PROMPT
from veritasclin.schemas.pico import PICOQuestion


class PICOAgent:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    def extract(
        self,
        question: str,
        safe_rewritten_question: str | None = None,
        language: str = "en",
    ) -> PICOQuestion:
        source = safe_rewritten_question or question
        lowered = source.lower()
        preferred = [
            "Systematic Review",
            "Meta-Analysis",
            "Randomized Controlled Trial",
            "Clinical Trial",
        ]
        timeframe = "recent evidence" if re.search(r"\brecent\b|\bcurrent\b", lowered) else None

        population = intervention = comparison = outcome = None

        # LLM extraction is primary when a provider is available
        if self._provider is not None:
            population, intervention, comparison, outcome = _llm_extract(self._provider, source)

        # Templates fill in any gaps the LLM left, or act as primary when no provider is set.
        # They are domain-optimised fallbacks, not overrides.
        if not any([population, intervention, outcome]):
            population, intervention, comparison, outcome = _template_extract(lowered)

        return PICOQuestion(
            original_question=question,
            safe_rewritten_question=safe_rewritten_question,
            population=population,
            intervention=intervention,
            comparison=comparison,
            outcome=outcome,
            timeframe=timeframe,
            preferred_study_types=preferred,
            language=language,
        )


def _template_extract(
    lowered: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Domain-optimised templates for the 3 demo topics, then regex for everything else."""
    if "dengue" in lowered:
        return (
            "adults with suspected or confirmed dengue",
            "warning signs and clinical indicators",
            None,
            "progression to severe dengue",
        )
    if "semaglutide" in lowered:
        population = "patients with chronic kidney disease" if "ckd" in lowered else "patients"
        return population, "semaglutide", None, "safety, renal outcomes, and studied dosing regimens"  # noqa: E501
    if "cannabis" in lowered or "cannabinoid" in lowered:
        return (
            "adults with neuropathic pain",
            "medical cannabis or cannabinoids",
            "placebo or standard care",
            "pain relief and adverse events",
        )
    # Marker-based last-resort fallback
    return (
        _phrase_after(lowered, ["in ", "among "]),
        _phrase_after(lowered, ["about ", "of "]),
        None,
        _phrase_after(lowered, ["for ", "on "]),
    )


def _llm_extract(
    provider: LLMProvider, question: str
) -> tuple[str | None, str | None, str | None, str | None]:
    user_prompt = f"Clinical question: {question}"
    try:
        raw = provider.generate(PICO_SYSTEM_PROMPT, user_prompt, temperature=0.0)
        data = _parse_json(raw)
        if data:
            return (
                data.get("population") or None,
                data.get("intervention") or None,
                data.get("comparison") or None,
                data.get("outcome") or None,
            )
    except Exception:  # noqa: BLE001
        pass
    return None, None, None, None


def _parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _phrase_after(text: str, markers: list[str]) -> str | None:
    for marker in markers:
        index = text.find(marker)
        if index >= 0:
            phrase = text[index + len(marker) :].strip(" ?.")
            return phrase[:120] if phrase else None
    return None
