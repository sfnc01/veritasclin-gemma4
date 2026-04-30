# Judging Strategy

VeritasClin Field is built to be understood quickly: it is an evidence-pack system for medical teams, not a generic research chatbot.

## Differentiation

| Judge question | Answer |
| --- | --- |
| Is this just PubMed search plus a summary? | No. The output is a portable Evidence Pack with a Claim Ledger, caution map, freshness score, exports, and offline Q&A. |
| Is this an AI doctor? | No. It blocks diagnosis, prescription, emergency triage, and patient-identifiable data. |
| Is this a clone of Elicit, Consensus, Perplexity, Semantic Scholar, or scite? | No. Those are online research assistants. VeritasClin is offline-first and audit-pack centered. |
| Can it run without credentials? | Yes. Mock mode supports a deterministic full demo without fake PMIDs. |
| Can it use real evidence? | Yes. PubMed/NCBI mode uses E-utilities with API key, email, cache, rate limit, and graceful failure handling. |

## Why It Is Not Just RAG Over PubMed

Standard RAG usually retrieves documents and produces an answer. VeritasClin creates a durable review artifact:

- the query is visible;
- source papers are preserved;
- claims are extracted into a ledger;
- unsupported claims are flagged;
- cautions are mapped;
- exports can be reviewed offline;
- offline answers are constrained to the pack.

The main object is not a chat response. It is an Evidence Pack.

## Why Gemma 4 Is Central

Gemma 4 is the local reasoning layer for:

- PICO extraction;
- safe rewriting;
- evidence synthesis;
- patient-friendly explanation;
- offline pack Q&A;
- baseline comparison.

Deterministic code handles safety gates, ranking heuristics, citation coverage, unsupported claim detection, and pack serialization. This division keeps the system useful while reducing the risk of unconstrained medical prose.

## Health And Social Impact

The target user is a public health worker, clinician, researcher, or educator who needs accountable evidence in constrained settings. The dengue demo shows why offline portability matters: evidence can be prepared online and used later where connectivity, privacy, or accountability constraints are real.

## What Judges Should Look For

1. Build the dengue Evidence Pack.
2. Inspect the PubMed query and Evidence Map.
3. Open the Claim Ledger and find cited claims.
4. Open the Caution & Conflict Map.
5. Load the pack offline.
6. Ask: `Quais sinais indicam maior risco de dengue grave?`
7. Confirm the answer cites pack claims and PMIDs.
8. Try: `What dose of semaglutide should I take if I have CKD?`
9. Confirm the safety rewrite avoids individualized dosing advice.

## Winning Message

VeritasClin Field shows that medical AI can be useful without pretending to be a clinician. It carries evidence, constraints, uncertainty, and auditability into the places where answers alone are not enough.
