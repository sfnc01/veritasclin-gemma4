from __future__ import annotations

from veritasclin.schemas.pack import EvidencePack


def pack_to_markdown(pack: EvidencePack) -> str:
    claim_rows = "\n".join(
        f"| {claim.id} | {claim.support_status} | {claim.risk_level} | "
        f"{', '.join(claim.pmids) or 'None'} | {claim.text} |"
        for claim in pack.claim_ledger
    )
    evidence_rows = "\n".join(
        f"| {item.paper.pmid} | {item.evidence_level} | {item.study_type} | "
        f"{item.relevance_score} | {item.paper.title} |"
        for item in pack.evidence_items
    )
    caution_rows = "\n".join(
        f"| {item.id} | {item.claim_id} | {item.caution_type} | {item.severity} | "
        f"{item.explanation} |"
        for item in pack.caution_map
    )
    unsupported = "\n".join(
        f"- {claim.id}: {claim.text}"
        for claim in pack.claim_ledger
        if claim.support_status == "unsupported"
    )
    return f"""# VeritasClin Field Evidence Pack

## Pack Metadata
- Pack ID: {pack.pack_id}
- Title: {pack.title}
- Topic: {pack.topic}
- Created: {pack.created_at}
- Source: {pack.source}
- Language: {pack.language}

## Clinical Question
{pack.pico.original_question}

## Safety Decision
This pack is for biomedical evidence review only.
It is not a diagnostic, prescription, or emergency triage tool.

## Safe Rewritten Question
{pack.pico.safe_rewritten_question or "No rewrite required."}

## PICO
- Population: {pack.pico.population or "Not specified"}
- Intervention/Exposure: {pack.pico.intervention or "Not specified"}
- Comparison: {pack.pico.comparison or "Not specified"}
- Outcome: {pack.pico.outcome or "Not specified"}
- Timeframe: {pack.pico.timeframe or "Not specified"}

## PubMed Search Strategy
```text
{pack.pubmed_query}
```

## Evidence Freshness
- Score: {pack.freshness.score}
- Last search date: {pack.freshness.last_search_date}
- Newest publication year: {pack.freshness.newest_publication_year}
- Recommended refresh days: {pack.freshness.recommended_refresh_days}
- Rationale: {pack.freshness.rationale}

## Evidence Map
| PMID/ID | Level | Study Type | Score | Title |
| --- | --- | --- | ---: | --- |
{evidence_rows or "| None | None | None | 0 | No evidence loaded |"}

## Claim Ledger
| Claim ID | Status | Risk | PMIDs/IDs | Claim |
| --- | --- | --- | --- | --- |
{claim_rows or "| None | None | None | None | No claims extracted |"}

## Caution & Conflict Map
| Caution ID | Claim ID | Type | Severity | Explanation |
| --- | --- | --- | --- | --- |
{caution_rows or "| None | None | None | None | No cautions identified |"}

## Executive Summary
{pack.executive_summary}

## Clinical Interpretation
{pack.clinical_interpretation}

## What the Evidence Does Not Prove
{chr(10).join(f"- {item}" for item in pack.what_the_evidence_does_not_prove)}

## Patient-Friendly Explanation
{pack.patient_friendly_explanation}

## Unsupported Claims
{unsupported or "No unsupported claims identified in the Claim Ledger."}

## Safety Notice
{pack.safety_notice}

## Methodology
VeritasClin Field builds an auditable Evidence Pack by running a safety check,
extracting PICO, preserving the PubMed query, ranking evidence, synthesizing
with citations, extracting claims, and verifying each claim against loaded
paper IDs.

## Disclaimer
This project is for research, education, and hackathon demonstration.
It does not provide diagnosis, prescription, emergency triage, or individualized
medical advice.
"""
