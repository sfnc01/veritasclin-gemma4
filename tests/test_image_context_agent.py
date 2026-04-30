from __future__ import annotations

import pytest

from veritasclin.agents.image_context_agent import ImageContextAgent
from veritasclin.llm.mock import MockLLMProvider


def test_image_context_agent_mock_returns_empty():
    agent = ImageContextAgent(provider=MockLLMProvider())
    result = agent.describe(b"fake image bytes")
    assert result == ""


def test_image_context_agent_describe_returns_string():
    agent = ImageContextAgent(provider=MockLLMProvider())
    result = agent.describe(b"any bytes", mime_type="image/png")
    assert isinstance(result, str)


@pytest.mark.integration
def test_image_context_agent_with_real_provider():
    import base64

    from veritasclin.llm.ollama import OllamaProvider

    # Minimal valid 1×1 white JPEG
    minimal_jpg = base64.b64decode(
        "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDB"
        "kSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAAR"
        "CAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAA"
        "AAAAAAAAAAAAAP/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAA"
        "AAAAAAAA/9oADAMBAAIRAxEAPwCwABmX/9k="
    )
    agent = ImageContextAgent(provider=OllamaProvider())
    result = agent.describe(minimal_jpg)
    assert isinstance(result, str)
