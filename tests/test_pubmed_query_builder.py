import httpx

from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.config import reset_settings_cache
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


def test_pubmed_failure_does_not_expose_secret(monkeypatch, capsys):
    monkeypatch.setenv("NCBI_API_KEY", "test-secret-value")
    monkeypatch.setenv("NCBI_EMAIL", "test@example.org")
    reset_settings_cache()

    def raise_error(*args, **kwargs):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr("httpx.Client.get", raise_error)
    result = search_pubmed("veritasclin-failure-test-unique", max_results=1)
    captured = capsys.readouterr()

    assert result == []
    assert "test-secret-value" not in captured.out
    assert "test-secret-value" not in captured.err
    reset_settings_cache()
