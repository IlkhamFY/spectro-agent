#!/usr/bin/env python3
"""
Consolidate IRexp -- an open EXPERIMENTAL IR dataset scraped from papers.

Takes the real IR band lists harvested from the literature (data/bulk and/or
data/irexp), drops instrument-range/empty artifacts, resolves structures from the
reported compound name (OPSIN, batched), dedups, and writes the IRexp dataset:
real experimental IR + co-reported NMR + structure (where resolvable).

    python scripts/build_irexp.py --sources data/bulk/spectra.jsonl data/irexp/ir.jsonl \
        --out data/irexp
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from py2opsin import py2opsin                              # noqa: E402
from spectro_scraper.extract import _is_instrument_range   # noqa: E402
from spectro_scraper.normalize import canonical_and_keys   # noqa: E402


def _ir_of(r):
    return r.get("ir_bands_cm-1") or r.get("ir_bands")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+",
                    default=["data/bulk/spectra.jsonl", "data/irexp/ir.jsonl"])
    ap.add_argument("--out", default="data/irexp")
    ap.add_argument("--min-bands", type=int, default=4)
    args = ap.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    # Gather clean experimental-IR records.
    recs = []
    for src in args.sources:
        p = Path(src)
        if not p.exists():
            continue
        for line in p.open():
            try:
                r = json.loads(line)
            except Exception:
                continue
            bands = _ir_of(r)
            if not bands or len(bands) < args.min_bands:
                continue
            if _is_instrument_range(bands, r.get("ir_raw") or r.get("ir") or ""):
                continue
            recs.append(r)
    print(f"clean experimental-IR records: {len(recs):,}", flush=True)

    # Batch-resolve structures from names.
    names = [r.get("name") or "" for r in recs]
    smiles = [""] * len(recs)
    idx = [i for i, n in enumerate(names) if n]
    CH = 2000
    for s in range(0, len(idx), CH):
        chunk = [names[i] for i in idx[s:s + CH]]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = py2opsin(chunk)
        res = res if isinstance(res, list) else [res]
        for i, smi in zip(idx[s:s + CH], res):
            smiles[i] = smi or ""
        print(f"  OPSIN {min(s+CH, len(idx)):,}/{len(idx):,}", flush=True)

    jf = (out / "irexp.jsonl").open("w")
    seen = set(); kept = withstruct = withnmr = 0
    for r, smi in zip(recs, smiles):
        bands = _ir_of(r)
        canon = inchikey = selfies = None
        if smi:
            canon, inchikey, selfies = canonical_and_keys(smi)
        key = inchikey or hashlib.sha256(
            (",".join(map(str, bands)) + (r.get("h_nmr") or "")).encode()).hexdigest()[:20]
        if key in seen:
            continue
        seen.add(key)
        h, c = r.get("h_nmr") or r.get("spectro_h"), r.get("c_nmr") or r.get("spectro_c")
        jf.write(json.dumps({
            "id": key,
            "ir_bands_cm-1": bands,
            "ir_source": "experimental",          # REAL IR from the paper
            "h_nmr": h, "c_nmr": c,
            "smiles": canon, "selfies": selfies, "inchikey": inchikey,
            "has_structure": bool(selfies),
            "source_doi": r.get("source_doi"),
        }, ensure_ascii=False) + "\n")
        kept += 1
        withstruct += bool(selfies); withnmr += bool(h or c)
    jf.close()
    stats = {"records": kept, "all_experimental_IR": kept,
             "with_co_reported_NMR": withnmr, "with_structure": withstruct,
             "note": "IRexp: experimental IR band lists scraped from open-access "
                     "papers; NMR co-reported; structure via OPSIN where named"}
    (out / "irexp_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
