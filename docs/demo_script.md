# Demo Script

## 0:00 - Problem

Medical AI should not just answer. It should carry its evidence with it, especially where connectivity is poor and accountability is high.

## 0:25 - Build Dengue Pack

Open the branded VeritasClin Field console and build an Evidence Pack for:
`What does recent evidence say about warning signs for severe dengue in adults?`
Show whether retrieval is using real PubMed credentials or mock fallback.

## 0:55 - Evidence Pack

Show PICO, PubMed query, Evidence Map, Claim Ledger, Caution Map, freshness score,
and citation coverage. Emphasize that the Claim Ledger is the centerpiece.

## 1:30 - Offline Query

Load `pack.json` offline and ask: `Quais sinais indicam maior risco de dengue grave?`

## 2:00 - Baseline Comparison

Show how a plain model answer lacks a portable Claim Ledger, while VeritasClin reports
citation coverage, unsupported claim counts, and the unsupported-claim delta.

## 2:35 - Safety Rewrite

Ask: `What dose of semaglutide should I take if I have CKD?` Show the safety rewrite into a research question.

## 3:00 - Close

VeritasClin Field turns PubMed into offline, multilingual, audit-ready Evidence Packs.
