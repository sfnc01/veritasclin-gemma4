from veritasclin.packs.builder import PackBuilder


def test_full_workflow_runs_in_mock_mode():
    pack, baseline = PackBuilder().build(
        "What does recent evidence say about warning signs for severe dengue in adults?",
        language="en",
        max_results=5,
        include_baseline=True,
        force_mock_retrieval=True,
    )
    assert pack.evidence_items
    assert pack.claim_ledger
    assert "Mock demo data" in pack.source
    assert baseline is not None
