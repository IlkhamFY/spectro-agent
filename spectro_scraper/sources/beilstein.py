"""Beilstein Journals adapter (Org. Chem. + Nanotechnology).

The Beilstein journals are gold open-access (CC-BY), with no paywall and no
anti-bot, and ship a Supporting Information PDF crammed with per-compound
1H/13C NMR (and frequently IR/HRMS). One SI PDF routinely yields 30-100
compounds -- the single highest-yield-per-request source we have.

Both journals share one platform and predictable asset URLs:

    bjoc   (Org. Chem.)        DOI 10.3762/bjoc.<vol>.<art>     ISSN 1860-5397
    bjnano (Nanotechnology)    DOI 10.3762/bjnano.<vol>.<art>   ISSN 2190-4286

    main PDF : /<slug>/content/pdf/<issn>-<vol>-<art>.pdf
    article  : /<slug>/articles/<vol>/<art>   (lists /supplementary/*.pdf)
"""

from __future__ import annotations

import re

from ..discover import Paper
from ..fetch import ResilientFetcher
from .base import SourceAdapter

HOST = "https://www.beilstein-journals.org"
# slug -> issn
_JOURNALS = {"bjoc": "1860-5397", "bjnano": "2190-4286"}
_DOI_RE = re.compile(r"10\.3762/(bjoc|bjnano)\.(\d+)\.(\d+)", re.IGNORECASE)
_SI_RE = re.compile(r"(/(?:bjoc|bjnano)/content/supplementary/[^\"'\s>]+\.pdf)",
                    re.IGNORECASE)


class BeilsteinAdapter(SourceAdapter):
    name = "beilstein"

    def matches(self, paper: Paper) -> bool:
        return bool(_DOI_RE.search(paper.doi or "")) \
            or "beilstein" in (paper.publisher or "").lower()

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        m = _DOI_RE.search(paper.doi or "")
        slug = vol = art = None
        if m:
            slug, vol, art = m.group(1).lower(), m.group(2), m.group(3)
            issn = _JOURNALS[slug]
            out.append(("main", f"{HOST}/{slug}/content/pdf/{issn}-{vol}-{art}.pdf"))
        for u in paper.pdf_links:
            if ("main", u) not in out:
                out.append(("main", u))

        # Discover SI by scraping the article landing page.
        if slug and vol and art:
            res = fetcher.get(f"{HOST}/{slug}/articles/{vol}/{art}")
            if res.ok:
                for href in dict.fromkeys(_SI_RE.findall(res.text)):
                    out.append(("si", self._abs(HOST, href)))
        return out
