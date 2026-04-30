from veritasclin.agents.claim_extractor import ClaimExtractor


def test_claim_extractor_extracts_claims():
    claims = ClaimExtractor().extract(
        "Warning signs are associated with severe dengue risk (MOCK-DENGUE-001). "
        "This evidence does not diagnose individual patients."
    )
    assert claims
    assert claims[0].pmids == ["MOCK-DENGUE-001"]
