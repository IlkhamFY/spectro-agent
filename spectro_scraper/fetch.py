"""
Resilient fetch layer built on Scrapling (https://github.com/D4Vinci/Scrapling).

Why Scrapling instead of Selenium (which the Spectro authors used to scrape
their NMR data)?

    * ``Fetcher.get(impersonate='chrome')`` sends a *real Chrome TLS/JA3
      fingerprint* via curl_cffi. This sails through Cloudflare's bot check on
      chemrxiv.org **without launching a browser** -- microseconds, not seconds,
      fully parallelisable, no webdriver babysitting. (Empirically: plain curl
      gets HTTP 403; Scrapling's impersonation gets 200.)
    * Only when a site throws a genuine interactive JS challenge do we escalate
      to ``StealthyFetcher`` (a stealth Firefox/camoufox that can solve
      Cloudflare Turnstile). Pay the heavy cost *only when forced to*.
    * Parsed responses expose lightning-fast CSS/XPath selectors (~12x faster
      than BeautifulSoup) and adaptive element relocation, so source adapters
      survive site redesigns.

This module wraps those engines with exponential-backoff retries, a tiny
on-disk cache (so re-runs never re-hit servers), and polite per-host rate
limiting.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse

from scrapling.fetchers import Fetcher

try:
    from scrapling.fetchers import StealthyFetcher
    _HAVE_STEALTH = True
except Exception:  # pragma: no cover
    _HAVE_STEALTH = False


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

# Block-page fingerprints that mean "TLS impersonation wasn't enough".
_CHALLENGE_MARKERS = (
    b"Just a moment",
    b"challenge-platform",
    b"cf-chl",
    b"Enable JavaScript and cookies to continue",
)


class FetchResult:
    __slots__ = ("url", "status", "content", "from_cache", "engine")

    def __init__(self, url, status, content, from_cache=False, engine="fetcher"):
        self.url = url
        self.status = status
        self.content = content            # always bytes
        self.from_cache = from_cache
        self.engine = engine

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", "replace")

    @property
    def ok(self) -> bool:
        return 200 <= (self.status or 0) < 300 and bool(self.content)


def _looks_like_challenge(content: bytes) -> bool:
    head = content[:4000]
    return any(m in head for m in _CHALLENGE_MARKERS)


class ResilientFetcher:
    """Scrapling-backed fetcher with cache, retries and per-host throttling."""

    def __init__(self, cache_dir="data/cache", min_interval=1.0,
                 max_retries=4, impersonate="chrome", allow_stealth=True):
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.impersonate = impersonate
        self.allow_stealth = allow_stealth and _HAVE_STEALTH
        self._last_hit: dict[str, float] = {}
        self.stats = {"requests": 0, "cache_hits": 0, "stealth": 0, "failures": 0}

    # -- cache -------------------------------------------------------------
    def _cache_path(self, url: str) -> Path:
        h = hashlib.sha256(url.encode()).hexdigest()[:24]
        return self.cache / f"{h}.bin"

    def _throttle(self, url: str) -> None:
        host = urlparse(url).netloc
        last = self._last_hit.get(host, 0.0)
        wait = self.min_interval - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        self._last_hit[host] = time.monotonic()

    # -- core --------------------------------------------------------------
    def get(self, url: str, *, binary=False, use_cache=True,
            headers=None) -> FetchResult:
        cpath = self._cache_path(url)
        if use_cache and cpath.exists():
            self.stats["cache_hits"] += 1
            return FetchResult(url, 200, cpath.read_bytes(),
                               from_cache=True, engine="cache")

        hdrs = dict(DEFAULT_HEADERS)
        if headers:
            hdrs.update(headers)

        content = b""
        status = None
        engine = "fetcher"
        for attempt in range(self.max_retries):
            self._throttle(url)
            self.stats["requests"] += 1
            try:
                page = Fetcher.get(url, impersonate=self.impersonate,
                                   timeout=60, headers=hdrs)
                status = page.status
                body = page.body
                content = body if isinstance(body, (bytes, bytearray)) else \
                    (page.html_content.encode() if hasattr(page, "html_content")
                     else str(body).encode())
                content = bytes(content)
                if status and 200 <= status < 300 and not _looks_like_challenge(content):
                    break
            except Exception:
                status = status or 0
            time.sleep(min(2 ** attempt, 16))

        # Escalate to a stealth browser only if still blocked.
        if (not (status and 200 <= status < 300) or _looks_like_challenge(content)) \
                and self.allow_stealth and not binary:
            try:
                self.stats["stealth"] += 1
                page = StealthyFetcher.fetch(url, headless=True,
                                             solve_cloudflare=True,
                                             network_idle=True)
                status = getattr(page, "status", 200)
                html = page.html_content if hasattr(page, "html_content") else str(page)
                content = html.encode("utf-8", "replace")
                engine = "stealth"
            except Exception:
                pass

        ok = status and 200 <= status < 300 and content
        if ok and use_cache:
            cpath.write_bytes(content)
        if not ok:
            self.stats["failures"] += 1
        return FetchResult(url, status, content, engine=engine)
