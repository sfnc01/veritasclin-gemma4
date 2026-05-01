from __future__ import annotations

import json
import re

from veritasclin.llm.base import LLMProvider, LLMProviderError
from veritasclin.llm.prompts import CAUTION_REASONING_SYSTEM_PROMPT
from veritasclin.schemas.caution import CautionItem
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem


class CautionMapper:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    def _llm_cautions(
        self,
        claims: list[Claim],
        evidence_items: list[EvidenceItem],
    ) -> list[CautionItem]:
        abstracts = "\n\n".join(
            f"[{item.paper.pmid}] {item.paper.title}\n{item.paper.abstract or ''}"
            for item in evidence_items[:6]
        )
        claim_summary = "\n".join(f"- {c.id}: {c.text}" for c in claims[:10])
        user_prompt = (
            f"Evidence abstracts:\n{abstracts}\n\n"
            f"Claims in the ledger:\n{claim_summary}\n\n"
            "Identify uncertainty signals. Output a JSON array of caution objects."
        )
        try:
            raw = self._provider.generate(  # type: ignore[union-attr]
                CAUTION_REASONING_SYSTEM_PROMPT, user_prompt, temperature=0.1
            )
            raw = raw.strip()
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start == -1 or end == 0:
                return []
            items = json.loads(raw[start:end])
            result = []
            for i, item in enumerate(items, start=1):
                ct = item.get("caution_type", "low_certainty")
                ex = item.get("explanation", "")
                sv = item.get("severity", "medium")
                if not ex:
                    continue
                result.append(
                    CautionItem(
                        id=f"LCAU{i:03d}",
                        claim_id=item.get("claim_id") or (claims[0].id if claims else ""),
                        supporting_pmids=[],
                        cautionary_pmids=[],
                        caution_type=ct,
                        explanation=ex,
                        severity=sv,
                    )
                )
            return result
        except (LLMProviderError, json.JSONDecodeError, KeyError, IndexError):
            return []

    def map(self, claims: list[Claim], evidence_items: list[EvidenceItem]) -> list[CautionItem]:
        cautions: list[CautionItem] = []

        if self._provider is not None:
            llm_cautions = self._llm_cautions(claims, evidence_items)
            cautions.extend(llm_cautions)

        # Build a lookup from PMID to EvidenceItem for per-claim scoping
        evidence_by_pmid: dict[str, EvidenceItem] = {
            item.paper.pmid: item for item in evidence_items
        }
        weak_pmids = [
            item.paper.pmid
            for item in evidence_items
            if item.evidence_level in {"low", "uncertain"} or item.limitations
        ]
        caution_index = 1

        def add(
            claim: Claim,
            caution_type: str,
            explanation: str,
            severity: str,
            cautionary_pmids: list[str] | None = None,
        ) -> None:
            nonlocal caution_index
            key = (claim.id, caution_type, explanation)
            existing = {
                (item.claim_id, item.caution_type, item.explanation) for item in cautions
            }
            if key in existing:
                return
            cautions.append(
                CautionItem(
                    id=f"CAU{caution_index:03d}",
                    claim_id=claim.id,
                    supporting_pmids=claim.pmids,
                    cautionary_pmids=cautionary_pmids or [],
                    caution_type=caution_type,
                    explanation=explanation,
                    severity=severity,
                )
            )
            caution_index += 1

        for claim in claims:
            if claim.support_status == "unsupported":
                add(
                    claim,
                    "insufficient_data",
                    "This claim is not supported by any PMID in the loaded evidence pack.",
                    "high" if claim.risk_level == "high" else "medium",
                )
                continue

            # Scope evidence text to only the PMIDs this claim cites
            cited_items = [evidence_by_pmid[p] for p in claim.pmids if p in evidence_by_pmid]
            cited_text = _evidence_text(cited_items) if cited_items else ""
            # Fall back to all evidence for low_certainty and indirect checks when no direct cite
            scope_text = cited_text or _evidence_text(evidence_items)

            if claim.evidence_level in {"low", "uncertain"} or (
                weak_pmids and set(claim.pmids).intersection(weak_pmids)
            ):
                add(
                    claim,
                    "low_certainty",
                    "The claim depends on low-certainty or limited evidence in the pack.",
                    "medium",
                    weak_pmids,
                )

            if _has_population_mismatch(claim.text, scope_text):
                add(
                    claim,
                    "population_mismatch",
                    "Some cited evidence may not directly match the target adult human population.",
                    "medium",
                    claim.pmids,
                )

            if _has_outcome_mismatch(claim.text, scope_text):
                add(
                    claim,
                    "outcome_mismatch",
                    (
                        "Cited evidence emphasizes surrogate or laboratory outcomes rather "
                        "than the claimed clinical outcome."
                    ),
                    "medium",
                    claim.pmids,
                )

            if _has_safety_signal(claim.text, scope_text):
                add(
                    claim,
                    "safety_signal",
                    (
                        "Cited evidence includes safety or adverse-event language relevant "
                        "to this claim."
                    ),
                    "medium" if claim.risk_level != "high" else "high",
                    claim.pmids,
                )

            if cited_text and _has_indirect_evidence(cited_text):
                add(
                    claim,
                    "indirect_evidence",
                    "Cited evidence is indirect for clinical decision-making "
                    "in the target setting.",
                    "medium",
                    claim.pmids,
                )

            if cited_text and _has_conflict_language(cited_text):
                add(
                    claim,
                    "conflicting_results",
                    (
                        "Cited evidence uses language suggesting mixed or "
                        "inconsistent results across studies."
                    ),
                    "medium",
                    claim.pmids,
                )

        # Pack-level cross-paper conflict: detect opposing conclusions across the full set
        if claims and _has_cross_paper_conflict(evidence_items):
            all_pmids = list({p for c in claims for p in c.pmids})
            existing_conflict_ids = {
                (item.claim_id, item.caution_type) for item in cautions
            }
            sentinel_claim = claims[0]
            if (sentinel_claim.id, "conflicting_results") not in existing_conflict_ids:
                cautions.append(
                    CautionItem(
                        id=f"CAU{caution_index:03d}",
                        claim_id=sentinel_claim.id,
                        supporting_pmids=[],
                        cautionary_pmids=all_pmids[:6],
                        caution_type="conflicting_results",
                        explanation=(
                            "Papers in this pack reach opposing conclusions on at least one "
                            "outcome — review individual study findings before drawing "
                            "clinical conclusions."
                        ),
                        severity="medium",
                    )
                )

        return cautions


def _evidence_text(evidence_items: list[EvidenceItem]) -> str:
    return " ".join(
        " ".join(
            [
                item.paper.title,
                item.paper.abstract or "",
                " ".join(item.paper.mesh_terms),
                " ".join(item.paper.publication_types),
                " ".join(item.limitations),
            ]
        )
        for item in evidence_items
    ).lower()


def _has_population_mismatch(claim_text: str, evidence_text: str) -> bool:
    claim_lower = claim_text.lower()
    adult_claim = any(term in claim_lower for term in ["adult", "adults", "human", "patients"])
    mismatch_terms = ["children", "pediatric", "paediatric", "pregnant", "animal", "mice", "rat"]
    return adult_claim and any(term in evidence_text for term in mismatch_terms)


def _has_outcome_mismatch(claim_text: str, evidence_text: str) -> bool:
    clinical_claim = any(
        term in claim_text.lower()
        for term in ["severe", "progression", "mortality", "hospitalization", "risk"]
    )
    surrogate_terms = ["surrogate", "biomarker", "laboratory", "hematocrit", "platelet"]
    return clinical_claim and any(term in evidence_text for term in surrogate_terms)


def _has_safety_signal(claim_text: str, evidence_text: str) -> bool:
    safety_terms = [
        "adverse",
        "bleeding",
        "toxicity",
        "harm",
        "safety",
        "sedation",
        "dizziness",
        "mortality",
    ]
    # Only fire when the claim itself contains a safety term.
    # The per-claim scoped evidence text caused false positives when a cited paper
    # mentioned e.g. "bleeding" in a context unrelated to the claim's assertion.
    return any(term in claim_text.lower() for term in safety_terms)


def _has_indirect_evidence(evidence_text: str) -> bool:
    return bool(
        re.search(
            r"\b(animal model|mice|rat model|in vitro|ex vivo|preclinical|indirect evidence"
            r"|observational|retrospective cohort)\b",
            evidence_text,
        )
    )


def _has_conflict_language(evidence_text: str) -> bool:
    return bool(
        re.search(
            r"\b(conflicting|inconsistent|mixed results|heterogeneity|high heterogeneity|"
            r"not significant|no significant|no association|no benefit|failed to show|"
            r"did not improve|uncertain|inconclusive|equivocal|limited evidence)\b",
            evidence_text,
        )
    )


def _has_cross_paper_conflict(evidence_items: list[EvidenceItem]) -> bool:
    """Detect when papers take opposite positions on the same outcome."""
    positive = re.compile(
        r"\b(improved|reduction|reduced|benefit|protective|significant decrease|"
        r"significantly lower|effective|efficacious)\b"
    )
    negative = re.compile(
        r"\b(no improvement|no benefit|no reduction|no significant|not effective|"
        r"no difference|failed|did not reduce|did not improve|no association)\b"
    )
    has_positive = any(
        positive.search((item.paper.abstract or "").lower()) for item in evidence_items
    )
    has_negative = any(
        negative.search((item.paper.abstract or "").lower()) for item in evidence_items
    )
    return has_positive and has_negative
