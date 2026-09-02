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
import json, glob, os, re, sys
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

# Pre-registered expansion rounds join the pool on the same terms, once their
# forward-verification bundle exists. Absent, the arm is simply not there and every
# number below is the committed n=194 one.
for _d in sorted(glob.glob("data/fverify_expand*")):
    _r = os.path.join("data", "benchmark" + os.path.basename(_d)[len("fverify"):])
    if os.path.exists(f"{_d}/candidates.jsonl") and os.path.isdir(_r):
        ARMS.append((f"{_d}/candidates.jsonl", f"{_d}/anon_map.json",
                     f"{_d}/raw/*.json", f"expansion round ({os.path.basename(_r)})",
                     [(_r, f"{_r}/clean_qids.json"
                       if os.path.exists(f"{_r}/clean_qids.json") else None)]))


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


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact test on a 2x2 table (sum of tables no likelier than
    the observed one). Used only to check that the two arms are homogeneous enough
    to pool -- a large p here is what licenses the pooled column."""
    n = a + b + c + d
    if n == 0: return 1.0
    def p(w, x, y, z):
        return comb(w + x, w) * comb(y + z, y) / comb(n, w + y)
    obs, tot = p(a, b, c, d), 0.0
    for i in range(0, min(a + b, a + c) + 1):
        j, k, l = a + b - i, a + c - i, d - (a - i)
        if j < 0 or k < 0 or l < 0: continue
        q = p(i, j, k, l)
        if q <= obs + 1e-12: tot += q
    return min(1.0, tot)


def heterogeneity(allrec):
    """Are the two arms consistent enough to pool? Compare them on the quantities
    the pooled column reports."""
    arms = sorted({r["arm"] for r in allrec})
    if len(arms) < 2: return
    if len(arms) > 2:
        # Every pair is compared rather than the first two, so adding an arm cannot make
        # this check quietly stop testing the arms it was meant to test.
        for i in range(len(arms)):
            for j in range(i + 1, len(arms)):
                heterogeneity([r for r in allrec
                               if r["arm"] in (arms[i], arms[j])])
        return
    A = [r for r in allrec if r["arm"] == arms[0]]
    B = [r for r in allrec if r["arm"] == arms[1]]
    print("\n=== ARM HOMOGENEITY (does pooling the two arms distort anything?) ===")
    tests = [
        ("verification precision | recall",
         lambda R: [r for r in R if r["recall"]], "verify"),
        ("verification precision, multi-candidate only",
         lambda R: [r for r in R if r["recall"] and r["n_cand"] > 1], "verify"),
        ("self-ranking, multi-candidate only",
         lambda R: [r for r in R if r["recall"] and r["n_cand"] > 1], "self"),
    ]
    for name, sel, key in tests:
        a, b = sel(A), sel(B)
        ha, hb = sum(r[key] for r in a), sum(r[key] for r in b)
        p = fisher_exact(ha, len(a) - ha, hb, len(b) - hb)
        print(f"  {name:<44} {ha}/{len(a)} vs {hb}/{len(b)}   Fisher p={p:.3f}")
    # composition: are the single-candidate fractions comparable?
    ca = [r for r in A if r["recall"]]; cb = [r for r in B if r["recall"]]
    sa = sum(1 for r in ca if r["n_cand"] == 1); sb = sum(1 for r in cb if r["n_cand"] == 1)
    p = fisher_exact(sa, len(ca) - sa, sb, len(cb) - sb)
    print(f"  {'single-candidate fraction | recall':<44} "
          f"{sa}/{len(ca)} vs {sb}/{len(cb)}   Fisher p={p:.3f}")
    print("  (large p = arms agree; pooling is licensed, not assumed)")


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


SIDECAR = "data/diagnosis.json"


def sidecar(allrec, path=SIDECAR):
    """Write the diagnosis counts the leading figure draws.

    The figure used to restate n=194 and its three segments as literals, so a change of
    cohort would have left it silently disagreeing with the numbers underneath it. It now
    reads them from here, and here is generated.
    """
    n = len(allrec)
    recalled = sum(r["recall"] for r in allrec)
    verified = sum(r["verify"] for r in allrec)
    out = {
        "n": n,
        "verified": verified,                 # true structure recalled AND ranked first
        "misranked": recalled - verified,     # recalled, but a distractor ranked first
        "wall": n - recalled,                 # never proposed at all
        "recalled": recalled,
        "self_ranked": sum(r["self"] for r in allrec),
        "conditional_verify": [verified, recalled],
        "arms": {a: sum(1 for r in allrec if r["arm"] == a)
                 for a in sorted({r["arm"] for r in allrec})},
    }
    assert out["verified"] + out["misranked"] + out["wall"] == n
    json.dump(out, open(path, "w"), indent=1)
    print(f"\nwrote {path}: n={n}, {out['verified']}/{out['misranked']}/{out['wall']} "
          f"(verified / mis-ranked / never proposed)")
    return out


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
    heterogeneity(allrec)
    block("POOLED — full benchmark", allrec)
    for d in ("simple", "complex"):
        block(f"POOLED — {d}", [r for r in allrec if r["difficulty"] == d])

    # calibration of the verified pick against its forward-match distance
    sidecar(allrec)

    cal = sorted((r["dist"], r["verify"]) for r in allrec if r["predicted"])
    print("\ncalibration (verified pick correct vs forward-match chamfer):")
    for lo, hi in [(0, 2), (2, 4), (4, 8), (8, 999)]:
        b = [t for d, t in cal if lo <= d < hi]
        if b:
            print(f"  {lo}-{hi} ppm: {sum(b)}/{len(b)} correct ({100*sum(b)/len(b):.0f}%)")


if __name__ == "__main__":
    main()
