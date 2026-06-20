"""Fallback adapter: just use whatever PDF links CrossRef gave us."""

from __future__ import annotations

from ..discover import Paper
from ..fetch import ResilientFetcher
from .base import SourceAdapter


class GenericAdapter(SourceAdapter):
    name = "generic"

    def matches(self, paper: Paper) -> bool:
        return True

    def pdf_candidates(self, paper: Paper,
                       fetcher: ResilientFetcher) -> list[tuple[str, str]]:
        return [("main", u) for u in paper.pdf_links]
