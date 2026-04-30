from __future__ import annotations

import httpx

from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        settings = get_settings()
        payload = {
            "model": settings.gemma_model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            with httpx.Client(timeout=45) as client:
                response = client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/generate", json=payload
                )
                response.raise_for_status()
                data = response.json()
                return str(data.get("response", "")).strip()
        except httpx.HTTPError as exc:
            return f"Ollama unavailable: {exc}"
