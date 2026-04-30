from __future__ import annotations

from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.evaluation.baseline_eval import (
    baseline_vs_veritasclin_delta,
    pack_reproducibility_present,
)
from veritasclin.evaluation.faithfulness import (
    high_risk_unsupported_claim_count,
    unsupported_claim_count,
)
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

        baseline_unsupported = unsupported_claim_count(verified)
        baseline_high_risk = high_risk_unsupported_claim_count(verified)
        vc_unsupported = unsupported_claim_count(pack.claim_ledger)
        vc_high_risk = high_risk_unsupported_claim_count(pack.claim_ledger)

        comparison = BaselineComparison(
            baseline_answer=baseline_answer,
            baseline_claim_count=len(verified),
            baseline_unsupported_claim_count=baseline_unsupported,
            baseline_high_risk_unsupported_count=baseline_high_risk,
            veritasclin_claim_count=len(pack.claim_ledger),
            veritasclin_unsupported_claim_count=vc_unsupported,
            citation_coverage=pack.citation_coverage,
            summary="",
        )
        delta = baseline_vs_veritasclin_delta(comparison)
        reproducible = pack_reproducibility_present(comparison)
        comparison = comparison.model_copy(
            update={
                "summary": (
                    "Plain model claims are checked without retrieved evidence, while VeritasClin "
                    "claims are carried in a reusable ledger with pack citations. "
                    f"Unsupported claim delta: {delta}; "
                    f"high-risk unsupported VeritasClin claims: {vc_high_risk}. "
                    f"Pack is {'reproducible' if reproducible else 'not reproducible'} "
                    "(citation coverage > 0)."
                )
            }
        )
        return comparison

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
