#!/usr/bin/env python3
"""
Bulk, streaming, resumable harvest toward 100k NMR+IR records.

Design for scale:
  * discovery via NCBI esearch over the PMC Open-Access subset (~460k chem+NMR
    papers) -- a few cheap calls enumerate tens of thousands of PMCIDs;
  * full text from NCBI PMC OAI (JATS XML, experimental section in the body);
  * Beilstein interleaved as a second host for extra throughput;
  * **structure resolution OFF** (the OPSIN JVM is the wall-clock killer) -- run
    `scripts/make_training_export.py` / a batched OPSIN pass later to add labels;
  * per-host token-bucket concurrency (NCBI at its polite ~3 req/s, with overlap);
  * **streaming append** output + a persisted seen-set, so it never holds 100k
    records in one rewrite and **resumes** on restart (skip processed PMCIDs).

    python scripts/bulk_harvest.py --target 100000 --out data/bulk --workers 10

Resume by re-running with the same --out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.discover import search_ncbi_pmc, search_crossref  # noqa: E402
from spectro_scraper.extract import extract_records                    # noqa: E402
from spectro_scraper.fetch import ResilientFetcher                     # noqa: E402
from spectro_scraper.pipeline import _xml_to_text                      # noqa: E402
from spectro_scraper.sources import select_adapter                     # noqa: E402

# Only journals that print the experimental section in the article *body* (so
# one full-text fetch yields many compounds). yield-per-paper -- not corpus size
# -- sets the wall-clock for 100k, and broad PMC queries mostly return
# NMR-in-SI papers that body-text extraction can't use. We slice each journal by
# publication year to get past esearch's 10k-results-per-query ceiling and reach
# the full corpus (Molecules/IJMS alone are 50k+ papers each).
HIGH_YIELD_JOURNALS = [
    "Molecules", "Int J Mol Sci", "Pharmaceuticals (Basel)", "Mar Drugs",
    "Beilstein J Org Chem", "Molbank", "Org Biomol Chem", "RSC Adv",
    "Antibiotics (Basel)", "Pharmaceutics", "Polymers (Basel)", "Metabolites",
    "Biomolecules", "Nanomaterials (Basel)", "Materials (Basel)", "Gels (Basel)",
    "Membranes (Basel)", "Catalysts", "Plants (Basel)", "Foods",
]
YEARS = list(range(2026, 2010, -1))
BEILSTEIN_TERMS = ["synthesis", "total synthesis", "heterocycle", "catalysis",
                   "natural product", "cycloaddition", "functionalization"]


def _shift_hash(r: dict) -> str:
    h = "|".join(p["shift"] for p in r.get("h_peaks", []))
    c = "|".join(p["shift"] for p in r.get("c_peaks", []))
    return hashlib.sha256((h + "##" + c).encode()).hexdigest()[:20]


def _collect(fetcher: ResilientFetcher, paper):
    """Fetch + extract one paper (no structure resolution, no cache). Returns a
    list of plain-dict records. Thread-safe (only touches the shared fetcher)."""
    out = []
    for kind, url in select_adapter(paper).pdf_candidates(paper, fetcher):
        res_txt = ""
        if kind == "xml":
            r = fetcher.get(url, use_cache=False)
            if r.ok:
                res_txt = _xml_to_text(r.text)
        else:
            from spectro_scraper.pdf import extract_pdf_text
            r = fetcher.get(url, binary=True, use_cache=False)
            if r.ok and r.content[:4] == b"%PDF":
                res_txt = extract_pdf_text(r.content)
        if not res_txt:
            continue
        for rec in extract_records(res_txt):
            d = rec.to_dict()
            d["source_doi"] = paper.doi
            from spectro_scraper.normalize import to_spectro_h, to_spectro_c
            d["spectro_h"], d["spectro_c"] = to_spectro_h(rec), to_spectro_c(rec)
            out.append(d)
    return out


def _load_resume(out: Path):
    seen_keys, seen_papers, kept, with_ir = set(), set(), 0, 0
    jf, pf = out / "spectra.jsonl", out / "seen_papers.txt"
    if jf.exists():
        for line in jf.open():
            try:
                r = json.loads(line)
                seen_keys.add(r.get("inchikey") or _shift_hash(r))
                kept += 1
                with_ir += bool(r.get("ir_bands"))
            except Exception:
                pass
    if pf.exists():
        seen_papers = set(pf.read_text().split())
    return seen_keys, seen_papers, kept, with_ir


def discover(seen_papers: set, want: int) -> list:
    """Enumerate a deep high-yield paper pool: each body-experimental journal
    sliced by publication year (so every slice is under esearch's 10k cap)."""
    papers, dois = [], set()
    need = max(want, 1) * 2          # over-discover to absorb low/zero-yield papers
    for journal in HIGH_YIELD_JOURNALS:
        for year in YEARS:
            term = (f'"{journal}"[Journal] AND {year}[pdat] AND '
                    f'(1H NMR OR 13C NMR) AND open access[filter]')
            try:
                ps, total = search_ncbi_pmc(term, retmax=5000)
            except Exception:
                continue
            for p in ps:
                if p.doi in seen_papers or p.doi in dois:
                    continue
                dois.add(p.doi); papers.append(p)
            time.sleep(0.34)
            if len(papers) >= need:
                print(f"  discovery reached {len(papers)} fresh papers", flush=True)
                return papers
    # Beilstein second host (small but different host -> parallel throughput).
    for issn in ("1860-5397", "2190-4286"):
        for q in BEILSTEIN_TERMS:
            try:
                for p in search_crossref(query=q, issn=issn, rows=40,
                                         filters={"has-license": "true"}):
                    if p.doi not in seen_papers and p.doi not in dois:
                        dois.add(p.doi); papers.append(p)
            except Exception:
                pass
    return papers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=100000)
    ap.add_argument("--out", default="data/bulk")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    fetcher = ResilientFetcher(
        min_interval=0.34, allow_stealth=False,
        host_concurrency={"eutils.ncbi.nlm.nih.gov": 3,
                          "www.ncbi.nlm.nih.gov": 3,
                          "www.beilstein-journals.org": 2})

    seen_keys, seen_papers, kept, with_ir = _load_resume(out)
    print(f"resume: {kept} records, {len(seen_papers)} papers already done")
    papers = discover(seen_papers, args.target - kept)
    print(f"discovered {len(papers)} fresh papers; target {args.target} "
          f"(have {kept})", flush=True)

    jf = (out / "spectra.jsonl").open("a")
    pf = (out / "seen_papers.txt").open("a")
    t0 = time.time(); done_papers = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(_collect, fetcher, p): p for p in papers}
        try:
            for fut in as_completed(futures):
                paper = futures[fut]
                done_papers += 1
                pf.write(paper.doi + "\n")
                try:
                    recs = fut.result()
                except Exception:
                    recs = []
                for r in recs:
                    key = r.get("inchikey") or _shift_hash(r)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    jf.write(json.dumps(r, ensure_ascii=False) + "\n")
                    kept += 1
                    with_ir += bool(r.get("ir_bands"))
                if done_papers % 100 == 0:
                    jf.flush(); pf.flush()
                    rate = kept / max(time.time() - t0, 1) * 60
                    print(f"  papers={done_papers} kept={kept} ir={with_ir} "
                          f"({rate:.0f} rec/min, fetch={fetcher.stats})", flush=True)
                if kept >= args.target:
                    break
        finally:
            for f in futures:
                f.cancel()
            ex.shutdown(wait=False, cancel_futures=True)
            jf.flush(); pf.flush(); jf.close(); pf.close()

    dt = time.time() - t0
    print(f"\n=== BULK: kept={kept} (IR {with_ir}) from {done_papers} papers in "
          f"{dt/60:.1f} min; {kept/max(dt,1)*60:.0f} rec/min ===", flush=True)
    print(f"fetcher: {fetcher.stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
