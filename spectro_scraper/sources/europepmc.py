"""Europe PMC adapter -- full-text JATS XML.

Europe PMC (ebi.ac.uk) is a large, fully-open corpus with no anti-bot. Many
chemistry articles (notably MDPI / RSC) carry their experimental section *in
the article body*, so a single full-text-XML fetch yields a paper's worth of
per-compound NMR/IR with no Supporting-Information hunt. Being a different host
from the publishers, it also gives the concurrent crawler real parallelism.

The candidate kind is ``"xml"`` -- the pipeline strips tags and runs the same
extraction engine on the body text.
"""

from __future__ import annotations

from ..discover import Paper
from ..fetch import ResilientFetcher
from .base import SourceAdapter


class EuropePMCAdapter(SourceAdapter):
    name = "europepmc"

    def matches(self, paper: Paper) -> bool:
        return bool(paper.fulltext_xml)

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        # kind "xml" signals the pipeline to fetch + de-tag rather than parse PDF
        return [("xml", paper.fulltext_xml)]
