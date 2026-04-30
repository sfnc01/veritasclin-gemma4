from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProviderError(Exception):
    """Raised when an LLM provider call fails and cannot be retried."""


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Generate text from a provider."""
