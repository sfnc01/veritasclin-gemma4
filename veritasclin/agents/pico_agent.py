from __future__ import annotations

import re

from veritasclin.schemas.pico import PICOQuestion


class PICOAgent:
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
        population = None
        intervention = None
        outcome = None
        comparison = None
        timeframe = "recent evidence" if re.search(r"\brecent\b|\bcurrent\b", lowered) else None

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
        else:
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


def _phrase_after(text: str, markers: list[str]) -> str | None:
    lowered = text.lower()
    for marker in markers:
        index = lowered.find(marker)
        if index >= 0:
            phrase = text[index + len(marker) :].strip(" ?.")
            return phrase[:120] if phrase else None
    return None
