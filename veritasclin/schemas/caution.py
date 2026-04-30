from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CautionType = Literal[
    "conflicting_results",
    "population_mismatch",
    "outcome_mismatch",
    "low_certainty",
    "safety_signal",
    "insufficient_data",
    "indirect_evidence",
]
Severity = Literal["low", "medium", "high"]


class CautionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    claim_id: str
    supporting_pmids: list[str] = Field(default_factory=list)
    cautionary_pmids: list[str] = Field(default_factory=list)
    caution_type: CautionType
    explanation: str
    severity: Severity


class EvidenceFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float
    last_search_date: str
    newest_publication_year: int | None = None
    oldest_publication_year: int | None = None
    recommended_refresh_days: int
    rationale: str
