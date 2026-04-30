from __future__ import annotations

import httpx

from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider, LLMProviderError


class OllamaProvider(LLMProvider):
    name = "ollama"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        settings = get_settings()
        base_url = settings.ollama_base_url.rstrip("/")
        headers = {}
        if settings.ollama_api_key:
            headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

        payload = {
            "model": settings.gemma_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            with httpx.Client(timeout=120) as client:
                response = client.post(
                    f"{base_url}/api/chat",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                return str(data["message"]["content"]).strip()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"HTTP {exc.response.status_code} from {exc.request.url}. "
                f"Check OLLAMA_BASE_URL (use https://ollama.com for cloud, "
                f"http://localhost:11434 for local) and OLLAMA_API_KEY."
            ) from exc
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMProviderError(f"Ollama provider unreachable: {exc}") from exc
