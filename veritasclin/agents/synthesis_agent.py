from __future__ import annotations

from veritasclin.llm import LLMProvider, get_llm_provider
from veritasclin.llm.prompts import SYNTHESIS_SYSTEM_PROMPT
from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.pico import PICOQuestion


class SynthesisResult:
    def __init__(
        self,
        executive_summary: str,
        clinical_interpretation: str,
        what_the_evidence_does_not_prove: list[str],
        patient_friendly_explanation: str,
        safety_notice: str,
    ) -> None:
        self.executive_summary = executive_summary
        self.clinical_interpretation = clinical_interpretation
        self.what_the_evidence_does_not_prove = what_the_evidence_does_not_prove
        self.patient_friendly_explanation = patient_friendly_explanation
        self.safety_notice = safety_notice


_SAFETY_NOTICE = (
    "VeritasClin Field is not a diagnostic, prescription, or emergency triage tool. "
    "Strong clinical claims require PMID/PMCID or an explicit mock evidence ID."
)

_WHAT_DOES_NOT_PROVE = [
    "It does not diagnose any individual patient.",
    "It does not replace urgent clinical evaluation for warning signs.",
    "It does not prove that every warning sign has equal predictive value "
    "in every setting.",
]


class SynthesisAgent:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def synthesize(
        self,
        pico: PICOQuestion,
        evidence_items: list[EvidenceItem],
        language: str = "en",
    ) -> SynthesisResult:
        top_items = evidence_items[:5]
        user_prompt = _build_synthesis_prompt(pico, top_items, language)
        raw = self.provider.generate(SYNTHESIS_SYSTEM_PROMPT, user_prompt, temperature=0.1)
        executive_summary, clinical_interpretation = _parse_synthesis(raw, pico, top_items)
        patient_explanation = _patient_explanation_prompt(
            pico, top_items, language, self.provider
        )
        return SynthesisResult(
            executive_summary=executive_summary,
            clinical_interpretation=clinical_interpretation,
            what_the_evidence_does_not_prove=_WHAT_DOES_NOT_PROVE,
            patient_friendly_explanation=patient_explanation,
            safety_notice=_SAFETY_NOTICE,
        )


def _build_synthesis_prompt(
    pico: PICOQuestion,
    top_items: list[EvidenceItem],
    language: str,
) -> str:
    evidence_block = "\n".join(
        f"- ID: {item.paper.pmid} | Study: {item.study_type} | "
        f"Level: {item.evidence_level}\n  Abstract: {item.paper.abstract or '(no abstract)'}"
        for item in top_items
    )
    lang_instruction = {
        "pt": "Write the summary in Portuguese (Brazilian).",
        "es": "Write the summary in Spanish.",
    }.get(language, "Write the summary in English.")
    return (
        f"Clinical question: {pico.safe_rewritten_question or pico.original_question}\n"
        f"Population: {pico.population or 'not specified'}\n"
        f"Intervention/Exposure: {pico.intervention or 'not specified'}\n"
        f"Outcome: {pico.outcome or 'not specified'}\n\n"
        f"Loaded evidence (cite IDs inline — never invent new IDs):\n{evidence_block}\n\n"
        f"Instructions: Write a 2–3 sentence executive summary citing evidence IDs inline "
        f"(e.g. MOCK-DENGUE-001). Do not diagnose, prescribe, or give individualized advice. "
        f"Do not invent IDs not listed above. {lang_instruction}"
    )


def _parse_synthesis(
    raw: str,
    pico: PICOQuestion,
    top_items: list[EvidenceItem],
) -> tuple[str, str]:
    summary = raw.strip() if raw and len(raw.strip()) > 20 else _fallback_summary(pico, top_items)
    interpretation = (
        f"{summary} These findings should be used for evidence review and education, "
        "not for individual diagnosis, emergency triage, or treatment instructions."
    )
    return summary, interpretation


def _fallback_summary(pico: PICOQuestion, top_items: list[EvidenceItem]) -> str:
    citations = ", ".join(item.paper.pmid for item in top_items[:3]) or "no evidence loaded"
    topic = pico.intervention or pico.original_question
    return (
        f"The loaded evidence addresses {topic} with citation-backed findings ({citations}). "
        "Review the Claim Ledger for individual claim support status and evidence levels."
    )


def _patient_explanation_prompt(
    pico: PICOQuestion,
    top_items: list[EvidenceItem],
    language: str,
    provider: LLMProvider,
) -> str:
    citations = ", ".join(item.paper.pmid for item in top_items[:3]) or "no evidence loaded"
    lang_instruction = {
        "pt": "Write in simple Portuguese (Brazilian) for a non-specialist reader.",
        "es": "Write in simple Spanish for a non-specialist reader.",
    }.get(language, "Write in plain English for a non-specialist reader.")
    prompt = (
        f"In 1–2 sentences, explain what the evidence says about "
        f"'{pico.original_question}' in terms a patient or community health worker can "
        f"understand. Cite these source IDs: {citations}. "
        f"Do not diagnose or give individualized advice. {lang_instruction}"
    )
    raw = provider.generate(SYNTHESIS_SYSTEM_PROMPT, prompt, temperature=0.2)
    if raw and len(raw.strip()) > 20:
        return raw.strip()
    return (
        f"This pack summarizes published evidence and cites loaded sources ({citations}). "
        "Always seek local clinical care for individual health decisions."
    )
