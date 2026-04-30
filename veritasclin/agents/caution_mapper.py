from __future__ import annotations

import re

from veritasclin.schemas.caution import CautionItem
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem


class CautionMapper:
    def map(self, claims: list[Claim], evidence_items: list[EvidenceItem]) -> list[CautionItem]:
        cautions: list[CautionItem] = []
        evidence_text = _evidence_text(evidence_items)
        evidence_pmids = [item.paper.pmid for item in evidence_items]
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
                    "This claim is not supported by a PMID or loaded mock evidence ID.",
                    "high" if claim.risk_level == "high" else "medium",
                )
                continue

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

            if _has_population_mismatch(claim.text, evidence_text):
                add(
                    claim,
                    "population_mismatch",
                    "Some evidence may not directly match the target adult human population.",
                    "medium",
                    evidence_pmids,
                )

            if _has_outcome_mismatch(claim.text, evidence_text):
                add(
                    claim,
                    "outcome_mismatch",
                    (
                        "Some evidence emphasizes surrogate or laboratory outcomes rather "
                        "than the claim."
                    ),
                    "medium",
                    evidence_pmids,
                )

            if _has_safety_signal(claim.text, evidence_text):
                add(
                    claim,
                    "safety_signal",
                    (
                        "Loaded evidence includes safety or adverse-event language relevant "
                        "to this claim."
                    ),
                    "medium" if claim.risk_level != "high" else "high",
                    evidence_pmids,
                )

            if _has_indirect_evidence(evidence_text):
                add(
                    claim,
                    "indirect_evidence",
                    "Some evidence is indirect for clinical decision-making in the target setting.",
                    "medium",
                    evidence_pmids,
                )

            if _has_conflict_language(evidence_text):
                add(
                    claim,
                    "conflicting_results",
                    (
                        "Loaded evidence uses cautious language suggesting mixed or "
                        "inconsistent results."
                    ),
                    "low",
                    evidence_pmids,
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
    return any(term in claim_text.lower() or term in evidence_text for term in safety_terms)


def _has_indirect_evidence(evidence_text: str) -> bool:
    return bool(re.search(r"\b(animal|mice|rat|in vitro|preclinical|indirect)\b", evidence_text))


def _has_conflict_language(evidence_text: str) -> bool:
    return bool(
        re.search(
            r"\b(conflicting|inconsistent|mixed results|heterogeneity|not significant|"
            r"no association|uncertain)\b",
            evidence_text,
        )
    )
