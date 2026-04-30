from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider, LLMProviderError
from veritasclin.llm.mock import MockLLMProvider
from veritasclin.llm.ollama import OllamaProvider
from veritasclin.llm.openai_compatible import OpenAICompatibleProvider


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    settings = get_settings()
    name = (provider_name or settings.gemma_provider or "mock").lower()
    if name == "ollama":
        return OllamaProvider()
    if name == "openai_compatible":
        return OpenAICompatibleProvider()
    return MockLLMProvider()


__all__ = [
    "LLMProvider",
    "LLMProviderError",
    "MockLLMProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "get_llm_provider",
]
