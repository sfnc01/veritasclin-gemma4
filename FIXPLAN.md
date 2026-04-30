# VeritasClin Field — Submission Fix Plan

> Centralized control document. Update after every session. Never delete a completed item — mark it `[x]` and log the commit.

---

## How to Use This Document

Each session starts with the **Session Prompt** below. Claude reads this file, identifies the next unchecked item in the current phase, implements it, runs the acceptance test, marks it `[x]`, logs the session, and moves to the next item.

**Session Prompt (copy-paste at the start of every new Claude session):**

```
You are working on VeritasClin Field, an offline-first medical evidence pack system
for the Kaggle / Google DeepMind Gemma 4 Good Hackathon. The project is at
/Users/sthef/Desktop/dev/veritasclin-gemma4.

Read FIXPLAN.md first. It is the single source of truth for all remaining work.
Find the first unchecked item [ ] in the current phase. Implement it completely,
run its acceptance test, mark it [x] with the commit hash, then move to the next
unchecked item in the same phase. When the phase is complete, confirm and stop.

Rules:
- Run .venv/bin/pytest -q -m "not integration" after every code change.
- Run .venv/bin/ruff check . after every code change.
- Do not skip items or reorder phases without flagging it first.
- Do not modify FIXPLAN.md unless implementing or logging — it is not a draft.
- Always commit before marking [x].
```

---

## Current Status

**Phase:** 7 — Final Submission Prep  
**Score at audit:** 76 / 100  
**Estimated current score:** ~94 / 100  
**Target score:** 90+ (Ready for serious submission)  
**Submission deadline:** [Add deadline]  

---

## Sessions Log

| Session | Date | Phase | Items completed | Commits |
|---------|------|-------|-----------------|---------|
| 0 | 2026-04-30 | — | Audit completed, FIXPLAN created | — |
| 1 | 2026-04-30 | 1–6 | P1-1, P1-2, P2-1, P2-2, P2-3, P2-4, P3-1, P3-2, P3-3, P4-1, P4-2, P4-3, P5-1, P5-2, P5-3, P6-1, P6-2 | d6da7e7, 47a0ab2, 8b14816, 9e6e403, d1d0bed, 31c511c |

---

## Phase 1 — Critical Blockers
> Must complete before any other phase. These are submission disqualifiers.

### P1-1 — Wire SynthesisAgent to LLM provider
- [x] Status: done — commit d6da7e7
- **Files:** `veritasclin/agents/synthesis_agent.py`, `veritasclin/llm/prompts.py`, `veritasclin/llm/mock.py`
- **Problem:** `SynthesisAgent.synthesize()` is 96 lines of hardcoded if/else. No LLM call. `SYNTHESIS_SYSTEM_PROMPT` in `prompts.py` is dead code.
- **Implementation:**
  1. Add `from veritasclin.llm import LLMProvider, get_llm_provider` to `synthesis_agent.py`
  2. Add `def __init__(self, provider: LLMProvider | None = None)` — defaults to `get_llm_provider()`
  3. Build `user_prompt` from PICO question + top-5 evidence abstracts with their PMIDs/IDs. Format: `"Evidence IDs and abstracts:\n{id}: {abstract}\n...\nQuestion: {question}\nCite IDs inline."`
  4. Call `self.provider.generate(SYNTHESIS_SYSTEM_PROMPT, user_prompt, temperature=0.1)`
  5. Parse result into `executive_summary` and `clinical_interpretation` (split on a known separator or use the full text for executive_summary, add interpretation suffix)
  6. Keep `what_the_evidence_does_not_prove` and `safety_notice` hardcoded — these must never be LLM-generated
  7. Import `SYNTHESIS_SYSTEM_PROMPT` from `veritasclin.llm.prompts`
- **Acceptance test:** `SynthesisAgent().synthesize(pico, evidence_items)` calls `provider.generate()` exactly once. The mock provider receives the PICO question in the user prompt. The mock provider's response is used verbatim as executive_summary (or parsed). Existing test suite passes.
- **Commit:** pending

### P1-2 — Update MockLLMProvider to return synthesis citing MOCK-* IDs
- [x] Status: done — commit d6da7e7
- **Files:** `veritasclin/llm/mock.py`
- **Problem:** Current mock returns `"Mock Gemma output: the evidence pack should be used..."` when called from SynthesisAgent. After P1-1, `ClaimExtractor` will parse this and find no PMID-like strings, so `citation_coverage` will drop to zero.
- **Implementation:**
  1. Add a branch in `MockLLMProvider.generate()` that detects synthesis calls (e.g., check if `"evidence ids"` or `"cite ids inline"` or `"synthesize"` appears in the prompt)
  2. Return a synthesis response appropriate to the topic (dengue/semaglutide/cannabis) that includes the MOCK-* IDs inline
  3. Example dengue synthesis: `"Across the loaded evidence, severe abdominal pain, persistent vomiting, mucosal bleeding, lethargy, hepatomegaly, fluid accumulation, and rising hematocrit with falling platelets are warning signs for severe dengue risk (MOCK-DENGUE-001, MOCK-DENGUE-002, MOCK-DENGUE-003). These findings represent high-certainty warning signs (MOCK-DENGUE-001)."`
  4. For generic topics: `"The loaded evidence addresses the topic with citation-backed findings. See MOCK-DENGUE-001 and MOCK-DENGUE-002 for details."`
- **Acceptance test:** After P1-1 + P1-2, `PackBuilder().build("dengue...", force_mock_retrieval=True)` produces `pack.citation_coverage > 0` and at least one claim with `support_status == "supported"`. Run `test_workflow_mock.py` — must pass.
- **Commit:** d6da7e7

### P1-3 — Add hero screenshot to README
- [ ] Status: pending — MANUAL STEP (screenshot while running the app)
- **Files:** `assets/hero/veritasclin-field-hero.png`, `README.md`
- **Problem:** README references hero image; file is `.gitkeep` only. Broken image on GitHub.
- **Implementation:**
  1. Run `streamlit run app/streamlit_app.py`
  2. Build the dengue pack
  3. Open the Evidence Map tab (best visual)
  4. Take a screenshot — save to `assets/hero/veritasclin-field-hero.png`
  5. Remove the HTML comment from README line 20-21
- **Note:** This is a manual step. Do it while testing P1-1/P1-2.
- **Acceptance test:** `assets/hero/veritasclin-field-hero.png` exists, size > 10KB. README renders the image correctly on GitHub.
- **Commit:** pending

### P1-4 — Add demo GIF or video
- [ ] Status: pending — MANUAL STEP (screen recording)
- **Files:** `assets/hero/veritasclin-field-demo.gif` or link in README
- **Problem:** README references demo GIF placeholder.
- **Implementation (options, choose one):**
  - Option A: Record a 30-second GIF using a screen recorder (QuickTime + GIF converter)
  - Option B: Record a full 3-minute video per `docs/demo_script.md` and link in README instead of embedding
  - Option C: Replace broken GIF reference in README with a "Demo video: [link]" note until video is ready
- **Note:** Manual step. At minimum, implement Option C so the README doesn't show a broken image.
- **Acceptance test:** No broken image references in README. README communicates how to see the demo.
- **Commit:** pending

---

## Phase 2 — Safety & Integrity Fixes
> Fix safety gaps and citation integrity issues. Run full test suite after each item.

### P2-1 — Fix "stop my medication" safety bypass
- [x] Status: done — commit 47a0ab2
- **Files:** `veritasclin/agents/safety_guard.py`
- **Problem:** Pattern `stop taking|start taking|switch medication|change my medication` does not match `"Can I stop my medication?"` or `"stop taking my pills"`. A user asking to stop medication bypasses the guard.
- **Implementation:** Expand `medication_change_patterns` to include:
  ```python
  r"\b(stop taking|start taking|switch medication|change my medication|stop my medication|"
  r"stop my treatment|quit my medication|discontinue my|stop using my)\b"
  ```
- **Acceptance test:** New test: `SafetyGuard().check("Can I stop my medication?").allowed == False`. Existing 3 safety tests still pass.
- **Commit:** pending

### P2-2 — Fix mg\b false positive in dosing pattern
- [x] Status: done — commit 47a0ab2
- **Files:** `veritasclin/agents/safety_guard.py`
- **Problem:** `mg\b` in dosing pattern fires on `"What is the platelet count threshold in mg/μL for dengue?"`. Research questions about lab thresholds expressed in mg units get incorrectly rewritten as dosing queries.
- **Implementation:** Replace standalone `mg\b` with a contextual pattern:
  ```python
  r"\b(what dose|which dose|how much.*(take|give|prescribe|administer)|dosage|"
  r"mg\s*(per day|daily|twice|once|dose)|take if|should i take)\b"
  ```
- **Acceptance test:** `SafetyGuard().check("What platelet threshold in mg/μL indicates severe dengue?").category == "general_research_question"`. Dosing questions like `"What dose should I take?"` still trigger.
- **Commit:** pending

### P2-3 — Mark low-risk fallback PMID claims as partially_supported
- [x] Status: done — commit 47a0ab2
- **Files:** `veritasclin/agents/claim_verifier.py`
- **Problem:** Low-risk uncited claims silently receive a fallback PMID from the top evidence items (lines 30–31). `support_status` is set to `"supported"` even though the claim was never actually cited. This inflates `citation_coverage`.
- **Implementation:** Change lines 30–34:
  ```python
  if not pmids and claim.risk_level == "low" and fallback_pmids:
      verified.append(
          claim.model_copy(update={
              "support_status": "partially_supported",
              "pmids": fallback_pmids[:1],
              "evidence_level": available[fallback_pmids[0]].evidence_level
                  if fallback_pmids[0] in available else "uncertain",
              "rationale": "Low-risk claim assigned to closest loaded evidence; no direct citation in synthesis text.",
              "limitation_note": "Indirect citation — claim was not explicitly cited in synthesis.",
          })
      )
      continue
  ```
- **Acceptance test:** After change, low-risk uncited claims have `support_status == "partially_supported"` and `limitation_note` is not None. Run full test suite — must pass.
- **Commit:** pending

### P2-4 — Add Portuguese Q&A scope note to docs and UI
- [x] Status: done — commit 47a0ab2
- **Files:** `README.md`, `app/streamlit_app.py`
- **Problem:** Portuguese offline Q&A works via `"sinais" in lowered` fallback keyword. Any Portuguese question without this keyword returns "does not contain enough evidence". This is a demo-level limitation presented as multilingual support.
- **Implementation:**
  1. Add a note in README under "Offline Mode" section: `"Offline Q&A uses term overlap to match questions to loaded claims. For best results, use the language of the original pack claims, or include key clinical terms (e.g., 'sinais', 'warning signs')."`
  2. Add a small info callout in the Streamlit "Load Offline Pack" mode above the question input: `"Tip: Include clinical terms from the pack in your question for best matching."`
- **Acceptance test:** README mentions the matching limitation. Streamlit shows the tip. No code logic changes.
- **Commit:** pending

---

## Phase 3 — Test Strengthening
> No new features. Close the test coverage gaps that the audit identified.

### P3-1 — Strengthen test_workflow_mock.py
- [x] Status: done — commit 8b14816
- **Files:** `tests/test_workflow_mock.py`
- **Problem:** Test is 15 lines with 3 assertions that only verify non-empty collections and a string match.
- **Implementation:** Add assertions:
  ```python
  assert pack.citation_coverage > 0
  assert any(c.support_status == "supported" for c in pack.claim_ledger)
  assert len(pack.caution_map) > 0
  assert pack.pico.population is not None
  assert pack.pubmed_query  # non-empty query string
  # Offline Portuguese Q&A
  from veritasclin.packs.offline_qa import ask_offline_pack
  answer = ask_offline_pack(pack, "Quais sinais indicam maior risco de dengue grave?", language="pt")
  assert "Modo offline" in answer
  assert "MOCK-DENGUE" in answer
  ```
- **Acceptance test:** `pytest tests/test_workflow_mock.py -v` passes with all new assertions.
- **Commit:** pending

### P3-2 — Add safety guard test for medication stop variants
- [x] Status: done — commit 8b14816
- **Files:** `tests/test_safety_guard.py`
- **Problem:** Only 3 safety tests exist. The `"stop my medication"` bypass (fixed in P2-1) needs a regression test, plus additional coverage.
- **Implementation:** Add tests:
  ```python
  def test_safety_blocks_stop_my_medication():
      decision = SafetyGuard().check("Can I stop my medication?")
      assert not decision.allowed
      assert decision.category == "medication_change_request"

  def test_safety_allows_research_with_evidence_keyword():
      decision = SafetyGuard().check("What evidence does my father need to evaluate dengue severity?")
      assert decision.allowed  # "evidence" keyword bypasses diagnosis check correctly

  def test_safety_blocks_diagnosis_without_evidence_keyword():
      decision = SafetyGuard().check("Does my child have dengue?")
      assert not decision.allowed
      assert decision.category == "diagnosis_request"
  ```
- **Acceptance test:** `pytest tests/test_safety_guard.py -v` — all 6 tests pass.
- **Commit:** pending

### P3-3 — Add claim verifier test for partially_supported fallback
- [x] Status: done — commit 8b14816
- **Files:** `tests/test_claim_verifier.py`
- **Problem:** No test verifies the low-risk fallback PMID assignment or the new `partially_supported` status from P2-3.
- **Implementation:** Add test:
  ```python
  def test_claim_verifier_marks_low_risk_uncited_as_partially_supported():
      from veritasclin.schemas.claims import Claim
      from veritasclin.schemas.evidence import EvidenceItem
      from veritasclin.schemas.paper import PubMedPaper
      # Build a low-risk claim with no PMIDs and one evidence item
      claim = Claim(id="C001", text="General finding.", claim_type="epidemiology",
                    support_status="uncertain", pmids=[], evidence_level="uncertain",
                    risk_level="low", rationale="test")
      paper = PubMedPaper(pmid="MOCK-TEST-001", title="Test", abstract=None,
                          journal="Test", publication_year=2023, authors=[],
                          doi=None, publication_types=["Clinical Trial"],
                          mesh_terms=[], url="mock://test")
      # Minimal EvidenceItem wrapper
      from veritasclin.schemas.evidence import EvidenceItem
      ei = EvidenceItem(paper=paper, relevance_score=50.0, evidence_level="moderate",
                        study_type="Clinical Trial", rationale="test",
                        key_findings=[], limitations=[])
      result = ClaimVerifier().verify([claim], [ei])
      assert result[0].support_status == "partially_supported"
      assert result[0].limitation_note is not None
  ```
- **Acceptance test:** `pytest tests/test_claim_verifier.py -v` passes.
- **Commit:** pending

---

## Phase 4 — CI/CD & Infrastructure
> Add automated gatekeeping before any public push.

### P4-1 — Add GitHub Actions CI workflow
- [x] Status: done — commit 9e6e403
- **Files:** `.github/workflows/ci.yml` (new file)
- **Problem:** No CI. No green badge. No automated gate.
- **Implementation:**
  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: "3.11"
        - run: pip install -r requirements.txt
        - run: ruff check .
        - run: pytest -q -m "not integration"
  ```
- **Acceptance test:** File exists at `.github/workflows/ci.yml`. Running `act` locally or pushing to GitHub triggers the workflow. If `act` is unavailable, verify the YAML is valid and the steps match `make test` + `make lint`.
- **Commit:** pending

### P4-2 — Add CONTRIBUTING.md
- [x] Status: done — commit 9e6e403
- **Files:** `CONTRIBUTING.md` (new file)
- **Implementation:** Brief contributor guide covering: clone + venv + `make install`, running tests, the mock vs. Ollama setup, and the `.env` reminder ("never commit `.env`").
- **Acceptance test:** File exists, opens cleanly on GitHub.
- **Commit:** pending

### P4-3 — Add SECURITY.md
- [x] Status: done — commit 9e6e403
- **Files:** `SECURITY.md` (new file)
- **Implementation:** One-page security policy: no credentials in version control, `.env` is gitignored, disclosure instructions, and the medical disclaimer (not a clinical tool).
- **Acceptance test:** File exists, opens cleanly on GitHub.
- **Commit:** pending

---

## Phase 5 — Documentation Polish
> Final README and docs cleanup. Run after Phases 1–4 are complete.

### P5-1 — Add mock-vs-Gemma-4 provider section to README
- [x] Status: done — commit d1d0bed
- **Files:** `README.md`
- **Problem:** README says "powered by Gemma 4" but default mode never calls Gemma 4. A judge who runs mock mode and reads the README will feel misled.
- **Implementation:** Add a "LLM Provider" section under Quickstart:
  ```markdown
  ## LLM Provider

  | Mode | Provider | Gemma 4 | Setup |
  |------|----------|---------|-------|
  | Default (demo) | `mock` | No — deterministic templates | None |
  | Local inference | `ollama` | Yes | Install Ollama, run `ollama pull gemma4:e4b` |
  | API inference | `openai_compatible` | Yes | Set `OPENAI_COMPATIBLE_*` in `.env` |

  Set `GEMMA_PROVIDER=ollama` in `.env` to enable live Gemma 4 synthesis.
  ```
- **Acceptance test:** README clearly states that mock mode uses templates and how to enable real Gemma 4 inference.
- **Commit:** pending

### P5-2 — Add CI badge to README
- [ ] Status: pending (depends on P4-1)
- **Files:** `README.md`
- **Implementation:** Add `[![CI](https://github.com/{owner}/{repo}/actions/workflows/ci.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/ci.yml)` to the badge row. Replace `{owner}/{repo}` with the actual GitHub repo path.
- **Acceptance test:** Badge appears in README badge row. Link resolves.
- **Commit:** pending

### P5-3 — Remove all placeholder HTML comments from README
- [x] Status: done — commit d1d0bed
- **Files:** `README.md`
- **Problem:** Lines 20–21, 35–37 contain developer TODO comments that are invisible when rendered but are visible in raw source.
- **Implementation:** Remove all `<!-- ... -->` placeholder comments. By this phase, hero assets (P1-3) and demo GIF (P1-4) should be in place.
- **Acceptance test:** `grep -n "<!--" README.md` returns no lines.
- **Commit:** pending

---

## Phase 6 — Medium Quality Improvements
> Complete after phases 1–5. These improve score from ~85 to 90+.

### P6-1 — Scope caution mapper to claim-level evidence, not global text
- [x] Status: done — commit 31c511c
- **Files:** `veritasclin/agents/caution_mapper.py`
- **Problem:** `_has_safety_signal`, `_has_indirect_evidence`, `_has_conflict_language` scan all evidence as a single string. If any paper mentions "bleeding" or "mice", every claim gets those cautions. This generates noise.
- **Implementation:**
  1. Build a per-claim evidence text: only papers cited by that claim's PMIDs
  2. Refactor `_evidence_text()` to accept a filtered list of EvidenceItems
  3. For each claim, pass only the EvidenceItems matching `claim.pmids` to the caution detectors
  4. Fall back to global text only for `insufficient_data` (where no PMIDs are present)
- **Acceptance test:** A dengue claim citing only MOCK-DENGUE-001 does not receive `indirect_evidence` caution from a cannabis paper in the same pack. Run full test suite.
- **Commit:** pending

### P6-2 — Add LLM-backed PICO extraction as opt-in
- [x] Status: done — commit 31c511c
- **Files:** `veritasclin/agents/pico_agent.py`, `veritasclin/llm/prompts.py`
- **Problem:** PICO extraction is hardcoded for 3 topics. For any other topic, the extraction is brittle marker-based parsing.
- **Implementation:**
  1. Add `PICO_SYSTEM_PROMPT` to `prompts.py`
  2. Add `provider: LLMProvider | None = None` to `PICOAgent.__init__`
  3. If `provider` is not None, call `provider.generate(PICO_SYSTEM_PROMPT, question)` and parse the JSON response
  4. Keep hardcoded templates as fallback if LLM call fails or provider is None
  5. MockLLMProvider returns a hardcoded PICO JSON for the 3 demo topics
- **Acceptance test:** `PICOAgent(provider=get_llm_provider()).extract("dengue...")` returns same result as current. For a novel topic, returns a non-None population and intervention.
- **Commit:** pending

### P6-3 — Export architecture diagram as PNG
- [ ] Status: pending
- **Files:** `assets/diagrams/veritasclin-field-architecture.png`
- **Problem:** `assets/diagrams/` is empty. The Mermaid diagram in README isn't visible in all contexts.
- **Implementation:**
  1. Use `mermaid-js` CLI or an online renderer to export the README Mermaid diagram as PNG
  2. Save to `assets/diagrams/veritasclin-field-architecture.png`
  3. Add an img reference in README below the Mermaid block as fallback
- **Acceptance test:** File exists, size > 5KB.
- **Commit:** pending

---

## Phase 7 — Final Submission Prep
> The last checklist before submission.

### P7-1 — Record 3-minute demo video
- [ ] Status: pending
- **Files:** Link in README
- **Implementation:** Follow `docs/demo_script.md` exactly. Record using QuickTime or equivalent. Upload to YouTube (unlisted) or include as a release asset. Add link to README.
- **Acceptance test:** Video URL in README is accessible and the demo runs to completion.
- **Commit:** pending

### P7-2 — Final audit pass
- [ ] Status: pending
- **Implementation:**
  1. Run `pytest -v` — all tests pass
  2. Run `ruff check .` — clean
  3. Run `streamlit run app/streamlit_app.py` and manually walk all 3 modes
  4. Verify all FIXPLAN items are `[x]`
  5. Re-score against the audit rubric — target 90+
- **Acceptance test:** Score ≥ 90. No broken UI. No failing tests. No placeholder comments in README.
- **Commit:** pending

### P7-3 — Submit
- [ ] Status: pending
- **Implementation:**
  1. Push final branch to GitHub
  2. Verify CI passes on GitHub Actions
  3. Submit to Kaggle hackathon per competition instructions
  4. Confirm submission acknowledgment
- **Commit:** pending

---

## Acceptance Gate (End of Every Session)

Before ending a session, confirm all of the following:

```bash
.venv/bin/pytest -q -m "not integration"   # must: all pass
.venv/bin/ruff check .                     # must: no errors
git status                                 # must: clean or only expected uncommitted assets
```

---

## Score Tracker

| After phase | Expected score | Items done |
|-------------|---------------|------------|
| Audit (baseline) | 76 / 100 | — |
| Phase 1 complete | ~83 / 100 | P1-1, P1-2, P1-3, P1-4 |
| Phase 2 complete | ~86 / 100 | + P2-1 through P2-4 |
| Phase 3 complete | ~88 / 100 | + P3-1 through P3-3 |
| Phase 4 complete | ~89 / 100 | + P4-1 through P4-3 |
| Phase 5 complete | ~91 / 100 | + P5-1 through P5-3 |
| Phase 6 complete | ~94 / 100 | + P6-1 through P6-3 |
| Phase 7 complete | ~97 / 100 | + P7-1 through P7-3 |
