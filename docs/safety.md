# Safety

VeritasClin Field is an evidence review system. It is not a diagnosis, prescription, or emergency triage tool.

## Product Boundaries

| Request | Behavior |
| --- | --- |
| General biomedical evidence question | Allowed |
| Literature summary | Allowed |
| Patient-friendly general education | Allowed |
| Individual diagnosis | Blocked |
| Emergency triage | Blocked with urgent-care language |
| Medication start/stop instructions | Blocked |
| Individual dosing advice | Rewritten when safe |
| Identifiable patient records | Blocked |

## SafetyGuard

`SafetyGuard` runs before PICO extraction, retrieval, synthesis, and offline Q&A. It classifies prompts into categories such as:

- `general_research_question`
- `diagnosis_request`
- `prescription_or_dosing_request`
- `medication_change_request`
- `emergency_request`
- `identifiable_patient_data`
- `unsupported_medical_advice_request`

The goal is to allow legitimate evidence questions while refusing individualized medical advice.

## Safety Rewriter

Some risky prompts can be converted into research questions.

| Input | Safe rewrite |
| --- | --- |
| `What dose of semaglutide should I take if I have CKD?` | `What semaglutide dosing regimens have been studied in clinical trials involving patients with chronic kidney disease?` |

The rewritten prompt can support evidence review, but it does not provide personal dosing instructions.

## Hard Evidence Rule

**No PMID/PMCID or explicit mock evidence ID, no strong clinical claim.**

The Claim Verifier marks strong uncited clinical claims as unsupported. This rule is intentionally simple and conservative for a hackathon MVP.

## Offline Safety

Offline Q&A uses only loaded pack contents. If the answer is not supported by the pack, the system says the pack does not contain enough evidence instead of improvising.

## Disclaimer Language

VeritasClin Field is for biomedical evidence review and education. It does not provide diagnosis, prescription, emergency triage, or individualized medical advice. Healthcare decisions should be made by qualified professionals using local clinical protocols and current evidence.
