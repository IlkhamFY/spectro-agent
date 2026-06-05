"""
spectro_scraper -- an efficient agent that harvests NMR + IR spectra from
public chemistry papers, in the exact format the Spectro molecule-elucidation
model (chemrxiv-2024-37v2j) consumes.

Built on Scrapling for Cloudflare-proof, browser-free fetching.
"""

from .discover import Paper, lookup_doi, search_crossref
from .extract import CompoundRecord, extract_records
from .fetch import ResilientFetcher
from .pipeline import Harvester
from .normalize import enrich, capabilities

__version__ = "0.1.0"
__all__ = [
    "Paper",
    "lookup_doi",
    "search_crossref",
    "CompoundRecord",
    "extract_records",
    "ResilientFetcher",
    "Harvester",
    "enrich",
    "capabilities",
]
