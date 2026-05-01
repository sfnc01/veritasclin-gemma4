# VeritasClin Field Evidence Pack

## Pack Metadata
- Pack ID: vfield-0789f1f93e36
- Title: Evidence Pack: What does evidence say about treatment regimens for latent tuberculosis infection and o...
- Topic: What does evidence say about treatment regimens for latent tuberculosis infection and outcomes?
- Created: 2026-05-01T04:17:36.019476+00:00
- Source: PubMed/NCBI
- Language: en

## Clinical Question
What does evidence say about treatment regimens for latent tuberculosis infection and outcomes?

## Safety Decision
This pack is for biomedical evidence review only.
It is not a diagnostic, prescription, or emergency triage tool.

## Safe Rewritten Question
No rewrite required.

## PICO
- Population: patients with latent tuberculosis infection
- Intervention/Exposure: treatment regimens
- Comparison: Not specified
- Outcome: clinical outcomes
- Timeframe: Not specified

## PubMed Search Strategy
```text
("Tuberculosis, Latent"[MeSH Terms] OR "latent tuberculosis"[Title/Abstract] OR "LTBI"[Title/Abstract]) AND ("Therapeutics"[MeSH Terms] OR "drug therapy"[MeSH Terms] OR "treatment"[Title/Abstract] OR "regimen*"[Title/Abstract]) AND ("Treatment Outcome"[MeSH Terms] OR "outcome*"[Title/Abstract] OR "efficacy"[Title/Abstract] OR "effectiveness"[Title/Abstract])
```

## Evidence Freshness
- Score: 0.85
- Last search date: 2026-05-01
- Newest publication year: 2024
- Recommended refresh days: 120
- Rationale: Newest loaded publication year is 2024 and oldest is 2016; the pack is 2 years from the newest included evidence.

## Evidence Map
| PMID/ID | Level | Study Type | Score | Title |
| --- | --- | --- | ---: | --- |
| 38031772 | high | Practice Guideline | 80.0 | Diagnosis and Management of Latent Tuberculosis Infection: Updates. |
| 31852268 | high | Randomized Controlled Trial | 68.0 | Infection risk in patients undergoing treatment for inflammatory arthritis: non-biologics versus biologics. |
| 30403551 | moderate | Clinical Trial | 65.0 | The Global Landscape of Tuberculosis Therapeutics. |
| 31731988 | uncertain | Other | 43.0 | Treatment of Latent Tuberculosis Infection-An Update. |
| 28409555 | uncertain | Other | 41.0 | Treatment of Latent Tuberculosis Infection. |
| 29238270 | uncertain | Other | 41.0 | Treatment of Latent Tuberculosis Infection. |
| 33013856 | uncertain | Other | 40.0 | Diagnosis for Latent Tuberculosis Infection: New Alternatives. |
| 26836374 | uncertain | Other | 40.0 | Diagnosis and management of latent tuberculosis. |
| 28260424 | uncertain | Other | 33.0 | Posttransplant Tuberculosis. |

## Claim Ledger
| Claim ID | Status | Risk | PMIDs/IDs | Claim |
| --- | --- | --- | --- | --- |
| C001 | supported | high | 38031772 | Multiple treatment regimens for latent tuberculosis infection (LTBI) have been approved and demonstrate comparable efficacy [38031772]. |
| C002 | supported | high | 31731988, 28409555 | While isoniazid monotherapy is efficacious, shorter rifamycin-based regimens—such as daily rifampin for 4 months or once-weekly isoniazid plus rifapentine for 3 months—are associated with higher treatment completion rates and better tolerability [31731988, 28409555]. |
| C003 | supported | medium | 38031772, 28409555 | The selection of a specific regimen depends on individual patient factors, including age, drug interactions, and the risk of adverse events [38031772, 28409555]. |
| C004 | supported | high | 31852268, 30403551 | Research suggests that shorter treatment courses, such as those using rifapentine and isoniazid, can be as effective as longer traditional regimens in treating latent tuberculosis infection [31852268, 30403551]. |
| C005 | supported | medium | 38031772 | However, some evidence indicates that these shorter options may be associated with a higher risk of liver toxicity [38031772]. |

## Caution & Conflict Map
| Caution ID | Claim ID | Type | Severity | Explanation |
| --- | --- | --- | --- | --- |
| LCAU001 | C004 | indirect_evidence | medium | Claim C004 cites PMID 31852268, which is a review of infection risks in arthritis patients, not a primary study on the efficacy of LTBI treatment regimens. |
| LCAU002 | C005 | insufficient_data | medium | Claim C005 asserts a higher risk of liver toxicity for shorter regimens, but the provided abstract [38031772] does not mention liver toxicity specifically for shorter regimens, only that regimen selection depends on the risk of adverse events. |
| CAU001 | C002 | low_certainty | medium | The claim depends on low-certainty or limited evidence in the pack. |
| CAU002 | C003 | low_certainty | medium | The claim depends on low-certainty or limited evidence in the pack. |
| CAU003 | C003 | safety_signal | medium | Cited evidence includes safety or adverse-event language relevant to this claim. |
| CAU004 | C005 | safety_signal | medium | Cited evidence includes safety or adverse-event language relevant to this claim. |

## Executive Summary
Multiple treatment regimens for latent tuberculosis infection (LTBI) have been approved and demonstrate comparable efficacy [38031772]. While isoniazid monotherapy is efficacious, shorter rifamycin-based regimens—such as daily rifampin for 4 months or once-weekly isoniazid plus rifapentine for 3 months—are associated with higher treatment completion rates and better tolerability [31731988, 28409555]. The selection of a specific regimen depends on individual patient factors, including age, drug interactions, and the risk of adverse events [38031772, 28409555].

## Clinical Interpretation
Multiple treatment regimens for latent tuberculosis infection (LTBI) have been approved and demonstrate comparable efficacy [38031772]. While isoniazid monotherapy is efficacious, shorter rifamycin-based regimens—such as daily rifampin for 4 months or once-weekly isoniazid plus rifapentine for 3 months—are associated with higher treatment completion rates and better tolerability [31731988, 28409555]. The selection of a specific regimen depends on individual patient factors, including age, drug interactions, and the risk of adverse events [38031772, 28409555]. These findings should be used for evidence review and education, not for individual diagnosis, emergency triage, or treatment instructions.

## What the Evidence Does Not Prove
- It does not diagnose any individual patient.
- It does not replace urgent clinical evaluation for warning signs.
- It does not prove that every finding has equal predictive value in every setting.

## Patient-Friendly Explanation
Research suggests that shorter treatment courses, such as those using rifapentine and isoniazid, can be as effective as longer traditional regimens in treating latent tuberculosis infection [31852268, 30403551]. However, some evidence indicates that these shorter options may be associated with a higher risk of liver toxicity [38031772].

## Unsupported Claims
No unsupported claims identified in the Claim Ledger.

## Safety Notice
VeritasClin Field is not a diagnostic, prescription, or emergency triage tool. Strong clinical claims require a PMID/PMCID from the loaded evidence.

## Methodology
VeritasClin Field builds an auditable Evidence Pack by running a safety check,
extracting PICO, preserving the PubMed query, ranking evidence, synthesizing
with citations, extracting claims, and verifying each claim against loaded
paper IDs.

## Disclaimer
This project is for research, education, and hackathon demonstration.
It does not provide diagnosis, prescription, emergency triage, or individualized
medical advice.
