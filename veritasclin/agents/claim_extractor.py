from __future__ import annotations

import json
import re

from veritasclin.llm.base import LLMProvider, LLMProviderError
from veritasclin.llm.prompts import CLAIM_EXTRACTION_SYSTEM_PROMPT
from veritasclin.schemas.claims import Claim


class ClaimExtractor:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    def extract(self, text: str) -> list[Claim]:
        if self._provider is not None:
            llm_claims = self._llm_extract(text)
            if llm_claims:
                return llm_claims
        return self._regex_extract(text)

    def _llm_extract(self, text: str) -> list[Claim]:
        try:
            raw = self._provider.generate(
                CLAIM_EXTRACTION_SYSTEM_PROMPT,
                f"Synthesis text:\n{text}",
                temperature=0.0,
            )
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if not match:
                return []
            sentences = json.loads(match.group(0))
            if not isinstance(sentences, list):
                return []
            claims = []
            for i, sentence in enumerate(sentences, start=1):
                if isinstance(sentence, str) and len(sentence.strip()) > 20:
                    pmids = _extract_pmids(sentence)
                    claims.append(
                        Claim(
                            id=f"C{i:03d}",
                            text=sentence.strip(),
                            claim_type=_claim_type(sentence),
                            support_status="uncertain",
                            pmids=pmids,
                            evidence_level="uncertain",
                            risk_level=_risk_level(sentence),
                            rationale="Extracted by LLM as a verifiable clinical assertion.",
                            limitation_note=None,
                        )
                    )
            return claims
        except (LLMProviderError, json.JSONDecodeError, ValueError):
            return []

    def _regex_extract(self, text: str) -> list[Claim]:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", text)
            if len(s.strip()) > 35
        ]
        claims = []
        for i, sentence in enumerate(sentences, start=1):
            pmids = _extract_pmids(sentence)
            claims.append(
                Claim(
                    id=f"C{i:03d}",
                    text=sentence,
                    claim_type=_claim_type(sentence),
                    support_status="uncertain",
                    pmids=pmids,
                    evidence_level="uncertain",
                    risk_level=_risk_level(sentence),
                    rationale="Extracted from generated synthesis for verification.",
                    limitation_note=None,
                )
            )
        return claims


def _extract_pmids(text: str) -> list[str]:
    matches = re.findall(r"\b(?:PMID:?\s*)?((?:MOCK-[A-Z0-9-]+)|(?:\d{6,9}))\b", text)
    return list(dict.fromkeys(matches))


def _claim_type(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["warning", "risk", "prognosis", "progression"]):
        return "prognosis"
    if any(term in lowered for term in ["adverse", "safety", "bleeding", "dizziness"]):
        return "safety"
    if any(term in lowered for term in ["diagnos"]):
        return "diagnosis"
    if any(term in lowered for term in ["mechanism", "pathway"]):
        return "mechanism"
    if any(term in lowered for term in ["does not", "uncertain", "limited"]):
        return "limitation"
    return "epidemiology"


def _risk_level(text: str) -> str:
    lowered = text.lower()
    if any(
        term in lowered for term in ["dose", "diagnos", "treatment", "should take", "emergency"]
    ):
        return "high"
    if any(term in lowered for term in ["risk", "warning", "severe", "safety", "adverse"]):
        return "medium"
    return "low"
