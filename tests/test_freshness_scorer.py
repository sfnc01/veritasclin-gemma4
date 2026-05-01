from datetime import UTC, datetime

from veritasclin.agents.evidence_ranker import EvidenceRanker
from veritasclin.agents.freshness_scorer import FreshnessScorer
from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.paper import PubMedPaper
from veritasclin.tools.pubmed import bundled_demo_papers


def test_freshness_scorer_returns_score():
    pico = PICOAgent().extract("Dengue warning signs in adults")
    evidence = EvidenceRanker().rank(bundled_demo_papers("dengue"), pico)
    freshness = FreshnessScorer().score(evidence)
    assert 0 <= freshness.score <= 1
    assert freshness.recommended_refresh_days > 0


def test_freshness_scorer_bounds_current_stale_and_missing_years():
    current = _evidence("1", datetime.now(UTC).year)
    stale = _evidence("2", 2001)
    missing = _evidence("3", None)

    current_score = FreshnessScorer().score([current])
    stale_score = FreshnessScorer().score([stale])
    missing_score = FreshnessScorer().score([missing])

    assert current_score.score == 1.0
    assert stale_score.score == 0.3
    assert missing_score.score == 0.2
    assert stale_score.recommended_refresh_days < current_score.recommended_refresh_days


def _evidence(pmid: str, year: int | None) -> EvidenceItem:
    return EvidenceItem(
        paper=PubMedPaper(
            pmid=pmid,
            title="Dengue evidence",
            abstract="Clinical evidence.",
            journal="Test",
            publication_year=year,
            authors=[],
            doi=None,
            publication_types=["Clinical Trial"],
            mesh_terms=["Dengue"],
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        ),
        relevance_score=10,
        evidence_level="moderate",
        study_type="Clinical Trial",
        rationale="Test.",
        key_findings=[],
        limitations=[],
    )
