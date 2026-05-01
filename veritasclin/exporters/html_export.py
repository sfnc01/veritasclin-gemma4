"""Generate a self-contained HTML field report for a VeritasClin Evidence Pack.

The output is a single .html file with embedded CSS — no external dependencies.
It opens in any browser, works offline, and prints cleanly to PDF.
Designed for public health workers, not data analysts.
"""
from __future__ import annotations

import html as _html
from datetime import UTC, datetime

from veritasclin.schemas.pack import EvidencePack

# ── Colour tokens ────────────────────────────────────────────────────────────

_STATUS_COLOUR = {
    "supported": ("#1a7a4a", "#d4f0e2"),
    "partially_supported": ("#7a5c00", "#fff3cd"),
    "unsupported": ("#9b1c1c", "#fde8e8"),
    "uncertain": ("#374151", "#f3f4f6"),
}
_SEV_COLOUR = {
    "high": ("#9b1c1c", "#fde8e8"),
    "medium": ("#7a5c00", "#fff3cd"),
    "low": ("#1e3a5f", "#dbeafe"),
}
_DEFAULT_COLOUR = ("#374151", "#f3f4f6")

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #1a2635;
  background: #ffffff;
  max-width: 860px;
  margin: 0 auto;
  padding: 28px 24px 56px;
}
h1 { font-size: 1.45rem; color: #0c4a6e; margin-bottom: 4px; }
h2 {
  font-size: 1.05rem;
  color: #0c4a6e;
  border-bottom: 2px solid #bae6fd;
  padding-bottom: 4px;
  margin: 28px 0 12px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
h3 { font-size: 0.92rem; color: #164e63; margin-bottom: 4px; }
p { margin-bottom: 10px; }
ul { padding-left: 20px; margin-bottom: 10px; }
li { margin-bottom: 4px; }

.header-band {
  background: linear-gradient(135deg, #0c4a6e 0%, #0891b2 100%);
  color: #fff;
  border-radius: 8px;
  padding: 20px 24px 16px;
  margin-bottom: 24px;
}
.header-band h1 { color: #fff; font-size: 1.3rem; margin-bottom: 6px; }
.header-meta { font-size: 0.78rem; opacity: .85; }
.header-meta span { margin-right: 16px; }

.alert-box {
  background: #fff3cd;
  border-left: 4px solid #d97706;
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 20px;
  font-size: 0.87rem;
}
.alert-box strong { display: block; margin-bottom: 2px; color: #92400e; }

.pico-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
}
.pico-card {
  border: 1px solid #e0f2fe;
  border-radius: 6px;
  padding: 10px 14px;
  background: #f0f9ff;
}
.pico-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #0891b2;
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: 2px;
}
.pico-value { font-size: 0.88rem; }

.claim {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 10px;
  background: #fafafa;
}
.claim-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: .04em;
  white-space: nowrap;
}
.claim-text { font-size: 0.88rem; margin-bottom: 4px; }
.claim-meta { font-size: 0.75rem; color: #6b7280; }

.caution {
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 8px;
  border: 1px solid transparent;
}
.caution-header { font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .04em; margin-bottom: 4px; }
.caution-text { font-size: 0.86rem; }

.evidence-row {
  display: grid;
  grid-template-columns: 120px 80px 1fr;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.83rem;
}
.evidence-row:last-child { border-bottom: none; }
.evidence-pmid { font-family: monospace; font-size: 0.78rem; color: #6b7280; }
.evidence-level {
  font-size: 0.72rem;
  font-weight: 700;
  color: #0891b2;
  text-transform: uppercase;
}
.evidence-title { color: #1a2635; }

.freshness-bar-bg {
  background: #e5e7eb;
  border-radius: 4px;
  height: 8px;
  width: 180px;
  display: inline-block;
  vertical-align: middle;
  margin: 0 8px;
}
.freshness-bar-fill {
  background: #0891b2;
  border-radius: 4px;
  height: 8px;
}

.query-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 10px 14px;
  font-family: monospace;
  font-size: 0.8rem;
  color: #334155;
  word-break: break-word;
  margin-bottom: 4px;
}

.disclaimer {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 14px 18px;
  margin-top: 32px;
  font-size: 0.8rem;
  color: #6b7280;
}

.section-summary {
  font-size: 0.88rem;
  color: #374151;
  margin-bottom: 14px;
}

@media print {
  body { padding: 0; font-size: 12px; }
  .header-band { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .claim, .caution, .pico-card { break-inside: avoid; }
  h2 { break-after: avoid; }
}
"""


def _e(text: str | None) -> str:
    return _html.escape(str(text or ""), quote=True)


def _pill(label: str, fg: str, bg: str) -> str:
    return (
        f'<span class="pill" style="color:{fg};background:{bg}">'
        f"{_e(label.replace('_', ' ').title())}</span>"
    )


def _status_pill(status: str) -> str:
    fg, bg = _STATUS_COLOUR.get(status, _DEFAULT_COLOUR)
    return _pill(status, fg, bg)


def _sev_pill(severity: str) -> str:
    fg, bg = _SEV_COLOUR.get(severity, _DEFAULT_COLOUR)
    return _pill(severity, fg, bg)


def pack_to_html(pack: EvidencePack) -> str:
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    freshness_pct = int(pack.freshness.score * 100)
    freshness_bar = (
        f'<div class="freshness-bar-bg"><div class="freshness-bar-fill" '
        f'style="width:{freshness_pct}%"></div></div>'
    )

    # ── Claims ────────────────────────────────────────────────────────────────
    claims_html = ""
    for claim in pack.claim_ledger:
        fg, bg = _STATUS_COLOUR.get(claim.support_status, _DEFAULT_COLOUR)
        risk_fg, risk_bg = _SEV_COLOUR.get(claim.risk_level, _DEFAULT_COLOUR)
        pmids_str = ", ".join(claim.pmids) if claim.pmids else "No citation"
        limitation = (
            f'<div class="claim-meta">Note: {_e(claim.limitation_note)}</div>'
            if claim.limitation_note
            else ""
        )
        claims_html += (
            f'<div class="claim">'
            f'<div class="claim-header">'
            f'<span style="font-size:0.75rem;color:#9ca3af">{_e(claim.id)}</span>'
            f"{_status_pill(claim.support_status)}"
            f'{_pill(claim.risk_level + " risk", risk_fg, risk_bg)}'
            f"</div>"
            f'<div class="claim-text">{_e(claim.text)}</div>'
            f'<div class="claim-meta">Evidence level: {_e(claim.evidence_level)} '
            f"&nbsp;·&nbsp; Sources: {_e(pmids_str)}</div>"
            f"{limitation}"
            f"</div>"
        )

    # ── Cautions ─────────────────────────────────────────────────────────────
    cautions_html = ""
    for item in pack.caution_map:
        fg, bg = _SEV_COLOUR.get(item.severity, _DEFAULT_COLOUR)
        type_label = item.caution_type.replace("_", " ").title()
        cautions_html += (
            f'<div class="caution" style="background:{bg};border-color:{fg}30">'
            f'<div class="caution-header" style="color:{fg}">'
            f"{_e(type_label)} &nbsp;{_sev_pill(item.severity)}</div>"
            f'<div class="caution-text">{_e(item.explanation)}</div>'
            f"</div>"
        )

    # ── Evidence rows ─────────────────────────────────────────────────────────
    evidence_html = ""
    for item in pack.evidence_items:
        pub_url = item.paper.url or f"https://pubmed.ncbi.nlm.nih.gov/{item.paper.pmid}/"
        evidence_html += (
            f'<div class="evidence-row">'
            f'<span class="evidence-pmid">'
            f'<a href="{_e(pub_url)}" target="_blank">{_e(item.paper.pmid)}</a></span>'
            f'<span class="evidence-level">{_e(item.evidence_level)}</span>'
            f'<span class="evidence-title">{_e(item.paper.title)}'
            f" ({item.paper.publication_year or 'n/a'})</span>"
            f"</div>"
        )

    # ── PICO cards ────────────────────────────────────────────────────────────
    pico = pack.pico
    pico_html = (
        f'<div class="pico-grid">'
        f'<div class="pico-card"><div class="pico-label">Population</div>'
        f'<div class="pico-value">{_e(pico.population or "Not specified")}</div></div>'
        f'<div class="pico-card"><div class="pico-label">Intervention / Exposure</div>'
        f'<div class="pico-value">{_e(pico.intervention or "Not specified")}</div></div>'
        f'<div class="pico-card"><div class="pico-label">Comparison</div>'
        f'<div class="pico-value">{_e(pico.comparison or "Not specified")}</div></div>'
        f'<div class="pico-card"><div class="pico-label">Outcome</div>'
        f'<div class="pico-value">{_e(pico.outcome or "Not specified")}</div></div>'
        f"</div>"
    )

    # ── What it does not prove ────────────────────────────────────────────────
    limits_html = "".join(
        f"<li>{_e(item)}</li>" for item in pack.what_the_evidence_does_not_prove
    )

    # ── Coverage stat ─────────────────────────────────────────────────────────
    coverage_pct = int(pack.citation_coverage * 100)
    supported_n = sum(1 for c in pack.claim_ledger if c.support_status == "supported")
    unsupported_n = sum(1 for c in pack.claim_ledger if c.support_status == "unsupported")

    return f"""<!DOCTYPE html>
<html lang="{_e(pack.language)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_e(pack.title)}</title>
<style>{_CSS}</style>
</head>
<body>

<div class="header-band">
  <h1>{_e(pack.title)}</h1>
  <div class="header-meta">
    <span>&#128197; {_e(pack.created_at[:10])}</span>
    <span>&#127760; Language: {_e(pack.language.upper())}</span>
    <span>&#128209; Source: {_e(pack.source)}</span>
    <span>&#128203; Pack ID: {_e(pack.pack_id)}</span>
  </div>
</div>

<div class="alert-box">
  <strong>&#9888;&#65039; Medical Disclaimer</strong>
  {_e(pack.safety_notice)}
  This field report is for evidence review and education only.
  All clinical decisions must be made by qualified healthcare professionals.
</div>

<h2>&#128269; Clinical Question</h2>
<p class="section-summary">{_e(pico.original_question)}</p>
{pico_html}

<h2>&#128220; Executive Summary</h2>
<p class="section-summary">{_e(pack.executive_summary)}</p>

<h2>&#129489;&#8205;&#9877;&#65039; For the Patient or Community Worker</h2>
<p class="section-summary">{_e(pack.patient_friendly_explanation)}</p>

<h2>&#9989; Claim Ledger
  <span style="font-weight:400;font-size:0.82rem;color:#6b7280;margin-left:8px">
    {supported_n} supported &nbsp;·&nbsp; {unsupported_n} unsupported
    &nbsp;·&nbsp; {coverage_pct}% citation coverage
  </span>
</h2>
<p style="font-size:0.8rem;color:#6b7280;margin-bottom:12px">
  Every claim below is linked to the paper that supports it.
  A claim without a source is marked Unsupported.
</p>
{claims_html or "<p>No claims extracted.</p>"}

<h2>&#9888;&#65039; Caution &amp; Conflict Map</h2>
<p style="font-size:0.8rem;color:#6b7280;margin-bottom:12px">
  These signals indicate where the evidence has limitations,
  conflicts, or gaps a clinician should be aware of.
</p>
{cautions_html or "<p>No cautions identified.</p>"}

<h2>&#10060; What This Evidence Does NOT Prove</h2>
<ul>{limits_html}</ul>

<h2>&#128202; Evidence Freshness</h2>
<p style="font-size:0.86rem">
  Freshness score: <strong>{freshness_pct}%</strong>
  {freshness_bar}
  Newest paper: <strong>{pack.freshness.newest_publication_year or "unknown"}</strong>
  &nbsp;·&nbsp; Refresh in: <strong>{pack.freshness.recommended_refresh_days} days</strong>
</p>
<p style="font-size:0.8rem;color:#6b7280">{_e(pack.freshness.rationale)}</p>

<h2>&#128196; PubMed Search Strategy</h2>
<p style="font-size:0.8rem;color:#6b7280;margin-bottom:6px">
  Query method: {_e(pack.pubmed_query_method)}
</p>
<div class="query-box">{_e(pack.pubmed_query)}</div>

<h2>&#128214; Evidence Sources ({len(pack.evidence_items)} papers)</h2>
{evidence_html or "<p>No evidence loaded.</p>"}

<div class="disclaimer">
  <strong>VeritasClin Field</strong> &nbsp;·&nbsp;
  Generated {generated} &nbsp;·&nbsp;
  Pack ID: {_e(pack.pack_id)}<br>
  This report is for biomedical evidence review and education only.
  It does not provide diagnosis, prescription, emergency triage,
  or individualised medical advice.
  All clinical decisions must be made by qualified healthcare professionals
  using local protocols and current evidence.
</div>

</body>
</html>"""
