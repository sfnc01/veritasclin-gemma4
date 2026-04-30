# Security Policy

## Credentials and secrets

- **Never commit `.env`** — it is listed in `.gitignore`. The file may contain NCBI API keys and LLM provider credentials.
- Use `.env.example` as a template. It contains no secrets.
- If you suspect a credential was accidentally committed, rotate it immediately and contact the repository owner.

## Reporting a vulnerability

If you discover a security issue in this project, please open a GitHub issue marked **[SECURITY]** or contact the maintainer directly. Do not post credentials or vulnerability details publicly.

## Medical disclaimer

VeritasClin Field is a research and education tool for the Kaggle / Google DeepMind Gemma 4 Good Hackathon. It is **not** a clinical diagnostic tool, a prescription tool, or an emergency triage system. It does not provide individualized medical advice. All outputs carry a safety notice and require PMID/PMCID citation for strong clinical claims.

No patient-identifiable records or PHI are collected, stored, or processed by this system.

## Data handling

- PubMed results are cached locally in `.veritasclin_cache/` using DiskCache.
- No data is sent to third parties beyond NCBI E-utilities API calls (when configured) and your configured LLM provider.
- Evidence Packs saved to disk are stored in the local `evidence_packs/` directory (excluded from version control).
