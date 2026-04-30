from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from veritasclin.schemas.caution import CautionItem, EvidenceFreshness
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.paper import PubMedPaper
from veritasclin.schemas.pico import PICOQuestion


class EvidencePack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pack_id: str
    title: str
    topic: str
    created_at: str
    last_pubmed_search_at: str
    language: str
    source: str = "PubMed/NCBI"
    pico: PICOQuestion
    pubmed_query: str
    papers: list[PubMedPaper] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    claim_ledger: list[Claim] = Field(default_factory=list)
    caution_map: list[CautionItem] = Field(default_factory=list)
    freshness: EvidenceFreshness
    executive_summary: str
    clinical_interpretation: str
    what_the_evidence_does_not_prove: list[str] = Field(default_factory=list)
    patient_friendly_explanation: str
    safety_notice: str
    citation_coverage: float
