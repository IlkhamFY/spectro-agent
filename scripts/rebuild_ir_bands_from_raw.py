#!/usr/bin/env python3
"""Rebuild IR band lists from stored ir_raw using fixed _parse_ir_bands (F1).

Fast path: re-parse harvest snapshot ir_raw, then propagate new bands into
curated irexp / release rows by matching (source_doi, old_bands) or
(source_doi, h_nmr, c_nmr). Does not invent data; rows without a match keep
old bands and are counted as unmatched.

Outputs staged under data/irexp_rebuild_YYYYMMDD/ (never overwrites HF).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spectro_scraper.extract import _parse_ir_bands  # noqa: E402


def _open_in(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def _open_out(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        return gzip.open(path, "wt", encoding="utf-8")
    return open(path, "w", encoding="utf-8")


def _band_key(bands) -> tuple:
    if not bands:
        return tuple()
    return tuple(float(x) for x in bands)


def _norm_doi(d) -> str:
    return (d or "").strip()


def rebuild_harvest(harvest_path: Path, out_path: Path) -> dict:
    """Re-parse every ir_raw; write new harvest jsonl.gz. Return stats + maps."""
    n = 0
    changed = 0
    max_lt_before = 0
    max_lt_after = 0
    thousands_raw = 0
    pmc626_examples = []
    # maps for propagating to curated
    by_doi_old = defaultdict(list)  # (doi, old_bands) -> new_bands
    by_doi_nmr = {}  # (doi, h_nmr, c_nmr) -> new_bands

    with _open_in(harvest_path) as fin, _open_out(out_path) as fout:
        for line in fin:
            o = json.loads(line)
            n += 1
            old = list(o.get("ir_bands_cm-1") or [])
            raw = o.get("ir_raw") or ""
            if old and max(float(x) for x in old) < 1000:
                max_lt_before += 1
            if isinstance(raw, str) and (
                re_search_thousands(raw)
            ):
                thousands_raw += 1
            new = _parse_ir_bands(raw) if raw else list(old)
            if old != new:
                changed += 1
            if new and max(float(x) for x in new) < 1000:
                max_lt_after += 1
            o["ir_bands_cm-1"] = new
            o["ir_bands_old_cm-1"] = old
            fout.write(json.dumps(o, ensure_ascii=False) + "\n")

            doi = _norm_doi(o.get("source_doi"))
            by_doi_old[(doi, _band_key(old))].append(_band_key(new))
            by_doi_nmr[(doi, o.get("h_nmr"), o.get("c_nmr"))] = _band_key(new)

            if "6268696" in doi:
                pmc626_examples.append(
                    {
                        "source_doi": doi,
                        "name": o.get("name"),
                        "ir_raw": raw[:200],
                        "old": old,
                        "new": new,
                    }
                )

    # collapse maps to unique new bands (majority / first)
    map_old = {}
    for k, vals in by_doi_old.items():
        # prefer the most common new tuple
        c = Counter(vals)
        map_old[k] = list(c.most_common(1)[0][0])

    map_nmr = {k: list(v) for k, v in by_doi_nmr.items()}

    stats = {
        "source": str(harvest_path),
        "output": str(out_path),
        "n": n,
        "changed": changed,
        "max_lt_1000_before": max_lt_before,
        "max_lt_1000_after": max_lt_after,
        "thousands_pattern_raw": thousands_raw,
        "pmc626_examples": pmc626_examples[:20],
    }
    return stats, map_old, map_nmr


def re_search_thousands(raw: str) -> bool:
    import re

    return bool(re.search(r"\d,\d{3}(?:\D|$)", raw))


def apply_maps_to_curated(
    in_path: Path,
    out_path: Path,
    map_old: dict,
    map_nmr: dict,
    band_field: str = "ir_bands_cm-1",
) -> dict:
    n = 0
    changed = 0
    unmatched = 0
    matched_old = 0
    matched_nmr = 0
    max_lt_before = 0
    max_lt_after = 0
    pmc626 = []

    with _open_in(in_path) as fin, _open_out(out_path) as fout:
        for line in fin:
            o = json.loads(line)
            n += 1
            old = list(o.get(band_field) or [])
            if old and max(float(x) for x in old) < 1000:
                max_lt_before += 1
            doi = _norm_doi(o.get("source_doi"))
            new = None
            key_old = (doi, _band_key(old))
            if key_old in map_old:
                new = map_old[key_old]
                matched_old += 1
            else:
                key_nmr = (doi, o.get("h_nmr"), o.get("c_nmr"))
                if key_nmr in map_nmr:
                    new = map_nmr[key_nmr]
                    matched_nmr += 1
            if new is None:
                unmatched += 1
                new = old
            else:
                new = list(new)
            if old != new:
                changed += 1
            if new and max(float(x) for x in new) < 1000:
                max_lt_after += 1
            o[band_field] = new
            o["ir_bands_old_cm-1"] = old
            fout.write(json.dumps(o, ensure_ascii=False) + "\n")
            pmc = str(o.get("pmcid") or "") + doi
            if "6268696" in pmc:
                pmc626.append(
                    {
                        "id": o.get("id"),
                        "inchikey": o.get("inchikey"),
                        "old": old,
                        "new": new,
                        "smiles": o.get("smiles"),
                    }
                )

    return {
        "source": str(in_path),
        "output": str(out_path),
        "n": n,
        "changed": changed,
        "unmatched": unmatched,
        "matched_via_doi_old_bands": matched_old,
        "matched_via_doi_nmr": matched_nmr,
        "max_lt_1000_before": max_lt_before,
        "max_lt_1000_after": max_lt_after,
        "pmc626_examples": pmc626[:20],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--outdir",
        default=None,
        help="Staging dir (default data/irexp_rebuild_YYYYMMDD)",
    )
    ap.add_argument(
        "--harvest",
        default=str(ROOT / "data/irexp/ir_harvest_snapshot.jsonl.gz"),
    )
    args = ap.parse_args()
    stamp = date.today().strftime("%Y%m%d")
    outdir = Path(args.outdir or ROOT / f"data/irexp_rebuild_{stamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    harvest_out = outdir / "ir_harvest_snapshot_reparsed.jsonl.gz"
    print(f"Rebuilding harvest -> {harvest_out}")
    h_stats, map_old, map_nmr = rebuild_harvest(Path(args.harvest), harvest_out)
    print(json.dumps({k: v for k, v in h_stats.items() if k != "pmc626_examples"}, indent=2))

    curated_jobs = [
        (ROOT / "data/irexp/irexp.jsonl.gz", outdir / "irexp_reparsed.jsonl.gz"),
        (
            ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz",
            outdir / "irexp_resolved_reparsed.jsonl.gz",
        ),
        (
            ROOT / "data/irexp_release/train.jsonl.gz",
            outdir / "release_train_reparsed.jsonl.gz",
        ),
        (
            ROOT / "data/irexp_release/test.jsonl.gz",
            outdir / "release_test_reparsed.jsonl.gz",
        ),
        (
            ROOT / "data/irexp_release/pretrain_ir.jsonl.gz",
            outdir / "release_pretrain_ir_reparsed.jsonl.gz",
        ),
        (
            ROOT / "data/irexp_release/train_no_bench.jsonl.gz",
            outdir / "release_train_no_bench_reparsed.jsonl.gz",
        ),
    ]
    all_stats = {"harvest": h_stats, "curated": {}}
    for src, dst in curated_jobs:
        if not src.exists():
            print(f"SKIP missing {src}")
            continue
        print(f"Applying maps -> {dst.name}")
        st = apply_maps_to_curated(src, dst, map_old, map_nmr)
        all_stats["curated"][dst.name] = st
        print(
            f"  n={st['n']} changed={st['changed']} unmatched={st['unmatched']} "
            f"max_lt {st['max_lt_1000_before']} -> {st['max_lt_1000_after']}"
        )

    stats_path = outdir / "rebuild_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, indent=2, ensure_ascii=False)
    print(f"Wrote {stats_path}")

    # quick PMC6268696 check on curated
    irexp_out = outdir / "irexp_reparsed.jsonl.gz"
    if irexp_out.exists():
        expected = [3060.0, 2976.0, 2874.0, 1730.0, 1678.0]
        found = []
        with _open_in(irexp_out) as f:
            for line in f:
                o = json.loads(line)
                if "6268696" in str(o.get("pmcid") or "") or "6268696" in str(
                    o.get("source_doi") or ""
                ):
                    found.append(o.get("ir_bands_cm-1"))
        print("PMC6268696 bands after rebuild (all compounds):")
        for b in found:
            ok = b == expected
            print(f"  {b}  match_expected_compound3={ok}")
        # at least one should match expected
        any_ok = any(b == expected for b in found)
        print(f"PMC6268696 expected compound bands present: {any_ok}")


if __name__ == "__main__":
    main()
