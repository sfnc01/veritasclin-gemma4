from __future__ import annotations

import pytest

from tests.support.fake_provider import FakeLLMProvider
from veritasclin.agents.function_calling_query_agent import FunctionCallingQueryAgent
from veritasclin.schemas.pico import PICOQuestion


def _dengue_pico() -> PICOQuestion:
    return PICOQuestion(
        original_question="What are warning signs for severe dengue?",
        population="adults with dengue",
        intervention="warning signs",
        comparison=None,
        outcome="severe dengue progression",
        preferred_study_types=["Systematic Review"],
        language="en",
    )


def test_function_calling_query_agent_falls_back_with_mock():
    agent = FunctionCallingQueryAgent(provider=FakeLLMProvider())
    query = agent.build(_dengue_pico())
    assert isinstance(query, str)
    assert len(query) > 0
    assert agent.used_function_calling is False


def test_function_calling_query_agent_fallback_query_is_non_empty():
    agent = FunctionCallingQueryAgent(provider=FakeLLMProvider())
    query = agent.build(_dengue_pico())
    assert "dengue" in query.lower() or len(query) > 5


@pytest.mark.integration
def test_function_calling_query_agent_with_real_provider():
    from veritasclin.llm.ollama import OllamaProvider

    agent = FunctionCallingQueryAgent(provider=OllamaProvider())
    query = agent.build(_dengue_pico())
    assert isinstance(query, str)
    assert len(query) > 5
