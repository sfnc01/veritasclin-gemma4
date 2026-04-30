from veritasclin.agents.caution_mapper import CautionMapper
from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier


def test_caution_mapper_detects_insufficient_data():
    claims = ClaimExtractor().extract("This treatment should be used for severe disease.")
    verified = ClaimVerifier().verify(claims, [])
    cautions = CautionMapper().map(verified, [])
    assert cautions
    assert cautions[0].caution_type == "insufficient_data"
