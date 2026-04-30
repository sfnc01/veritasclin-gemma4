# Architecture

VeritasClin Field is organized around one artifact: the Evidence Pack. The online build path gathers and verifies evidence; the offline path only reads the pack.

```mermaid
flowchart TD
  A["Question"] --> B["SafetyGuard"]
  B --> C["PICOAgent"]
  C --> D["QueryAgent"]
  D --> E["PubMed/NCBI"]
  E --> F["EvidenceRanker"]
  F --> G["SynthesisAgent"]
  G --> H["ClaimExtractor"]
  H --> I["ClaimVerifier"]
  I --> J["CautionMapper"]
  J --> K["FreshnessScorer"]
  K --> L["EvidencePack JSON/Markdown/CSV"]
  L --> M["Offline Pack Loader"]
  M --> N["OfflineQA"]
```

## Online Build Mode

The build path performs safety checking, PICO extraction, auditable query generation, PubMed retrieval when configured, ranking, synthesis, claim verification, caution mapping, and export.

If PubMed credentials are configured, the app uses NCBI E-utilities and caches responses.
If credentials or retrieval fail, the UI clearly labels mock fallback data.

## Offline Query Mode

Offline mode loads `pack.json` and answers only from the included papers, evidence items, and Claim Ledger. It does not call PubMed or any external retrieval service.
