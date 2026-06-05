"""Source adapter interface + selector.

An adapter turns a :class:`~spectro_scraper.discover.Paper` into a list of
``(kind, url)`` PDF candidates -- typically the main article plus any
Supporting Information, which is where the bulk of the per-compound NMR/IR data
lives in synthetic-chemistry papers.
"""

from __future__ import annotations

import re

from ..discover import Paper
from ..fetch import ResilientFetcher


class SourceAdapter:
    name = "base"

    def matches(self, paper: Paper) -> bool:
        raise NotImplementedError

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        """Return list of (kind, url). kind in {'main', 'si'}."""
        out = [("main", u) for u in paper.pdf_links]
        return out

    # -- helpers shared by subclasses -------------------------------------
    @staticmethod
    def _abs(host: str, href: str) -> str:
        if href.startswith("http"):
            return href
        if href.startswith("//"):
            return "https:" + href
        return host.rstrip("/") + "/" + href.lstrip("/")


def select_adapter(paper: Paper) -> "SourceAdapter":
    from .beilstein import BeilsteinAdapter
    from .chemrxiv import ChemRxivAdapter
    from .europepmc import EuropePMCAdapter
    from .generic import GenericAdapter

    for adapter in (EuropePMCAdapter(), BeilsteinAdapter(), ChemRxivAdapter()):
        if adapter.matches(paper):
            return adapter
    return GenericAdapter()
