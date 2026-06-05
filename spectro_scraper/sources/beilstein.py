"""Beilstein Journal of Organic Chemistry adapter.

Beilstein JOC is gold open-access (CC-BY), with no paywall and no anti-bot, and
every methodology paper ships a Supporting Information PDF crammed with
per-compound 1H/13C NMR (and frequently IR/HRMS). One SI PDF routinely yields
30-100 compounds -- the single highest-yield-per-request source we have.

DOIs look like ``10.3762/bjoc.13.258`` (volume 13, article 258); assets live at
predictable URLs, and the article page lists the ``/supplementary/`` files.
"""

from __future__ import annotations

import re

from ..discover import Paper
from ..fetch import ResilientFetcher
from .base import SourceAdapter

HOST = "https://www.beilstein-journals.org"
_DOI_RE = re.compile(r"10\.3762/bjoc\.(\d+)\.(\d+)", re.IGNORECASE)
_SI_RE = re.compile(r"(/bjoc/content/supplementary/[^\"'\s>]+\.pdf)", re.IGNORECASE)


class BeilsteinAdapter(SourceAdapter):
    name = "beilstein"

    def matches(self, paper: Paper) -> bool:
        return bool(_DOI_RE.search(paper.doi or "")) or "beilstein" in (paper.publisher or "").lower()

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        m = _DOI_RE.search(paper.doi or "")
        vol = art = None
        if m:
            vol, art = m.group(1), m.group(2)
            out.append(("main", f"{HOST}/bjoc/content/pdf/1860-5397-{vol}-{art}.pdf"))
        for u in paper.pdf_links:
            if ("main", u) not in out:
                out.append(("main", u))

        # Discover SI by scraping the article landing page.
        if vol and art:
            art_url = f"{HOST}/bjoc/articles/{vol}/{art}"
            res = fetcher.get(art_url)
            if res.ok:
                for href in dict.fromkeys(_SI_RE.findall(res.text)):
                    out.append(("si", self._abs(HOST, href)))
        return out
