from __future__ import annotations

import re

from veritasclin.schemas.claims import Claim


class ClaimExtractor:
    def extract(self, text: str) -> list[Claim]:
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if len(sentence.strip()) > 35
        ]
        claims: list[Claim] = []
        for index, sentence in enumerate(sentences, start=1):
            pmids = _extract_pmids(sentence)
            claims.append(
                Claim(
                    id=f"C{index:03d}",
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
