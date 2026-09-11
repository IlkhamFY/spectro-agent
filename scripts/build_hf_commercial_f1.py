#!/usr/bin/env python3
"""Build F1 commercial publish set with F2/F3 flags for HF upload."""
from __future__ import annotations

import gzip
import json
import time
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\zolot\.openclaw\workspace\projects\spectro-agent")
STAGE = ROOT / "data" / "irexp_rebuild_20260910"
OUT = STAGE / "hf_publish"
OUT.mkdir(parents=True, exist_ok=True)

FLAG_KEYS = ("ir_shared_in_paper", "ir_table_flatten_suspect")
LICENSE_KEYS = ("license", "license_pool", "license_raw", "license_source")


def load_flags(path: Path) -> dict[str, dict]:
    flags: dict[str, dict] = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            rid = rec.get("id")
            if not rid:
                continue
            flags[rid] = {
                "ir_shared_in_paper": bool(rec.get("ir_shared_in_paper", False)),
                "ir_table_flatten_suspect": bool(rec.get("ir_table_flatten_suspect", False)),
            }
    return flags


def attach_flags(rec: dict, flags: dict[str, dict]) -> dict:
    out = dict(rec)
    fl = flags.get(rec.get("id"), {})
    for k in FLAG_KEYS:
        out[k] = bool(fl.get(k, False))
    # ensure licence fields present
    for k in LICENSE_KEYS:
        out.setdefault(k, None if k != "license_pool" else "")
    return out


def write_commercial(src: Path, flags: dict[str, dict], dest: Path, label: str) -> dict:
    t0 = time.time()
    n_in = 0
    n_out = 0
    pools = Counter()
    f2 = f3 = f2or3 = 0
    missing_lic = 0
    pmc_check = None
    with gzip.open(src, "rt", encoding="utf-8") as fin, gzip.open(dest, "wt", encoding="utf-8") as fout:
        for line in fin:
            n_in += 1
            rec = json.loads(line)
            pools[rec.get("license_pool") or "(missing)"] += 1
            if rec.get("license_pool") != "commercial":
                continue
            row = attach_flags(rec, flags)
            if not row.get("license_pool"):
                missing_lic += 1
            if row["ir_shared_in_paper"]:
                f2 += 1
            if row["ir_table_flatten_suspect"]:
                f3 += 1
            if row["ir_shared_in_paper"] or row["ir_table_flatten_suspect"]:
                f2or3 += 1
            pmc = (row.get("pmcid") or "").upper().replace("PMC", "")
            if pmc == "6268696" or (row.get("pmcid") or "").upper() == "PMC6268696":
                pmc_check = {
                    "id": row.get("id"),
                    "pmcid": row.get("pmcid"),
                    "license_pool": row.get("license_pool"),
                    "ir_bands_cm-1": row.get("ir_bands_cm-1"),
                    "ir_shared_in_paper": row["ir_shared_in_paper"],
                    "ir_table_flatten_suspect": row["ir_table_flatten_suspect"],
                }
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_out += 1
    stats = {
        "label": label,
        "source": str(src.relative_to(ROOT)).replace("\\", "/"),
        "dest": str(dest.relative_to(ROOT)).replace("\\", "/"),
        "n_in": n_in,
        "n_commercial": n_out,
        "pools_in": dict(pools),
        "f2": f2,
        "f3": f3,
        "f2_or_f3": f2or3,
        "missing_license_pool_on_out": missing_lic,
        "bytes": dest.stat().st_size,
        "seconds": round(time.time() - t0, 2),
        "pmc6268696": pmc_check,
    }
    print(json.dumps({k: stats[k] for k in ("label", "n_commercial", "f2", "f3", "f2_or_f3", "bytes")}, indent=2))
    return stats


def main() -> None:
    print("loading flags...")
    flags_all = load_flags(STAGE / "irexp_ir_quality_flags.jsonl.gz")
    flags_resolved = load_flags(STAGE / "irexp_resolved_ir_quality_flags.jsonl.gz")
    print(f"flags_all={len(flags_all)} flags_resolved={len(flags_resolved)}")

    stats = {}
    stats["commercial"] = write_commercial(
        STAGE / "irexp_reparsed_refetch.jsonl.gz",
        flags_all,
        OUT / "irexp_commercial.jsonl.gz",
        "commercial",
    )
    stats["resolved_commercial"] = write_commercial(
        STAGE / "irexp_resolved_reparsed_refetch.jsonl.gz",
        flags_resolved,
        OUT / "irexp_resolved_commercial.jsonl.gz",
        "resolved_commercial",
    )

    # commercial-filtered train_no_bench (bands from staged; license via curated id map)
    print("building commercial train_no_bench...")
    lic_by_id = {}
    with gzip.open(STAGE / "irexp_reparsed_refetch.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            lic_by_id[rec["id"]] = {k: rec.get(k) for k in LICENSE_KEYS}

    t0 = time.time()
    n_in = n_out = f2 = f3 = 0
    dest = OUT / "train_no_bench_commercial.jsonl.gz"
    with gzip.open(STAGE / "release_train_no_bench_reparsed.jsonl.gz", "rt", encoding="utf-8") as fin, gzip.open(dest, "wt", encoding="utf-8") as fout:
        for line in fin:
            n_in += 1
            rec = json.loads(line)
            lic = lic_by_id.get(rec.get("id"), {})
            if lic.get("license_pool") != "commercial":
                continue
            row = dict(rec)
            for k in LICENSE_KEYS:
                row[k] = lic.get(k)
            fl = flags_resolved.get(rec.get("id")) or flags_all.get(rec.get("id"), {})
            for k in FLAG_KEYS:
                row[k] = bool(fl.get(k, False))
            if row["ir_shared_in_paper"]:
                f2 += 1
            if row["ir_table_flatten_suspect"]:
                f3 += 1
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_out += 1
    stats["train_no_bench_commercial"] = {
        "label": "train_no_bench_commercial",
        "n_in": n_in,
        "n_commercial": n_out,
        "f2": f2,
        "f3": f3,
        "bytes": dest.stat().st_size,
        "seconds": round(time.time() - t0, 2),
        "dest": str(dest.relative_to(ROOT)).replace("\\", "/"),
    }
    print(json.dumps(stats["train_no_bench_commercial"], indent=2))

    summary_path = OUT / "build_stats.json"
    summary_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"wrote {summary_path}")
    assert stats["commercial"]["n_commercial"] == 88545, stats["commercial"]["n_commercial"]
    assert stats["resolved_commercial"]["n_commercial"] == 28899, stats["resolved_commercial"]["n_commercial"]
    print("ASSERT_OK commercial=88545 resolved_commercial=28899")


if __name__ == "__main__":
    main()
