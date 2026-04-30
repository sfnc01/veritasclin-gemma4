from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from veritasclin.schemas.paper import PubMedPaper


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper: PubMedPaper
    relevance_score: float
    evidence_level: str
    study_type: str
    rationale: str
    key_findings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
