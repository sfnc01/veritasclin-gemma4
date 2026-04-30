from __future__ import annotations

from veritasclin.schemas.caution import CautionItem
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem


class CautionMapper:
    def map(self, claims: list[Claim], evidence_items: list[EvidenceItem]) -> list[CautionItem]:
        cautions: list[CautionItem] = []
        for index, claim in enumerate(claims, start=1):
            if claim.support_status == "unsupported":
                cautions.append(
                    CautionItem(
                        id=f"CAU{index:03d}",
                        claim_id=claim.id,
                        supporting_pmids=[],
                        cautionary_pmids=[],
                        caution_type="insufficient_data",
                        explanation=(
                            "This claim is not supported by a PMID or loaded mock evidence ID."
                        ),
                        severity="high" if claim.risk_level == "high" else "medium",
                    )
                )
            elif claim.evidence_level in {"low", "uncertain"}:
                cautions.append(
                    CautionItem(
                        id=f"CAU{index:03d}",
                        claim_id=claim.id,
                        supporting_pmids=claim.pmids,
                        cautionary_pmids=[],
                        caution_type="low_certainty",
                        explanation="The claim is supported only by low or uncertain evidence.",
                        severity="medium",
                    )
                )
        text = " ".join(
            item.paper.title + " " + (item.paper.abstract or "") for item in evidence_items
        ).lower()
        if "animal" in text and claims:
            cautions.append(
                CautionItem(
                    id=f"CAU{len(cautions) + 1:03d}",
                    claim_id=claims[0].id,
                    supporting_pmids=claims[0].pmids,
                    cautionary_pmids=[],
                    caution_type="population_mismatch",
                    explanation=(
                        "Some loaded evidence may not directly match the target human population."
                    ),
                    severity="medium",
                )
            )
        return cautions
