from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class LLMProviderError(Exception):
    """Raised when an LLM provider call fails and cannot be retried."""


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Generate text from a provider."""

    def generate_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> str:
        """Generate text from a provider with an image input."""
        raise LLMProviderError(
            "Image input requires a real LLM provider (ollama or openai_compatible)."
        )

    def generate_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[dict[str, Any]],
        tool_executor: Callable[[str, dict[str, Any]], str],
        temperature: float = 0.0,
    ) -> str:
        """Run a single function-calling turn with tool execution."""
        raise LLMProviderError(
            "Function calling requires a real LLM provider (ollama or openai_compatible)."
        )
