from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from veritasclin.agents.baseline_agent import BaselineAgent
from veritasclin.agents.caution_mapper import CautionMapper
from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.agents.evidence_ranker import EvidenceRanker
from veritasclin.agents.freshness_scorer import FreshnessScorer
from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.agents.query_agent import QueryAgent
from veritasclin.agents.safety_guard import SafetyGuard
from veritasclin.agents.synthesis_agent import SynthesisAgent
from veritasclin.config import get_settings
from veritasclin.evaluation.faithfulness import citation_coverage as eval_citation_coverage
from veritasclin.llm import LLMProvider, get_llm_provider
from veritasclin.schemas.baseline import BaselineComparison
from veritasclin.schemas.pack import EvidencePack
from veritasclin.tools.pubmed import fetch_pubmed_papers, mock_pubmed_papers, search_pubmed


class PackBuilder:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or get_llm_provider()

    def build(
        self,
        question: str,
        language: str = "en",
        max_results: int = 10,
        include_baseline: bool = True,
        force_mock_retrieval: bool = False,
    ) -> tuple[EvidencePack, BaselineComparison | None]:
        settings = get_settings()
        now = datetime.now(UTC)
        safety = SafetyGuard(provider=self._provider).check(question)
        if not safety.allowed:
            raise ValueError(safety.user_message)

        research_question = safety.safe_rewritten_question or question
        pico = PICOAgent(provider=self._provider).extract(
            question=question,
            safe_rewritten_question=safety.safe_rewritten_question,
            language=language,
        )
        query = QueryAgent().build(pico)
        papers = []
        source = "PubMed/NCBI"

        if not force_mock_retrieval and settings.pubmed_configured:
            pmids = search_pubmed(query, max_results=max_results)
            papers = fetch_pubmed_papers(pmids)

        if not papers:
            papers = mock_pubmed_papers(research_question)
            source = "Mock demo data - not real PubMed retrieval"

        evidence_items = EvidenceRanker().rank(papers, pico)[:max_results]
        synthesis = SynthesisAgent(provider=self._provider).synthesize(
            pico, evidence_items, language=language
        )
        claim_text = " ".join(
            [
                synthesis.executive_summary,
                synthesis.clinical_interpretation,
                synthesis.patient_friendly_explanation,
            ]
        )
        extracted_claims = ClaimExtractor(provider=self._provider).extract(claim_text)
        claim_ledger = ClaimVerifier().verify(extracted_claims, evidence_items)
        caution_map = CautionMapper().map(claim_ledger, evidence_items)
        freshness = FreshnessScorer().score(evidence_items, search_date=now.date().isoformat())
        pack = EvidencePack(
            pack_id=f"vfield-{uuid4().hex[:12]}",
            title=_title_from_question(research_question),
            topic=research_question,
            created_at=now.isoformat(),
            last_pubmed_search_at=now.isoformat(),
            language=language,
            source=source,
            pico=pico,
            pubmed_query=query,
            papers=papers,
            evidence_items=evidence_items,
            claim_ledger=claim_ledger,
            caution_map=caution_map,
            freshness=freshness,
            executive_summary=synthesis.executive_summary,
            clinical_interpretation=synthesis.clinical_interpretation,
            what_the_evidence_does_not_prove=synthesis.what_the_evidence_does_not_prove,
            patient_friendly_explanation=synthesis.patient_friendly_explanation,
            safety_notice=synthesis.safety_notice,
            citation_coverage=eval_citation_coverage(claim_ledger),
        )
        baseline = (
            BaselineAgent(provider=self._provider).compare(question, pack)
            if include_baseline
            else None
        )
        return pack, baseline


def _title_from_question(question: str) -> str:
    cleaned = question.strip(" ?.").capitalize()
    if len(cleaned) > 90:
        cleaned = cleaned[:87].rstrip() + "..."
    return f"Evidence Pack: {cleaned}"
