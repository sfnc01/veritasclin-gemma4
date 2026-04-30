from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SafetyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    requires_rewrite: bool
    category: str
    risk_level: str
    reason: str
    safe_rewritten_question: str | None = None
    user_message: str
