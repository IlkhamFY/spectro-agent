#!/usr/bin/env python3
"""Build a benchmark-held-out IRexp training pool.

The public irexp_release/train.jsonl.gz overlaps IRSpectra-Bench by 117/200
InChIKey-14 (main + v3 + v2_ctrl). This script filters data/irexp_resolved to
exclude every benchmark IK-14 across all cohorts and writes
data/irexp_release/train_no_bench.jsonl.gz for fine-tuning.

  python scripts/build_train_no_bench.py
  python scripts/build_train_no_bench.py --require-nmr   # both H and C present
"""
import argparse, gzip, json, glob, os
from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

BENCH_GLOBS = "data/benchmark_*/answers2.jsonl"
SRC = "data/irexp_resolved/irexp_resolved.jsonl.gz"
OUT = "data/irexp_release/train_no_bench.jsonl.gz"
OUT_NMR = "data/irexp_release/train_no_bench_nmr.jsonl.gz"
STATS = "data/irexp_release/train_no_bench_stats.json"


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None


def bench_ik14():
    out = set()
    for path in sorted(glob.glob(BENCH_GLOBS)):
        for line in open(path):
            a = json.loads(line)
            smi = a.get("smiles")
            ik = a.get("inchikey", "")[:14] or ik14(smi)
            if ik:
                out.add(ik)
    return out


def has_both_nmr(row):
    return bool(str(row.get("h_nmr") or "").strip() and str(row.get("c_nmr") or "").strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-nmr", action="store_true",
                    help="keep only rows with both 1H and 13C shift lists")
    args = ap.parse_args()

    exclude = bench_ik14()
    kept, skipped_bench, skipped_nmr = [], 0, 0
    with gzip.open(SRC, "rt") as f:
        for line in f:
            row = json.loads(line)
            ik = (row.get("inchikey") or row.get("id") or "")[:14] or ik14(row.get("smiles"))
            if ik in exclude:
                skipped_bench += 1
                continue
            if args.require_nmr and not has_both_nmr(row):
                skipped_nmr += 1
                continue
            kept.append(row)

    out_path = OUT_NMR if args.require_nmr else OUT
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with gzip.open(out_path, "wt") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    stats = {
        "source": SRC,
        "output": out_path,
        "benchmark_ik14_excluded": len(exclude),
        "rows_written": len(kept),
        "skipped_benchmark_overlap": skipped_bench,
        "skipped_missing_nmr": skipped_nmr,
        "require_nmr": args.require_nmr,
    }
    stats_path = STATS if not args.require_nmr else STATS.replace(".json", "_nmr.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"benchmark IK-14 held out: {len(exclude)}")
    print(f"wrote {len(kept):,} rows -> {out_path}")
    if args.require_nmr:
        print(f"skipped (no H+C NMR): {skipped_nmr:,}")


if __name__ == "__main__":
    main()
