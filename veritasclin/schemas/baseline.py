from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaselineComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline_answer: str
    baseline_claim_count: int
    baseline_unsupported_claim_count: int
    baseline_high_risk_unsupported_count: int
    veritasclin_claim_count: int
    veritasclin_unsupported_claim_count: int
    citation_coverage: float
    summary: str
