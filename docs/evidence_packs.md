# Evidence Packs

An Evidence Pack is the core artifact of VeritasClin Field: a portable, audit-ready record of a medical evidence review.

## What A Pack Contains

| Section | Purpose |
| --- | --- |
| Metadata | Pack ID, title, topic, creation time, source, and language |
| Safety context | Original question, rewritten question when needed, and safety notice |
| PICO | Population, intervention, comparison, outcome, timeframe, study preferences |
| PubMed strategy | Visible query and last search timestamp |
| Papers | PubMed records or clearly labeled mock records |
| Evidence map | Ranked evidence items with rationale, findings, and limitations |
| Claim Ledger | Clinically meaningful claims with support status and citations |
| Caution map | Low certainty, indirect evidence, mismatch, or safety-signal notes |
| Freshness | Newest/oldest years, score, and refresh recommendation |
| Summaries | Executive, clinical, patient-friendly, and "does not prove" sections |

## Example Export Tree

```text
examples/dengue_severe_adults_pack/
  pack.json
  dossier.md
  claim_ledger.csv
  caution_map.json
```

`pack.json` is the portable source of truth. The Markdown and CSV files are human-readable review artifacts for clinicians, educators, reviewers, and judges.

## Portability

A pack can be built online, moved as a file, and loaded later in a low-connectivity setting. Offline Q&A reads only the loaded pack. It does not perform new PubMed retrieval.

## Auditability

The pack keeps:

- The original clinical evidence question.
- The safe rewritten question, when applicable.
- The PICO extraction.
- The exact PubMed query.
- The search timestamp.
- The source papers.
- The claim ledger.
- Caution and freshness metadata.

This makes the answer traceable back to the evidence that traveled with it.

## Reproducibility

Another reviewer can inspect the pack, rerun the visible query, compare PMIDs, and review each claim's support status. Mock packs are labeled as mock demo data and never use fake real PMIDs.

## Why This Is Not Just A Chat Transcript

| Chat transcript | Evidence Pack |
| --- | --- |
| Hard to audit after the fact | Structured JSON and export files |
| Claims mixed into prose | Claims separated into a ledger |
| Citations may be lost | PMIDs travel with the pack |
| Requires online context | Can be loaded offline |
| Often model-dependent | Reproducible artifact with deterministic checks |
