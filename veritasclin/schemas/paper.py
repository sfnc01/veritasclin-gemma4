from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PubMedPaper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pmid: str
    pmcid: str | None = None
    title: str
    abstract: str | None = None
    journal: str | None = None
    publication_year: int | None = None
    authors: list[str] = Field(default_factory=list)
    doi: str | None = None
    publication_types: list[str] = Field(default_factory=list)
    mesh_terms: list[str] = Field(default_factory=list)
    url: str
