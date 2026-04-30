from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.tools.pubmed import build_pubmed_query, fetch_pubmed_papers, search_pubmed


def test_pubmed_query_builder_creates_auditable_query():
    pico = PICOAgent().extract(
        "What does recent evidence say about warning signs for severe dengue in adults?"
    )
    query = build_pubmed_query(pico)
    assert "dengue" in query.lower()
    assert "Title/Abstract" in query
    assert "humans" in query.lower()


def test_pubmed_client_fails_gracefully_for_empty_inputs():
    assert search_pubmed("", max_results=0) == []
    assert fetch_pubmed_papers([]) == []
