from veritasclin.packs.builder import PackBuilder
from veritasclin.packs.offline_qa import ask_offline_pack


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
    assert pack.citation_coverage > 0
    assert any(c.support_status == "supported" for c in pack.claim_ledger)
    assert len(pack.caution_map) > 0
    assert pack.pico.population is not None
    assert pack.pubmed_query


def test_workflow_portuguese_offline_qa_cites_mock_ids():
    pack, _ = PackBuilder().build(
        "What does recent evidence say about warning signs for severe dengue in adults?",
        force_mock_retrieval=True,
    )
    answer = ask_offline_pack(
        pack, "Quais sinais indicam maior risco de dengue grave?", language="pt"
    )
    assert "Modo offline" in answer
    assert "MOCK-DENGUE" in answer
