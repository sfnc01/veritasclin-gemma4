# Judging Strategy

VeritasClin Field is not Elicit, Consensus, Semantic Scholar, Perplexity, scite, or a generic PubMed chatbot.

It is a field-ready evidence system:

- Offline-first.
- Portable Evidence Packs.
- Claim Ledger as a central artifact.
- Safety-first prompt rewriting.
- Caution and conflict mapping.
- Gemma 4 positioned as a local reasoning layer.

## Impact

The primary user is a public health worker, clinician, researcher, or educator who needs accountable medical evidence under low-connectivity constraints.

## Technical Depth

The project combines retrieval, safety classification, PICO extraction, ranking,
synthesis, claim verification, caution mapping, evidence freshness, export,
baseline comparison, and offline pack Q&A.

## Accessibility

Mock mode runs without credentials. PubMed and Ollama/Gemma are optional enhancements.
Credentialed PubMed tests can run locally with `.env`, while public contributors
still get a deterministic no-key path.

## Safety

The app refuses diagnosis, prescription, emergency triage, and patient-identifiable data.
