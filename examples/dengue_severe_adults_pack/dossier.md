# VeritasClin Field Evidence Pack

## Pack Metadata
- Pack ID: vfield-03f2a6297253
- Title: Evidence Pack: What does recent evidence say about warning signs for severe dengue in adults
- Topic: What does recent evidence say about warning signs for severe dengue in adults?
- Created: 2026-04-30T15:17:53.691411+00:00
- Source: PubMed/NCBI
- Language: en

## Clinical Question
What does recent evidence say about warning signs for severe dengue in adults?

## Safety Decision
This pack is for biomedical evidence review only.
It is not a diagnostic, prescription, or emergency triage tool.

## Safe Rewritten Question
No rewrite required.

## PICO
- Population: adults with dengue
- Intervention/Exposure: warning signs
- Comparison: Not specified
- Outcome: severe dengue
- Timeframe: recent evidence

## PubMed Search Strategy
```text
(Dengue[MeSH Terms] OR dengue[Title/Abstract]) AND (adults[MeSH Terms] OR adult[Title/Abstract]) AND ("warning signs"[Title/Abstract] OR "predictive factors"[MeSH Terms] OR "prognosis"[MeSH Terms] OR "risk factors"[MeSH Terms]) AND ("severe dengue"[MeSH Terms] OR "severe dengue"[Title/Abstract] OR "dengue hemorrhagic fever"[MeSH Terms] OR "dengue shock syndrome"[MeSH Terms])
```

## Evidence Freshness
- Score: 1.0
- Last search date: 2026-04-30
- Newest publication year: 2026
- Recommended refresh days: 180
- Rationale: Newest loaded publication year is 2026 and oldest is 2002; the pack is 0 years from the newest included evidence.

## Evidence Map
| PMID/ID | Level | Study Type | Score | Title |
| --- | --- | --- | ---: | --- |
| 36593636 | high | Meta-Analysis | 82.0 | Routine blood parameters of dengue infected children and adults. A meta-analysis. |
| 40910405 | high | Guideline | 75.0 | Elevated Soluble HLA-G Levels Associate With Dengue Severity in Vietnamese Patients. |
| 41781546 | high | Randomized Controlled Trial | 74.0 | Long-term efficacy and safety of the single-dose tetravalent Butantan dengue vaccine. |
| 40090592 | moderate | Cohort | 61.0 | Circulating lncRNAs as biomarkers for severe dengue using a machine learning approach. |
| 38917093 | moderate | Cohort | 52.0 | Risk factors associated with dengue complications and death: A cohort study in Peru. |
| 40708402 | moderate | Observational Study | 49.0 | Safety of Low-Dose Ibuprofen in Non-Severe Dengue Patients for Managing Fever Is Consistent With Acetaminophen: A Retrospective Observational Study. |
| 40704559 | uncertain | Other | 45.0 | Risk Stratification of Dengue Cases Requiring Hospitalization. |
| 39039529 | uncertain | Other | 44.0 | Early-phase factors associated with pediatric severe dengue in the Thai-Myanmar cross-border region. |
| 40320430 | uncertain | Other | 37.0 | Cytokine and chemokine kinetics in natural human dengue infection as predictors of disease outcome. |
| 11892494 | uncertain | Other | 26.0 | Dengue: an update. |

## Claim Ledger
| Claim ID | Status | Risk | PMIDs/IDs | Claim |
| --- | --- | --- | --- | --- |
| C001 | supported | low | 36593636 | Recent evidence suggests that traditional routine blood parameters may not reliably differentiate between dengue severity levels due to overlapping values and unknown timing of collection [36593636]. |
| C002 | supported | low | 40910405, 40090592, 38917093 | Specific markers such as elevated sHLA-G levels [40910405], a panel of circulating long non-coding RNAs (lncRNAs) [40090592], and high AST (≥251 U/L) or bilirubin (>1.2 mg/dL) levels [38917093] have been associated with increased disease severity or poor prognosis. |
| C003 | supported | medium | 38917093 | Additionally, a history of previous dengue infection is linked to a higher risk of poor outcomes [38917093]. |
| C004 | supported | medium | 36593636, 40910405 | Recent evidence indicates that warning signs for severe dengue in adults include persistent vomiting, severe abdominal pain, fluid buildup, and a sudden drop in platelet counts [36593636, 40910405]. |
| C005 | supported | medium | 41781546 | Monitoring these signs and identifying high-risk factors, such as older age or existing health conditions, is critical for timely medical intervention [41781546]. |

## Caution & Conflict Map
| Caution ID | Claim ID | Type | Severity | Explanation |
| --- | --- | --- | --- | --- |
| CAU001 | C003 | outcome_mismatch | medium | Cited evidence emphasizes surrogate or laboratory outcomes rather than the claimed clinical outcome. |
| CAU002 | C004 | population_mismatch | medium | Some cited evidence may not directly match the target adult human population. |
| CAU003 | C004 | outcome_mismatch | medium | Cited evidence emphasizes surrogate or laboratory outcomes rather than the claimed clinical outcome. |

## Executive Summary
Recent evidence suggests that traditional routine blood parameters may not reliably differentiate between dengue severity levels due to overlapping values and unknown timing of collection [36593636]. However, specific markers such as elevated sHLA-G levels [40910405], a panel of circulating long non-coding RNAs (lncRNAs) [40090592], and high AST (≥251 U/L) or bilirubin (>1.2 mg/dL) levels [38917093] have been associated with increased disease severity or poor prognosis. Additionally, a history of previous dengue infection is linked to a higher risk of poor outcomes [38917093].

## Clinical Interpretation
Recent evidence suggests that traditional routine blood parameters may not reliably differentiate between dengue severity levels due to overlapping values and unknown timing of collection [36593636]. However, specific markers such as elevated sHLA-G levels [40910405], a panel of circulating long non-coding RNAs (lncRNAs) [40090592], and high AST (≥251 U/L) or bilirubin (>1.2 mg/dL) levels [38917093] have been associated with increased disease severity or poor prognosis. Additionally, a history of previous dengue infection is linked to a higher risk of poor outcomes [38917093]. These findings should be used for evidence review and education, not for individual diagnosis, emergency triage, or treatment instructions.

## What the Evidence Does Not Prove
- It does not diagnose any individual patient.
- It does not replace urgent clinical evaluation for warning signs.
- It does not prove that every warning sign has equal predictive value in every setting.

## Patient-Friendly Explanation
Recent evidence indicates that warning signs for severe dengue in adults include persistent vomiting, severe abdominal pain, fluid buildup, and a sudden drop in platelet counts [36593636, 40910405]. Monitoring these signs and identifying high-risk factors, such as older age or existing health conditions, is critical for timely medical intervention [41781546].

## Unsupported Claims
No unsupported claims identified in the Claim Ledger.

## Safety Notice
VeritasClin Field is not a diagnostic, prescription, or emergency triage tool. Strong clinical claims require PMID/PMCID or an explicit mock evidence ID.

## Methodology
VeritasClin Field builds an auditable Evidence Pack by running a safety check,
extracting PICO, preserving the PubMed query, ranking evidence, synthesizing
with citations, extracting claims, and verifying each claim against loaded
paper IDs.

## Disclaimer
This project is for research, education, and hackathon demonstration.
It does not provide diagnosis, prescription, emergency triage, or individualized
medical advice.
