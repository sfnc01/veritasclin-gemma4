from __future__ import annotations

import base64
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from veritasclin.agents.safety_guard import SafetyGuard
from veritasclin.config import get_settings, reset_settings_cache
from veritasclin.evaluation.faithfulness import (
    high_risk_unsupported_claim_count,
    unsupported_claim_count,
)
from veritasclin.evaluation.safety_eval import safety_rewrite_success
from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv
from veritasclin.exporters.html_export import pack_to_html
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


def _img_b64(path: Path) -> str:
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""

st.set_page_config(page_title="VeritasClin Field", page_icon="VC", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&family=Noto+Sans:wght@300;400;500;700&display=swap');

    :root {
      --vc-navy:        #0C2340;
      --vc-ink:         #164E63;
      --vc-muted:       #4B6E7D;
      --vc-line:        #CBD5E1;
      --vc-panel:       #F8FFFE;
      --vc-panel-alt:   #EFF9FF;
      --vc-teal:        #0891B2;
      --vc-teal-light:  #E0F7FA;
      --vc-green:       #059669;
      --vc-green-light: #D1FAE5;
      --vc-amber:       #D97706;
      --vc-amber-light: #FEF3C7;
      --vc-red:         #DC2626;
      --vc-red-light:   #FEE2E2;
      --vc-alert-bg:    #FFF7ED;
      --vc-alert-text:  #431407;
      --vc-alert-border:#EA580C;
    }

    html, body, [class*="css"] {
      font-family: 'Figtree', 'Noto Sans', system-ui, sans-serif;
      color: var(--vc-ink);
      font-size: 16px;
      line-height: 1.6;
    }

    /* Make Streamlit's default header transparent so our app bar sits flush */
    header[data-testid="stHeader"] {
      background: transparent !important;
      backdrop-filter: none !important;
    }
    .block-container {
      padding-top: 4.2rem;
      max-width: 1300px;
    }
    /* Kill Streamlit's default inter-element gap */
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }

    /* ── App bar (console header) ────────────────────────────────── */
    .vc-appbar {
      position: relative;
      box-sizing: border-box;
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      column-gap: 28px;
      padding: 14px 22px;
      min-height: 72px;
      background:
        radial-gradient(600px 200px at 100% 0%, rgba(34,211,238,0.16) 0%, rgba(34,211,238,0) 70%),
        linear-gradient(90deg, #0A1F3A 0%, #0D3B55 100%);
      border: 1px solid rgba(165, 243, 252, 0.18);
      border-radius: 14px;
      overflow: hidden;
      margin-bottom: 14px;
      box-shadow:
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 12px 28px rgba(8, 31, 58, 0.18);
    }
    .vc-appbar-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
      padding-right: 22px;
      border-right: 1px solid rgba(255,255,255,0.08);
    }
    .vc-appbar-mark {
      width: 40px;
      height: 40px;
      border-radius: 9px;
      background: #FFFFFF;
      border: 1px solid rgba(255,255,255,0.7);
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      display: grid;
      place-items: center;
      padding: 6px;
      flex: 0 0 auto;
    }
    .vc-appbar-mark img {
      width: 100%; height: 100%;
      display: block; object-fit: contain;
    }
    .vc-appbar-mark-fallback {
      color: #0C2340;
      font-size: 1.05rem;
      font-weight: 900;
      line-height: 1;
    }
    .vc-appbar-wordmark {
      display: flex;
      flex-direction: column;
      min-width: 0;
      line-height: 1.05;
    }
    .vc-appbar-wordmark-main {
      color: #FFFFFF !important;
      font-size: 0.97rem;
      font-weight: 800;
      letter-spacing: -0.005em;
      white-space: nowrap;
    }
    .vc-appbar-wordmark-sub {
      color: rgba(165, 243, 252, 0.72) !important;
      font-size: 0.6rem;
      font-weight: 700;
      letter-spacing: 0.22em;
      margin-top: 0.32rem;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .vc-appbar-tagline {
      display: flex;
      flex-direction: column;
      min-width: 0;
      line-height: 1.25;
    }
    .vc-appbar-tagline-pri {
      color: #FFFFFF !important;
      font-size: 0.96rem;
      font-weight: 600;
      letter-spacing: -0.005em;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .vc-appbar-tagline-pri b {
      color: #67E8F9;
      font-weight: 700;
    }
    .vc-appbar-tagline-sec {
      color: rgba(226, 255, 250, 0.62) !important;
      font-size: 0.78rem;
      font-weight: 500;
      margin-top: 3px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .vc-appbar-status {
      display: flex;
      flex-wrap: nowrap;
      align-items: center;
      gap: 6px;
      padding-left: 22px;
      border-left: 1px solid rgba(255,255,255,0.08);
    }
    .vc-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 0.72rem;
      color: rgba(226, 255, 250, 0.86) !important;
      font-weight: 500;
      white-space: nowrap;
      line-height: 1.2;
    }
    .vc-chip-accent {
      background: rgba(34, 211, 238, 0.1);
      border-color: rgba(165, 243, 252, 0.32);
      color: #A5F3FC !important;
      font-weight: 600;
    }
    .vc-chip-accent svg { color: #67E8F9; }
    .vc-chip-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      display: inline-block;
      flex-shrink: 0;
    }
    .dot-green { background: #34D399; box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.2); }
    .dot-teal  { background: #22D3EE; box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.2); }
    .dot-amber { background: #FBBF24; box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2); }
    .dot-muted { background: rgba(255,255,255,0.32); }

    /* ── Disclaimer notice ───────────────────────────────────────── */
    .vc-disclaimer {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border: 1px solid var(--vc-line);
      background: #FAFBFC;
      border-radius: 8px;
      padding: 0.58rem 1rem;
      margin: 0.15rem 0 1.15rem 0;
      color: var(--vc-muted);
      font-size: 0.8rem;
    }

    /* ── Section headings ────────────────────────────────────────── */
    .vc-section-head {
      border-bottom: 2px solid var(--vc-teal-light);
      padding-bottom: 0.5rem;
      margin: 1.25rem 0 0.9rem 0;
    }
    .vc-section-head h2 {
      color: var(--vc-navy);
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0;
    }
    .vc-section-sub {
      color: var(--vc-muted);
      font-size: 0.82rem;
      margin-top: 0.18rem;
    }

    /* ── Safety decision widget ──────────────────────────────────── */
    .vc-safety-allowed {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: var(--vc-green-light);
      border: 1px solid #6EE7B7;
      border-radius: 8px;
      padding: 0.8rem 1.05rem;
      margin-bottom: 0.9rem;
    }
    .vc-safety-rewritten {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: var(--vc-amber-light);
      border: 1px solid #FCD34D;
      border-radius: 8px;
      padding: 0.8rem 1.05rem;
      margin-bottom: 0.9rem;
    }
    .vc-safety-blocked {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: var(--vc-red-light);
      border: 1px solid #FCA5A5;
      border-radius: 8px;
      padding: 0.8rem 1.05rem;
      margin-bottom: 0.9rem;
    }
    .vc-safety-badge {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      border-radius: 4px;
      padding: 0.18rem 0.55rem;
      white-space: nowrap;
      margin-top: 0.05rem;
    }
    .badge-allowed  { background: #059669; color: #fff; }
    .badge-rewritten{ background: #D97706; color: #fff; }
    .badge-blocked  { background: #DC2626; color: #fff; }
    .vc-safety-body { flex: 1; }
    .vc-safety-title {
      font-weight: 600;
      font-size: 0.92rem;
      color: var(--vc-navy);
      margin-bottom: 0.22rem;
    }
    .vc-safety-detail {
      font-size: 0.84rem;
      color: var(--vc-ink);
      opacity: 0.85;
    }
    .vc-rewrite-box {
      background: rgba(255,255,255,0.65);
      border-radius: 5px;
      padding: 0.5rem 0.75rem;
      margin-top: 0.5rem;
      font-size: 0.86rem;
      color: var(--vc-navy);
      font-style: italic;
    }

    /* ── Metric cards ────────────────────────────────────────────── */
    .metric-row { display: flex; gap: 0.65rem; margin-bottom: 1rem; }
    .metric-card {
      flex: 1;
      border: 1px solid var(--vc-line);
      border-radius: 8px;
      background: var(--vc-panel);
      padding: 0.9rem 1rem;
    }
    .metric-card-label {
      color: var(--vc-muted);
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.07em;
      text-transform: uppercase;
      display: block;
      margin-bottom: 0.4rem;
    }
    .metric-card-value {
      font-size: 1.55rem;
      font-weight: 700;
      line-height: 1;
      display: block;
      margin-bottom: 0.22rem;
    }
    .metric-card-sub {
      color: var(--vc-muted);
      font-size: 0.76rem;
      display: block;
    }
    .color-green  { color: var(--vc-green); }
    .color-amber  { color: var(--vc-amber); }
    .color-red    { color: var(--vc-red); }
    .color-navy   { color: var(--vc-navy); }
    .color-teal   { color: var(--vc-teal); }

    /* ── Pack section headings ───────────────────────────────────── */
    .pack-section-label {
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--vc-teal);
      border-bottom: 1px solid var(--vc-teal-light);
      padding-bottom: 0.35rem;
      margin: 1.1rem 0 0.6rem 0;
    }

    /* ── PICO display ────────────────────────────────────────────── */
    .pico-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.6rem;
      margin: 0.6rem 0 1rem 0;
    }
    .pico-card {
      background: var(--vc-panel-alt);
      border: 1px solid var(--vc-line);
      border-radius: 8px;
      padding: 0.75rem 0.95rem;
    }
    .pico-letter {
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--vc-teal);
      display: block;
      margin-bottom: 0.2rem;
    }
    .pico-value {
      font-size: 0.9rem;
      color: var(--vc-navy);
      font-weight: 500;
    }

    /* ── Claim status pills ──────────────────────────────────────── */
    .pill {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      border-radius: 4px;
      padding: 0.15rem 0.5rem;
    }
    .pill-supported     { background: #D1FAE5; color: #065F46; }
    .pill-partial       { background: #FEF3C7; color: #92400E; }
    .pill-unsupported   { background: #FEE2E2; color: #991B1B; }
    .pill-uncertain     { background: #EDE9FE; color: #4C1D95; }

    /* ── Caution severity ────────────────────────────────────────── */
    .sev-high   { color: #991B1B; font-weight: 700; }
    .sev-medium { color: #92400E; font-weight: 600; }
    .sev-low    { color: #065F46; font-weight: 500; }

    /* ── Export grid ─────────────────────────────────────────────── */
    .export-card {
      background: var(--vc-panel-alt);
      border: 1px solid var(--vc-line);
      border-radius: 8px;
      padding: 0.9rem 1rem;
      margin-bottom: 0.6rem;
    }
    .export-title { font-weight: 700; color: var(--vc-navy); margin-bottom: 0.2rem; }
    .export-desc  { font-size: 0.83rem; color: var(--vc-muted); margin-bottom: 0.6rem; }

    /* ── Progress steps ──────────────────────────────────────────── */
    .pipeline-step {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 0;
      color: var(--vc-muted);
      font-size: 0.88rem;
      border-bottom: 1px solid var(--vc-teal-light);
    }
    .pipeline-step-active { color: var(--vc-teal); font-weight: 600; }
    .pipeline-step-done   { color: var(--vc-green); }

    /* ── Baseline comparison ─────────────────────────────────────── */
    .compare-col {
      background: var(--vc-panel);
      border: 1px solid var(--vc-line);
      border-radius: 10px;
      padding: 1.1rem 1.2rem;
    }
    .compare-col h3 {
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 0.65rem;
    }
    .plain-head { color: var(--vc-muted); }
    .vc-head    { color: var(--vc-teal);  }
    .delta-pill {
      display: inline-block;
      background: var(--vc-green-light);
      color: #065F46;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.25rem 0.8rem;
      margin-top: 0.5rem;
    }

    /* ── Buttons ─────────────────────────────────────────────────── */
    .stButton button, .stDownloadButton button {
      min-height: 44px;
      border-radius: 6px;
      font-weight: 700;
      transition: filter 0.15s ease;
    }
    .stButton button:hover  { filter: brightness(1.08); }
    .stButton button:focus,
    .stDownloadButton button:focus {
      outline: 3px solid rgba(8, 145, 178, 0.4);
      outline-offset: 2px;
    }

    /* ── Data tables ─────────────────────────────────────────────── */
    div[data-testid="stDataFrame"] {
      border: 1px solid var(--vc-line);
      border-radius: 6px;
      overflow: hidden;
    }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
      background-color: #F0F9FF;
      border-right: 1px solid var(--vc-line);
    }
    .vc-sidebar-brand {
      width: 108px;
      height: 108px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #FFFFFF;
      border: 1px solid rgba(203, 213, 225, 0.9);
      border-radius: 8px;
      box-shadow: 0 1px 8px rgba(12, 35, 64, 0.08);
      margin: 0.2rem 0 1.35rem 0;
    }
    .vc-sidebar-brand img {
      width: 86px;
      height: 86px;
      display: block;
      object-fit: contain;
    }
    [data-testid="stSidebar"] h3 {
      color: var(--vc-navy);
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.07em;
      text-transform: uppercase;
      margin: 1rem 0 0.4rem 0;
    }
    [data-testid="stSidebar"] .stRadio label {
      font-size: 0.9rem;
      color: var(--vc-ink);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--vc-muted);
    }
    /* ── Force light background on inputs ───────────────────────── */
    .stTextArea textarea,
    .stTextInput input {
      background-color: #FFFFFF !important;
      color: var(--vc-navy) !important;
      border: 1px solid var(--vc-line) !important;
      border-radius: 6px !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
      border-color: var(--vc-teal) !important;
      box-shadow: 0 0 0 3px rgba(8,145,178,0.15) !important;
    }

    /* ── Responsive ──────────────────────────────────────────────── */
    @media (max-width: 1100px) {
      .vc-appbar { grid-template-columns: auto 1fr; row-gap: 10px; padding: 14px 18px; }
      .vc-appbar-status {
        grid-column: 1 / -1;
        padding-left: 0;
        border-left: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 10px;
        flex-wrap: wrap;
      }
    }

    @media (max-width: 720px) {
      .vc-appbar { grid-template-columns: 1fr; padding: 14px 16px; }
      .vc-appbar-brand { padding-right: 0; border-right: none; }
      .vc-appbar-tagline-pri { white-space: normal; }
      .vc-appbar-tagline-sec { display: none; }
      .vc-appbar-status { gap: 6px; }
      .pico-grid              { grid-template-columns: 1fr; }
      .metric-row             { flex-direction: column; }
      .block-container        { padding-left: 1rem; padding-right: 1rem; }
    }

    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; animation: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

_SL = '<div class="pack-section-label">{}</div>'


def _sec(text: str) -> None:
    st.markdown(_SL.format(text), unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    _mark_src = f"data:image/png;base64,{_img_b64(MARK_PATH)}" if MARK_PATH.exists() else ""
    if _mark_src:
        st.markdown(
            (
                f'<div class="vc-sidebar-brand">'
                f'<img src="{_mark_src}" alt="VeritasClin Field">'
                f"</div>"
            ),
            unsafe_allow_html=True,
        )
    st.markdown("### Mode")
    mode = st.radio(
        "Select mode",
        ["Build Evidence Pack", "Load Offline Pack", "Plain Gemma vs VeritasClin Demo"],
        label_visibility="collapsed",
    )

    st.markdown("### Provider")
    _provider_options = ["ollama", "openai_compatible"]
    _env_provider = os.environ.get("GEMMA_PROVIDER", "ollama")
    _provider_default = (
        _provider_options.index(_env_provider)
        if _env_provider in _provider_options
        else 0
    )
    provider = st.selectbox("LLM provider", _provider_options, index=_provider_default)
    if os.environ.get("GEMMA_PROVIDER") != provider:
        os.environ["GEMMA_PROVIDER"] = provider
        reset_settings_cache()

    st.markdown("### Retrieval")
    language_label = st.selectbox("Language", ["English", "Portuguese", "Spanish"], index=0)
    language = {"English": "en", "Portuguese": "pt", "Spanish": "es"}[language_label]
    max_results = st.slider("Max PubMed results", min_value=5, max_value=20, value=10)
    _s = get_settings()
    use_pubmed = st.toggle(
        "Use PubMed",
        value=_s.pubmed_configured,
        help="When off, the app uses bundled demo papers (no external retrieval).",
    )
    _settings_sidebar = get_settings()
    _pubmed_status = "configured" if _settings_sidebar.pubmed_configured else "not configured"
    st.caption(f"PubMed credentials: **{_pubmed_status}**")

    st.markdown("---")
    st.markdown("### Demo Questions")
    demo = st.radio(
        "Select a demo",
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

# ── Derived state ──────────────────────────────────────────────────────────

settings = get_settings()
source_mode = "PubMed enabled" if use_pubmed and settings.pubmed_configured else "Bundled demo data"
offline_state = "Loaded" if "pack" in st.session_state else "No pack loaded"
provider_label = provider.replace("_", " ").title()

# ── Provider warnings ─────────────────────────────────────────────────────

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

# ── Header ─────────────────────────────────────────────────────────────────

_hero_mark_src = f"data:image/png;base64,{_img_b64(MARK_PATH)}" if MARK_PATH.exists() else ""
_hero_mark_html = (
    f'<img src="{_hero_mark_src}" alt="VeritasClin Field">'
    if _hero_mark_src
    else '<span class="vc-appbar-mark-fallback">V</span>'
)

_retrieval_dot = "dot-green" if (use_pubmed and settings.pubmed_configured) else "dot-amber"
_offline_dot = "dot-green" if "pack" in st.session_state else "dot-muted"

st.markdown(
    f"""
    <header class="vc-appbar" role="banner" aria-label="VeritasClin Field console">
      <div class="vc-appbar-brand">
        <div class="vc-appbar-mark">{_hero_mark_html}</div>
        <div class="vc-appbar-wordmark">
          <span class="vc-appbar-wordmark-main">VeritasClin</span>
          <span class="vc-appbar-wordmark-sub">Field Console</span>
        </div>
      </div>
      <div class="vc-appbar-tagline">
        <span class="vc-appbar-tagline-pri">
          Audit-ready medical evidence <b>for field teams</b>
        </span>
        <span class="vc-appbar-tagline-sec">
          PubMed-backed packs &middot; offline-capable &middot; English, Portuguese, Spanish
        </span>
      </div>
      <div class="vc-appbar-status">
        <span class="vc-chip vc-chip-accent" title="Powered by Gemma 4 — 8 pipeline touchpoints">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          Gemma&nbsp;4
        </span>
        <span class="vc-chip">
          <span class="vc-chip-dot dot-teal"></span>
          {provider_label}
        </span>
        <span class="vc-chip">
          <span class="vc-chip-dot {_retrieval_dot}"></span>
          {source_mode}
        </span>
        <span class="vc-chip">
          <span class="vc-chip-dot {_offline_dot}"></span>
          {offline_state}
        </span>
      </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ── Disclaimer ─────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="vc-disclaimer">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
           style="flex-shrink:0;opacity:0.6">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <span>
        <strong style="color:#374151">Medical disclaimer:</strong>&nbsp;
        Evidence review and education only — not a diagnostic, prescription, or triage tool.
        All clinical decisions must be made by qualified healthcare professionals.
      </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Helper: safety decision widget ────────────────────────────────────────

def render_safety_widget(safety) -> None:
    """Render a clean, human-readable safety decision card."""
    if not safety.allowed:
        st.markdown(
            f"""
            <div class="vc-safety-blocked">
              <span class="vc-safety-badge badge-blocked">Blocked</span>
              <div class="vc-safety-body">
                <div class="vc-safety-title">Request blocked</div>
                <div class="vc-safety-detail">{safety.user_message}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif safety.safe_rewritten_question:
        rewritten = safety.safe_rewritten_question
        rewrite_ok = safety_rewrite_success(safety)
        st.markdown(
            f"""
            <div class="vc-safety-rewritten">
              <span class="vc-safety-badge badge-rewritten">Rewritten</span>
              <div class="vc-safety-body">
                <div class="vc-safety-title">
                  Question reframed as a research question
                  {"&#10003;" if rewrite_ok else ""}
                </div>
                <div class="vc-safety-detail">{safety.user_message}</div>
                <div class="vc-rewrite-box">{rewritten}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="vc-safety-allowed">
              <span class="vc-safety-badge badge-allowed">Allowed</span>
              <div class="vc-safety-body">
                <div class="vc-safety-title">Question cleared for evidence retrieval</div>
                <div class="vc-safety-detail">No safety concerns detected.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Helper: metric card color ──────────────────────────────────────────────

def _coverage_color(val: float) -> str:
    if val >= 0.8:
        return "color-green"
    if val >= 0.5:
        return "color-amber"
    return "color-red"


def _unsupported_color(n: int) -> str:
    if n == 0:
        return "color-green"
    if n <= 2:
        return "color-amber"
    return "color-red"


def _freshness_color(val: float) -> str:
    if val >= 0.7:
        return "color-green"
    if val >= 0.4:
        return "color-amber"
    return "color-red"


# ── Helper: render full pack ───────────────────────────────────────────────

def render_pack(pack: EvidencePack) -> None:
    st.markdown(
        f"""
        <div class="vc-section-head">
          <h2>{pack.title}</h2>
          <div class="vc-section-sub">Source: <b>{pack.source}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Metric row ─────────────────────────────────────────────────
    n_unsupported = unsupported_claim_count(pack.claim_ledger)
    n_high = high_risk_unsupported_claim_count(pack.claim_ledger)
    cov = pack.citation_coverage
    fresh = pack.freshness.score

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"""<div class="metric-card">
          <span class="metric-card-label">Citation coverage</span>
          <span class="metric-card-value {_coverage_color(cov)}">{cov:.0%}</span>
          <span class="metric-card-sub">Claims linked to evidence</span>
        </div>""",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""<div class="metric-card">
          <span class="metric-card-label">Unsupported claims</span>
          <span class="metric-card-value {_unsupported_color(n_unsupported)}">{n_unsupported}</span>
          <span class="metric-card-sub">Assertions without citation</span>
        </div>""",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"""<div class="metric-card">
          <span class="metric-card-label">High-risk unsupported</span>
          <span class="metric-card-value {_unsupported_color(n_high)}">{n_high}</span>
          <span class="metric-card-sub">High-risk uncited claims</span>
        </div>""",
        unsafe_allow_html=True,
    )
    c4.markdown(
        f"""<div class="metric-card">
          <span class="metric-card-label">Freshness</span>
          <span class="metric-card-value {_freshness_color(fresh)}">{fresh:.0%}</span>
          <span class="metric-card-sub">Refresh in {pack.freshness.recommended_refresh_days}d</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Tabs ───────────────────────────────────────────────────────
    tabs = st.tabs(
        ["Pack Summary", "PICO & Query", "Evidence Map", "Claim Ledger", "Caution Map", "Exports"]
    )

    # Pack Summary tab
    with tabs[0]:
        _sec('Executive Summary')
        st.write(pack.executive_summary)
        _sec('Clinical Interpretation')
        st.write(pack.clinical_interpretation)
        _sec('What the Evidence Does Not Prove')
        _does_not_prove = pack.what_the_evidence_does_not_prove
        if isinstance(_does_not_prove, list):
            for _item in _does_not_prove:
                st.markdown(f"- {_item}")
        else:
            st.write(_does_not_prove)
        _sec('Patient-Friendly Explanation')
        st.write(pack.patient_friendly_explanation)
        st.info(pack.safety_notice)

    # PICO & Query tab
    with tabs[1]:
        pico = pack.pico
        _sec('PICO Framework')

        def _pico_val(v) -> str:
            if not v:
                return "<em style='opacity:0.5'>Not specified</em>"
            if isinstance(v, list):
                return ", ".join(str(x) for x in v)
            return str(v)

        st.markdown(
            f"""
            <div class="pico-grid">
              <div class="pico-card">
                <span class="pico-letter">P — Population</span>
                <span class="pico-value">{_pico_val(getattr(pico, "population", None))}</span>
              </div>
              <div class="pico-card">
                <span class="pico-letter">I — Intervention</span>
                <span class="pico-value">{_pico_val(getattr(pico, "intervention", None))}</span>
              </div>
              <div class="pico-card">
                <span class="pico-letter">C — Comparison</span>
                <span class="pico-value">{_pico_val(getattr(pico, "comparison", None))}</span>
              </div>
              <div class="pico-card">
                <span class="pico-letter">O — Outcome</span>
                <span class="pico-value">{_pico_val(getattr(pico, "outcome", None))}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _sec('PubMed Query')
        st.code(pack.pubmed_query, language="text")
        _method = pack.pubmed_query_method
        _method_label = (
            "Gemma 4 native function calling"
            if _method == "gemma4-function-calling"
            else "Algorithmic fallback"
        )
        _method_color = "color-green" if _method == "gemma4-function-calling" else "color-amber"
        st.markdown(
            f'Query method: <span class="{_method_color}" style="font-weight:600">'
            f"{_method_label}</span>&nbsp;&nbsp;|&nbsp;&nbsp;Source: <b>{pack.source}</b>",
            unsafe_allow_html=True,
        )

    # Evidence Map tab
    with tabs[2]:
        _sec('Ranked Evidence')
        st.caption(
            f"{len(pack.evidence_items)} papers retrieved and ranked by "
            "study type, recency, and PICO overlap."
        )
        df_ev = pd.DataFrame(
            [
                {
                    "ID / PMID": item.paper.pmid,
                    "Title": item.paper.title[:90] + ("…" if len(item.paper.title) > 90 else ""),
                    "Year": item.paper.publication_year,
                    "Study type": item.study_type,
                    "Evidence level": item.evidence_level,
                    "Relevance": f"{item.relevance_score:.2f}",
                }
                for item in pack.evidence_items
            ]
        )
        st.dataframe(df_ev, use_container_width=True, hide_index=True)

    # Claim Ledger tab
    with tabs[3]:
        _sec('Claim Ledger')
        st.caption(
            "Every clinical assertion extracted from the synthesis, with support status, "
            "evidence level, risk level, and cited evidence IDs."
        )

        _status_map = {
            "supported": ("pill pill-supported", "Supported"),
            "partially_supported": ("pill pill-partial", "Partial"),
            "unsupported": ("pill pill-unsupported", "Unsupported"),
            "uncertain": ("pill pill-uncertain", "Uncertain"),
        }

        for i, claim in enumerate(pack.claim_ledger):
            _css, _label = _status_map.get(
                claim.support_status, ("pill pill-uncertain", claim.support_status)
            )
            _suffix = "…" if len(claim.text) > 80 else ""
            with st.expander(
                f"Claim {i + 1} — {claim.text[:80]}{_suffix}",
                expanded=False,
            ):
                st.markdown(
                    f'<span class="{_css}">{_label}</span>&nbsp;&nbsp;'
                    f'Risk: <b>{claim.risk_level}</b>&nbsp;&nbsp;'
                    f'Evidence: <b>{claim.evidence_level}</b>',
                    unsafe_allow_html=True,
                )
                st.write(claim.text)
                if claim.pmids:
                    st.caption(f"Cited IDs: {', '.join(claim.pmids)}")
                if claim.rationale:
                    st.caption(f"Rationale: {claim.rationale}")
                if claim.limitation_note:
                    st.caption(f"Limitations: {claim.limitation_note}")

        # Also show full table for download / review
        with st.expander("Full table view"):
            st.dataframe(
                pd.DataFrame([c.model_dump(mode="json") for c in pack.claim_ledger]),
                use_container_width=True,
                hide_index=True,
            )

    # Caution Map tab
    with tabs[4]:
        _sec('Caution & Conflict Map')
        st.caption(
            f"{len(pack.caution_map)} uncertainty signals detected across "
            "7 categories: low certainty, population mismatch, safety signal, "
            "indirect evidence, conflicting results, insufficient data, outcome mismatch."
        )
        _sev_css = {"high": "sev-high", "medium": "sev-medium", "low": "sev-low"}
        for item in pack.caution_map:
            _sev = str(item.severity).lower()
            _css = _sev_css.get(_sev, "sev-medium")
            _expl = item.explanation
            with st.expander(
                f"{item.caution_type.replace('_', ' ').title()} — "
                f"{_expl[:70]}{'…' if len(_expl) > 70 else ''}",
                expanded=False,
            ):
                st.markdown(
                    f'Severity: <span class="{_css}">{_sev.upper()}</span>',
                    unsafe_allow_html=True,
                )
                st.write(_expl)
                if item.claim_id:
                    st.caption(f"Linked claim ID: {item.claim_id}")

        with st.expander("Full table view"):
            st.dataframe(
                pd.DataFrame([i.model_dump(mode="json") for i in pack.caution_map]),
                use_container_width=True,
                hide_index=True,
            )

    # Exports tab
    with tabs[5]:
        _sec('Download Artifacts')
        st.caption(
            "All artifacts travel together with the pack: query, PMIDs, claims, cautions, "
            "and timestamps. The pack is fully self-contained for offline use."
        )

        # Primary export — HTML field report (human-readable, browser-only, print-to-PDF)
        st.markdown(
            '<div class="export-card">'
            '<div class="export-title">&#127760; Field Report (HTML)</div>'
            '<div class="export-desc">'
            "<strong>Start here.</strong> A readable field report — opens in any browser, "
            "works offline, and prints to PDF. Designed for healthcare workers, "
            "not data analysts. Contains summary, claim ledger, caution map, "
            "evidence sources, and safety notice.</div>",
            unsafe_allow_html=True,
        )
        _pack_slug = pack.pack_id.replace("vfield-", "")
        st.download_button(
            "Download field_report.html",
            pack_to_html(pack),
            f"veritasclin_field_report_{_pack_slug}.html",
            "text/html",
            use_container_width=True,
            type="primary",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                '<div class="export-card">'
                '<div class="export-title">pack.json</div>'
                '<div class="export-desc">Complete self-contained Evidence Pack. '
                "Upload this file in Load Offline Pack mode to enable offline Q&A.</div>",
                unsafe_allow_html=True,
            )
            st.download_button(
                "Download pack.json",
                pack_to_json(pack),
                "pack.json",
                "application/json",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                '<div class="export-card">'
                '<div class="export-title">claim_ledger.csv</div>'
                '<div class="export-desc">All extracted claims with support status, '
                "risk level, evidence level, and cited IDs. Opens in Excel or Sheets.</div>",
                unsafe_allow_html=True,
            )
            st.download_button(
                "Download claim_ledger.csv",
                claims_to_csv(pack.claim_ledger),
                "claim_ledger.csv",
                "text/csv",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown(
                '<div class="export-card">'
                '<div class="export-title">dossier.md</div>'
                '<div class="export-desc">Markdown dossier — '
                "executive summary, PICO, evidence list, and clinical interpretation.</div>",
                unsafe_allow_html=True,
            )
            st.download_button(
                "Download dossier.md",
                pack_to_markdown(pack),
                "dossier.md",
                "text/markdown",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                '<div class="export-card">'
                '<div class="export-title">caution_map.json</div>'
                '<div class="export-desc">Structured uncertainty signals — '
                "severity, signal type, and description for each detected risk.</div>",
                unsafe_allow_html=True,
            )
            st.download_button(
                "Download caution_map.json",
                caution_map_to_json(pack.caution_map),
                "caution_map.json",
                "application/json",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


# ── LLM provider ───────────────────────────────────────────────────────────

llm = get_llm_provider(provider)

# ══════════════════════════════════════════════════════════════════════════
# MODE: Build Evidence Pack
# ══════════════════════════════════════════════════════════════════════════

if mode == "Build Evidence Pack":
    st.markdown(
        """
        <div class="vc-section-head">
          <h2>Build Evidence Pack</h2>
          <div class="vc-section-sub">
            Enter a clinical evidence question. Gemma 4 will extract PICO, build a
            PubMed query via native function calling, retrieve and rank evidence,
            then synthesise a cited, audit-ready Evidence Pack.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Clinical evidence question",
        value=DEMO_QUESTIONS[demo],
        height=90,
        placeholder="e.g. What does evidence say about warning signs for severe dengue in adults?",
    )

    uploaded_image = st.file_uploader(
        "Clinical image, lab report, or chart (optional — Gemma 4 multimodal input)",
        type=["jpg", "jpeg", "png"],
        help=(
            "Gemma 4 will read the image and include its findings in the evidence question. "
            "Requires Ollama or OpenAI-compatible provider."
        ),
    )
    image_bytes: bytes | None = uploaded_image.read() if uploaded_image else None
    if uploaded_image and provider not in ("ollama", "openai_compatible"):
        st.warning(
            "Image analysis requires Ollama or OpenAI-compatible provider. "
            "The image will be ignored with the current provider selection.",
            icon="⚠️",
        )

    # Safety check
    safety = SafetyGuard(provider=llm).check(question)
    render_safety_widget(safety)

    if st.button("Build Evidence Pack", type="primary", use_container_width=False):
        if not safety.allowed:
            st.error(safety.user_message)
        else:
            steps = [
                ("Safety check", True),
                ("Image analysis (Gemma 4 multimodal)" if image_bytes else "PICO extraction", True),
                ("PICO extraction", not bool(image_bytes)),
                ("PubMed query via Gemma 4 function calling", True),
                ("PubMed retrieval or bundled demo papers", True),
                ("Evidence ranking", True),
                ("Gemma 4 synthesis", True),
                ("Claim extraction", True),
                ("Claim verification", True),
                ("Caution mapping", True),
                ("Freshness scoring", True),
            ]
            active_steps = [(s, v) for s, v in steps if v]
            progress = st.progress(0)
            status = st.empty()
            for idx, (step, _) in enumerate(active_steps, start=1):
                status.markdown(
                    f'<div class="pipeline-step pipeline-step-active">'
                    f"Running: {step}...</div>",
                    unsafe_allow_html=True,
                )
                progress.progress(idx / len(active_steps))
            try:
                pack, baseline = PackBuilder(provider=llm).build(
                    question,
                    language=language,
                    max_results=max_results,
                    include_baseline=True,
                    use_bundled_papers=not use_pubmed,
                    image_bytes=image_bytes,
                )
                st.session_state["pack"] = pack
                st.session_state["baseline"] = baseline
                status.success("Evidence Pack ready. Scroll down to explore results.")
            except ValueError as exc:
                st.error(str(exc))

    if "pack" in st.session_state:
        render_pack(st.session_state["pack"])

# ══════════════════════════════════════════════════════════════════════════
# MODE: Load Offline Pack
# ══════════════════════════════════════════════════════════════════════════

elif mode == "Load Offline Pack":
    st.markdown(
        """
        <div class="vc-section-head">
          <h2>Load Offline Pack</h2>
          <div class="vc-section-sub">
            Upload a <code>pack.json</code> exported from Build mode. The app will answer
            questions exclusively from the loaded Claim Ledger — no PubMed, no internet.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("Upload pack.json", type=["json"])
    pack = st.session_state.get("pack")
    if uploaded:
        pack = PackLoader().loads(uploaded.read())
        st.session_state["pack"] = pack

    if pack:
        # Pack info card
        st.markdown(
            f"""
            <div style="background:var(--vc-green-light);border:1px solid #6EE7B7;
                        border-radius:8px;padding:0.8rem 1.1rem;margin-bottom:1rem;">
              <div style="font-weight:700;color:#065F46;margin-bottom:0.35rem;">
                Offline pack loaded — no PubMed retrieval used
              </div>
              <div style="font-size:0.88rem;color:var(--vc-ink);">
                <b>Title:</b> {pack.title}<br>
                <b>Pack ID:</b> {pack.pack_id}<br>
                <b>Source:</b> {pack.source}&nbsp;&nbsp;
                <b>Claims:</b> {len(pack.claim_ledger)}&nbsp;&nbsp;
                <b>Coverage:</b> {pack.citation_coverage:.0%}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info(
            "Tip: Include clinical keywords from the pack topic for best results. "
            "Unsupported questions will be refused."
        )

        demo_q = "What are the warning signs for severe dengue in adults?"
        offline_question = st.text_input(
            "Ask within the loaded pack",
            value=demo_q,
            placeholder="Ask a clinical question answered by this pack's evidence…",
        )

        lang_label = {"en": "English", "pt": "Portuguese", "es": "Spanish"}.get(language, language)
        st.caption(f"Response language: **{lang_label}**")

        if st.button("Ask offline", type="primary"):
            with st.spinner("Answering from loaded Claim Ledger only…"):
                answer = ask_offline_pack(pack, offline_question, language=language, provider=llm)
            st.markdown(
                '<div class="pack-section-label">Offline Answer</div>',
                unsafe_allow_html=True,
            )
            st.write(answer)

        st.markdown("---")
        render_pack(pack)
    else:
        st.info(
            "No pack loaded. Build an Evidence Pack in Build mode and download `pack.json`, "
            "then upload it here for offline use."
        )

# ══════════════════════════════════════════════════════════════════════════
# MODE: Plain Gemma vs VeritasClin Demo
# ══════════════════════════════════════════════════════════════════════════

else:
    st.markdown(
        """
        <div class="vc-section-head">
          <h2>Plain Gemma vs VeritasClin</h2>
          <div class="vc-section-sub">
            Side-by-side comparison of a raw model answer against a VeritasClin
            Evidence Pack response. Build the dengue pack first, then return here.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pack = st.session_state.get("pack")
    baseline = st.session_state.get("baseline")
    if not pack:
        st.info("Build the dengue Evidence Pack first, then return here for the comparison.")
    elif baseline:
        st.markdown(
            f"""
            <div style="background:var(--vc-panel-alt);border:1px solid var(--vc-line);
                        border-radius:8px;padding:0.8rem 1.1rem;margin-bottom:1.1rem;
                        font-size:0.9rem;color:var(--vc-ink);">
              <b>Baseline delta:</b> {baseline.summary}
            </div>
            """,
            unsafe_allow_html=True,
        )
        left, right = st.columns(2)
        with left:
            st.markdown(
                '<div class="compare-col">'
                '<h3 class="plain-head">Plain model answer</h3>',
                unsafe_allow_html=True,
            )
            st.write(baseline.baseline_answer)
            _delta_unsup = (
                baseline.baseline_unsupported_claim_count
                - baseline.veritasclin_unsupported_claim_count
            )
            c_a, c_b = st.columns(2)
            c_a.metric("Unsupported claims", baseline.baseline_unsupported_claim_count)
            c_b.metric("High-risk unsupported", baseline.baseline_high_risk_unsupported_count)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="compare-col">'
                '<h3 class="vc-head">VeritasClin Evidence Pack</h3>',
                unsafe_allow_html=True,
            )
            st.write(pack.executive_summary)
            c_c, c_d = st.columns(2)
            c_c.metric(
                "Unsupported claims",
                baseline.veritasclin_unsupported_claim_count,
                delta=-_delta_unsup if _delta_unsup > 0 else None,
                delta_color="inverse",
            )
            c_d.metric("Citation coverage", f"{baseline.citation_coverage:.0%}")
            if _delta_unsup > 0:
                st.markdown(
                    f'<div class="delta-pill">'
                    f"{_delta_unsup} fewer unsupported claims than plain Gemma"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Baseline comparison was not generated for the current pack.")
