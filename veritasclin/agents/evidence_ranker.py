from __future__ import annotations

import re

from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.paper import PubMedPaper
from veritasclin.schemas.pico import PICOQuestion

STUDY_BOOSTS = {
    "systematic review": 35,
    "meta-analysis": 35,
    "practice guideline": 32,
    "guideline": 30,
    "randomized controlled trial": 28,
    "clinical trial": 22,
    "cohort": 16,
    "observational study": 12,
    "case report": -12,
}


class EvidenceRanker:
    def rank(self, papers: list[PubMedPaper], pico: PICOQuestion) -> list[EvidenceItem]:
        query_terms = _keywords(
            " ".join(
                item
                for item in [
                    pico.population,
                    pico.intervention,
                    pico.comparison,
                    pico.outcome,
                    pico.original_question,
                ]
                if item
            )
        )
        items = [self._score_paper(paper, query_terms) for paper in papers]
        return sorted(items, key=lambda item: item.relevance_score, reverse=True)

    def _score_paper(self, paper: PubMedPaper, query_terms: set[str]) -> EvidenceItem:
        publication_types = " ".join(paper.publication_types).lower()
        title_abstract = (
            f"{paper.title} {paper.abstract or ''} {' '.join(paper.mesh_terms)}".lower()
        )
        overlap = len(query_terms.intersection(_keywords(title_abstract)))
        score = 10.0 + min(overlap * 4, 28)

        study_type = "Other"
        for label, boost in STUDY_BOOSTS.items():
            if label in publication_types or label in title_abstract:
                score += boost
                study_type = label.title()
                break
        if paper.abstract:
            score += 8
        else:
            score -= 8
        if paper.publication_year:
            score += max(0, min(12, paper.publication_year - 2014))
        if "animals" in title_abstract and "humans" not in title_abstract:
            score -= 15
        evidence_level = _evidence_level(study_type)
        rationale = (
            f"Ranked by study type ({study_type}), PICO term overlap ({overlap}), "
            f"abstract availability, and publication year."
        )
        findings = _findings_from_abstract(paper)
        limitations = []
        if not paper.abstract:
            limitations.append("No abstract available for automated evidence extraction.")
        if study_type == "Other":
            limitations.append(
                "Publication type does not clearly identify a high-level clinical design."
            )
        return EvidenceItem(
            paper=paper,
            relevance_score=round(score, 2),
            evidence_level=evidence_level,
            study_type=study_type,
            rationale=rationale,
            key_findings=findings,
            limitations=limitations,
        )


def _keywords(text: str) -> set[str]:
    stopwords = {
        "what",
        "does",
        "recent",
        "evidence",
        "say",
        "about",
        "with",
        "and",
        "the",
        "for",
        "into",
        "from",
        "clinical",
        "patients",
    }
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", text.lower())
        if token not in stopwords
    }


def _evidence_level(study_type: str) -> str:
    lowered = study_type.lower()
    if any(value in lowered for value in ["systematic", "meta", "guideline", "randomized"]):
        return "high"
    if any(value in lowered for value in ["clinical trial", "cohort", "observational"]):
        return "moderate"
    if "case" in lowered:
        return "low"
    return "uncertain"


def _findings_from_abstract(paper: PubMedPaper) -> list[str]:
    if not paper.abstract:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", paper.abstract)
    return [sentence.strip() for sentence in sentences[:2] if len(sentence.strip()) > 20]
