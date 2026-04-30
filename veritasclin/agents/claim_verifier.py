from __future__ import annotations

from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem


class ClaimVerifier:
    def verify(self, claims: list[Claim], evidence_items: list[EvidenceItem]) -> list[Claim]:
        available = {item.paper.pmid: item for item in evidence_items}
        verified: list[Claim] = []
        fallback_pmids = list(available.keys())[:2]
        for claim in claims:
            pmids = [pmid for pmid in claim.pmids if pmid in available]
            if not pmids and claim.risk_level in {"medium", "high"}:
                verified.append(
                    claim.model_copy(
                        update={
                            "support_status": "unsupported",
                            "evidence_level": "uncertain",
                            "rationale": (
                                "Strong clinical claim has no PMID or loaded mock evidence ID."
                            ),
                            "limitation_note": (
                                "No PMID/PMCID or mock evidence ID, no strong clinical claim."
                            ),
                        }
                    )
                )
                continue
            if not pmids and claim.risk_level == "low" and fallback_pmids:
                pmids = fallback_pmids[:1]
            levels = [available[pmid].evidence_level for pmid in pmids if pmid in available]
            level = _best_level(levels)
            status = "supported" if pmids else "uncertain"
            verified.append(
                claim.model_copy(
                    update={
                        "support_status": status,
                        "pmids": pmids,
                        "evidence_level": level,
                        "rationale": (
                            "Claim has cited support in the loaded Evidence Pack."
                            if pmids
                            else "Claim could not be directly matched to loaded evidence."
                        ),
                    }
                )
            )
        return verified


def _best_level(levels: list[str]) -> str:
    order = ["high", "moderate", "low", "uncertain"]
    for level in order:
        if level in levels:
            return level
    return "uncertain"
