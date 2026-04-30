from __future__ import annotations

from veritasclin.llm.base import LLMProvider, LLMProviderError
from veritasclin.llm.prompts import OFFLINE_QA_SYSTEM_PROMPT
from veritasclin.schemas.claims import Claim
from veritasclin.schemas.pack import EvidencePack


def ask_offline_pack(
    pack: EvidencePack,
    question: str,
    language: str = "en",
    provider: LLMProvider | None = None,
) -> str:
    relevant_claims = [
        claim
        for claim in pack.claim_ledger
        if _overlaps(question, claim.text)
        and claim.support_status in {"supported", "partially_supported"}
    ]
    if not relevant_claims:
        return _insufficient(language)

    top_claims = relevant_claims[:4]

    if provider is not None:
        return _llm_answer(pack, question, top_claims, language, provider)

    return _deterministic_answer(top_claims, language)


class OfflineQA:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    def answer(self, pack: EvidencePack, question: str, language: str = "en") -> str:
        return ask_offline_pack(pack, question, language=language, provider=self._provider)


def _llm_answer(
    pack: EvidencePack,
    question: str,
    relevant_claims: list[Claim],
    language: str,
    provider: LLMProvider,
) -> str:
    claims_block = "\n".join(
        f"- {c.id} [{', '.join(c.pmids)}]: {c.text}" for c in relevant_claims
    )
    lang_instruction = {
        "pt": "Respond in Portuguese (Brazilian).",
        "es": "Respond in Spanish.",
    }.get(language, "Respond in English.")
    user_prompt = (
        f"Pack topic: {pack.topic}\n\n"
        f"Loaded claims (cite claim IDs and evidence IDs inline):\n{claims_block}\n\n"
        f"Question: {question}\n\n"
        f"{lang_instruction} Answer in 2-3 sentences. "
        "Do not diagnose, prescribe, or give individualized advice."
    )
    try:
        raw = provider.generate(OFFLINE_QA_SYSTEM_PROMPT, user_prompt, temperature=0.1)
        if raw and len(raw.strip()) > 20:
            return raw.strip()
    except LLMProviderError:
        pass
    return _deterministic_answer(relevant_claims, language)


def _deterministic_answer(relevant_claims: list[Claim], language: str) -> str:
    cited = "; ".join(
        f"{c.id}: {c.text} [PMIDs/IDs: {', '.join(c.pmids)}]" for c in relevant_claims[:3]
    )
    if language == "pt":
        return (
            "Modo offline: nenhuma busca externa foi realizada. "
            f"Com base apenas no Claim Ledger do pacote carregado: {cited}"
        )
    if language == "es":
        return (
            "Modo offline: no se realizo busqueda externa. "
            f"Con base solo en el Claim Ledger del paquete cargado: {cited}"
        )
    return (
        f"Offline mode: no external retrieval. Based only on the loaded pack Claim Ledger: {cited}"
    )


def _overlaps(question: str, claim: str) -> bool:
    question_terms = {term for term in question.lower().split() if len(term) > 4}
    claim_terms = {term.strip(".,;:()[]").lower() for term in claim.split() if len(term) > 4}
    return bool(question_terms.intersection(claim_terms))


def _insufficient(language: str) -> str:
    if language == "pt":
        return (
            "O pacote carregado nao contem evidencia suficiente para responder a esta pergunta. "
            "Nenhuma busca externa foi realizada em modo offline."
        )
    if language == "es":
        return (
            "El paquete cargado no contiene evidencia suficiente para responder. "
            "No se realizo ninguna busqueda externa en modo offline."
        )
    return (
        "The loaded pack does not contain enough evidence to answer this question. "
        "No external retrieval was used in offline mode."
    )
