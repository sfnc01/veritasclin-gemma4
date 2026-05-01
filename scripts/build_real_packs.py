"""Build real Evidence Packs using live PubMed retrieval and Gemma 4.

Run from the project root:
    python scripts/build_real_packs.py

Requires:
    - NCBI_API_KEY or NCBI_EMAIL in .env
    - GEMMA_PROVIDER=ollama with OLLAMA_API_KEY in .env
    - Internet access
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure project root is on the path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Force real provider before any veritasclin imports touch the cache
os.environ["GEMMA_PROVIDER"] = "ollama"

from veritasclin.config import reset_settings_cache  # noqa: E402
from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv  # noqa: E402
from veritasclin.exporters.json_export import pack_to_json  # noqa: E402
from veritasclin.exporters.markdown import pack_to_markdown  # noqa: E402
from veritasclin.llm import get_llm_provider  # noqa: E402
from veritasclin.packs.builder import PackBuilder  # noqa: E402

reset_settings_cache()

TOPICS = [
    {
        "slug": "dengue_warning_signs_adults",
        "question": (
            "What does recent evidence say about warning signs for severe dengue in adults?"
        ),
        "language": "en",
    },
    {
        "slug": "semaglutide_ckd_renal_outcomes",
        "question": (
            "What does evidence say about semaglutide safety and renal outcomes in patients "
            "with chronic kidney disease?"
        ),
        "language": "en",
    },
    {
        "slug": "cannabis_neuropathic_pain",
        "question": (
            "What does evidence say about medical cannabis or cannabinoids for neuropathic "
            "pain in adults?"
        ),
        "language": "en",
    },
    {
        "slug": "malaria_severe_treatment_adults",
        "question": (
            "What does evidence say about treatment of severe malaria in adults "
            "in endemic settings?"
        ),
        "language": "en",
    },
    {
        "slug": "tuberculosis_latent_treatment_outcomes",
        "question": (
            "What does evidence say about treatment regimens for latent tuberculosis "
            "infection and outcomes?"
        ),
        "language": "en",
    },
    {
        "slug": "maternal_health_postpartum_hemorrhage",
        "question": (
            "What does evidence say about prevention and management of postpartum hemorrhage?"
        ),
        "language": "en",
    },
]

OUT_DIR = ROOT / "evidence_packs"


def _slug_dir(slug: str) -> Path:
    d = OUT_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_and_save(topic: dict, provider) -> None:
    slug = topic["slug"]
    question = topic["question"]
    language = topic["language"]
    print(f"\n{'='*60}")
    print(f"Building: {slug}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    pack, baseline = PackBuilder(provider=provider).build(
        question=question,
        language=language,
        max_results=10,
        include_baseline=True,
        use_bundled_papers=False,
    )

    out = _slug_dir(slug)

    # pack.json
    (out / "pack.json").write_text(pack_to_json(pack), encoding="utf-8")
    print(f"  ✓ pack.json  (source: {pack.source})")
    print(f"    PMIDs: {[p.pmid for p in pack.papers[:5]]}")
    print(f"    Claims: {len(pack.claim_ledger)}"
          f"  |  Citation coverage: {pack.citation_coverage:.0%}")
    print(f"    Query method: {pack.pubmed_query_method}")

    # dossier.md
    (out / "dossier.md").write_text(pack_to_markdown(pack), encoding="utf-8")
    print("  ✓ dossier.md")

    # claim_ledger.csv
    (out / "claim_ledger.csv").write_text(claims_to_csv(pack.claim_ledger), encoding="utf-8")
    print("  ✓ claim_ledger.csv")

    # caution_map.json
    (out / "caution_map.json").write_text(
        caution_map_to_json(pack.caution_map), encoding="utf-8"
    )
    print("  ✓ caution_map.json")

    # baseline summary
    if baseline:
        (out / "baseline_comparison.json").write_text(
            json.dumps(baseline.model_dump(mode="json"), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  ✓ baseline_comparison.json  (delta: {baseline.summary[:80]}...)")


def main() -> None:
    from veritasclin.config import get_settings
    settings = get_settings()
    print("VeritasClin Field — Real Evidence Pack Builder")
    print(f"  Provider : {settings.gemma_provider}")
    print(f"  Model    : {settings.gemma_model}")
    _pm = "configured" if settings.pubmed_configured else "NOT configured — aborting"
    print(f"  PubMed   : {_pm}")
    print(f"  Output   : {OUT_DIR}")

    if not settings.pubmed_configured:
        print("\nERROR: Set NCBI_API_KEY or NCBI_EMAIL in .env before running this script.")
        sys.exit(1)

    if settings.gemma_provider == "mock":
        print("\nERROR: GEMMA_PROVIDER=mock will produce mock data. Set GEMMA_PROVIDER=ollama.")
        sys.exit(1)

    provider = get_llm_provider()
    errors = []
    for topic in TOPICS:
        try:
            build_and_save(topic, provider)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR building {topic['slug']}: {exc}")
            errors.append((topic["slug"], exc))

    print(f"\n{'='*60}")
    print(f"Done. {len(TOPICS) - len(errors)}/{len(TOPICS)} packs built successfully.")
    if errors:
        for slug, exc in errors:
            print(f"  FAILED: {slug} — {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
