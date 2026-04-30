import pytest

from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.config import get_settings, reset_settings_cache
from veritasclin.packs.builder import PackBuilder
from veritasclin.tools.pubmed import build_pubmed_query, fetch_pubmed_papers, search_pubmed


def _has_pubmed_credentials() -> bool:
    reset_settings_cache()
    settings = get_settings()
    return bool(settings.ncbi_api_key and settings.ncbi_email)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _has_pubmed_credentials(),
        reason="NCBI_API_KEY and NCBI_EMAIL are required for PubMed integration tests.",
    ),
]


def test_pubmed_integration_search_returns_numeric_pmids():
    pico = PICOAgent().extract(
        "What does recent evidence say about warning signs for severe dengue in adults?"
    )
    pmids = search_pubmed(build_pubmed_query(pico), max_results=5)
    assert pmids
    assert all(pmid.isdigit() for pmid in pmids)


def test_pubmed_integration_fetch_returns_pubmed_papers():
    pico = PICOAgent().extract(
        "What does recent evidence say about warning signs for severe dengue in adults?"
    )
    pmids = search_pubmed(build_pubmed_query(pico), max_results=3)
    papers = fetch_pubmed_papers(pmids)
    assert papers
    assert all(paper.pmid.isdigit() for paper in papers)
    assert all(paper.url.startswith("https://pubmed.ncbi.nlm.nih.gov/") for paper in papers)


def test_workflow_pubmed_builds_real_dengue_pack():
    pack, _ = PackBuilder().build(
        "What does recent evidence say about warning signs for severe dengue in adults?",
        max_results=5,
        include_baseline=False,
    )
    assert pack.source == "PubMed/NCBI"
    assert pack.papers
    assert all(paper.pmid.isdigit() for paper in pack.papers)
