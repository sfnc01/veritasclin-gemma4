# 3-Minute Demo Script

Main use case: severe dengue warning signs in adults.

## 0:00 - 0:20 Problem

"Medical AI should not just answer. It should carry its evidence with it."

Show the VeritasClin Field landing view. Explain the field setting: a public health worker needs trustworthy dengue evidence where connectivity may be unreliable.

## 0:20 - 0:45 Build The Pack

Select the dengue demo question:

```text
What does recent evidence say about warning signs for severe dengue in adults?
```

Run the workflow. Point out:
- The green **ALLOWED** safety badge (question cleared).
- The pipeline steps — safety check → PICO extraction → Gemma 4 function-calling query build → PubMed retrieval → evidence ranking → Gemma 4 synthesis.

## 0:45 - 1:20 Evidence Pack

Show the generated pack using the six tabs:

- **Pack Summary** — executive summary, clinical interpretation, what the evidence does not prove, patient-friendly explanation.
- **PICO & Query** — structured P/I/C/O framework cards; PubMed query string; query method badge showing `Gemma 4 native function calling`.
- **Evidence Map** — ranked papers table with study type, evidence level, and relevance score.
- **Claim Ledger** — each clinical claim with support-status pill (Supported / Partial / Unsupported), risk level, evidence level, and cited IDs.
- **Caution Map** — uncertainty signals with severity indicators.
- **Exports** — download `pack.json`, `dossier.md`, `claim_ledger.csv`, `caution_map.json`.

Narration: "The answer is not the product. The pack is the product."

## 1:20 - 1:55 Offline Portuguese Q&A

Switch to Load Offline Pack mode. Load `pack.json`.

Ask:

```text
Quais sinais indicam maior risco de dengue grave?
```

Show that the answer cites claims and PMIDs already inside the pack. Emphasize that no PubMed retrieval is being used in offline mode.

## 1:55 - 2:25 Baseline Comparison

Show Plain Gemma vs VeritasClin:

- unsupported claims;
- high-risk unsupported claims;
- citation coverage;
- reproducibility status.

Narration: "The difference is not just better prose. It is a portable audit trail."

## 2:25 - 2:50 Safety Rewrite

Enter the unsafe dosing prompt:

```text
What dose of semaglutide should I take if I have CKD?
```

Show that VeritasClin refuses individualized dosing advice and rewrites it as a research question about dosing regimens studied in clinical trials.

## 2:50 - 3:00 Close

"VeritasClin Field turns PubMed into offline, multilingual, audit-ready Evidence Packs for healthcare teams working under low-connectivity, high-risk, and high-accountability conditions."
