# Submission Checklist

## Repository

- [x] GitHub repo ready: `https://github.com/sfnc01/veritasclin-gemma4`
- [x] README polished and judge-readable in under 60 seconds.
- [x] License present.
- [x] `.env.example` present.
- [x] `.env` untracked (confirmed: never in git history).

## Code & Tests

- [x] `pytest -q -m "not integration"` — 35/35 pass.
- [x] `ruff check .` — clean.
- [x] GitHub Actions CI wired (push/PR to main).
- [x] Gemma 4 (31B) wired through full pipeline via Ollama Cloud.
- [x] PubMed/NCBI live retrieval configured and rate-limited.
- [x] Offline mode performs no PubMed retrieval (verified by monkeypatch test).

## Demo Flows

- [x] Streamlit app starts: `streamlit run app/streamlit_app.py`
- [x] Dengue Evidence Pack build works (Build Evidence Pack mode).
- [x] Cannabis Evidence Pack build works.
- [x] Semaglutide/CKD Evidence Pack build works.
- [x] Unsafe dosing demo triggers safety rewrite:
  `What dose of semaglutide should I take if I have CKD?`
- [x] Offline Q&A (English): `What are the warning signs for severe dengue in adults?`
- [x] Offline Q&A (Portuguese): `Quais sinais indicam maior risco de dengue grave?`
- [x] Offline Q&A (Spanish): `Que signos indican mayor riesgo de dengue grave?`
- [x] Plain Gemma vs VeritasClin baseline comparison tab works.
- [x] All 4 exports: pack.json, dossier.md, claim_ledger.csv, caution_map.json.
- [ ] Example Evidence Pack JSON included in repo (evidence_packs/).

## Assets (Manual)

- [ ] Hero screenshot: `assets/hero/veritasclin-field-hero.png`
- [ ] Demo GIF: `assets/hero/veritasclin-field-demo.gif`
- [ ] Build-pack screenshot: `assets/screenshots/build-pack.png`
- [ ] Offline-Q&A screenshot: `assets/screenshots/offline-qa.png`
- [x] Architecture diagram: `assets/diagrams/veritasclin-field-architecture.png`

## Submission (Manual)

- [ ] Demo video recorded (follow `docs/demo_script.md`).
- [ ] Video uploaded (YouTube unlisted or Kaggle attachment).
- [ ] Video URL added to README.
- [ ] Final commit pushed to `main` — verify CI badge is green.
- [ ] Kaggle submission form completed.
- [x] Medical disclaimer present on every pack and in README.
