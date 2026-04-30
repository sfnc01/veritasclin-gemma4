from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from veritasclin.agents.safety_guard import SafetyGuard
from veritasclin.config import get_settings, reset_settings_cache
from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv
from veritasclin.exporters.json_export import pack_to_json
from veritasclin.exporters.markdown import pack_to_markdown
from veritasclin.llm import get_llm_provider
from veritasclin.packs.builder import PackBuilder
from veritasclin.packs.loader import PackLoader
from veritasclin.packs.offline_qa import ask_offline_pack
from veritasclin.schemas.pack import EvidencePack

ASSET_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSET_DIR / "veritasclin-field-logo.png"
MARK_PATH = ASSET_DIR / "veritasclin-field-mark.png"

st.set_page_config(page_title="VeritasClin Field", page_icon="VC", layout="wide")

st.markdown(
    """
    <style>
    :root {
      --vc-navy: #061e42;
      --vc-ink: #11263b;
      --vc-muted: #526676;
      --vc-line: #d9e7e4;
      --vc-panel: #f6fbfa;
      --vc-panel-strong: #e7f7f5;
      --vc-teal: #08a895;
      --vc-cyan: #0891b2;
      --vc-alert: #9a3412;
      --vc-danger: #991b1b;
    }
    html, body, [class*="css"] {
      color: var(--vc-ink);
      font-size: 16px;
    }
    .block-container {
      padding-top: 1.1rem;
      max-width: 1280px;
    }
    .vc-shell {
      border-bottom: 1px solid var(--vc-line);
      padding-bottom: 1rem;
      margin-bottom: 1rem;
    }
    .vc-kicker {
      color: var(--vc-teal);
      font-size: 0.76rem;
      font-weight: 750;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.25rem;
    }
    .vc-title h1 {
      color: var(--vc-navy);
      letter-spacing: 0;
      margin: 0;
      line-height: 1.08;
    }
    .vc-title p {
      color: var(--vc-muted);
      margin: 0.3rem 0 0 0;
      max-width: 74ch;
    }
    .vc-status-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.55rem;
      margin-top: 0.85rem;
    }
    .vc-status {
      background: var(--vc-panel);
      border: 1px solid var(--vc-line);
      padding: 0.65rem 0.8rem;
      min-height: 4.25rem;
    }
    .vc-status span {
      color: var(--vc-muted);
      display: block;
      font-size: 0.78rem;
      margin-bottom: 0.18rem;
    }
    .vc-status b {
      color: var(--vc-navy);
      font-size: 0.95rem;
    }
    .vc-section {
      border-bottom: 1px solid var(--vc-line);
      padding-bottom: 0.65rem;
      margin: 1.1rem 0 0.85rem 0;
    }
    .vc-section h2, .vc-section h3 {
      color: var(--vc-navy);
      margin-bottom: 0.2rem;
    }
    .vc-safety {
      border-left: 4px solid var(--vc-alert);
      background: #fff7ed;
      padding: 0.75rem 1rem;
      margin: 0.5rem 0 1rem 0;
      color: #431407;
    }
    .metric-card {
      border: 1px solid var(--vc-line);
      background: var(--vc-panel);
      padding: 0.9rem;
      min-height: 5.5rem;
    }
    .metric-card b { color: var(--vc-teal); font-size: 1.35rem; }
    .metric-card span {
      color: var(--vc-muted);
      display: block;
      font-size: 0.78rem;
      margin-top: 0.25rem;
    }
    div[data-testid="stDataFrame"] {
      border: 1px solid var(--vc-line);
    }
    .stButton button, .stDownloadButton button {
      min-height: 44px;
      border-radius: 6px;
      font-weight: 700;
    }
    .stButton button:focus, .stDownloadButton button:focus {
      outline: 3px solid rgba(8, 168, 149, 0.35);
      outline-offset: 2px;
    }
    @media (max-width: 760px) {
      .vc-status-grid { grid-template-columns: 1fr; }
      .block-container { padding-left: 1rem; padding-right: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    if MARK_PATH.exists():
        st.image(str(MARK_PATH), width=120)
    st.header("Controls")
    mode = st.radio(
        "Mode",
        ["Build Evidence Pack", "Load Offline Pack", "Plain Gemma vs VeritasClin Demo"],
    )
    _provider_options = ["openai_compatible", "ollama", "mock"]
    _env_provider = os.environ.get("GEMMA_PROVIDER", "mock")
    _provider_default = (
        _provider_options.index(_env_provider)
        if _env_provider in _provider_options
        else _provider_options.index("mock")
    )
    provider = st.selectbox("Provider", _provider_options, index=_provider_default)
    if os.environ.get("GEMMA_PROVIDER") != provider:
        os.environ["GEMMA_PROVIDER"] = provider
        reset_settings_cache()
    language_label = st.selectbox("Language", ["English", "Portuguese", "Spanish"], index=0)
    language = {"English": "en", "Portuguese": "pt", "Spanish": "es"}[language_label]
    max_results = st.slider("Max PubMed results", min_value=5, max_value=20, value=10)
    _s = get_settings()
    use_pubmed = st.toggle(
        "Use PubMed when configured",
        value=_s.pubmed_configured,
        help="When off, the app uses deterministic mock demo data.",
    )
    _settings_sidebar = get_settings()
    st.caption(
        "PubMed credentials: "
        + ("configured" if _settings_sidebar.pubmed_configured else "not configured")
    )
    st.divider()
    st.caption("Demo questions")
    demo = st.radio(
        "Select",
        [
            "Severe dengue warning signs in adults",
            "Medical cannabis for neuropathic pain",
            "Semaglutide safety and renal outcomes in CKD",
            "Unsafe dosing demo",
        ],
        label_visibility="collapsed",
    )

DEMO_QUESTIONS = {
    "Severe dengue warning signs in adults": (
        "What does recent evidence say about warning signs for severe dengue in adults?"
    ),
    "Medical cannabis for neuropathic pain": (
        "What does evidence say about medical cannabis for neuropathic pain in adults?"
    ),
    "Semaglutide safety and renal outcomes in CKD": (
        "What does evidence say about semaglutide safety and renal outcomes in CKD?"
    ),
    "Unsafe dosing demo": "What dose of semaglutide should I take if I have CKD?",
}

settings = get_settings()
source_mode = "PubMed enabled" if use_pubmed and settings.pubmed_configured else "Mock fallback"
offline_state = "Loaded" if "pack" in st.session_state else "No pack loaded"
provider_label = provider.replace("_", " ")

settings = get_settings()

if provider == "ollama" and not settings.ollama_api_key and "ollama.com" in (
    settings.ollama_base_url or ""
):
    st.warning(
        "Ollama Cloud selected but OLLAMA_API_KEY is not set. "
        "Get a key at ollama.com/settings/keys and add it to your .env file.",
        icon="⚠️",
    )
elif provider == "openai_compatible" and not (
    settings.openai_compatible_base_url
    and settings.openai_compatible_api_key
    and settings.openai_compatible_model
):
    st.warning(
        "OpenAI-compatible provider selected but not fully configured. "
        "Set OPENAI_COMPATIBLE_BASE_URL, OPENAI_COMPATIBLE_API_KEY, and "
        "OPENAI_COMPATIBLE_MODEL in your .env file.",
        icon="⚠️",
    )

header_logo, header_text = st.columns([1, 2.4], vertical_alignment="center")
with header_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width="stretch")
    else:
        st.title("VeritasClin Field")
with header_text:
    st.markdown(
        f"""
        <div class="vc-shell">
          <div class="vc-title">
            <div class="vc-kicker">Offline-first evidence pack console</div>
            <h1>Audit-ready medical evidence for field teams</h1>
            <p>
              Build PubMed-backed Evidence Packs online, carry their Claim Ledger offline,
              and answer only from loaded evidence in English, Portuguese, or Spanish.
            </p>
          </div>
          <div class="vc-status-grid">
            <div class="vc-status"><span>Provider</span><b>{provider_label}</b></div>
            <div class="vc-status"><span>Retrieval</span><b>{source_mode}</b></div>
            <div class="vc-status"><span>Offline pack</span><b>{offline_state}</b></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="vc-safety">
      Not a diagnostic, prescription, or emergency triage tool.
      No PMID/PMCID or explicit mock evidence ID, no strong clinical claim.
    </div>
    """,
    unsafe_allow_html=True,
)


def render_pack(pack: EvidencePack) -> None:
    st.markdown(
        f"""
        <div class="vc-section">
          <h2>{pack.title}</h2>
          <p>Evidence Pack source: <b>{pack.source}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    unsupported = [claim for claim in pack.claim_ledger if claim.support_status == "unsupported"]
    high_unsupported = [claim for claim in unsupported if claim.risk_level == "high"]
    c1.markdown(
        f'<div class="metric-card">Citation coverage<br><b>{pack.citation_coverage:.0%}</b></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="metric-card">Unsupported claims<br><b>{len(unsupported)}</b></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="metric-card">High-risk unsupported<br><b>{len(high_unsupported)}</b></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div class="metric-card">Freshness score<br><b>{pack.freshness.score:.0%}</b>'
        f"<span>Refresh in {pack.freshness.recommended_refresh_days} days</span></div>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "Pack",
            "PICO & Query",
            "Evidence Map",
            "Claim Ledger",
            "Caution Map",
            "Exports",
        ]
    )
    with tabs[0]:
        st.markdown("### Executive Summary")
        st.write(pack.executive_summary)
        st.markdown("### Clinical Interpretation")
        st.write(pack.clinical_interpretation)
        st.markdown("### What the Evidence Does Not Prove")
        st.write(pack.what_the_evidence_does_not_prove)
        st.markdown("### Patient-Friendly Explanation")
        st.write(pack.patient_friendly_explanation)
        st.info(pack.safety_notice)
    with tabs[1]:
        st.json(pack.pico.model_dump(mode="json"))
        st.code(pack.pubmed_query, language="text")
        st.caption(f"Source: {pack.source}")
    with tabs[2]:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "pmid_or_id": item.paper.pmid,
                        "title": item.paper.title,
                        "year": item.paper.publication_year,
                        "study_type": item.study_type,
                        "evidence_level": item.evidence_level,
                        "score": item.relevance_score,
                    }
                    for item in pack.evidence_items
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    with tabs[3]:
        st.dataframe(
            pd.DataFrame([claim.model_dump(mode="json") for claim in pack.claim_ledger]),
            use_container_width=True,
            hide_index=True,
        )
    with tabs[4]:
        st.dataframe(
            pd.DataFrame([item.model_dump(mode="json") for item in pack.caution_map]),
            use_container_width=True,
            hide_index=True,
        )
    with tabs[5]:
        st.download_button(
            "Download pack.json", pack_to_json(pack), "pack.json", "application/json"
        )
        st.download_button(
            "Download dossier.md", pack_to_markdown(pack), "dossier.md", "text/markdown"
        )
        st.download_button(
            "Download claim_ledger.csv",
            claims_to_csv(pack.claim_ledger),
            "claim_ledger.csv",
            "text/csv",
        )
        st.download_button(
            "Download caution_map.json",
            caution_map_to_json(pack.caution_map),
            "caution_map.json",
            "application/json",
        )


llm = get_llm_provider(provider)

if mode == "Build Evidence Pack":
    st.markdown(
        '<div class="vc-section"><h2>Build Evidence Pack</h2></div>',
        unsafe_allow_html=True,
    )
    question = st.text_area("Clinical evidence question", value=DEMO_QUESTIONS[demo], height=90)
    safety = SafetyGuard(provider=llm).check(question)
    with st.expander("Safety decision", expanded=True):
        st.json(safety.model_dump(mode="json"))
    if st.button("Build pack", type="primary"):
        if not safety.allowed:
            st.error(safety.user_message)
        else:
            steps = [
                "safety check",
                "PICO extraction",
                "PubMed retrieval or mock fallback",
                "evidence ranking",
                "Gemma 4 synthesis",
                "claim extraction",
                "claim verification",
                "caution mapping",
                "freshness scoring",
            ]
            progress = st.progress(0)
            status = st.empty()
            for index, step in enumerate(steps, start=1):
                status.write(f"Running {step}...")
                progress.progress(index / len(steps))
            try:
                pack, baseline = PackBuilder(provider=llm).build(
                    question,
                    language=language,
                    max_results=max_results,
                    include_baseline=True,
                    force_mock_retrieval=not use_pubmed,
                )
                st.session_state["pack"] = pack
                st.session_state["baseline"] = baseline
                status.success("Evidence Pack ready.")
            except ValueError as exc:
                st.error(str(exc))
    if "pack" in st.session_state:
        render_pack(st.session_state["pack"])

elif mode == "Load Offline Pack":
    st.markdown('<div class="vc-section"><h2>Load Offline Pack</h2></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload pack.json", type=["json"])
    pack = st.session_state.get("pack")
    if uploaded:
        pack = PackLoader().loads(uploaded.read())
        st.session_state["pack"] = pack
    if pack:
        st.success("Offline pack loaded. No PubMed retrieval is used in this mode.")
        st.write({"pack_id": pack.pack_id, "title": pack.title, "source": pack.source})
        st.info(
            "Tip: Offline Q&A matches your question to the loaded Claim Ledger. "
            "Include clinical keywords from the pack topic for best results."
        )
        offline_question = st.text_input(
            "Ask within the loaded pack",
            value="What are the warning signs for severe dengue in adults?",
        )
        if st.button("Ask offline", type="primary"):
            answer = ask_offline_pack(pack, offline_question, language=language, provider=llm)
            st.markdown("### Offline Answer")
            st.write(answer)
    else:
        st.info("Build a pack first or upload a pack.json.")

else:
    st.markdown(
        '<div class="vc-section"><h2>Plain Gemma vs VeritasClin Demo</h2></div>',
        unsafe_allow_html=True,
    )
    pack = st.session_state.get("pack")
    baseline = st.session_state.get("baseline")
    if not pack:
        st.info("Build the dengue Evidence Pack first, then return here for comparison.")
    elif baseline:
        left, right = st.columns(2)
        with left:
            st.subheader("Plain model")
            st.write(baseline.baseline_answer)
            st.metric("Unsupported claims", baseline.baseline_unsupported_claim_count)
            st.metric("High-risk unsupported", baseline.baseline_high_risk_unsupported_count)
        with right:
            st.subheader("VeritasClin")
            st.write(pack.executive_summary)
            st.metric("Unsupported claims", baseline.veritasclin_unsupported_claim_count)
            st.metric("Citation coverage", f"{baseline.citation_coverage:.0%}")
        st.info(baseline.summary)
    else:
        st.warning("Baseline comparison was not generated for the current pack.")
