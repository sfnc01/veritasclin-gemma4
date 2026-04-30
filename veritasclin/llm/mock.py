from __future__ import annotations

from veritasclin.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        prompt = f"{system_prompt}\n{user_prompt}".lower()
        if "portuguese" in prompt or "portugues" in prompt or "quais sinais" in prompt:
            return (
                "Com base apenas no pacote carregado, sinais de alerta para dengue grave "
                "incluem dor abdominal intensa, vomitos persistentes, sangramento de mucosa, "
                "letargia, hepatomegalia e sinais de extravasamento plasmatico. Ver Claim "
                "Ledger para PMIDs ou IDs mock associados."
            )
        if "spanish" in prompt or "espanol" in prompt:
            return (
                "Segun el paquete cargado, los signos de alarma incluyen dolor abdominal, "
                "vomitos persistentes, sangrado de mucosas, letargo y signos de fuga plasmatica."
            )
        return (
            "Mock Gemma output: the evidence pack should be used to answer with cited, "
            "auditable claims rather than unsupported medical advice."
        )
