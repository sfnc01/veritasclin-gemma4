from veritasclin.agents.baseline_agent import BaselineAgent
from veritasclin.packs.builder import PackBuilder


def test_baseline_comparison_produces_metrics():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    comparison = BaselineAgent().compare("Dengue warning signs in adults", pack)
    assert comparison.baseline_claim_count >= 1
    assert (
        comparison.baseline_unsupported_claim_count
        >= comparison.veritasclin_unsupported_claim_count
    )
    assert 0 <= comparison.citation_coverage <= 1
    assert "Unsupported claim delta" in comparison.summary
