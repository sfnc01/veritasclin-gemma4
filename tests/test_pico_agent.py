from veritasclin.agents.pico_agent import PICOAgent
from veritasclin.schemas.pico import PICOQuestion


def test_pico_agent_returns_valid_schema():
    pico = PICOAgent().extract(
        "What does recent evidence say about warning signs for severe dengue in adults?"
    )
    assert isinstance(pico, PICOQuestion)
    assert "dengue" in pico.population.lower()
    assert pico.outcome
