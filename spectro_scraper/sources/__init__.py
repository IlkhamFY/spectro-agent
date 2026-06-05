"""Per-source adapters that know how to locate a paper's PDF + SI assets."""

from .base import SourceAdapter, select_adapter
from .beilstein import BeilsteinAdapter
from .chemrxiv import ChemRxivAdapter
from .generic import GenericAdapter

__all__ = [
    "SourceAdapter",
    "select_adapter",
    "BeilsteinAdapter",
    "ChemRxivAdapter",
    "GenericAdapter",
]
