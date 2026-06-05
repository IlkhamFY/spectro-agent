"""
Paper discovery via fully-open scholarly APIs.

Genius move #2: decouple *discovery* from *fetching*. Scholarly metadata APIs
(CrossRef, OpenAlex) are NOT behind Cloudflare and expose canonical PDF URLs.
So we enumerate open-access organic-chemistry papers through them -- cheaply,
politely, with no anti-bot fight -- and reserve Scrapling's TLS-impersonation
muscle for the actual (often protected) PDF download.

CrossRef is the workhorse here: it indexes ChemRxiv, Beilstein, RSC, etc., lets
us filter by ISSN / type / open-access licence, and hands back ``link`` arrays
that point straight at the PDF.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

CROSSREF = "https://api.crossref.org"
MAILTO = "ilkhamfy@gmail.com"   # polite pool -> faster, more reliable CrossRef
UA = f"spectro-agent/0.1 (https://chemrxiv.org; mailto:{MAILTO})"


@dataclass
class Paper:
    doi: str
    title: str
    publisher: str = ""
    issn: str = ""
    url: str = ""
    pdf_links: list[str] = field(default_factory=list)
    is_oa: bool = False
    license: str = ""
    fulltext_xml: str = ""    # Europe PMC JATS full-text URL, when available

    def best_pdf(self) -> Optional[str]:
        return self.pdf_links[0] if self.pdf_links else None


def _get_json(url: str, retries: int = 4) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:               # noqa: BLE001
            last = e
            time.sleep(min(2 ** attempt, 16))
    raise RuntimeError(f"GET failed {url}: {last}")


def _paper_from_item(it: dict) -> Paper:
    pdfs: list[str] = []
    for l in it.get("link", []):
        u = l.get("URL", "")
        if l.get("content-type") == "application/pdf" or u.lower().endswith(".pdf"):
            if u not in pdfs:
                pdfs.append(u)
    lic = ""
    for L in it.get("license", []):
        if L.get("URL"):
            lic = L["URL"]
            break
    return Paper(
        doi=it.get("DOI", ""),
        title=(it.get("title") or ["(untitled)"])[0],
        publisher=it.get("publisher", ""),
        issn=(it.get("ISSN") or [""])[0],
        url=it.get("URL", ""),
        pdf_links=pdfs,
        is_oa=bool(lic),
        license=lic,
    )


def search_crossref(query: str = "", issn: str = "", rows: int = 20,
                    filters: Optional[dict] = None) -> list[Paper]:
    """Search CrossRef works. ``issn`` scopes to a single journal."""
    params = {
        "rows": str(rows),
        "select": "DOI,title,link,publisher,ISSN,URL,license",
        "mailto": MAILTO,
    }
    if query:
        params["query"] = query
    f = {"type": "journal-article"}
    if filters:
        f.update(filters)
    params["filter"] = ",".join(f"{k}:{v}" for k, v in f.items())
    base = f"{CROSSREF}/journals/{issn}/works" if issn else f"{CROSSREF}/works"
    url = base + "?" + urllib.parse.urlencode(params)
    data = _get_json(url)
    return [_paper_from_item(it) for it in data.get("message", {}).get("items", [])]


def lookup_doi(doi: str) -> Paper:
    """Resolve a single DOI to a Paper (works for ChemRxiv preprints too)."""
    url = f"{CROSSREF}/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    data = _get_json(url)
    return _paper_from_item(data["message"])


# ---------------------------------------------------------------------------
# Europe PMC -- a second, large, fully-open (no-Cloudflare) corpus that serves
# JATS full-text XML directly. Crucially, MDPI/RSC/etc. articles here carry the
# experimental section *in the body*, so one XML fetch == one paper's worth of
# NMR/IR with no SI hunt. A different host than the publishers -> real
# concurrency headroom.
# ---------------------------------------------------------------------------
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
PMC_OAI = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _pmc_paper(num: str) -> Paper:
    """A Paper whose full text is the NCBI PMC OAI JATS XML for PMC<num>."""
    return Paper(
        doi=f"PMC:{num}", title="", is_oa=True,
        url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{num}/",
        fulltext_xml=(f"{PMC_OAI}?verb=GetRecord&metadataPrefix=pmc"
                      f"&identifier=oai:pubmedcentral.nih.gov:{num}"),
    )


def search_ncbi_pmc(term: str, retmax: int = 5000, retstart: int = 0):
    """NCBI esearch over PMC. Returns (papers, total_hits). esearch UIDs are the
    PMC numbers, so one cheap call enumerates thousands of PMCIDs -- the scalable
    discovery path for a 100k-record bulk crawl."""
    url = (f"{NCBI_EUTILS}/esearch.fcgi?db=pmc&retmode=json"
           f"&retmax={retmax}&retstart={retstart}"
           f"&term={urllib.parse.quote(term)}&tool=spectro-agent&email={MAILTO}")
    data = _get_json(url)
    res = data.get("esearchresult", {})
    ids = res.get("idlist", [])
    return [_pmc_paper(i) for i in ids], int(res.get("count", 0))


def search_europepmc(query: str, page_size: int = 25,
                     oa_only: bool = True) -> list[Paper]:
    """Search Europe PMC; return papers that have full-text XML in EPMC."""
    q = query
    if oa_only:
        q = f"({query}) AND (OPEN_ACCESS:y) AND (IN_EPMC:y)"
    url = (f"{EUROPEPMC}/search?query={urllib.parse.quote(q)}"
           f"&format=json&pageSize={page_size}&resultType=lite")
    data = _get_json(url)
    out: list[Paper] = []
    for r in data.get("resultList", {}).get("result", []):
        pmcid = r.get("pmcid")
        if not pmcid or r.get("inEPMC") != "Y":
            continue
        # Europe PMC finds the papers; NCBI's PMC OAI service serves the actual
        # full-text JATS XML reliably (a different host -> concurrency headroom).
        num = pmcid.replace("PMC", "")
        title = re.sub(r"<[^>]+>", "", r.get("title", "(untitled)"))
        out.append(Paper(
            doi=r.get("doi", "") or f"PMC:{pmcid}",
            title=title,
            publisher=r.get("journalTitle", ""),
            url=f"https://europepmc.org/article/PMC/{pmcid}",
            is_oa=True,
            fulltext_xml=(f"{PMC_OAI}?verb=GetRecord&metadataPrefix=pmc"
                          f"&identifier=oai:pubmedcentral.nih.gov:{num}"),
        ))
    return out
