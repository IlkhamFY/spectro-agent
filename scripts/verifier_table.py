#!/usr/bin/env python3
"""
Table 8: the four re-rankers (solver self-ranking, deterministic HOSE lookup, learned
GNN, LLM forward-verifier) on ONE identical candidate set, with the paired tests.

  python scripts/verifier_table.py          # 60-compound arm  (n=19 conditional)
  python scripts/verifier_table.py --all    # whole benchmark  (n=65 conditional)

Every verifier sees exactly the same candidates and the same observed 13C; only the
13C predictor changes. Requires the HOSE table and the GNN checkpoint (see
scripts/hose_predict.py build and scripts/gnn_predict.py train).
"""
import json, glob, sys
from math import comb
from collections import defaultdict

import hose_predict, gnn_predict
from specmetrics import chamfer

ARMS = ["data/fverify"] + (["data/fverify_main"] if "--all" in sys.argv else [])


def mcnemar_exact(b, c):
    n = b + c
    if n == 0: return 1.0
    lo = min(b, c)
    return min(1.0, 2 * sum(comb(n, k) for k in range(lo + 1)) / 2 ** n)


def main():
    comps, llm = defaultdict(list), {}
    for arm in ARMS:
        amap = json.load(open(f"{arm}/anon_map.json"))
        pred = {}
        for f in sorted(glob.glob(f"{arm}/raw/*.json")):
            pred.update(json.load(open(f)))
        for l in open(f"{arm}/candidates.jsonl"):
            r = json.loads(l)
            comps[(arm, r["dir"], r["qid"])].append(r)
            llm[r["smiles"]] = pred.get(amap.get(r["smiles"]))

    hose_cache, gnn_cache = {}, {}
    rows = []
    for key, cands in comps.items():
        if not any(c["is_true"] for c in cands):
            continue                       # conditional-on-recall set only
        obs = cands[0]["obs_c13"]
        for c in cands:
            s = c["smiles"]
            if s not in hose_cache: hose_cache[s] = hose_predict.predict_c13(s)
            if s not in gnn_cache:  gnn_cache[s]  = gnn_predict.predict_c13(s)
            c["d_hose"] = chamfer(hose_cache[s], obs)
            c["d_gnn"]  = chamfer(gnn_cache[s],  obs)
            c["d_llm"]  = chamfer(llm.get(s), obs) if llm.get(s) else 999.0
        rows.append({
            "self": sorted(cands, key=lambda c: c["self_rank"])[0]["is_true"],
            "hose": min(cands, key=lambda c: c["d_hose"])["is_true"],
            "gnn":  min(cands, key=lambda c: c["d_gnn"])["is_true"],
            "llm":  min(cands, key=lambda c: c["d_llm"])["is_true"],
            "multi": len(cands) > 1,
        })

    n = len(rows)
    print(f"arms: {', '.join(ARMS)}")
    print(f"\nCONDITIONAL ON RECALL, n={n}\n")
    print(f"  {'verifier':<26}{'top-1 | recall':>16}")
    for k, name in [("self", "solver self-ranking"), ("hose", "HOSE lookup"),
                    ("gnn", "learned GNN"), ("llm", "LLM forward-verifier")]:
        h = sum(r[k] for r in rows)
        print(f"  {name:<26}{f'{h}/{n} ({100*h/n:.0f}%)':>16}")

    print("\npaired tests (McNemar exact, discordant pairs):")
    for a, b_ in [("self", "hose"), ("self", "llm"), ("self", "gnn"),
                  ("hose", "gnn"), ("hose", "llm"), ("gnn", "llm")]:
        b = sum(1 for r in rows if r[a] and not r[b_])
        c = sum(1 for r in rows if r[b_] and not r[a])
        print(f"  {a:>4} vs {b_:<4}  b={b} c={c}  p={mcnemar_exact(b, c):.3f}")

    multi = [r for r in rows if r["multi"]]
    print(f"\nmulti-candidate only, n={len(multi)}:")
    for k, name in [("self", "solver self-ranking"), ("hose", "HOSE lookup"),
                    ("gnn", "learned GNN"), ("llm", "LLM forward-verifier")]:
        h = sum(r[k] for r in multi)
        print(f"  {name:<26}{f'{h}/{len(multi)} ({100*h/len(multi):.0f}%)':>16}")


if __name__ == "__main__":
    main()
