from veritasclin.agents.evidence_ranker import EvidenceRanker
from veritasclin.agents.freshness_scorer import FreshnessScorer
from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.tools.pubmed import mock_pubmed_papers


def test_freshness_scorer_returns_score():
    pico = PICOAgent().extract("Dengue warning signs in adults")
    evidence = EvidenceRanker().rank(mock_pubmed_papers("dengue"), pico)
    freshness = FreshnessScorer().score(evidence)
    assert 0 <= freshness.score <= 1
    assert freshness.recommended_refresh_days > 0
