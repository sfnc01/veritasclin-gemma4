from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from veritasclin.agents.safety_guard import SafetyGuard
from veritasclin.agents.workflow import build_evidence_pack
from veritasclin.config import get_settings
from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv
from veritasclin.exporters.json_export import pack_to_json
from veritasclin.exporters.markdown import pack_to_markdown
from veritasclin.packs.loader import PackLoader
from veritasclin.packs.offline_qa import ask_offline_pack
from veritasclin.schemas.pack import EvidencePack

st.set_page_config(page_title="VeritasClin Field", page_icon="VC", layout="wide")

st.markdown(
    """
    <style>
    :root {
      --vc-ink: #1e2623;
      --vc-muted: #5a6762;
      --vc-line: #d7ded8;
      --vc-panel: #f7f8f5;
      --vc-accent: #0b6b58;
      --vc-alert: #9a3412;
    }
    .block-container { padding-top: 1.5rem; }
    .vc-title {
      border-bottom: 1px solid var(--vc-line);
      padding-bottom: 0.8rem;
      margin-bottom: 1rem;
    }
    .vc-title h1 {
      color: var(--vc-ink);
      letter-spacing: 0;
      margin-bottom: 0.15rem;
    }
    .vc-title p { color: var(--vc-muted); margin: 0; }
    .vc-safety {
      border-left: 4px solid var(--vc-alert);
      background: #fff7ed;
      padding: 0.75rem 1rem;
      margin: 0.75rem 0 1rem 0;
      color: #431407;
    }
    .metric-card {
      border: 1px solid var(--vc-line);
      background: var(--vc-panel);
      padding: 0.9rem;
      min-height: 5.5rem;
    }
    .metric-card b { color: var(--vc-accent); font-size: 1.35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="vc-title">
      <h1>VeritasClin Field</h1>
      <p>Offline-first, audit-ready medical evidence packs powered by Gemma 4.</p>
    </div>
    <div class="vc-safety">
      Not a diagnostic, prescription, or emergency triage tool.
      No PMID/PMCID or explicit mock evidence ID, no strong clinical claim.
    </div>
    """,
    unsafe_allow_html=True,
)

settings = get_settings()

with st.sidebar:
    st.header("Controls")
    mode = st.radio(
        "Mode",
        ["Build Evidence Pack", "Load Offline Pack", "Plain Gemma vs VeritasClin Demo"],
    )
    provider = st.selectbox("Provider", ["mock", "ollama", "openai_compatible"], index=0)
    os.environ["GEMMA_PROVIDER"] = provider
    language_label = st.selectbox("Language", ["English", "Portuguese", "Spanish"], index=0)
    language = {"English": "en", "Portuguese": "pt", "Spanish": "es"}[language_label]
    max_results = st.slider("Max PubMed results", min_value=5, max_value=20, value=10)
    use_pubmed = st.toggle(
        "Use PubMed when configured",
        value=settings.pubmed_configured,
        help="When off, the app uses deterministic mock demo data.",
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


def render_pack(pack: EvidencePack) -> None:
    st.subheader(pack.title)
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
        f'<div class="metric-card">Freshness score<br><b>{pack.freshness.score:.0%}</b></div>',
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


if mode == "Build Evidence Pack":
    st.header("Build Evidence Pack")
    question = st.text_area("Clinical evidence question", value=DEMO_QUESTIONS[demo], height=90)
    safety = SafetyGuard().check(question)
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
                "synthesis",
                "claim verification",
                "caution mapping",
                "freshness scoring",
                "pack export",
            ]
            progress = st.progress(0)
            status = st.empty()
            for index, step in enumerate(steps, start=1):
                status.write(f"Running {step}...")
                progress.progress(index / len(steps))
            try:
                pack, baseline = build_evidence_pack(
                    question,
                    language=language,
                    max_results=max_results,
                    include_baseline=True,
                )
                if not use_pubmed:
                    from veritasclin.packs.builder import PackBuilder

                    pack, baseline = PackBuilder().build(
                        question,
                        language=language,
                        max_results=max_results,
                        include_baseline=True,
                        force_mock_retrieval=True,
                    )
                st.session_state["pack"] = pack
                st.session_state["baseline"] = baseline
                status.success("Evidence Pack ready.")
            except ValueError as exc:
                st.error(str(exc))
    if "pack" in st.session_state:
        render_pack(st.session_state["pack"])

elif mode == "Load Offline Pack":
    st.header("Load Offline Pack")
    uploaded = st.file_uploader("Upload pack.json", type=["json"])
    pack = st.session_state.get("pack")
    if uploaded:
        pack = PackLoader().loads(uploaded.read())
        st.session_state["pack"] = pack
    if pack:
        st.success("Offline pack loaded. No PubMed retrieval is used in this mode.")
        st.write({"pack_id": pack.pack_id, "title": pack.title, "source": pack.source})
        offline_question = st.text_input(
            "Ask within the loaded pack",
            value="Quais sinais indicam maior risco de dengue grave?",
        )
        if st.button("Ask offline", type="primary"):
            answer = ask_offline_pack(pack, offline_question, language=language)
            st.markdown("### Offline Answer")
            st.write(answer)
    else:
        st.info("Build a pack first or upload a pack.json.")

else:
    st.header("Plain Gemma vs VeritasClin Demo")
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
