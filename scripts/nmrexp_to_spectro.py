#!/usr/bin/env python3
"""
Convert NMRexp (Zenodo 10.5281/zenodo.17296666, 3.37M experimental NMR records)
into a Spectro-format training set.

NMRexp gives one row per (molecule, nucleus): SMILES + source DOI + a *validated,
pre-parsed* peak list (``NMR_processed``) -- i.e. NMR with structure labels at
massive scale, but **no IR**. We use NMRexp's own peak parsing (>99% accurate per
their manual validation) rather than re-parsing the raw text, and pivot per
molecule into Spectro's exact inputs:

    (SMILES) -> { h_nmr "δ 7.27-7.24 (2H, m), ...", c_nmr "δ 180 (1C, d), ...",
                  selfies, inchikey, ir_bands: null  (join IR by InChIKey later) }

    python scripts/nmrexp_to_spectro.py --parquet data/nmrexp/NMRexp.parquet \
        --out data/training_nmrexp --target 100000
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spectro_scraper.normalize import canonical_and_keys  # noqa: E402


def _fmt(x) -> str:
    """Format a shift float without a trailing '.0' but keeping real decimals."""
    try:
        f = float(x)
        return f"{f:g}"
    except (TypeError, ValueError):
        return str(x)


def _spectro_h(processed: str):
    """1H NMR_processed -> 'δ shift (nH, mult), ...' (NMRexp's own peak parse)."""
    try:
        peaks = ast.literal_eval(processed)
    except Exception:
        return None
    out = []
    for t in peaks:
        if not isinstance(t, (list, tuple)) or len(t) < 5:
            continue
        mult, _j, integ, hi, lo = t[0], t[1], t[2], t[3], t[4]
        shift = _fmt(hi) if hi == lo else f"{_fmt(hi)}-{_fmt(lo)}"
        nH = "?H"
        if integ:
            import re
            m = re.match(r"(\d+)", str(integ))
            nH = f"{m.group(1)}H" if m else "?H"
        out.append(f"{shift} ({nH}, {mult})")
    return ("δ " + ", ".join(out)) if out else None


def _spectro_c(processed: str):
    """13C NMR_processed -> 'δ shift (1C, mult), ...'."""
    try:
        peaks = ast.literal_eval(processed)
    except Exception:
        return None
    out = []
    for t in peaks:
        if not isinstance(t, (list, tuple)) or not t:
            continue
        shift = _fmt(t[0])
        mult = (t[1] if len(t) > 1 and t[1] else "s")
        out.append(f"{shift} (1C, {mult})")
    return ("δ " + ", ".join(out)) if out else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/nmrexp/NMRexp.parquet")
    ap.add_argument("--csv", help="use a CSV instead of parquet")
    ap.add_argument("--out", default="data/training_nmrexp")
    ap.add_argument("--target", type=int, default=100000)
    ap.add_argument("--require-both", action="store_true", default=True)
    args = ap.parse_args(argv)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    import pandas as pd
    want = ["SMILES", "smiles_actual", "NMR_type", "NMR_shift_text",
            "NMR_processed", "Filename", "is_same_molecule", "is_same_skeleton"]
    print("loading NMRexp ...", flush=True)
    if args.csv:
        df = pd.read_csv(args.csv, usecols=lambda c: c in want, low_memory=False,
                         encoding="latin-1")
    else:
        import pyarrow.parquet as pq
        have = set(pq.ParquetFile(args.parquet).schema.names)
        df = pd.read_parquet(args.parquet, columns=[c for c in want if c in have])
    print(f"  {len(df):,} rows; columns={list(df.columns)}", flush=True)

    def truthy(x):
        return str(x).strip().upper() in ("TRUE", "1", "YES", "T")
    df = df[df["NMR_type"].isin(["1H NMR", "13C NMR"])]
    if "is_same_molecule" in df.columns:
        df = df[df["is_same_molecule"].map(truthy)]
    if "is_same_skeleton" in df.columns:
        df = df[df["is_same_skeleton"].map(truthy)]
    smi_col = "smiles_actual" if "smiles_actual" in df.columns else "SMILES"
    df["smi"] = (df[smi_col].fillna(df["SMILES"]) if smi_col != "SMILES"
                 else df["SMILES"])
    df = df[df["smi"].notna() & (df["smi"].astype(str).str.len() > 1)]
    df = df[df["NMR_processed"].notna()]
    print(f"  {len(df):,} usable 1H/13C rows", flush=True)

    # Per (molecule, nucleus): keep the richest entry (most peaks).
    df["npk"] = df["NMR_processed"].astype(str).str.count(r"\),")
    best = (df.sort_values("npk", ascending=False)
              .drop_duplicates(["smi", "NMR_type"]))
    h = best[best.NMR_type == "1H NMR"].set_index("smi")
    c = best[best.NMR_type == "13C NMR"].set_index("smi")
    mols = (sorted(set(h.index) & set(c.index)) if args.require_both
            else sorted(set(h.index) | set(c.index)))
    print(f"  {len(mols):,} molecules with both 1H and 13C", flush=True)

    jf = (out / "train.jsonl").open("w")
    kept = 0
    for smi in mols:
        h_nmr = _spectro_h(h.loc[smi, "NMR_processed"]) if smi in h.index else None
        c_nmr = _spectro_c(c.loc[smi, "NMR_processed"]) if smi in c.index else None
        if not (h_nmr or c_nmr):
            continue
        canon, inchikey, selfies = canonical_and_keys(str(smi))
        if not selfies:
            continue
        doi = (h.loc[smi, "Filename"] if smi in h.index else c.loc[smi, "Filename"])
        jf.write(json.dumps({
            "id": inchikey or str(smi),
            "smiles": canon or str(smi),
            "selfies": selfies,
            "h_nmr": h_nmr,
            "c_nmr": c_nmr,
            "ir_bands_cm-1": None,          # join IR by InChIKey separately
            "source_doi": str(doi).replace("_", "/", 1) if doi else None,
            "source": "NMRexp",
        }, ensure_ascii=False) + "\n")
        kept += 1
        if kept % 10000 == 0:
            jf.flush(); print(f"  converted {kept:,}", flush=True)
        if kept >= args.target:
            break
    jf.close()
    (out / "stats.json").write_text(json.dumps(
        {"records": kept, "source": "NMRexp Zenodo 17296666",
         "has_structure": kept, "has_ir": 0,
         "note": "NMR+structure from NMRexp (their validated peak parse); "
                 "IR to be joined by InChIKey"}, indent=2))
    print(f"\nWrote {kept:,} Spectro-format records -> {out}/train.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
