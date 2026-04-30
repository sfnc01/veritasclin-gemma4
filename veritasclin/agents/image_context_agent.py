from __future__ import annotations

from veritasclin.llm import LLMProvider, get_llm_provider
from veritasclin.llm.base import LLMProviderError

_SYSTEM = (
    "You are a clinical document reader. "
    "Describe any clinical findings, measurements, lab values, symptoms, diagnoses, "
    "or diagnostic information visible in this image or document. "
    "Report findings only. Do not diagnose the patient. Keep your response under 150 words."
)

_USER_PROMPT = (
    "What clinical findings, measurements, or diagnostic information are visible in this image?"
)


class ImageContextAgent:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or get_llm_provider()

    def describe(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Return a text description of clinical findings, or empty string if unsupported."""
        try:
            return self._provider.generate_with_image(
                _SYSTEM, _USER_PROMPT, image_bytes, mime_type
            )
        except LLMProviderError:
            return ""
