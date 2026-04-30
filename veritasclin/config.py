from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    ncbi_api_key: str | None
    ncbi_email: str | None
    ncbi_tool: str
    ncbi_max_rps: float
    gemma_provider: str
    gemma_model: str
    ollama_base_url: str
    ollama_api_key: str | None
    openai_compatible_base_url: str | None
    openai_compatible_api_key: str | None
    openai_compatible_model: str | None
    pack_dir: Path

    @property
    def pubmed_configured(self) -> bool:
        return bool(self.ncbi_email or self.ncbi_api_key)


def _empty_to_none(value: str | None) -> str | None:
    return value if value else None


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        ncbi_api_key=_empty_to_none(os.getenv("NCBI_API_KEY")),
        ncbi_email=_empty_to_none(os.getenv("NCBI_EMAIL")),
        ncbi_tool=os.getenv("NCBI_TOOL", "veritasclin-field"),
        ncbi_max_rps=float(os.getenv("NCBI_MAX_RPS", "3")),
        gemma_provider=os.getenv("GEMMA_PROVIDER", "mock"),
        gemma_model=os.getenv("GEMMA_MODEL", "gemma4:e4b"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_api_key=_empty_to_none(os.getenv("OLLAMA_API_KEY")),
        openai_compatible_base_url=_empty_to_none(os.getenv("OPENAI_COMPATIBLE_BASE_URL")),
        openai_compatible_api_key=_empty_to_none(os.getenv("OPENAI_COMPATIBLE_API_KEY")),
        openai_compatible_model=_empty_to_none(os.getenv("OPENAI_COMPATIBLE_MODEL")),
        pack_dir=Path(os.getenv("VERITASCLIN_PACK_DIR", "evidence_packs")),
    )


def reset_settings_cache() -> None:
    get_settings.cache_clear()
