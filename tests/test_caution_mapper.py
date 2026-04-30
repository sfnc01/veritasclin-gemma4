from veritasclin.agents.caution_mapper import CautionMapper
from veritasclin.agents.claim_extractor import ClaimExtractor
from veritasclin.agents.claim_verifier import ClaimVerifier
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.paper import PubMedPaper


def test_caution_mapper_detects_insufficient_data():
    claims = ClaimExtractor().extract("This treatment should be used for severe disease.")
    verified = ClaimVerifier().verify(claims, [])
    cautions = CautionMapper().map(verified, [])
    assert cautions
    assert cautions[0].caution_type == "insufficient_data"


def test_caution_mapper_detects_layer_2_patterns():
    # Claim with safety language → safety_signal should fire
    safety_claim = Claim(
        id="C001",
        text="Adults with warning signs have higher risk of severe dengue adverse outcomes.",
        claim_type="safety",
        support_status="supported",
        pmids=["123456"],
        evidence_level="low",
        risk_level="medium",
        rationale="Test claim.",
    )
    # Claim without safety language → safety_signal should NOT fire from evidence alone
    prognosis_claim = Claim(
        id="C002",
        text="Adults with warning signs have higher risk of severe dengue outcomes.",
        claim_type="prognosis",
        support_status="supported",
        pmids=["123456"],
        evidence_level="low",
        risk_level="medium",
        rationale="Test claim.",
    )
    evidence = [
        EvidenceItem(
            paper=PubMedPaper(
                pmid="123456",
                title="Pediatric animal model with mixed results for dengue biomarkers",
                abstract=(
                    "Animal and pediatric evidence described inconsistent biomarker findings, "
                    "laboratory platelet outcomes, and bleeding safety signals."
                ),
                journal="Test",
                publication_year=2012,
                authors=[],
                doi=None,
                publication_types=["Case Reports"],
                mesh_terms=["Dengue", "Animals"],
                url="https://pubmed.ncbi.nlm.nih.gov/123456/",
            ),
            relevance_score=10,
            evidence_level="low",
            study_type="Case Reports",
            rationale="Test evidence.",
            key_findings=[],
            limitations=["Indirect evidence."],
        )
    ]

    safety_cautions = {
        item.caution_type for item in CautionMapper().map([safety_claim], evidence)
    }
    prognosis_cautions = {
        item.caution_type for item in CautionMapper().map([prognosis_claim], evidence)
    }

    # safety_claim mentions "adverse" → safety_signal fires
    assert "safety_signal" in safety_cautions
    # prognosis_claim has no safety terms → safety_signal must NOT fire from evidence alone
    assert "safety_signal" not in prognosis_cautions

    # Other layer-2 cautions still fire for both (evidence-based)
    for caution_types in (safety_cautions, prognosis_cautions):
        assert "low_certainty" in caution_types
        assert "population_mismatch" in caution_types
        assert "outcome_mismatch" in caution_types
        assert "indirect_evidence" in caution_types
        assert "conflicting_results" in caution_types
