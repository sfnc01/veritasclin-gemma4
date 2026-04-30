from veritasclin.agents.safety_guard import SafetyGuard


def test_safety_allows_general_questions():
    decision = SafetyGuard().check(
        "What does recent evidence say about warning signs for severe dengue in adults?"
    )
    assert decision.allowed
    assert decision.category == "general_research_question"


def test_safety_rewrites_dosing_questions():
    decision = SafetyGuard().check("What dose of semaglutide should I take if I have CKD?")
    assert decision.allowed
    assert decision.requires_rewrite
    assert "studied" in decision.safe_rewritten_question.lower()


def test_safety_blocks_emergency_questions():
    decision = SafetyGuard().check(
        "My father has chest pain and shortness of breath, what should I do?"
    )
    assert not decision.allowed
    assert decision.category == "emergency_request"
