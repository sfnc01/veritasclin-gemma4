from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PICOQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_question: str
    safe_rewritten_question: str | None = None
    population: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    outcome: str | None = None
    timeframe: str | None = None
    preferred_study_types: list[str] = Field(default_factory=list)
    language: str = "en"
