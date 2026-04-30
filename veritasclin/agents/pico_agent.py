from __future__ import annotations

import json
import re

from veritasclin.llm import LLMProvider
from veritasclin.llm.prompts import PICO_SYSTEM_PROMPT
from veritasclin.schemas.pico import PICOQuestion


class PICOAgent:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        # If a provider is passed, attempt LLM-backed extraction for unknown topics.
        # The hardcoded templates always take precedence for the 3 demo topics.
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

        # Hardcoded templates for the 3 known demo topics (always preferred)
        population = intervention = comparison = outcome = None
        if "dengue" in lowered:
            population = "adults with suspected or confirmed dengue"
            intervention = "warning signs and clinical indicators"
            outcome = "progression to severe dengue"
        elif "semaglutide" in lowered:
            population = "patients with chronic kidney disease" if "ckd" in lowered else "patients"
            intervention = "semaglutide"
            outcome = "safety, renal outcomes, and studied dosing regimens"
        elif "cannabis" in lowered or "cannabinoid" in lowered:
            population = "adults with neuropathic pain"
            intervention = "medical cannabis or cannabinoids"
            comparison = "placebo or standard care"
            outcome = "pain relief and adverse events"
        elif self._provider is not None:
            # LLM-backed extraction for unknown topics
            population, intervention, comparison, outcome = _llm_extract(
                self._provider, source
            )
        else:
            # Marker-based fallback for unknown topics without a provider
            population = _phrase_after(source, ["in ", "among "])
            intervention = _phrase_after(source, ["about ", "of "])
            outcome = _phrase_after(source, ["for ", "on "])

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
    # Try to extract a JSON object from the LLM response
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _phrase_after(text: str, markers: list[str]) -> str | None:
    lowered = text.lower()
    for marker in markers:
        index = lowered.find(marker)
        if index >= 0:
            phrase = text[index + len(marker) :].strip(" ?.")
            return phrase[:120] if phrase else None
    return None
