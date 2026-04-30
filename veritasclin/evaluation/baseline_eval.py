from __future__ import annotations

from veritasclin.schemas.baseline import BaselineComparison


def baseline_vs_veritasclin_delta(comparison: BaselineComparison) -> int:
    return (
        comparison.baseline_unsupported_claim_count - comparison.veritasclin_unsupported_claim_count
    )


def pack_reproducibility_present(comparison: BaselineComparison) -> bool:
    return comparison.citation_coverage > 0
