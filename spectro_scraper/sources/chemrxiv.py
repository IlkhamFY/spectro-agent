"""ChemRxiv (Cambridge Open Engage) adapter.

ChemRxiv is the source named in the task. It is fully open-access but sits
behind Cloudflare -- plain ``curl`` gets HTTP 403, while Scrapling's TLS
impersonation gets 200 (verified). The canonical, stable PDF URL is simply::

    https://chemrxiv.org/doi/pdf/<DOI>

which CrossRef also reports as the paper's PDF link. For preprints the full
experimental section is usually inside that main PDF; where a separate SI asset
is referenced on the article page we pick it up too.
"""

from __future__ import annotations

import re

from ..discover import Paper
from ..fetch import ResilientFetcher
from .base import SourceAdapter

HOST = "https://chemrxiv.org"
_DOI_RE = re.compile(r"10\.26434/chemrxiv", re.IGNORECASE)
_ASSET_RE = re.compile(
    r"(https://chemrxiv\.org/engage/api-gateway/chemrxiv/assets/[^\"'\s>]+\.pdf)",
    re.IGNORECASE,
)


class ChemRxivAdapter(SourceAdapter):
    name = "chemrxiv"

    def matches(self, paper: Paper) -> bool:
        return bool(_DOI_RE.search(paper.doi or "")) \
            or "chemrxiv" in (paper.url or "").lower()

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        if paper.doi:
            out.append(("main", f"{HOST}/doi/pdf/{paper.doi}"))
        for u in paper.pdf_links:
            if ("main", u) not in out:
                out.append(("main", u))

        # Try to surface a supplementary asset from the article HTML.
        art = paper.url or f"{HOST}/doi/full/{paper.doi}"
        res = fetcher.get(art)
        if res.ok:
            for href in dict.fromkeys(_ASSET_RE.findall(res.text)):
                kind = "si" if "supplement" in href.lower() else "main"
                if (kind, href) not in out:
                    out.append((kind, href))
        return out
