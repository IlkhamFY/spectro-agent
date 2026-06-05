"""
Command-line interface for the Spectro spectra-harvesting agent.

Examples
--------
Harvest from the curated seed list (open-access, IR+NMR-rich papers)::

    python -m spectro_scraper.cli --seeds data/seeds.yaml --target 120

Harvest a single ChemRxiv / journal DOI::

    python -m spectro_scraper.cli --doi 10.3762/bjoc.13.258

Discover + harvest by topic from CrossRef::

    python -m spectro_scraper.cli --search "total synthesis" --issn 1860-5397 --rows 25
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fetch import ResilientFetcher
from .normalize import capabilities
from .pipeline import Harvester


def _load_seeds(path: str) -> list[str]:
    dois: list[str] = []
    p = Path(path)
    if not p.exists():
        return dois
    try:
        import yaml
        data = yaml.safe_load(p.read_text())
        for entry in (data.get("dois") or []):
            dois.append(entry["doi"] if isinstance(entry, dict) else str(entry))
    except Exception:
        # Fallback: treat as a plain list of DOIs, one per line / "- doi".
        for line in p.read_text().splitlines():
            line = line.strip().lstrip("-").strip().strip('"').strip("'")
            if line and not line.endswith(":") and "/" in line and "doi" not in line[:4].lower():
                dois.append(line)
    return dois


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="spectro_scraper",
                                 description="Harvest NMR+IR spectra from public papers.")
    ap.add_argument("--seeds", help="YAML file of curated DOIs")
    ap.add_argument("--doi", action="append", default=[], help="DOI to harvest (repeatable)")
    ap.add_argument("--search", help="CrossRef free-text query")
    ap.add_argument("--issn", default="", help="restrict --search to a journal ISSN")
    ap.add_argument("--rows", type=int, default=20, help="max papers for --search")
    ap.add_argument("--target", type=int, default=None, help="stop after N unique records")
    ap.add_argument("--out", default="data/output", help="output directory")
    ap.add_argument("--basename", default="spectra", help="output file basename")
    ap.add_argument("--no-structures", action="store_true",
                    help="skip OPSIN/RDKit structure resolution (faster)")
    ap.add_argument("--nist-ir", action="store_true",
                    help="capstone: join structure-resolved records to NIST IR "
                         "spectra (JDX), mirroring Spectro's own dataset build")
    ap.add_argument("--min-interval", type=float, default=1.0,
                    help="seconds between requests to the same host")
    ap.add_argument("--no-cache", action="store_true", help="ignore the response cache")
    args = ap.parse_args(argv)

    print("capabilities:", capabilities())
    fetcher = ResilientFetcher(min_interval=args.min_interval)
    if args.no_cache:
        fetcher.get = _wrap_no_cache(fetcher.get)  # type: ignore

    h = Harvester(fetcher=fetcher, resolve_structures=not args.no_structures)

    dois: list[str] = list(args.doi)
    if args.seeds:
        dois += _load_seeds(args.seeds)
    if dois:
        print(f"harvesting {len(dois)} seed DOIs ...")
        h.harvest_dois(dois)
    if args.search:
        print(f"searching CrossRef: {args.search!r} issn={args.issn or '-'}")
        h.harvest_search(args.search, issn=args.issn, rows=args.rows,
                         target=args.target)

    if not h.records:
        print("No records harvested.", file=sys.stderr)
        return 1

    if args.nist_ir:
        print("joining structure-resolved records to NIST IR spectra ...")
        h.join_nist_ir()

    report = h.write(out_dir=args.out, basename=args.basename)
    s = report["stats"]
    print("\n================ HARVEST SUMMARY ================")
    print(f"papers seen        : {s['papers_seen']}")
    print(f"PDFs fetched       : {s['pdfs_fetched']}  ({s['pdf_bytes']/1e6:.1f} MB)")
    print(f"records kept       : {s['records_kept']}")
    print(f"  with IR          : {s['with_ir']}")
    print(f"  paired (NMR+IR)  : {s['with_paired']}")
    print(f"  with structure   : {s['with_structure']}")
    if s.get('nist_ir_joined'):
        print(f"  + NIST IR joined : {s['nist_ir_joined']}  (full IR curves, Spectro-style)")
    print(f"per source         : {s['per_source']}")
    print(f"fetcher            : {report['fetcher']}")
    print(f"outputs            : {report['outputs']}")
    print("================================================")
    print(f"\n{s['records_kept']} NMR records harvested "
          f"({s['with_ir']} with IR) -> {'GOAL MET' if s['records_kept']>100 else 'below target'}")
    return 0


def _wrap_no_cache(fn):
    def inner(url, **kw):
        kw["use_cache"] = False
        return fn(url, **kw)
    return inner


if __name__ == "__main__":
    raise SystemExit(main())
