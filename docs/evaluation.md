# Evaluation

VeritasClin Field uses simple, inspectable metrics rather than opaque scores.

- `citation_coverage`: fraction of claims with cited pack evidence.
- `unsupported_claim_count`: claims marked unsupported.
- `high_risk_unsupported_claim_count`: high-risk unsupported claims.
- `baseline_vs_veritasclin_delta`: reduction in unsupported claims versus plain model.
- `pack_reproducibility_present`: whether cited evidence is present.
- `safety_rewrite_success`: whether unsafe dosing prompts were safely rewritten.

Tests run in mock mode so contributors do not need NCBI or model credentials.

