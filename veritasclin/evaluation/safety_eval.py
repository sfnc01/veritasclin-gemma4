from __future__ import annotations

from veritasclin.schemas.safety import SafetyDecision


def safety_rewrite_success(decision: SafetyDecision) -> bool:
    return decision.allowed and decision.requires_rewrite and bool(decision.safe_rewritten_question)
