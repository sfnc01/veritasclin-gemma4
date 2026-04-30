from veritasclin.agents.evidence_ranker import EvidenceRanker
from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.schemas.paper import PubMedPaper


def _paper(pmid: str, publication_types: list[str], year: int = 2020) -> PubMedPaper:
    return PubMedPaper(
        pmid=pmid,
        title="Dengue warning signs in adults",
        abstract="Dengue warning signs and severe dengue outcomes in adults.",
        journal="Test",
        publication_year=year,
        authors=[],
        doi=None,
        publication_types=publication_types,
        mesh_terms=["Dengue"],
        url=f"https://example.test/{pmid}",
    )


def test_evidence_ranker_boosts_stronger_study_types():
    pico = PICOAgent().extract("Dengue warning signs in adults")
    ranked = EvidenceRanker().rank(
        [
            _paper("2", ["Case Reports"], 2024),
            _paper("1", ["Systematic Review"], 2020),
        ],
        pico,
    )
    assert ranked[0].paper.pmid == "1"
