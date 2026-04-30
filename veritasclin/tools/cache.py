from __future__ import annotations

from pathlib import Path
from typing import Any

from diskcache import Cache

_CACHE: Cache | None = None


def get_cache(directory: str | Path = ".veritasclin_cache") -> Cache:
    global _CACHE
    if _CACHE is None:
        _CACHE = Cache(str(directory))
    return _CACHE


def cache_get(key: str) -> Any | None:
    return get_cache().get(key)


def cache_set(key: str, value: Any, expire: int = 60 * 60 * 24) -> None:
    get_cache().set(key, value, expire=expire)
