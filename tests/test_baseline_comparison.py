from veritasclin.agents.baseline_agent import BaselineAgent
from veritasclin.packs.builder import PackBuilder


def test_baseline_comparison_produces_metrics():
    pack, _ = PackBuilder().build("Dengue warning signs in adults", force_mock_retrieval=True)
    comparison = BaselineAgent().compare("Dengue warning signs in adults", pack)
    assert comparison.baseline_claim_count >= 1
    assert 0 <= comparison.citation_coverage <= 1
