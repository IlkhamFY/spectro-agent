"""
End-to-end harvest orchestration.

    discover (CrossRef)  ->  resolve PDF/SI urls (source adapter)
        ->  fetch PDF (Scrapling, Cloudflare-proof)  ->  extract text (pypdf)
        ->  per-compound NMR/IR records (extract.py)
        ->  Spectro-format + structure resolution (normalize.py)
        ->  dedup (InChIKey / shift-hash)  ->  JSONL + YAML

The unit of value is a *paired* record (NMR **and** IR), which is exactly what
the Spectro model trains on -- but we keep NMR-only records too, since the
model uses 1H/13C even when IR is absent.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from .discover import Paper, lookup_doi, search_crossref
from .extract import CompoundRecord, extract_records
from .fetch import ResilientFetcher
from .normalize import capabilities, enrich
from .pdf import fetch_pdf_text
from .sources import select_adapter


# Inline JATS formatting tags carry *no* token separation -- "1<sup>H</sup>"
# must become "1H", not "1 H" (which would break the NMR nucleus match) and
# "CDCl<sub>3</sub>" -> "CDCl3". Everything else (block structure) becomes a space.
_INLINE_TAGS = re.compile(
    r"</?(?:sup|sub|italic|bold|i|b|sc|monospace|underline|"
    r"named-content|styled-content|inline-formula|tex-math)[^>]*>", re.IGNORECASE)


def _xml_to_text(xml: str) -> str:
    xml = _INLINE_TAGS.sub("", xml)          # inline formatting -> nothing
    xml = re.sub(r"<[^>]+>", " ", xml)       # block tags -> space
    return html.unescape(xml)                # &#x3B4; -> δ, &amp; -> & ...


def _blob_text(fetcher: ResilientFetcher, kind: str, url: str) -> tuple[str, int]:
    """Fetch a source blob and return (plain text, n_bytes). Handles both PDF
    candidates and PMC full-text JATS XML (``kind == 'xml'``)."""
    if kind == "xml":
        res = fetcher.get(url)
        if not res.ok:
            return "", len(res.content)
        return _xml_to_text(res.text), len(res.content)
    return fetch_pdf_text(fetcher, url)


@dataclass
class HarvestStats:
    papers_seen: int = 0
    pdfs_fetched: int = 0
    pdf_bytes: int = 0
    records_raw: int = 0
    records_kept: int = 0
    with_ir: int = 0
    with_paired: int = 0
    with_structure: int = 0
    nist_ir_joined: int = 0
    quarantined: int = 0
    per_source: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return self.__dict__


def _shift_hash(rec: CompoundRecord) -> str:
    """Fingerprint a record by its shift values (for dedup when no InChIKey)."""
    h = [p.shift for p in rec.h_peaks]
    c = [p.shift for p in rec.c_peaks]
    key = "|".join(h) + "##" + "|".join(c)
    return hashlib.sha256(key.encode()).hexdigest()[:20]


class Harvester:
    def __init__(self, fetcher: ResilientFetcher | None = None,
                 resolve_structures: bool = True, quality_gate: bool = False):
        self.fetcher = fetcher or ResilientFetcher()
        self.resolve_structures = resolve_structures
        self.quality_gate = quality_gate
        self.stats = HarvestStats()
        self._seen: set[str] = set()
        self.records: list[CompoundRecord] = []
        self.quarantine: list[CompoundRecord] = []

    def seed_seen(self, keys) -> None:
        """Pre-load dedup keys (InChIKeys / shift-hashes) to resume a crawl."""
        self._seen.update(keys)

    def _collect(self, paper: Paper) -> tuple[str, list[CompoundRecord], int, int]:
        """Fetch + extract + enrich for one paper. Thread-safe: touches only the
        (thread-safe) fetcher and returns fresh records -- no shared-state writes,
        so it can run in a worker pool. Returns (src, records, n_bytes, n_blobs)."""
        adapter = select_adapter(paper)
        out: list[CompoundRecord] = []
        nbytes = nblobs = 0
        for kind, url in adapter.pdf_candidates(paper, self.fetcher):
            text, nb = _blob_text(self.fetcher, kind, url)
            nbytes += nb
            if not text:
                continue
            nblobs += 1
            for rec in extract_records(text):
                rec.source_doi = paper.doi
                rec.source_url = url
                if self.resolve_structures:
                    enrich(rec)
                else:
                    from .normalize import to_spectro_c, to_spectro_h
                    rec.spectro_h = to_spectro_h(rec)
                    rec.spectro_c = to_spectro_c(rec)
                out.append(rec)
        return adapter.name, out, nbytes, nblobs

    def _merge(self, src: str, recs: list[CompoundRecord],
               nbytes: int, nblobs: int) -> int:
        """Dedup + quality-gate + accumulate. Main-thread only (mutates state)."""
        self.stats.papers_seen += 1
        self.stats.per_source.setdefault(src, 0)
        self.stats.pdfs_fetched += nblobs
        self.stats.pdf_bytes += nbytes
        self.stats.records_raw += len(recs)
        added = 0
        for rec in recs:
            key = rec.inchikey or _shift_hash(rec)
            if key in self._seen:
                continue
            self._seen.add(key)
            if self.quality_gate:
                from .quality import gate
                ok, reasons = gate(rec.to_dict())
                if not ok:
                    rec.quarantine_reasons = reasons
                    self.quarantine.append(rec)
                    self.stats.quarantined += 1
                    continue
            self.records.append(rec)
            self.stats.per_source[src] += 1
            added += 1
            self.stats.records_kept += 1
            if rec.has_ir:
                self.stats.with_ir += 1
            if rec.has_paired:
                self.stats.with_paired += 1
            if rec.smiles:
                self.stats.with_structure += 1
        return added

    def harvest_paper(self, paper: Paper) -> int:
        return self._merge(*self._collect(paper))

    def harvest_papers_concurrent(self, papers: list[Paper], max_workers: int = 8,
                                  target: int | None = None,
                                  checkpoint=None, checkpoint_every: int = 50) -> None:
        """Multi-host concurrent harvest. Workers fetch+extract in parallel (the
        per-host lock in ResilientFetcher keeps each host polite while different
        hosts run together); results are merged on the main thread. The more
        distinct hosts in ``papers``, the more real parallelism."""
        last_ckpt = 0
        seen_dois: set[str] = set()
        todo = [p for p in papers if not (p.doi in seen_dois or seen_dois.add(p.doi))]
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(self._collect, p): p for p in todo}
            for fut in as_completed(futures):
                paper = futures[fut]
                try:
                    src, recs, nbytes, nblobs = fut.result()
                except Exception as e:                       # noqa: BLE001
                    print(f"  ! {paper.doi}: {e}")
                    continue
                n = self._merge(src, recs, nbytes, nblobs)
                if n:
                    print(f"  + {paper.doi}  [{src}]  +{n}  "
                          f"(kept {len(self.records)}, quarantined "
                          f"{self.stats.quarantined})", flush=True)
                if checkpoint and len(self.records) - last_ckpt >= checkpoint_every:
                    checkpoint(self)
                    last_ckpt = len(self.records)
                if target and len(self.records) >= target:
                    break
        if checkpoint:
            checkpoint(self)

    def join_nist_ir(self, limit: int | None = None) -> int:
        """
        Capstone join, mirroring Spectro's own dataset construction: for every
        structure-resolved record, fetch the IR spectrum from NIST (as a JDX
        file) keyed by InChIKey and attach the full curve. Returns the number of
        records successfully joined to a NIST IR spectrum.
        """
        from .sources.nist import NISTIRClient
        client = NISTIRClient(self.fetcher)
        joined = 0
        targets = [r for r in self.records if r.inchikey]
        if limit:
            targets = targets[:limit]
        for rec in targets:
            try:
                info = client.fetch_ir(inchikey=rec.inchikey, name=rec.name,
                                       save_as=rec.inchikey)
            except Exception:
                info = None
            if not info:
                continue
            rec.nist_id = info["nist_id"]
            rec.nist_ir_jdx = info["jdx_path"]
            rec.nist_ir_npoints = info["npoints"]
            rec.nist_ir_xrange = info["x_range"]
            joined += 1
        self.stats.nist_ir_joined = joined
        print(f"  NIST IR join: {joined}/{len(targets)} structure-resolved "
              f"records matched a NIST IR spectrum")
        return joined

    def harvest_dois(self, dois: list[str]) -> None:
        for doi in dois:
            try:
                paper = lookup_doi(doi)
            except Exception as e:                  # noqa: BLE001
                print(f"  ! discover failed for {doi}: {e}")
                continue
            n = self.harvest_paper(paper)
            print(f"  + {doi}  [{select_adapter(paper).name}]  -> {n} new records "
                  f"(total {len(self.records)})")

    def harvest_search(self, query: str, issn: str = "", rows: int = 20,
                       oa_only: bool = True, target: int | None = None) -> None:
        filters = {}
        if oa_only:
            filters["has-license"] = "true"
        papers = search_crossref(query=query, issn=issn, rows=rows, filters=filters)
        for paper in papers:
            self.harvest_paper(paper)
            if target and len(self.records) >= target:
                break

    def harvest_search_multi(self, queries: list[str], issns: list[str],
                             rows: int = 40, oa_only: bool = True,
                             target: int | None = None,
                             checkpoint=None, checkpoint_every: int = 50) -> None:
        """
        Scale-out discovery: sweep many (query x journal) combinations, dedup
        across them, and checkpoint to disk every ``checkpoint_every`` records so
        a long crawl is crash-safe and resumable. ``checkpoint`` is a callable
        invoked with the harvester to persist progress.
        """
        filters = {"has-license": "true"} if oa_only else {}
        seen_dois: set[str] = set()
        last_ckpt = 0
        for issn in (issns or [""]):
            for q in queries:
                try:
                    papers = search_crossref(query=q, issn=issn, rows=rows,
                                             filters=filters)
                except Exception as e:                       # noqa: BLE001
                    print(f"  ! search failed q={q!r} issn={issn}: {e}")
                    continue
                for paper in papers:
                    if paper.doi in seen_dois:
                        continue
                    seen_dois.add(paper.doi)
                    n = self.harvest_paper(paper)
                    if n:
                        print(f"  + {paper.doi}  q={q[:18]!r}  +{n}  "
                              f"(kept {len(self.records)}, quarantined "
                              f"{self.stats.quarantined})")
                    if checkpoint and len(self.records) - last_ckpt >= checkpoint_every:
                        checkpoint(self)
                        last_ckpt = len(self.records)
                    if target and len(self.records) >= target:
                        if checkpoint:
                            checkpoint(self)
                        return
        if checkpoint:
            checkpoint(self)

    # -- output ------------------------------------------------------------
    def write(self, out_dir="data/output", basename="spectra") -> dict:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        jsonl = out / f"{basename}.jsonl"
        with jsonl.open("w") as f:
            for rec in self.records:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")

        # Spectro-style YAML-ish view (the format their pipeline consumes).
        spectro = out / f"{basename}_spectro.jsonl"
        with spectro.open("w") as f:
            for rec in self.records:
                f.write(json.dumps({
                    "id": rec.inchikey or _shift_hash(rec),
                    "label": rec.label,
                    "smiles": rec.smiles,
                    "selfies": rec.selfies,
                    "h_nmr": rec.spectro_h,
                    "c_nmr": rec.spectro_c,
                    "ir_bands_cm-1": rec.ir_bands or None,
                    "nist_ir_jdx": rec.nist_ir_jdx,
                    "nist_ir_npoints": rec.nist_ir_npoints,
                    "source_doi": rec.source_doi,
                }, ensure_ascii=False) + "\n")

        # Quarantined (quality-gate failures), for inspection.
        if self.quarantine:
            with (out / f"{basename}_quarantine.jsonl").open("w") as f:
                for rec in self.quarantine:
                    f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")

        # Data-quality audit (physics + structure cross-checks).
        from .quality import audit
        quality = audit([r.to_dict() for r in self.records])
        (out / f"{basename}_quality.json").write_text(json.dumps(quality, indent=2))

        report = {
            "stats": self.stats.as_dict(),
            "capabilities": capabilities(),
            "fetcher": self.fetcher.stats,
            "quality": quality,
            "outputs": {"records": str(jsonl), "spectro": str(spectro),
                        "quality": str(out / f"{basename}_quality.json")},
        }
        (out / f"{basename}_report.json").write_text(json.dumps(report, indent=2))
        return report
