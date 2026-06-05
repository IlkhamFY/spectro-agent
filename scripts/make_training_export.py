#!/usr/bin/env python3
"""
Build a training-ready export for the Spectro model from all harvested datasets.

Merges every harvested dataset, dedups by InChIKey (structure-resolved) or
shift-hash (otherwise), and splits the data by *what it can actually train*:

  supervised pairs  (NMR text -> SELFIES)  : records that HAVE a structure label
      -> train.jsonl / test.jsonl  (80/20, split by InChIKey so a molecule never
         appears in both -> no leakage). This is the directly-trainable set for
         the spectra->structure task.

  pretrain_nmr.jsonl : ALL NMR records (label-free) -> for self-supervised
      pretraining of the NMR text encoder (LLM2Vec), which needs no target.

Each supervised row carries the exact Spectro inputs/target:
  {id, smiles, selfies, h_nmr, c_nmr, ir_bands_cm-1, nist_ir_jdx, source_doi}

    python scripts/make_training_export.py --out data/training
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import random
from pathlib import Path


def _shift_hash(r: dict) -> str:
    h = "|".join(p["shift"] for p in r.get("h_peaks", []))
    c = "|".join(p["shift"] for p in r.get("c_peaks", []))
    return hashlib.sha256((h + "##" + c).encode()).hexdigest()[:20]


def _spectro_row(r: dict) -> dict:
    return {
        "id": r.get("inchikey") or _shift_hash(r),
        "smiles": r.get("smiles"),
        "selfies": r.get("selfies"),
        "h_nmr": r.get("spectro_h"),          # "δ 7.85 (2H, d), ..."
        "c_nmr": r.get("spectro_c"),
        "ir_bands_cm-1": r.get("ir_bands") or None,
        "nist_ir_jdx": r.get("nist_ir_jdx"),  # full IR curve (Spectro's j-IR-vis input)
        "source_doi": r.get("source_doi"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="*", default=[
        "data/output/spectra.jsonl", "data/scaled/spectra.jsonl",
        "data/multihost/spectra.jsonl"])
    ap.add_argument("--out", default="data/training")
    ap.add_argument("--test-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    seen: dict[str, dict] = {}
    for path in args.inputs:
        for f in glob.glob(path):
            for line in open(f):
                r = json.loads(line)
                key = r.get("inchikey") or _shift_hash(r)
                # prefer the richer copy (more peaks / has IR / has structure)
                prev = seen.get(key)
                score = (bool(r.get("selfies")), bool(r.get("ir_bands")),
                         len(r.get("h_peaks", [])) + len(r.get("c_peaks", [])))
                if prev is None or score > prev["_score"]:
                    r["_score"] = score
                    seen[key] = r

    records = list(seen.values())
    supervised = [r for r in records if r.get("selfies")]
    rng = random.Random(args.seed)
    rng.shuffle(supervised)
    n_test = int(len(supervised) * args.test_frac)
    test, train = supervised[:n_test], supervised[n_test:]

    def dump(name, rows):
        with (out / name).open("w") as fh:
            for r in rows:
                fh.write(json.dumps(_spectro_row(r), ensure_ascii=False) + "\n")

    dump("train.jsonl", train)
    dump("test.jsonl", test)
    # label-free NMR pretraining pool (every record with any NMR)
    pre = [r for r in records if r.get("h_peaks") or r.get("c_peaks")]
    with (out / "pretrain_nmr.jsonl").open("w") as fh:
        for r in pre:
            fh.write(json.dumps({
                "id": r.get("inchikey") or _shift_hash(r),
                "h_nmr": r.get("spectro_h"), "c_nmr": r.get("spectro_c"),
                "ir_bands_cm-1": r.get("ir_bands") or None,
                "source_doi": r.get("source_doi"),
            }, ensure_ascii=False) + "\n")

    stats = {
        "unique_records": len(records),
        "supervised_pairs_total": len(supervised),
        "train": len(train), "test": len(test),
        "supervised_with_ir": sum(1 for r in supervised if r.get("ir_bands")),
        "supervised_with_nist_curve": sum(1 for r in supervised if r.get("nist_ir_jdx")),
        "pretrain_nmr_pool": len(pre),
    }
    (out / "export_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    print(f"\nwrote {args.out}/{{train,test,pretrain_nmr}}.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
