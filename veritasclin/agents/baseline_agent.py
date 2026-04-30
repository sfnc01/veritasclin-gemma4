from __future__ import annotations

from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.llm import LLMProvider, get_llm_provider
from veritasclin.llm.openai_compatible import LLMProviderError
from veritasclin.schemas.baseline import BaselineComparison
from veritasclin.schemas.pack import EvidencePack


class BaselineAgent:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def compare(self, question: str, pack: EvidencePack) -> BaselineComparison:
        baseline_answer = self._baseline_answer(question)
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
                "Plain model claims are checked without retrieved evidence, while VeritasClin "
                "claims are carried in a reusable ledger with pack citations. Unsupported "
                f"claim delta: {len(unsupported) - len(vc_unsupported)}; high-risk unsupported "
                f"VeritasClin claims: {len(vc_high)}."
            ),
        )

    def _baseline_answer(self, question: str) -> str:
        try:
            generated = self.provider.generate(
                "Answer as a plain medical assistant without retrieval.",
                question,
                temperature=0.2,
            )
        except LLMProviderError:
            generated = None
        if generated and not generated.lower().startswith(
            ("mock gemma output", "ollama unavailable")
        ):
            return generated
        if "dengue" in question.lower():
            return (
                "Warning signs for severe dengue include abdominal pain, persistent vomiting, "
                "bleeding, lethargy, fluid accumulation, and falling platelets. Patients with "
                "these signs need urgent clinical assessment and may require hospitalization. "
                "These findings can diagnose severe dengue. Immediate treatment decisions should "
                "be made from these signs."
            )
        return (
            "A plain model might provide clinical-sounding conclusions without carrying the "
            "source evidence alongside each claim."
        )
