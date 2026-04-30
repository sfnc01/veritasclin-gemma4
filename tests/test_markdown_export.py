from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv
from veritasclin.exporters.json_export import pack_to_json
from veritasclin.exporters.markdown import pack_to_markdown
from veritasclin.packs.builder import PackBuilder


def test_markdown_export_includes_claim_ledger_and_caution_map():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    markdown = pack_to_markdown(pack)
    assert "## Claim Ledger" in markdown
    assert "## Caution & Conflict Map" in markdown
    assert "## Evidence Map" in markdown


def test_json_csv_exports_include_pack_and_claims():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    assert '"claim_ledger"' in pack_to_json(pack)
    assert '"evidence_items"' in pack_to_json(pack)
    assert "support_status" in claims_to_csv(pack.claim_ledger)
    assert "caution_type" in caution_map_to_json(pack.caution_map)
