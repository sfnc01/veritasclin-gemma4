from __future__ import annotations

from veritasclin.llm import LLMProvider
from veritasclin.packs.builder import PackBuilder
from veritasclin.packs.offline_qa import ask_offline_pack
from veritasclin.schemas.baseline import BaselineComparison
from veritasclin.schemas.pack import EvidencePack


def build_evidence_pack(
    question: str,
    language: str = "en",
    max_results: int = 10,
    include_baseline: bool = True,
    provider: LLMProvider | None = None,
) -> tuple[EvidencePack, BaselineComparison | None]:
    return PackBuilder(provider=provider).build(
        question=question,
        language=language,
        max_results=max_results,
        include_baseline=include_baseline,
    )


__all__ = ["ask_offline_pack", "build_evidence_pack"]
