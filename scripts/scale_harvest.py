#!/usr/bin/env python3
"""
Scaled, crash-safe multi-journal harvest.

Sweeps many topic queries across the two Beilstein gold-OA journals (Org. Chem.
+ Nanotechnology), applies the quality gate (quarantining physics-impossible
records), dedups across queries, and checkpoints to disk so a long run is
resumable. Designed to be launched in the background.

    python scripts/scale_harvest.py --target 1500 --out data/scaled

Resume simply by re-running with the same --out: already-seen molecules are
skipped (cache + dedup keys are reloaded).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.fetch import ResilientFetcher        # noqa: E402
from spectro_scraper.pipeline import Harvester, _shift_hash  # noqa: E402

# Diverse organic/materials topics -> broad coverage, high IR co-occurrence.
QUERIES = [
    "synthesis", "total synthesis", "cycloaddition", "catalysis",
    "natural product", "heterocycle", "fluorination", "C-H activation",
    "asymmetric synthesis", "cross coupling", "photocatalysis", "macrocycle",
    "organocatalysis", "functionalization", "rearrangement", "annulation",
    "amination", "oxidation", "reduction", "metathesis",
]
ISSNS = ["1860-5397", "2190-4286"]   # bjoc, bjnano


def make_checkpoint(out: Path, basename: str):
    def _ckpt(h: Harvester):
        h.write(out_dir=str(out), basename=basename)
        q = h.stats
        print(f"    [checkpoint] kept={q.records_kept} ir={q.with_ir} "
              f"struct={q.with_structure} quarantined={q.quarantined}", flush=True)
    return _ckpt


def load_resume_keys(out: Path, basename: str) -> list[str]:
    """Reload dedup keys from a previous run's output to resume."""
    keys: list[str] = []
    p = out / f"{basename}.jsonl"
    if p.exists():
        for line in p.open():
            try:
                r = json.loads(line)
                keys.append(r.get("inchikey") or _shift_hash(r))
            except Exception:
                pass
    return keys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=1500)
    ap.add_argument("--rows", type=int, default=40, help="papers per query")
    ap.add_argument("--out", default="data/scaled")
    ap.add_argument("--basename", default="spectra")
    ap.add_argument("--min-interval", type=float, default=0.7)
    ap.add_argument("--no-structures", action="store_true")
    args = ap.parse_args(argv)

    out = Path(args.out)
    fetcher = ResilientFetcher(min_interval=args.min_interval)
    h = Harvester(fetcher=fetcher, resolve_structures=not args.no_structures,
                  quality_gate=True)
    h.seed_seen(load_resume_keys(out, args.basename))
    if h._seen:
        print(f"resuming: {len(h._seen)} molecules already harvested")

    h.harvest_search_multi(QUERIES, ISSNS, rows=args.rows, target=args.target,
                           checkpoint=make_checkpoint(out, args.basename),
                           checkpoint_every=50)
    report = h.write(out_dir=str(out), basename=args.basename)
    s = report["stats"]
    print("\n================ SCALED HARVEST ================")
    print(f"papers seen   : {s['papers_seen']}")
    print(f"PDFs fetched  : {s['pdfs_fetched']} ({s['pdf_bytes']/1e6:.0f} MB)")
    print(f"records kept  : {s['records_kept']}  (IR {s['with_ir']}, "
          f"structure {s['with_structure']}, quarantined {s['quarantined']})")
    print(f"quality score : {report['quality'].get('quality_score')}/100")
    print(f"fetcher       : {report['fetcher']}")
    print("===============================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
