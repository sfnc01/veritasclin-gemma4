from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from veritasclin.config import get_settings
from veritasclin.schemas.paper import PubMedPaper
from veritasclin.schemas.pico import PICOQuestion
from veritasclin.tools.cache import cache_get, cache_set
from veritasclin.tools.rate_limit import RateLimiter

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def mock_pubmed_papers(topic: str = "dengue") -> list[PubMedPaper]:
    label = "[MOCK DEMO DATA - NOT A REAL PMID]"
    if "cannabis" in topic.lower():
        return [
            PubMedPaper(
                pmid="MOCK-CANNABIS-001",
                title=f"{label} Cannabinoids for chronic neuropathic pain systematic review",
                abstract=(
                    "Mock evidence summary: modest pain reduction was reported in some trials, "
                    "with dizziness and sedation as common adverse events."
                ),
                journal="VeritasClin Mock Evidence",
                publication_year=2021,
                authors=["Mock Evidence Team"],
                doi=None,
                publication_types=["Systematic Review"],
                mesh_terms=["Neuralgia", "Cannabinoids"],
                url="mock://cannabis-neuropathic-pain-001",
            )
        ]
    if "semaglutide" in topic.lower() or "ckd" in topic.lower():
        return [
            PubMedPaper(
                pmid="MOCK-SEMAGLUTIDE-001",
                title=f"{label} Semaglutide kidney outcomes in chronic kidney disease",
                abstract=(
                    "Mock evidence summary: trials describe studied dosing regimens and kidney "
                    "outcomes, but this does not provide individualized dosing advice."
                ),
                journal="VeritasClin Mock Evidence",
                publication_year=2024,
                authors=["Mock Evidence Team"],
                doi=None,
                publication_types=["Randomized Controlled Trial"],
                mesh_terms=["Semaglutide", "Renal Insufficiency, Chronic"],
                url="mock://semaglutide-ckd-001",
            )
        ]
    return [
        PubMedPaper(
            pmid="MOCK-DENGUE-001",
            title=f"{label} Warning signs associated with progression to severe dengue in adults",
            abstract=(
                "Mock evidence summary: abdominal pain, persistent vomiting, mucosal bleeding, "
                "lethargy, hepatomegaly, rising hematocrit with falling platelets, and plasma "
                "leakage are warning signs associated with severe dengue risk."
            ),
            journal="VeritasClin Mock Evidence",
            publication_year=2023,
            authors=["Mock Evidence Team"],
            doi=None,
            publication_types=["Systematic Review"],
            mesh_terms=["Dengue", "Warning Signs", "Adult"],
            url="mock://dengue-warning-signs-001",
        ),
        PubMedPaper(
            pmid="MOCK-DENGUE-002",
            title=f"{label} Clinical warning signs for severe dengue: adult cohort study",
            abstract=(
                "Mock evidence summary: severe abdominal pain, mucosal bleeding, lethargy, "
                "clinical fluid accumulation, and laboratory changes were associated with "
                "higher risk of severe dengue outcomes."
            ),
            journal="VeritasClin Mock Evidence",
            publication_year=2020,
            authors=["Mock Evidence Team"],
            doi=None,
            publication_types=["Clinical Study"],
            mesh_terms=["Dengue", "Adult", "Prognosis"],
            url="mock://dengue-warning-signs-002",
        ),
        PubMedPaper(
            pmid="MOCK-DENGUE-003",
            title=f"{label} Dengue warning signs guideline summary",
            abstract=(
                "Mock evidence summary: guidelines recommend urgent evaluation for warning "
                "signs while emphasizing that triage decisions require local clinical care."
            ),
            journal="VeritasClin Mock Evidence",
            publication_year=2019,
            authors=["Mock Evidence Team"],
            doi=None,
            publication_types=["Practice Guideline"],
            mesh_terms=["Dengue", "Practice Guideline"],
            url="mock://dengue-guideline-003",
        ),
    ]


def _term(value: str | None) -> list[str]:
    if not value:
        return []
    pieces = re.split(r"[,;/]|\band\b|\bor\b", value, flags=re.IGNORECASE)
    return [piece.strip() for piece in pieces if len(piece.strip()) > 2]


def build_pubmed_query(pico: PICOQuestion, max_terms: int = 12) -> str:
    terms: list[str] = []
    for value in [
        pico.population,
        pico.intervention,
        pico.comparison,
        pico.outcome,
        pico.timeframe,
        pico.original_question,
    ]:
        for piece in _term(value):
            normalized = re.sub(r"\s+", " ", piece).strip(" ?.")
            if normalized and normalized.lower() not in {item.lower() for item in terms}:
                terms.append(normalized)
    terms = terms[:max_terms]
    if not terms:
        terms = [pico.original_question.strip(" ?.")]
    query_terms = [f'("{term}"[Title/Abstract] OR "{term}"[MeSH Terms])' for term in terms]
    clinical_guard = "(humans[MeSH Terms] OR clinical[Title/Abstract] OR adult[Title/Abstract])"
    return " AND ".join(query_terms + [clinical_guard])


def _ncbi_params(extra: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    params = {"tool": settings.ncbi_tool, **extra}
    if settings.ncbi_email:
        params["email"] = settings.ncbi_email
    if settings.ncbi_api_key:
        params["api_key"] = settings.ncbi_api_key
    return params


def search_pubmed(query: str, max_results: int = 10, sort: str = "relevance") -> list[str]:
    if not query.strip() or max_results <= 0:
        return []
    settings = get_settings()
    cache_key = f"esearch:{query}:{max_results}:{sort}"
    cached = cache_get(cache_key)
    if isinstance(cached, list):
        return [str(item) for item in cached]

    limiter = RateLimiter(settings.ncbi_max_rps)
    params = _ncbi_params(
        {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": sort,
        }
    )
    try:
        limiter.wait()
        with httpx.Client(timeout=20) as client:
            response = client.get(f"{EUTILS_BASE}/esearch.fcgi", params=params)
            response.raise_for_status()
            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            if isinstance(pmids, list):
                cache_set(cache_key, pmids)
                return [str(pmid) for pmid in pmids]
    except (httpx.HTTPError, ValueError, KeyError):
        return []
    return []


def _text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    value = "".join(node.itertext()).strip()
    return html.unescape(value) if value else None


def _extract_year(article: ET.Element) -> int | None:
    for path in [
        ".//JournalIssue/PubDate/Year",
        ".//ArticleDate/Year",
        ".//PubMedPubDate/Year",
    ]:
        value = _text(article.find(path))
        if value and value.isdigit():
            return int(value)
    medline_date = _text(article.find(".//JournalIssue/PubDate/MedlineDate"))
    if medline_date:
        match = re.search(r"(19|20)\d{2}", medline_date)
        if match:
            return int(match.group(0))
    return None


def _parse_pubmed_xml(xml_text: str) -> list[PubMedPaper]:
    root = ET.fromstring(xml_text)
    papers: list[PubMedPaper] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article.find(".//PMID"))
        if not pmid:
            continue
        article_node = article.find(".//Article")
        title = _text(article.find(".//ArticleTitle")) or "Untitled PubMed article"
        abstract_parts = [
            part
            for part in (_text(node) for node in article.findall(".//Abstract/AbstractText"))
            if part
        ]
        authors = []
        for author in article.findall(".//Author"):
            last = _text(author.find("LastName"))
            fore = _text(author.find("ForeName"))
            collective = _text(author.find("CollectiveName"))
            name = collective or " ".join(item for item in [fore, last] if item)
            if name:
                authors.append(name)
        doi = None
        pmcid = None
        for article_id in article.findall(".//ArticleId"):
            id_type = article_id.attrib.get("IdType")
            value = _text(article_id)
            if id_type == "doi":
                doi = value
            elif id_type == "pmc":
                pmcid = value
        publication_types = [
            value
            for value in (_text(node) for node in article.findall(".//PublicationType"))
            if value
        ]
        mesh_terms = [
            value
            for value in (
                _text(node.find("DescriptorName")) for node in article.findall(".//MeshHeading")
            )
            if value
        ]
        papers.append(
            PubMedPaper(
                pmid=pmid,
                pmcid=pmcid,
                title=title,
                abstract=" ".join(abstract_parts) if abstract_parts else None,
                journal=_text(article_node.find(".//Journal/Title"))
                if article_node is not None
                else None,
                publication_year=_extract_year(article),
                authors=authors,
                doi=doi,
                publication_types=publication_types,
                mesh_terms=mesh_terms,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            )
        )
    return papers


def fetch_pubmed_papers(pmids: list[str]) -> list[PubMedPaper]:
    if not pmids:
        return []
    settings = get_settings()
    unique_pmids = [pmid for index, pmid in enumerate(pmids) if pmid not in pmids[:index]]
    cache_key = "efetch:" + ",".join(unique_pmids)
    cached = cache_get(cache_key)
    if isinstance(cached, list):
        try:
            return [PubMedPaper.model_validate(item) for item in cached]
        except ValueError:
            pass

    params = _ncbi_params({"db": "pubmed", "id": ",".join(unique_pmids), "retmode": "xml"})
    try:
        RateLimiter(settings.ncbi_max_rps).wait()
        with httpx.Client(timeout=25) as client:
            response = client.get(f"{EUTILS_BASE}/efetch.fcgi", params=params)
            response.raise_for_status()
            papers = _parse_pubmed_xml(response.text)
            cache_set(cache_key, [paper.model_dump(mode="json") for paper in papers])
            return papers
    except (httpx.HTTPError, ET.ParseError, ValueError):
        return []
