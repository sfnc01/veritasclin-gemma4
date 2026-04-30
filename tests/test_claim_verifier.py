from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier


def test_claim_verifier_flags_uncited_strong_claims():
    claims = ClaimExtractor().extract("This treatment should be used for severe disease.")
    verified = ClaimVerifier().verify(claims, [])
    assert verified[0].support_status == "unsupported"
