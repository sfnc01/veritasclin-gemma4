from __future__ import annotations

from veritasclin.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        combined = f"{system_prompt}\n{user_prompt}".lower()

        # Synthesis call — detected by the evidence-ID citation instruction
        if "cite ids inline" in combined or "cite these source ids" in combined:
            return _mock_synthesis(combined)

        # Baseline / plain model call
        if "plain medical assistant" in combined or "without retrieval" in combined:
            return _mock_baseline(combined)

        # Legacy path: direct language hints in prompt
        if "portuguese" in combined or "portugues" in combined or "quais sinais" in combined:
            return (
                "Com base apenas no pacote carregado, sinais de alerta para dengue grave "
                "incluem dor abdominal intensa, vomitos persistentes, sangramento de mucosa, "
                "letargia, hepatomegalia e sinais de extravasamento plasmatico. Ver Claim "
                "Ledger para PMIDs ou IDs mock associados."
            )
        if "spanish" in combined or "espanol" in combined:
            return (
                "Segun el paquete cargado, los signos de alarma incluyen dolor abdominal, "
                "vomitos persistentes, sangrado de mucosas, letargo y signos de fuga plasmatica."
            )

        return (
            "Mock Gemma output: the evidence pack should be used to answer with cited, "
            "auditable claims rather than unsupported medical advice."
        )


def _mock_synthesis(prompt: str) -> str:
    if "dengue" in prompt:
        return (
            "Across the loaded evidence, severe abdominal pain, persistent vomiting, "
            "mucosal bleeding, lethargy/restlessness, hepatomegaly, fluid accumulation, "
            "and rising hematocrit with falling platelets are warning signs for severe "
            "dengue risk (MOCK-DENGUE-001, MOCK-DENGUE-002, MOCK-DENGUE-003). "
            "High-certainty evidence supports clinical vigilance for these signs in adults "
            "(MOCK-DENGUE-001)."
        )
    if "semaglutide" in prompt or "ckd" in prompt or "kidney" in prompt:
        return (
            "The loaded evidence describes studied semaglutide dosing regimens and kidney "
            "outcomes in chronic kidney disease populations (MOCK-SEMAGLUTIDE-001). "
            "This is a summary of published trial evidence, not individualized dosing advice "
            "(MOCK-SEMAGLUTIDE-001)."
        )
    if "cannabis" in prompt or "cannabinoid" in prompt or "neuropathic" in prompt:
        return (
            "The loaded evidence reports modest pain reduction with cannabinoids in some "
            "neuropathic pain trials, with dizziness and sedation as common adverse events "
            "(MOCK-CANNABIS-001). Evidence certainty varies across trial designs "
            "(MOCK-CANNABIS-001)."
        )
    # Generic topic
    return (
        "The loaded evidence addresses the clinical question with citation-backed findings. "
        "Review the Claim Ledger for individual claim support status and cited evidence IDs."
    )


def _mock_baseline(prompt: str) -> str:
    if "dengue" in prompt:
        return (
            "Warning signs for severe dengue include abdominal pain, persistent vomiting, "
            "bleeding, lethargy, fluid accumulation, and falling platelets. Patients with "
            "these signs need urgent clinical assessment and may require hospitalization. "
            "These findings can diagnose severe dengue. Immediate treatment decisions should "
            "be made from these signs."
        )
    return (
        "A plain model might provide clinical-sounding conclusions without carrying the "
        "source evidence alongside each claim."
    )
