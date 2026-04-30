from __future__ import annotations

import pytest

from veritasclin.config import reset_settings_cache


@pytest.fixture(autouse=True)
def force_mock_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMMA_PROVIDER", "mock")
    reset_settings_cache()
    yield
    reset_settings_cache()
