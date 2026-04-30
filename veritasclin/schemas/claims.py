from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SupportStatus = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "uncertain",
]
RiskLevel = Literal["low", "medium", "high"]


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    claim_type: str
    support_status: SupportStatus
    pmids: list[str] = Field(default_factory=list)
    evidence_level: str
    risk_level: RiskLevel
    rationale: str
    limitation_note: str | None = None
