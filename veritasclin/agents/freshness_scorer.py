from __future__ import annotations

from datetime import UTC, datetime

from veritasclin.schemas.caution import EvidenceFreshness
from veritasclin.schemas.evidence import EvidenceItem


class FreshnessScorer:
    def score(
        self, evidence_items: list[EvidenceItem], search_date: str | None = None
    ) -> EvidenceFreshness:
        years = [
            item.paper.publication_year
            for item in evidence_items
            if item.paper.publication_year is not None
        ]
        now = datetime.now(UTC)
        newest = max(years) if years else None
        oldest = min(years) if years else None
        if newest is None:
            score = 0.25
            refresh_days = 30
            rationale = "No publication years were available, so freshness is uncertain."
        else:
            age = max(0, now.year - newest)
            score = max(0.1, min(1.0, 1.0 - age * 0.12))
            refresh_days = 90 if age <= 2 else 60 if age <= 5 else 30
            rationale = (
                f"Newest loaded publication year is {newest}; "
                "refresh interval reflects evidence age."
            )
        return EvidenceFreshness(
            score=round(score, 2),
            last_search_date=search_date or now.date().isoformat(),
            newest_publication_year=newest,
            oldest_publication_year=oldest,
            recommended_refresh_days=refresh_days,
            rationale=rationale,
        )
