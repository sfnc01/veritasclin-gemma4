from __future__ import annotations

import re

from veritasclin.schemas.safety import SafetyDecision


class SafetyGuard:
    emergency_patterns = re.compile(
        r"\b(chest pain|shortness of breath|cannot breathe|stroke|seizure|"
        r"unconscious|suicidal|overdose|bleeding heavily|emergency)\b",
        flags=re.IGNORECASE,
    )
    dosing_patterns = re.compile(
        r"\b(what dose|which dose|how much|dosage|mg\b|take if|should i take)\b",
        flags=re.IGNORECASE,
    )
    medication_change_patterns = re.compile(
        r"\b(stop taking|start taking|switch medication|change my medication)\b",
        flags=re.IGNORECASE,
    )
    diagnosis_patterns = re.compile(
        r"\b(do i have|does my|my father|my mother|my child|patient has|diagnose)\b",
        flags=re.IGNORECASE,
    )
    phi_patterns = re.compile(
        r"\b(mrn|medical record|cpf|ssn|social security|address|phone number)\b",
        flags=re.IGNORECASE,
    )

    def check(self, question: str) -> SafetyDecision:
        clean = question.strip()
        lowered = clean.lower()
        if self.emergency_patterns.search(clean):
            return SafetyDecision(
                allowed=False,
                requires_rewrite=False,
                category="emergency_request",
                risk_level="high",
                reason="The prompt appears to request emergency triage.",
                safe_rewritten_question=None,
                user_message=(
                    "I cannot provide emergency triage. Seek urgent medical care or contact "
                    "local emergency services immediately."
                ),
            )
        if self.phi_patterns.search(clean):
            return SafetyDecision(
                allowed=False,
                requires_rewrite=False,
                category="identifiable_patient_data",
                risk_level="high",
                reason="The prompt appears to include or request identifiable patient information.",
                safe_rewritten_question=None,
                user_message=(
                    "I cannot process identifiable patient records. Please remove personal "
                    "identifiers and ask a general evidence question."
                ),
            )
        if self.medication_change_patterns.search(clean):
            return SafetyDecision(
                allowed=False,
                requires_rewrite=False,
                category="medication_change_request",
                risk_level="high",
                reason="The prompt requests medication stop/start/change instructions.",
                safe_rewritten_question=None,
                user_message=(
                    "I cannot advise medication changes. I can summarize published evidence "
                    "about medication use when framed as a general research question."
                ),
            )
        if self.dosing_patterns.search(clean):
            rewritten = self._rewrite_to_research(clean)
            return SafetyDecision(
                allowed=True,
                requires_rewrite=True,
                category="prescription_or_dosing_request",
                risk_level="medium",
                reason="The prompt requests individualized dosing advice and can be rewritten.",
                safe_rewritten_question=rewritten,
                user_message=(
                    "I cannot provide individualized dosing advice, but I can summarize "
                    "published evidence about dosing regimens studied in clinical research."
                ),
            )
        if (
            self.diagnosis_patterns.search(clean)
            and "evidence" not in lowered
            and "research" not in lowered
        ):
            return SafetyDecision(
                allowed=False,
                requires_rewrite=False,
                category="diagnosis_request",
                risk_level="high",
                reason="The prompt appears to request diagnosis for an individual.",
                safe_rewritten_question=None,
                user_message=(
                    "I cannot diagnose an individual. Ask a general biomedical evidence "
                    "question without patient-identifying details."
                ),
            )
        return SafetyDecision(
            allowed=True,
            requires_rewrite=False,
            category="general_research_question",
            risk_level="low",
            reason="The prompt is framed as a general biomedical evidence question.",
            safe_rewritten_question=None,
            user_message="This can be handled as a general evidence question.",
        )

    def _rewrite_to_research(self, question: str) -> str:
        lowered = question.lower()
        if "semaglutide" in lowered and "ckd" in lowered:
            return (
                "What semaglutide dosing regimens have been studied in clinical trials "
                "involving patients with chronic kidney disease?"
            )
        medication = "the medication"
        match = re.search(r"\b(semaglutide|metformin|insulin|warfarin|aspirin)\b", lowered)
        if match:
            medication = match.group(1)
        return f"What {medication} regimens have been studied in published clinical research?"
