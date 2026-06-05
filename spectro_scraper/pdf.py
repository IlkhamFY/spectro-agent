"""PDF download + robust text extraction."""

from __future__ import annotations

import io

from pypdf import PdfReader

from .fetch import ResilientFetcher


def extract_pdf_text(content: bytes) -> str:
    """Extract all text from PDF bytes (best effort)."""
    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception:
        return ""
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def fetch_pdf_text(fetcher: ResilientFetcher, url: str) -> tuple[str, int]:
    """Download a PDF via Scrapling and return (text, n_bytes)."""
    res = fetcher.get(url, binary=True)
    if not res.ok or not res.content.startswith(b"%PDF"):
        # Some hosts 302 a .pdf URL to an HTML viewer; bail cleanly.
        if not res.content.startswith(b"%PDF"):
            return "", len(res.content)
    return extract_pdf_text(res.content), len(res.content)
