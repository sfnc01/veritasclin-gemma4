from __future__ import annotations

import httpx

from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        settings = get_settings()
        if not (
            settings.openai_compatible_base_url
            and settings.openai_compatible_api_key
            and settings.openai_compatible_model
        ):
            return "OpenAI-compatible provider is not configured."

        headers = {"Authorization": f"Bearer {settings.openai_compatible_api_key}"}
        payload = {
            "model": settings.openai_compatible_model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        try:
            with httpx.Client(timeout=45) as client:
                response = client.post(
                    f"{settings.openai_compatible_base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return str(data["choices"][0]["message"]["content"]).strip()
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            return f"OpenAI-compatible provider unavailable: {exc}"
