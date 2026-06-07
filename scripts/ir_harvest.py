#!/usr/bin/env python3
"""
IRexp builder -- a large, open, EXPERIMENTAL IR dataset scraped from the
literature. The IR analog of NMRexp, filling the gap that no such database
exists (NIST is ~16k common molecules; large corpora are NMR-only or compute IR).

The product is the real IR that chemists report -- "IR (neat) ν 3024, 1715, 1602
cm⁻¹" band lists -- kept only when actually present, with co-reported NMR and the
compound name (structures resolved in a batched OPSIN post-pass:
scripts/build_ir_triples.py-style). No synthetic IR.

Discovery targets IR-reporting open-access papers (NCBI esearch, IR markers +
body-experimental journals, sliced by year past the 10k cap). Streaming,
resumable, multi-host (PMC + Beilstein). Run under an auto-snapshot loop.

    python scripts/ir_harvest.py --target 100000 --out data/irexp --workers 10
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

# IR is reported in a minority of papers, so target it explicitly.
IR_MARK = '("IR (KBr" OR "IR (neat" OR "IR (ATR" OR "FT-IR" OR "FTIR" OR "infrared")'
JOURNALS = [
    "Molecules", "Int J Mol Sci", "Pharmaceuticals (Basel)", "Mar Drugs",
    "Beilstein J Org Chem", "Molbank", "Org Biomol Chem", "RSC Adv",
    "Antibiotics (Basel)", "Pharmaceutics", "Metabolites", "Biomolecules",
    "Polymers (Basel)", "Materials (Basel)", "Nanomaterials (Basel)",
    "Gels (Basel)", "Catalysts", "Plants (Basel)", "Foods", "Inorganics",
]
YEARS = list(range(2026, 2009, -1))
BEILSTEIN_TERMS = ["infrared", "FT-IR", "synthesis", "natural product",
                   "heterocycle", "total synthesis"]


def _hash(r: dict) -> str:
    ir = ",".join(str(b) for b in (r.get("ir_bands") or []))
    h = "|".join(p["shift"] for p in r.get("h_peaks", []))
    return hashlib.sha256((ir + "##" + h).encode()).hexdigest()[:20]


def _collect(fetcher: ResilientFetcher, paper):
    """Fetch + extract; keep ONLY records that actually carry experimental IR."""
    out = []
    for kind, url in select_adapter(paper).pdf_candidates(paper, fetcher):
        txt = ""
        if kind == "xml":
            r = fetcher.get(url, use_cache=False)
            if r.ok:
                txt = _xml_to_text(r.text)
        else:
            from spectro_scraper.pdf import extract_pdf_text
            r = fetcher.get(url, binary=True, use_cache=False)
            if r.ok and r.content[:4] == b"%PDF":
                txt = extract_pdf_text(r.content)
        if not txt:
            continue
        from spectro_scraper.normalize import to_spectro_h, to_spectro_c
        for rec in extract_records(txt):
            if not rec.ir_bands:                 # IR is the product -- require it
                continue
            out.append({
                "ir_bands_cm-1": rec.ir_bands,
                "ir_raw": rec.ir,
                "h_nmr": to_spectro_h(rec),
                "c_nmr": to_spectro_c(rec),
                "h_peaks": [p.__dict__ for p in rec.h_peaks],
                "name": rec.name,
                "source_doi": paper.doi,
            })
    return out


def discover(seen_papers: set, want: int) -> list:
    papers, dois = [], set()
    need = min(max(want, 1) * 2, 120000)   # lean per-session pool; resume continues
    for journal in JOURNALS:
        for year in YEARS:
            term = (f'{IR_MARK} AND "{journal}"[Journal] AND {year}[pdat] '
                    f'AND open access[filter]')
            try:
                ps, _ = search_ncbi_pmc(term, retmax=5000)
            except Exception:
                continue
            for p in ps:
                if p.doi not in seen_papers and p.doi not in dois:
                    dois.add(p.doi); papers.append(p)
            time.sleep(0.34)
            if len(papers) >= need:
                return papers
    # Broad sweep across the WHOLE OA IR corpus (~300-580k papers), not just the
    # 20 high-yield journals -- sliced by year/month to stay under esearch's 10k
    # cap. This is what makes 250k reachable.
    for year in YEARS:
        for month in range(1, 13):
            term = (f'{IR_MARK} AND {year}/{month:02d}[pdat] '
                    f'AND open access[filter]')
            try:
                ps, _ = search_ncbi_pmc(term, retmax=9000)
            except Exception:
                continue
            for p in ps:
                if p.doi not in seen_papers and p.doi not in dois:
                    dois.add(p.doi); papers.append(p)
            time.sleep(0.34)
            if len(papers) >= need:
                return papers
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


def _resume(out: Path):
    keys, papers, kept, nmr = set(), set(), 0, 0
    jf, pf = out / "ir.jsonl", out / "seen_papers.txt"
    if jf.exists():
        for line in jf.open():
            try:
                r = json.loads(line); keys.add(_hash_record(r)); kept += 1
                nmr += bool(r.get("h_nmr") or r.get("c_nmr"))
            except Exception:
                pass
    if pf.exists():
        papers = set(pf.read_text().split())
    return keys, papers, kept, nmr


def _hash_record(r: dict) -> str:
    ir = ",".join(str(b) for b in (r.get("ir_bands_cm-1") or []))
    return hashlib.sha256((ir + "##" + (r.get("h_nmr") or "")).encode()).hexdigest()[:20]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=100000)
    ap.add_argument("--out", default="data/irexp")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    fetcher = ResilientFetcher(min_interval=0.34, allow_stealth=False,
                               host_concurrency={"eutils.ncbi.nlm.nih.gov": 3,
                                                 "www.ncbi.nlm.nih.gov": 3,
                                                 "pmc.ncbi.nlm.nih.gov": 3,
                                                 "www.ebi.ac.uk": 3,
                                                 "www.beilstein-journals.org": 2})
    keys, seen_papers, kept, nmr = _resume(out)
    print(f"resume: {kept} IR records, {len(seen_papers)} papers done", flush=True)
    papers = discover(seen_papers, args.target - kept)
    # Split PMC full-text load across TWO hosts (NCBI + EBI) so throughput is the
    # SUM of their polite rates (~2x). Every other PMC paper goes to EBI.
    n_ebi = 0
    for i, p in enumerate(papers):
        if i % 2 and (p.doi or "").startswith("PMC:"):
            num = p.doi.split(":", 1)[1]
            p.fulltext_xml = (f"https://www.ebi.ac.uk/europepmc/webservices/"
                              f"rest/PMC{num}/fullTextXML")
            n_ebi += 1
    print(f"discovered {len(papers)} fresh IR papers ({n_ebi} routed to EBI, "
          f"rest NCBI) toward {args.target}", flush=True)

    jf = (out / "ir.jsonl").open("a"); pf = (out / "seen_papers.txt").open("a")
    t0 = time.time(); dp = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_collect, fetcher, p): p for p in papers}
        try:
            for fut in as_completed(futs):
                dp += 1; pf.write(futs[fut].doi + "\n")
                try:
                    recs = fut.result()
                except Exception:
                    recs = []
                for r in recs:
                    k = _hash_record(r)
                    if k in keys:
                        continue
                    keys.add(k); jf.write(json.dumps(r, ensure_ascii=False) + "\n")
                    kept += 1; nmr += bool(r.get("h_nmr") or r.get("c_nmr"))
                if dp % 100 == 0:
                    jf.flush(); pf.flush()
                    print(f"  papers={dp} IRrecords={kept} (with NMR {nmr}) "
                          f"{kept/max(time.time()-t0,1)*60:.0f}/min", flush=True)
                if kept >= args.target:
                    break
        finally:
            ex.shutdown(wait=False, cancel_futures=True)
            jf.flush(); pf.flush(); jf.close(); pf.close()
    print(f"\n=== IRexp: {kept} experimental IR records ({nmr} with co-reported "
          f"NMR) from {dp} papers in {(time.time()-t0)/60:.1f} min ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
