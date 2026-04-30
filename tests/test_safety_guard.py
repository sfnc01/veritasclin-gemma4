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


def test_safety_blocks_stop_my_medication():
    decision = SafetyGuard().check("Can I stop my medication?")
    assert not decision.allowed
    assert decision.category == "medication_change_request"


def test_safety_blocks_stop_taking_without_explicit_phrase():
    decision = SafetyGuard().check("I want to stop my treatment, is that safe?")
    assert not decision.allowed
    assert decision.category == "medication_change_request"


def test_safety_allows_research_with_evidence_keyword():
    decision = SafetyGuard().check(
        "What evidence does my father need to evaluate dengue severity?"
    )
    assert decision.allowed


def test_safety_blocks_diagnosis_without_evidence_keyword():
    decision = SafetyGuard().check("Does my child have dengue?")
    assert not decision.allowed
    assert decision.category == "diagnosis_request"


def test_safety_does_not_block_lab_value_mg_question():
    decision = SafetyGuard().check(
        "What platelet count threshold in mg per unit indicates severe dengue?"
    )
    assert decision.allowed
    assert decision.category == "general_research_question"
