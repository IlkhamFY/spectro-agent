#!/usr/bin/env python3
"""
Pooled forward-verification over the WHOLE n=194 benchmark: the original 60
(v3 + v2-control, data/fverify/) plus the 134 main-round compounds
(data/fverify_main/). Same generator output, same blind forward-prediction
protocol, same symmetric chamfer -- only the compound set grows.

This is the script that produces the recall-conditional numbers the paper's
central claim rests on, at n=194 rather than n=60.

  python scripts/forward_verify_all.py
"""
import json, glob, re, sys
from math import comb
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

# (candidates.jsonl, anon_map.json, raw/ glob, label, benchmark dirs supplying the
#  full compound roster -- so the denominators come from the answer keys, not from
#  whichever compounds happened to yield a parseable candidate)
ARMS = [("data/fverify/candidates.jsonl",      "data/fverify/anon_map.json",
         "data/fverify/raw/*.json",      "60-compound (v3 + v2-ctrl)",
         [("data/benchmark_v3", None), ("data/benchmark_v2_ctrl", None)]),
        ("data/fverify_main/candidates.jsonl", "data/fverify_main/anon_map.json",
         "data/fverify_main/raw/*.json", "134-compound (main round)",
         [("data/benchmark_main", "data/benchmark_main/clean_qids.json")])]


def roster(dirs):
    """{qid: difficulty} for every benchmark compound in the arm."""
    out = {}
    for d, cleanf in dirs:
        keep = set(json.load(open(cleanf))) if cleanf else None
        for l in open(f"{d}/answers2.jsonl"):
            a = json.loads(l)
            if keep is None or a["qid"] in keep:
                out[(d, a["qid"])] = a["difficulty"]
    return out


def chamfer(pred, obs):
    if not pred or not obs: return 999.0
    a = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    b = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (a + b) / 2


def mcnemar_exact(b, c):
    """Two-sided exact binomial test on the discordant pairs."""
    n = b + c
    if n == 0: return 1.0
    lo = min(b, c)
    tail = sum(comb(n, k) for k in range(0, lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load_arm(cand_path, amap_path, raw_glob, label, dirs):
    rows = [json.loads(l) for l in open(cand_path)]
    amap = json.load(open(amap_path))
    pred = {}
    for f in sorted(glob.glob(raw_glob)):
        pred.update(json.load(open(f)))
    missing = len(set(amap.values())) - len(set(amap.values()) & set(pred))
    comps = {}
    for r in rows:
        comps.setdefault((r["dir"], r["qid"]), []).append(r)
    out = []
    for key, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            c["pred"] = pred.get(amap.get(c["smiles"]))
            c["dist"] = chamfer(c["pred"], obs) if c["pred"] else 999.0
        best = min(cands, key=lambda c: c["dist"])
        out.append({
            "key": key, "arm": label, "difficulty": cands[0]["difficulty"],
            "n_cand": len(cands),
            "recall": any(c["is_true"] for c in cands),
            "self":   sorted(cands, key=lambda c: c["self_rank"])[0]["is_true"],
            "verify": best["is_true"],
            "dist":   best["dist"],
            "predicted": any(c["pred"] for c in cands),
        })
    # Compounds whose candidates were ALL unparseable produce no row in
    # candidates.jsonl. They are still benchmark compounds and still recall misses,
    # so take the roster (and each compound's difficulty) from the answer keys.
    seen = {r["key"] for r in out}
    pad = 0
    for key, diff in roster(dirs).items():
        if key in seen:
            continue
        pad += 1
        out.append({"key": key, "arm": label, "difficulty": diff, "n_cand": 0,
                    "recall": False, "self": False, "verify": False,
                    "dist": 999.0, "predicted": False})
    return out, missing, pad


def block(name, rec):
    n = len(rec)
    if not n: return
    ceil = sum(r["recall"] for r in rec)
    s1   = sum(r["self"]   for r in rec)
    v1   = sum(r["verify"] for r in rec)
    cond = [r for r in rec if r["recall"]]
    multi = [r for r in cond if r["n_cand"] > 1]
    print(f"\n=== {name}  (n={n}) ===")
    print(f"  generation recall              {ceil}/{n} ({100*ceil/n:.1f}%)")
    print(f"  top-1, solver self-ranking     {s1}/{n} ({100*s1/n:.1f}%)")
    print(f"  top-1, forward-verified        {v1}/{n} ({100*v1/n:.1f}%)")
    if cond:
        cs = sum(r["self"] for r in cond); cv = sum(r["verify"] for r in cond)
        print(f"  CONDITIONAL ON RECALL (n={len(cond)}):")
        print(f"    self-ranking     {cs}/{len(cond)} ({100*cs/len(cond):.1f}%)")
        print(f"    forward-verify   {cv}/{len(cond)} ({100*cv/len(cond):.1f}%)")
        b = sum(1 for r in cond if r["self"] and not r["verify"])
        c = sum(1 for r in cond if r["verify"] and not r["self"])
        print(f"    McNemar exact: b={b} (self only) c={c} (verify only) "
              f"p={mcnemar_exact(b, c):.3f}")
        print(f"    single-candidate compounds (no choice to make): "
              f"{len(cond)-len(multi)}/{len(cond)}")
    if multi:
        ms = sum(r["self"] for r in multi); mv = sum(r["verify"] for r in multi)
        b = sum(1 for r in multi if r["self"] and not r["verify"])
        c = sum(1 for r in multi if r["verify"] and not r["self"])
        print(f"  MULTI-CANDIDATE ONLY (n={len(multi)}):")
        print(f"    self-ranking     {ms}/{len(multi)} ({100*ms/len(multi):.1f}%)")
        print(f"    forward-verify   {mv}/{len(multi)} ({100*mv/len(multi):.1f}%)")
        print(f"    McNemar exact: b={b} c={c} p={mcnemar_exact(b, c):.3f}")
    # top-1 over the whole block, self vs verify
    b = sum(1 for r in rec if r["self"] and not r["verify"])
    c = sum(1 for r in rec if r["verify"] and not r["self"])
    print(f"  top-1 self vs verify, all {n}: b={b} c={c} p={mcnemar_exact(b, c):.3f}")


def main():
    allrec = []
    for cp, ap, rg, lab, dirs in ARMS:
        rec, missing, pad = load_arm(cp, ap, rg, lab, dirs)
        print(f"[{lab}] {len(rec)} compounds "
              f"({pad} with no parseable candidate), "
              f"{missing} unique SMILES lacking a forward prediction")
        allrec += rec
    for cp, ap, rg, lab, dirs in ARMS:
        block(lab, [r for r in allrec if r["arm"] == lab])
    block("POOLED — full benchmark", allrec)
    for d in ("simple", "complex"):
        block(f"POOLED — {d}", [r for r in allrec if r["difficulty"] == d])

    # calibration of the verified pick against its forward-match distance
    cal = sorted((r["dist"], r["verify"]) for r in allrec if r["predicted"])
    print("\ncalibration (verified pick correct vs forward-match chamfer):")
    for lo, hi in [(0, 2), (2, 4), (4, 8), (8, 999)]:
        b = [t for d, t in cal if lo <= d < hi]
        if b:
            print(f"  {lo}-{hi} ppm: {sum(b)}/{len(b)} correct ({100*sum(b)/len(b):.0f}%)")


if __name__ == "__main__":
    main()
