from veritasclin.packs.builder import PackBuilder
from veritasclin.schemas.pack import EvidencePack


def test_pack_builder_creates_valid_evidence_pack():
    pack, baseline = PackBuilder().build(
        "What does recent evidence say about warning signs for severe dengue in adults?",
        use_bundled_papers=True,
    )
    assert isinstance(pack, EvidencePack)
    assert pack.claim_ledger
    assert baseline is not None
