"""
spectro_scraper -- harvest NMR + IR band lists from open chemistry literature.

IRexp release construction uses PMC-OA S3 + Chemotion only (see
``scripts/s3_ir_harvest.py``, ``scripts/chemotion_to_irexp.py``). Scrapling-based
publisher fetchers are optional development adapters, not the release path.
"""

from .discover import Paper, lookup_doi, search_crossref
from .extract import CompoundRecord, extract_records
from .normalize import enrich, capabilities

# Lazy: ResilientFetcher / Harvester need optional Scrapling; extract/quality do not.
def __getattr__(name: str):
    if name == "ResilientFetcher":
        from .fetch import ResilientFetcher
        return ResilientFetcher
    if name == "Harvester":
        from .pipeline import Harvester
        return Harvester
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
