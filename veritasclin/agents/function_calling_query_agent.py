from __future__ import annotations

from typing import Any

from veritasclin.agents.query_agent import QueryAgent
from veritasclin.llm import LLMProvider, get_llm_provider
from veritasclin.llm.base import LLMProviderError
from veritasclin.schemas.pico import PICOQuestion

_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "set_pubmed_query",
        "description": (
            "Set the optimised PubMed search query for evidence retrieval. "
            "Use MeSH terms and Title/Abstract field tags for maximum precision and recall."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A valid PubMed search string using MeSH terms and field tags, "
                        "e.g. (dengue[Title/Abstract]) AND (severity[MeSH Terms])"
                    ),
                }
            },
            "required": ["query"],
        },
    },
}

_SYSTEM = (
    "You are a biomedical literature search expert. "
    "Given a clinical PICO question, call the set_pubmed_query tool with the optimal "
    "PubMed search string using MeSH terms and Title/Abstract field tags to maximise "
    "recall and precision. Always call the tool — do not respond with text only."
)


class FunctionCallingQueryAgent:
    used_function_calling: bool = False

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or get_llm_provider()
        self._fallback = QueryAgent()

    def build(self, pico: PICOQuestion) -> str:
        self.used_function_calling = False
        user_prompt = (
            f"Clinical question: {pico.safe_rewritten_question or pico.original_question}\n"
            f"Population: {pico.population or 'not specified'}\n"
            f"Intervention: {pico.intervention or 'not specified'}\n"
            f"Outcome: {pico.outcome or 'not specified'}\n"
            "Call set_pubmed_query with the optimal PubMed search string."
        )
        extracted: list[str] = []

        def executor(tool_name: str, args: dict[str, Any]) -> str:
            if tool_name == "set_pubmed_query":
                q = str(args.get("query", "")).strip()
                if q:
                    extracted.append(q)
                return f"Query registered: {q}"
            return "Unknown tool."

        try:
            self._provider.generate_with_tools(_SYSTEM, user_prompt, [_TOOL], executor)
        except LLMProviderError:
            return self._fallback.build(pico)

        if extracted:
            self.used_function_calling = True
            return extracted[0]
        return self._fallback.build(pico)
