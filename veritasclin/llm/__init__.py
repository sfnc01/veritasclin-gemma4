from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider, LLMProviderError
from veritasclin.llm.ollama import OllamaProvider
from veritasclin.llm.openai_compatible import OpenAICompatibleProvider


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    settings = get_settings()
    name = (provider_name or settings.gemma_provider or "ollama").lower()
    if name == "ollama":
        return OllamaProvider()
    if name == "openai_compatible":
        return OpenAICompatibleProvider()
    # "mock" is accepted only for test isolation — not a user-facing option
    from veritasclin.llm.mock import _MockLLMProvider  # noqa: PLC0415
    return _MockLLMProvider()


__all__ = [
    "LLMProvider",
    "LLMProviderError",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "get_llm_provider",
]
