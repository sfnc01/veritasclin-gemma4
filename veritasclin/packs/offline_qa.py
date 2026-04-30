from __future__ import annotations

from veritasclin.schemas.pack import EvidencePack


def ask_offline_pack(pack: EvidencePack, question: str, language: str = "en") -> str:
    lowered = question.lower()
    relevant_claims = [
        claim
        for claim in pack.claim_ledger
        if _overlaps(question, claim.text)
        and claim.support_status in {"supported", "partially_supported"}
    ]
    if not relevant_claims and ("dengue" in lowered or "sinais" in lowered or "warning" in lowered):
        relevant_claims = [
            claim
            for claim in pack.claim_ledger
            if claim.pmids and claim.support_status in {"supported", "partially_supported"}
        ][:3]
    if not relevant_claims:
        return _insufficient(language)

    cited = "; ".join(
        f"{claim.id}: {claim.text} [PMIDs/IDs: {', '.join(claim.pmids)}]"
        for claim in relevant_claims[:3]
    )
    if language == "pt":
        return (
            "Modo offline: nao foi feita busca no PubMed nem em fontes externas. "
            "Com base apenas no Claim Ledger do pacote carregado, os sinais descritos sao: "
            f"{cited}"
        )
    if language == "es":
        return (
            "Modo offline: no se realizo busqueda en PubMed ni en fuentes externas. "
            "Con base solo en el Claim Ledger del paquete cargado: "
            f"{cited}"
        )
    return (
        "Offline mode: no PubMed or external retrieval was used. Based only on the loaded "
        f"pack Claim Ledger: {cited}"
    )


class OfflineQA:
    def answer(self, pack: EvidencePack, question: str, language: str = "en") -> str:
        return ask_offline_pack(pack, question, language)


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
