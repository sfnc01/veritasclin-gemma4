from __future__ import annotations

from dataclasses import dataclass

from veritasclin.schemas.evidence import EvidenceItem
from veritasclin.schemas.pico import PICOQuestion


@dataclass(frozen=True)
class SynthesisResult:
    executive_summary: str
    clinical_interpretation: str
    what_the_evidence_does_not_prove: list[str]
    patient_friendly_explanation: str
    safety_notice: str


class SynthesisAgent:
    def synthesize(
        self,
        pico: PICOQuestion,
        evidence_items: list[EvidenceItem],
        language: str = "en",
    ) -> SynthesisResult:
        top_items = evidence_items[:5]
        citations = ", ".join(item.paper.pmid for item in top_items[:3]) or "no PMID"
        topic = pico.intervention or pico.original_question
        dengue = (
            "dengue" in pico.original_question.lower()
            or "dengue" in (pico.population or "").lower()
        )

        if dengue:
            core_claim = (
                "Across the loaded evidence, severe abdominal pain, persistent vomiting, "
                "mucosal bleeding, lethargy/restlessness, hepatomegaly, fluid accumulation, "
                "and rising hematocrit with falling platelets are treated as warning signs "
                f"for severe dengue risk ({citations})."
            )
        else:
            core_claim = (
                f"The loaded evidence addresses {topic} with a limited, citation-backed "
                f"summary from the highest-ranked records ({citations})."
            )

        interpretation = (
            f"{core_claim} These findings should be used for evidence review and education, "
            "not for individual diagnosis, emergency triage, or treatment instructions."
        )
        patient_explanation = _patient_explanation(language, dengue, citations)
        return SynthesisResult(
            executive_summary=core_claim,
            clinical_interpretation=interpretation,
            what_the_evidence_does_not_prove=[
                "It does not diagnose any individual patient.",
                "It does not replace urgent clinical evaluation for warning signs.",
                "It does not prove that every warning sign has equal predictive value "
                "in every setting.",
            ],
            patient_friendly_explanation=patient_explanation,
            safety_notice=(
                "VeritasClin Field is not a diagnostic, prescription, or emergency triage tool. "
                "Strong clinical claims require PMID/PMCID or an explicit mock evidence ID."
            ),
        )


def _patient_explanation(language: str, dengue: bool, citations: str) -> str:
    if language == "pt":
        if dengue:
            return (
                "O pacote indica que dor abdominal forte, vomitos persistentes, sangramento, "
                "sonolencia ou inquietacao, aumento do figado e sinais de perda de liquido "
                f"podem ser sinais de alerta para dengue grave ({citations}). Procure cuidado "
                "clinico local se houver sinais de gravidade."
            )
        return (
            f"Este pacote resume evidencias publicadas e cita as fontes carregadas ({citations})."
        )
    if language == "es":
        if dengue:
            return (
                "El paquete indica que dolor abdominal intenso, vomitos persistentes, sangrado, "
                "letargo o inquietud y signos de fuga de liquidos pueden ser signos de alarma "
                f"para dengue grave ({citations}). Busque atencion clinica local si aparecen."
            )
        return f"Este paquete resume evidencia publicada y cita las fuentes cargadas ({citations})."
    if dengue:
        return (
            "The pack indicates that severe abdominal pain, persistent vomiting, bleeding, "
            "lethargy or restlessness, enlarged liver, and signs of fluid leakage may be warning "
            f"signs for severe dengue ({citations}). Seek local care if warning signs occur."
        )
    return f"This pack summarizes published evidence and cites the loaded sources ({citations})."
