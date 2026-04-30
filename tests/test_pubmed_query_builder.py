import httpx

from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.config import reset_settings_cache
from veritasclin.tools.pubmed import (
    build_pubmed_query,
    fetch_pubmed_papers,
    search_pubmed,
    search_pubmed_details,
)


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


def test_pubmed_search_details_supports_entrez_history_and_pagination(monkeypatch):
    seen_params = {}
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_get", lambda key: None)
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_set", lambda key, value: None)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "esearchresult": {
                    "idlist": ["123", "456"],
                    "count": "42",
                    "retmax": "2",
                    "retstart": "20",
                    "querykey": "1",
                    "webenv": "NCID_1_test",
                    "querytranslation": "dengue[Title/Abstract]",
                }
            }

    def fake_get(self, url, params):  # noqa: ARG001
        seen_params.update(params)
        return FakeResponse()

    monkeypatch.setattr("httpx.Client.get", fake_get)
    result = search_pubmed_details(
        "veritasclin-history-pagination-test",
        max_results=2,
        retstart=20,
        use_history=True,
    )

    assert result.pmids == ["123", "456"]
    assert result.count == 42
    assert result.retstart == 20
    assert result.query_key == "1"
    assert result.webenv == "NCID_1_test"
    assert seen_params["usehistory"] == "y"
    assert seen_params["retstart"] == 20
    assert seen_params["retmax"] == 2
    assert seen_params["tool"]


def test_pubmed_search_legacy_helper_returns_pmids(monkeypatch):
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_get", lambda key: None)
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_set", lambda key, value: None)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"esearchresult": {"idlist": ["789"], "retmax": "1", "retstart": "0"}}

    def fake_get(self, url, params):  # noqa: ARG001
        return FakeResponse()

    monkeypatch.setattr("httpx.Client.get", fake_get)
    assert search_pubmed("veritasclin-legacy-search-test", max_results=1) == ["789"]


def test_pubmed_fetch_batches_large_uid_lists(monkeypatch):
    seen_batches = []
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_get", lambda key: None)
    monkeypatch.setattr("veritasclin.tools.pubmed.cache_set", lambda key, value: None)

    def fake_fetch_batch(pmids):
        seen_batches.append(pmids)
        return []

    monkeypatch.setattr("veritasclin.tools.pubmed._fetch_pubmed_batch", fake_fetch_batch)
    pmids = [str(index) for index in range(205)] + ["0"]
    assert fetch_pubmed_papers(pmids, batch_size=100) == []
    assert [len(batch) for batch in seen_batches] == [100, 100, 5]
    assert seen_batches[0][0] == "0"
    assert seen_batches[-1][-1] == "204"


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
