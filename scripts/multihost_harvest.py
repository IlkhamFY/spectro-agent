#!/usr/bin/env python3
"""
Concurrent, multi-host harvest (item #1: async/parallel + per-host token bucket).

Pulls papers from two *different* fully-open hosts -- Beilstein
(beilstein-journals.org, via CrossRef) and Europe PMC (ebi.ac.uk, full-text
XML) -- and harvests them through a thread pool. The per-host lock in
ResilientFetcher keeps each host polite (never two concurrent hits, min_interval
respected) while the two hosts run in parallel, so wall-clock throughput scales
with the number of hosts rather than being capped by one host's courtesy delay.

    python scripts/multihost_harvest.py --target 800 --workers 8 --out data/multihost
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.discover import search_crossref, search_europepmc  # noqa: E402
from spectro_scraper.fetch import ResilientFetcher                       # noqa: E402
from spectro_scraper.pipeline import Harvester, _shift_hash              # noqa: E402

QUERIES = ["synthesis", "total synthesis", "heterocycle", "natural product",
           "catalysis", "cycloaddition", "functionalization", "alkaloid"]
BEILSTEIN_ISSNS = ["1860-5397", "2190-4286"]
# Europe PMC: journals that put the experimental section in the body text.
EPMC_JOURNALS = ['JOURNAL:"Molecules"', 'JOURNAL:"Beilstein J Org Chem"',
                 'JOURNAL:"Org Biomol Chem"', 'JOURNAL:"RSC Adv"']


def discover(rows: int) -> list:
    """Build a mixed-host paper pool (interleaved so both hosts stay busy)."""
    beil, epmc = [], []
    seen = set()
    for issn in BEILSTEIN_ISSNS:
        for q in QUERIES:
            for p in search_crossref(query=q, issn=issn, rows=rows,
                                     filters={"has-license": "true"}):
                if p.doi not in seen:
                    seen.add(p.doi); beil.append(p)
    for jq in EPMC_JOURNALS:
        for q in QUERIES:
            try:
                for p in search_europepmc(f"{q} AND NMR AND {jq}", page_size=rows):
                    if p.doi not in seen:
                        seen.add(p.doi); epmc.append(p)
            except Exception as e:                           # noqa: BLE001
                print(f"  ! epmc search failed: {e}")
    # interleave so the worker pool always has both hosts in flight
    mixed = []
    for a, b in zip(beil, epmc):
        mixed += [a, b]
    mixed += beil[len(epmc):] + epmc[len(beil):]
    print(f"discovered: {len(beil)} Beilstein + {len(epmc)} Europe PMC "
          f"= {len(mixed)} papers (2 hosts)")
    return mixed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=800)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--rows", type=int, default=25)
    ap.add_argument("--out", default="data/multihost")
    ap.add_argument("--basename", default="spectra")
    ap.add_argument("--min-interval", type=float, default=0.8)
    args = ap.parse_args(argv)

    out = Path(args.out)
    papers = discover(args.rows)
    fetcher = ResilientFetcher(min_interval=args.min_interval)
    h = Harvester(fetcher=fetcher, resolve_structures=True, quality_gate=True)

    def ckpt(hv: Harvester):
        hv.write(out_dir=str(out), basename=args.basename)
        print(f"    [checkpoint] kept={hv.stats.records_kept} ir={hv.stats.with_ir} "
              f"struct={hv.stats.with_structure} src={hv.stats.per_source}", flush=True)

    t0 = time.time()
    h.harvest_papers_concurrent(papers, max_workers=args.workers,
                                target=args.target, checkpoint=ckpt,
                                checkpoint_every=50)
    dt = time.time() - t0
    report = h.write(out_dir=str(out), basename=args.basename)
    s = report["stats"]
    print("\n============ MULTI-HOST CONCURRENT HARVEST ============")
    print(f"workers       : {args.workers}   wall: {dt:.0f}s")
    print(f"papers parsed : {s['papers_seen']}   PDFs/XML: {s['pdfs_fetched']} "
          f"({s['pdf_bytes']/1e6:.0f} MB)")
    print(f"records kept  : {s['records_kept']}  (IR {s['with_ir']}, "
          f"structure {s['with_structure']}, quarantined {s['quarantined']})")
    print(f"per source    : {s['per_source']}")
    print(f"throughput    : {s['records_kept']/dt*60:.0f} records/min, "
          f"{s['papers_seen']/dt*60:.1f} papers/min")
    print(f"quality score : {report['quality'].get('quality_score')}/100")
    print(f"fetcher       : {report['fetcher']}")
    print("=======================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
