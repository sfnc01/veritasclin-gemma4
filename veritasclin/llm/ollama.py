from __future__ import annotations

import base64
import json
from collections.abc import Callable
from typing import Any

import httpx

from veritasclin.config import get_settings
from veritasclin.llm.base import LLMProvider, LLMProviderError


class OllamaProvider(LLMProvider):
    name = "ollama"

    def _headers(self, settings: Any) -> dict[str, str]:
        if settings.ollama_api_key:
            return {"Authorization": f"Bearer {settings.ollama_api_key}"}
        return {}

    def _base_url(self, settings: Any) -> str:
        return settings.ollama_base_url.rstrip("/")

    def _post(self, client: httpx.Client, url: str, payload: dict, headers: dict) -> dict:
        try:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"HTTP {exc.response.status_code} from {exc.request.url}. "
                f"Check OLLAMA_BASE_URL (use https://ollama.com for cloud, "
                f"http://localhost:11434 for local) and OLLAMA_API_KEY."
            ) from exc
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMProviderError(f"Ollama provider unreachable: {exc}") from exc

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        settings = get_settings()
        url = f"{self._base_url(settings)}/api/chat"
        payload = {
            "model": settings.gemma_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        with httpx.Client(timeout=120) as client:
            data = self._post(client, url, payload, self._headers(settings))
        return str(data["message"]["content"]).strip()

    def generate_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> str:
        settings = get_settings()
        url = f"{self._base_url(settings)}/api/chat"
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "model": settings.gemma_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt, "images": [b64]},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }
        with httpx.Client(timeout=120) as client:
            data = self._post(client, url, payload, self._headers(settings))
        return str(data["message"]["content"]).strip()

    def generate_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[dict[str, Any]],
        tool_executor: Callable[[str, dict[str, Any]], str],
        temperature: float = 0.0,
    ) -> str:
        settings = get_settings()
        url = f"{self._base_url(settings)}/api/chat"
        headers = self._headers(settings)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        payload: dict[str, Any] = {
            "model": settings.gemma_model,
            "messages": messages,
            "tools": tools,
            "stream": False,
            "options": {"temperature": temperature},
        }
        with httpx.Client(timeout=120) as client:
            data = self._post(client, url, payload, headers)
            msg = data["message"]
            tool_calls = msg.get("tool_calls") or []

            if not tool_calls:
                return str(msg.get("content", "")).strip()

            # Append assistant turn with tool calls
            messages.append({
                "role": "assistant",
                "content": msg.get("content", ""),
                "tool_calls": tool_calls,
            })

            # Execute each tool call and collect results
            for tc in tool_calls:
                fn = tc["function"]
                raw_args = fn.get("arguments", {})
                args: dict[str, Any] = (
                    json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                )
                result = tool_executor(fn["name"], args)
                messages.append({"role": "tool", "content": result})

            # Second call — Gemma 4 synthesises with tool results
            payload2: dict[str, Any] = {
                "model": settings.gemma_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            }
            data2 = self._post(client, url, payload2, headers)
        return str(data2["message"]["content"]).strip()
