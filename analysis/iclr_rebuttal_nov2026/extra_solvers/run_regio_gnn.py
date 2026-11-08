#!/usr/bin/env python3
"""Enlarge the frozen n=60 candidate lists by formula-preserving regioisomer enumeration, then rank with the local 13C GNN.

Seeds are the deposited candidate SMILES in data/fverify/candidates.jsonl.
The gold structure is not a seed and is not added to the pool.
IR and 1H are unused. 13C is the ranking target only.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from payloads import fverify_pool, load_arm  # noqa: E402
from peaks import parse_c  # noqa: E402
from score import score_ranked, summarize, write_json  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    out_dir = HERE / "outputs"
    public, gold = load_arm("60")
    pools = fverify_pool()
    missing = [r["uid"] for r in public if r["uid"] not in pools]
    if missing:
        raise SystemExit(f"frozen pool missing {missing[:5]}")

    enum = _load("enum", ROOT / "scripts" / "enumerate_isomers.py")
    gnn = _load("gnn", ROOT / "scripts" / "gnn_predict.py")

    rows = []
    t0 = time.time()
    cache: dict[str, list[float] | None] = {}
    for rec in public:
        obs = parse_c(rec["c_nmr"])
        seeds = [s for s in pools[rec["uid"]] if s]
        enlarged = list(seeds)
        seen = set(seeds)
        for seed in seeds:
            for iso in enum.enumerate_regioisomers(seed, cap=300):
                if iso not in seen:
                    seen.add(iso)
                    enlarged.append(iso)

        def dist(smiles: str) -> float:
            if smiles not in cache:
                cache[smiles] = gnn.predict_c13(smiles)
            pred = cache[smiles]
            return gnn.chamfer(pred, obs) if pred else 1e9

        base_ranked = sorted(seeds, key=dist)
        enum_ranked = sorted(enlarged, key=dist)
        base = score_ranked(base_ranked, gold[rec["uid"]])
        full = score_ranked(enum_ranked, gold[rec["uid"]])
        rows.append({
            "uid": rec["uid"],
            "formula": rec["formula"],
            "n_seed": len(seeds),
            "n_enlarged": len(enlarged),
            "base_top1": base["top1"],
            "base_recall": base["recall"],
            "top1": full["top1"],
            "recall": full["recall"],
            "hit_rank": full["hit_rank"],
            "n_invalid": full["n_invalid"],
            "rank1": enum_ranked[0] if enum_ranked else None,
        })
        print(f"{rec['uid']} seeds {len(seeds)} -> {len(enlarged)} top1 {full['top1']}", flush=True)

    summary = {
        "method": "regioisomer enumeration around frozen candidates + GNN 13C chamfer",
        "arm": "60",
        "seconds": round(time.time() - t0, 1),
        "base_pool": summarize([{"top1": r["base_top1"], "recall": r["base_recall"]} for r in rows]),
        "enlarged": summarize(rows),
        "median_enlarged": sorted(r["n_enlarged"] for r in rows)[len(rows) // 2],
        "n_unique_scored_smiles": len(cache),
        "rows": rows,
    }
    write_json(out_dir / "regio_gnn_arm60.json", summary)
    print(json.dumps({k: summary[k] for k in ("base_pool", "enlarged", "median_enlarged", "seconds")}))


if __name__ == "__main__":
    main()
