from __future__ import annotations

import httpx

from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider, LLMProviderError

__all__ = ["LLMProviderError", "OpenAICompatibleProvider"]


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        settings = get_settings()
        if not (
            settings.openai_compatible_base_url
            and settings.openai_compatible_api_key
            and settings.openai_compatible_model
        ):
            raise LLMProviderError(
                "openai_compatible provider is not fully configured. "
                "Set OPENAI_COMPATIBLE_BASE_URL, OPENAI_COMPATIBLE_API_KEY, "
                "and OPENAI_COMPATIBLE_MODEL in .env."
            )

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
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{settings.openai_compatible_base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return str(data["choices"][0]["message"]["content"]).strip()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"HTTP {exc.response.status_code} from {exc.request.url}. "
                f"Check OPENAI_COMPATIBLE_BASE_URL is the correct API endpoint "
                f"(e.g. http://localhost:11434/v1 for local Ollama)."
            ) from exc
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMProviderError(
                f"openai_compatible provider unreachable: {exc}"
            ) from exc
