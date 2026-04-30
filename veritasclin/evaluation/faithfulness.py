from __future__ import annotations

from veritasclin.schemas.claims import Claim


def citation_coverage(claims: list[Claim]) -> float:
    if not claims:
        return 0.0
    return round(sum(1 for claim in claims if claim.pmids) / len(claims), 2)


def unsupported_claim_count(claims: list[Claim]) -> int:
    return sum(1 for claim in claims if claim.support_status == "unsupported")


def high_risk_unsupported_claim_count(claims: list[Claim]) -> int:
    return sum(
        1
        for claim in claims
        if claim.support_status == "unsupported" and claim.risk_level == "high"
    )
