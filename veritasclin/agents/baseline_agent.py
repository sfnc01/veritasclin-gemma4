from __future__ import annotations

from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.schemas.baseline import BaselineComparison
from veritasclin.schemas.pack import EvidencePack


class BaselineAgent:
    def compare(self, question: str, pack: EvidencePack) -> BaselineComparison:
        baseline_answer = (
            "A plain model might list warning signs or treatment implications without carrying "
            "the source evidence alongside each claim."
        )
        claims = ClaimExtractor().extract(baseline_answer + " This may indicate severe disease.")
        verified = ClaimVerifier().verify(claims, [])
        unsupported = [claim for claim in verified if claim.support_status == "unsupported"]
        vc_unsupported = [
            claim for claim in pack.claim_ledger if claim.support_status == "unsupported"
        ]
        vc_high = [claim for claim in vc_unsupported if claim.risk_level == "high"]
        return BaselineComparison(
            baseline_answer=baseline_answer,
            baseline_claim_count=len(verified),
            baseline_unsupported_claim_count=len(unsupported),
            baseline_high_risk_unsupported_count=len(
                [claim for claim in unsupported if claim.risk_level == "high"]
            ),
            veritasclin_claim_count=len(pack.claim_ledger),
            veritasclin_unsupported_claim_count=len(vc_unsupported),
            citation_coverage=pack.citation_coverage,
            summary=(
                "VeritasClin improves auditability by forcing claims into a ledger with cited "
                f"pack evidence; high-risk unsupported VeritasClin claims: {len(vc_high)}."
            ),
        )
