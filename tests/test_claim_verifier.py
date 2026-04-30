from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.paper import PubMedPaper


def _make_evidence_item(pmid: str) -> EvidenceItem:
    paper = PubMedPaper(
        pmid=pmid,
        title="Test paper",
        abstract=None,
        journal="Test Journal",
        publication_year=2023,
        authors=[],
        doi=None,
        publication_types=["Clinical Trial"],
        mesh_terms=[],
        url=f"mock://{pmid}",
    )
    return EvidenceItem(
        paper=paper,
        relevance_score=50.0,
        evidence_level="moderate",
        study_type="Clinical Trial",
        rationale="test",
        key_findings=[],
        limitations=[],
    )


def test_claim_verifier_flags_uncited_strong_claims():
    claims = ClaimExtractor().extract("This treatment should be used for severe disease.")
    verified = ClaimVerifier().verify(claims, [])
    assert verified[0].support_status == "unsupported"


def test_claim_verifier_marks_low_risk_fallback_as_partially_supported():
    claim = Claim(
        id="C001",
        text="General observation about the topic.",
        claim_type="epidemiology",
        support_status="uncertain",
        pmids=[],
        evidence_level="uncertain",
        risk_level="low",
        rationale="test",
        limitation_note=None,
    )
    ei = _make_evidence_item("MOCK-TEST-001")
    result = ClaimVerifier().verify([claim], [ei])
    assert result[0].support_status == "partially_supported"
    assert result[0].limitation_note is not None
    assert result[0].pmids == ["MOCK-TEST-001"]


def test_claim_verifier_fully_supports_cited_claims():
    claims = ClaimExtractor().extract(
        "Evidence indicates warning signs in adults (MOCK-TEST-001)."
    )
    ei = _make_evidence_item("MOCK-TEST-001")
    result = ClaimVerifier().verify(claims, [ei])
    assert any(c.support_status == "supported" for c in result)
