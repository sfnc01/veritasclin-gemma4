from veritasclin.packs.builder import PackBuilder
from veritasclin.packs.offline_qa import ask_offline_pack


def test_offline_qa_uses_loaded_pack_only(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("PubMed should not be called in offline mode")

    monkeypatch.setattr("veritasclin.tools.pubmed.search_pubmed", fail_if_called)
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    answer = ask_offline_pack(
        pack, "Quais sinais indicam maior risco de dengue grave?", language="pt"
    )
    assert "Modo offline" in answer
    assert "Claim Ledger" in answer
    assert "MOCK-DENGUE" in answer


def test_offline_qa_spanish_cites_loaded_claims():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    answer = ask_offline_pack(
        pack, "Que signos indican mayor riesgo de dengue grave?", language="es"
    )
    assert "Modo offline" in answer
    assert "Claim Ledger" in answer
    assert "MOCK-DENGUE" in answer


def test_offline_qa_refuses_unsupported_question():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    answer = ask_offline_pack(pack, "What does this pack say about malaria treatment?")
    assert "does not contain enough evidence" in answer
