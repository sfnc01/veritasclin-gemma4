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
            score = 0.2
            refresh_days = 30
            rationale = (
                "No publication years were available, so freshness is uncertain and should "
                "be refreshed before field use."
            )
        else:
            age = max(0, now.year - newest)
            if age <= 1:
                score = 1.0
                refresh_days = 180
            elif age <= 3:
                score = 0.85
                refresh_days = 120
            elif age <= 5:
                score = 0.7
                refresh_days = 90
            elif age <= 10:
                score = 0.5
                refresh_days = 60
            else:
                score = 0.3
                refresh_days = 30
            rationale = (
                f"Newest loaded publication year is {newest} and oldest is {oldest}; "
                f"the pack is {age} years from the newest included evidence."
            )
        return EvidenceFreshness(
            score=round(score, 2),
            last_search_date=search_date or now.date().isoformat(),
            newest_publication_year=newest,
            oldest_publication_year=oldest,
            recommended_refresh_days=refresh_days,
            rationale=rationale,
        )
