# Evaluation

VeritasClin Field uses simple, inspectable metrics because healthcare evidence tools should be easy to challenge.

## Metrics

| Metric | What it checks |
| --- | --- |
| `citation_coverage` | Fraction of claims linked to pack evidence |
| `unsupported_claim_count` | Claims without sufficient cited support |
| `high_risk_unsupported_claim_count` | Higher-risk unsupported claims |
| `baseline_vs_veritasclin_delta` | Difference between plain model and VeritasClin unsupported claims |
| `pack_reproducibility_present` | Whether question, query, source records, claims, and exports are present |
| `safety_rewrite_success` | Whether unsafe prompts are rewritten or blocked correctly |

## Citation Coverage

The system extracts clinically meaningful claims and checks whether each claim has supporting PMIDs or explicit mock evidence IDs. Coverage is not a claim of truth; it is a signal that the answer is auditable.

## Unsupported Claim Detection

Strong clinical claims without cited evidence are marked `unsupported`. This is the core safety and audit behavior behind the rule:

> No PMID/PMCID or explicit mock evidence ID, no strong clinical claim.

## Baseline Comparison

The baseline path asks a plain model for an answer without PubMed retrieval. VeritasClin then compares:

- baseline claim count;
- baseline unsupported claims;
- baseline high-risk unsupported claims;
- VeritasClin unsupported claims;
- citation coverage.

The goal is not to embarrass a model. The goal is to show why portable evidence structure matters.

## Safety Tests

Tests cover:

- general evidence questions are allowed;
- dosing prompts are safely rewritten;
- emergency requests are blocked;
- uncited strong clinical claims are flagged;
- offline Q&A refuses unsupported answers.

## Offline Reproducibility

Offline tests monkeypatch retrieval paths so PubMed cannot be called. A valid offline answer must come from the loaded pack only.

## PubMed Integration Gate

Mock tests run without credentials. When `.env` includes `NCBI_API_KEY` and `NCBI_EMAIL`, integration tests also verify:

- PubMed search returns real numeric PMIDs;
- Entrez History Server metadata can be returned for audit;
- PubMed fetch returns parseable paper metadata;
- the dengue workflow builds a `PubMed/NCBI` Evidence Pack;
- failure paths do not print or expose secrets.
