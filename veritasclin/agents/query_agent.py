from __future__ import annotations

from veritasclin.schemas.pico import PICOQuestion
from veritasclin.tools.pubmed import build_pubmed_query


class QueryAgent:
    def build(self, pico: PICOQuestion, max_terms: int = 12) -> str:
        return build_pubmed_query(pico, max_terms=max_terms)
