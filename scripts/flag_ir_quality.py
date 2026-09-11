#!/usr/bin/env python3
"""Flag IR quality issues (referee F2 / F3) without dropping rows.

F2 ir_shared_in_paper: within same pmcid, identical ir_bands tuple across
    >=2 distinct record ids / InChIKeys.
F3 ir_table_flatten_suspect: band list falls into fingerprint (<1500) then
    later rises back into X-H region (>=2800) — table-row flatten heuristic.

Writes a sidecar jsonl.gz next to the curated input (or --out).
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _open_in(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def _open_out(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        return gzip.open(path, "wt", encoding="utf-8")
    return open(path, "w", encoding="utf-8")


def _bands(o) -> list[float]:
    b = o.get("ir_bands_cm-1") or o.get("ir_bands") or []
    return [float(x) for x in b]


def _band_tuple(bands) -> tuple:
    return tuple(bands)


def _pmcid(o) -> str:
    p = o.get("pmcid") or ""
    if p:
        return str(p).upper().replace("PMC", "PMC") if str(p).upper().startswith("PMC") else f"PMC{p}"
    doi = str(o.get("source_doi") or "")
    if doi.upper().startswith("PMC:"):
        return "PMC" + doi.split(":", 1)[1]
    if "PMC" in doi.upper():
        return doi.upper().replace("PMC:", "PMC")
    return ""


def _rec_id(o) -> str:
    return str(o.get("id") or o.get("inchikey") or o.get("smiles") or "")


def _inchikey(o) -> str:
    return str(o.get("inchikey") or "")


def is_flatten_suspect(bands: list[float]) -> bool:
    """After any band <1500, a later band >=2800."""
    seen_fp = False
    for b in bands:
        if b < 1500:
            seen_fp = True
        elif seen_fp and b >= 2800:
            return True
    return False


def flag_file(in_path: Path, out_path: Path) -> dict:
    rows = []
    with _open_in(in_path) as f:
        for line in f:
            rows.append(json.loads(line))

    # F2: group by pmcid -> band_tuple -> set of (id, inchikey)
    by_pmc_bands: dict[str, dict[tuple, set]] = defaultdict(lambda: defaultdict(set))
    for o in rows:
        pmc = _pmcid(o)
        if not pmc:
            continue
        bt = _band_tuple(_bands(o))
        if not bt:
            continue
        by_pmc_bands[pmc][bt].add((_rec_id(o), _inchikey(o)))

    shared_keys = set()  # (pmc, band_tuple) that are shared
    for pmc, bandmap in by_pmc_bands.items():
        for bt, ids in bandmap.items():
            distinct_ids = {i for i, _ in ids if i}
            distinct_ik = {ik for _, ik in ids if ik}
            if len(distinct_ids) >= 2 or len(distinct_ik) >= 2:
                shared_keys.add((pmc, bt))

    n_f2 = 0
    n_f3 = 0
    n = 0
    with _open_out(out_path) as fout:
        for o in rows:
            n += 1
            bands = _bands(o)
            pmc = _pmcid(o)
            bt = _band_tuple(bands)
            f2 = (pmc, bt) in shared_keys if pmc and bt else False
            f3 = is_flatten_suspect(bands)
            if f2:
                n_f2 += 1
            if f3:
                n_f3 += 1
            fout.write(
                json.dumps(
                    {
                        "id": o.get("id"),
                        "inchikey": o.get("inchikey"),
                        "pmcid": pmc or o.get("pmcid"),
                        "source_doi": o.get("source_doi"),
                        "ir_bands_cm-1": bands,
                        "ir_shared_in_paper": f2,
                        "ir_table_flatten_suspect": f3,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    return {
        "source": str(in_path),
        "output": str(out_path),
        "n": n,
        "f2_ir_shared_in_paper": n_f2,
        "f3_ir_table_flatten_suspect": n_f3,
        "f2_shared_pmc_band_groups": len(shared_keys),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        required=True,
        help="Curated irexp jsonl(.gz) with ir_bands_cm-1 + pmcid/id/inchikey",
    )
    ap.add_argument(
        "--out",
        default=None,
        help="Sidecar flags jsonl.gz (default: <input_stem>_ir_quality_flags.jsonl.gz)",
    )
    args = ap.parse_args()
    in_path = Path(args.input)
    if args.out:
        out_path = Path(args.out)
    else:
        stem = in_path.name.replace(".jsonl.gz", "").replace(".jsonl", "")
        out_path = in_path.parent / f"{stem}_ir_quality_flags.jsonl.gz"
    stats = flag_file(in_path, out_path)
    print(json.dumps(stats, indent=2))
    stats_path = out_path.with_name(out_path.name.replace(".jsonl.gz", "_stats.json").replace(".jsonl", "_stats.json"))
    if stats_path == out_path:
        stats_path = out_path.parent / (out_path.stem + "_stats.json")
    # simplify
    stats_path = Path(str(out_path).replace(".jsonl.gz", "_stats.json").replace(".jsonl", "_stats.json"))
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Wrote {out_path}")
    print(f"Wrote {stats_path}")


if __name__ == "__main__":
    main()
