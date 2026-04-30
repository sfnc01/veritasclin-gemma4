from veritasclin.exporters.markdown import pack_to_markdown
from veritasclin.packs.builder import PackBuilder


def test_markdown_export_includes_claim_ledger_and_caution_map():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    markdown = pack_to_markdown(pack)
    assert "## Claim Ledger" in markdown
    assert "## Caution & Conflict Map" in markdown
