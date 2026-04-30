from __future__ import annotations

import json

from veritasclin.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        combined = f"{system_prompt}\n{user_prompt}".lower()

        # Claim extraction call — JSON array of clinical assertions
        if "verifiable clinical" in combined or "json array" in combined:
            return _mock_claim_extraction(combined)

        # Safety rewrite call
        if "rewrite" in combined and "research question" in combined:
            return _mock_safety_rewrite(combined)

        # Offline Q&A call
        if "claim ledger" in combined and ("offline" in combined or "loaded claims" in combined):
            return _mock_offline_qa(combined)

        # PICO extraction call
        if "pico elements" in combined or '"population"' in combined:
            return _mock_pico(combined)

        # Synthesis call — detected by the evidence-ID citation instruction
        if "cite ids inline" in combined or "cite these source ids" in combined:
            return _mock_synthesis(combined)

        # Baseline / plain model call
        if "plain medical assistant" in combined or "without retrieval" in combined:
            return _mock_baseline(combined)

        return (
            "Mock Gemma output: the evidence pack should be used to answer with cited, "
            "auditable claims rather than unsupported medical advice."
        )


def _mock_claim_extraction(prompt: str) -> str:
    if "dengue" in prompt:
        return json.dumps([
            "Warning signs for severe dengue include abdominal pain, persistent vomiting, "
            "mucosal bleeding, lethargy, and fluid accumulation (MOCK-DENGUE-001).",
            "Rising hematocrit with falling platelets is associated with plasma leakage "
            "and severe dengue risk (MOCK-DENGUE-002).",
            "Clinical guidelines recommend urgent evaluation for patients presenting with "
            "multiple dengue warning signs (MOCK-DENGUE-003).",
        ])
    if "semaglutide" in prompt or "ckd" in prompt or "kidney" in prompt:
        return json.dumps([
            "Studied semaglutide dosing regimens in CKD populations show evidence of "
            "kidney-protective effects (MOCK-SEMAGLUTIDE-001).",
            "Trial evidence describes safety outcomes for semaglutide in chronic kidney "
            "disease, not individualized dosing advice (MOCK-SEMAGLUTIDE-001).",
        ])
    if "cannabis" in prompt or "cannabinoid" in prompt or "neuropathic" in prompt:
        return json.dumps([
            "Cannabinoids showed modest pain reduction in some neuropathic pain trials "
            "(MOCK-CANNABIS-001).",
            "Dizziness and sedation were the most commonly reported adverse events with "
            "cannabinoid use (MOCK-CANNABIS-001).",
        ])
    return json.dumps([
        "The loaded evidence addresses the clinical question with citation-backed findings.",
    ])


def _mock_safety_rewrite(prompt: str) -> str:
    if "semaglutide" in prompt and "ckd" in prompt:
        return (
            "What semaglutide dosing regimens have been studied in clinical trials "
            "involving patients with chronic kidney disease?"
        )
    if "semaglutide" in prompt:
        return "What semaglutide regimens have been studied in published clinical research?"
    return "What does the published evidence say about the studied regimens for this condition?"


def _mock_offline_qa(prompt: str) -> str:
    if "dengue" in prompt:
        return (
            "Based on the loaded pack Claim Ledger, warning signs for severe dengue "
            "include abdominal pain and mucosal bleeding (C001 [MOCK-DENGUE-001], "
            "C002 [MOCK-DENGUE-002]). These findings are from loaded evidence only — "
            "no external retrieval was performed."
        )
    return (
        "Based on the loaded pack Claim Ledger, the evidence addresses the queried topic. "
        "See claim IDs for individual citation details. No external retrieval was performed."
    )


def _mock_synthesis(prompt: str) -> str:
    if "dengue" in prompt:
        return (
            "Across the loaded evidence, severe abdominal pain, persistent vomiting, "
            "mucosal bleeding, lethargy/restlessness, hepatomegaly, fluid accumulation, "
            "and rising hematocrit with falling platelets are warning signs for severe "
            "dengue risk (MOCK-DENGUE-001, MOCK-DENGUE-002, MOCK-DENGUE-003). "
            "High-certainty evidence supports clinical vigilance for these signs in adults "
            "(MOCK-DENGUE-001)."
        )
    if "semaglutide" in prompt or "ckd" in prompt or "kidney" in prompt:
        return (
            "The loaded evidence describes studied semaglutide dosing regimens and kidney "
            "outcomes in chronic kidney disease populations (MOCK-SEMAGLUTIDE-001). "
            "This is a summary of published trial evidence, not individualized dosing advice "
            "(MOCK-SEMAGLUTIDE-001)."
        )
    if "cannabis" in prompt or "cannabinoid" in prompt or "neuropathic" in prompt:
        return (
            "The loaded evidence reports modest pain reduction with cannabinoids in some "
            "neuropathic pain trials, with dizziness and sedation as common adverse events "
            "(MOCK-CANNABIS-001). Evidence certainty varies across trial designs "
            "(MOCK-CANNABIS-001)."
        )
    return (
        "The loaded evidence addresses the clinical question with citation-backed findings. "
        "Review the Claim Ledger for individual claim support status and cited evidence IDs."
    )


def _mock_pico(prompt: str) -> str:
    if "dengue" in prompt:
        data = {
            "population": "adults with dengue",
            "intervention": "warning signs",
            "comparison": None,
            "outcome": "severe dengue progression",
            "timeframe": "recent",
        }
    elif "semaglutide" in prompt:
        data = {
            "population": "patients with CKD",
            "intervention": "semaglutide",
            "comparison": None,
            "outcome": "renal outcomes and safety",
            "timeframe": None,
        }
    elif "cannabis" in prompt or "cannabinoid" in prompt:
        data = {
            "population": "adults with neuropathic pain",
            "intervention": "cannabinoids",
            "comparison": "placebo",
            "outcome": "pain relief",
            "timeframe": None,
        }
    else:
        data = {
            "population": None,
            "intervention": None,
            "comparison": None,
            "outcome": None,
            "timeframe": None,
        }
    return json.dumps(data)


def _mock_baseline(prompt: str) -> str:
    if "dengue" in prompt:
        return (
            "Warning signs for severe dengue include abdominal pain, persistent vomiting, "
            "bleeding, lethargy, fluid accumulation, and falling platelets. Patients with "
            "these signs need urgent clinical assessment and may require hospitalization. "
            "These findings can diagnose severe dengue. Immediate treatment decisions should "
            "be made from these signs."
        )
    return (
        "A plain model might provide clinical-sounding conclusions without carrying the "
        "source evidence alongside each claim."
    )
