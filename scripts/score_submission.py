#!/usr/bin/env python3
"""Score an external IRSpectra-Bench submission.

Predictions file: JSONL with one object per compound —
  {"qid": "R01", "candidates": ["SMILES1", "SMILES2", ...]}

Up to three ranked candidates are scored (constitution = InChIKey connectivity).

  python scripts/score_submission.py --predictions my_run.jsonl --name "MyModel v1"
  python scripts/score_submission.py --predictions my_run.jsonl --stereo
"""
import argparse, glob, json, random, sys
from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import AllChem, DataStructs

STEREO = False


def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    if not m:
        return None
    k = Chem.MolToInchiKey(m)
    return k if STEREO else k[:14]


def fp(s):
    m = Chem.MolFromSmiles(s) if s else None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def load_cohort(ext):
    rows = []
    a = {json.loads(l)["qid"]: json.loads(l) for l in open("data/benchmark_main/answers2.jsonl")}
    clean = set(json.load(open("data/benchmark_main/clean_qids.json")))
    for qid, ans in a.items():
        if qid not in clean or qid not in ext:
            continue
        rows.append((ans, ext[qid][:3]))
    for d in ["data/benchmark_v3", "data/benchmark_v2_ctrl"]:
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        for qid, ans in a.items():
            if qid not in ext:
                continue
            rows.append((ans, ext[qid][:3]))
    return rows


def metrics(rows):
    res = []
    for ans, cands in rows:
        t = ik(ans["smiles"])
        cs = cands[:3]
        top1 = bool(cs) and t is not None and ik(cs[0]) == t
        rec = t is not None and any(ik(s) == t for s in cs)
        af = fp(ans["smiles"])
        best = 0.0
        for s in cs:
            pf = fp(s)
            if af and pf:
                best = max(best, DataStructs.TanimotoSimilarity(af, pf))
        res.append({"top1": top1, "rec": rec, "tani": best,
                    "diff": ans.get("difficulty", "?")})
    return res


def boot(vals, f, n=2000):
    if not vals:
        return (0, 0, 0)
    pt = f(vals)
    bs = []
    for _ in range(n):
        s = [vals[random.randrange(len(vals))] for _ in vals]
        bs.append(f(s))
    bs.sort()
    return (pt, bs[int(0.025 * n)], bs[int(0.975 * n)])


def main():
    global STEREO
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True, help="JSONL: qid + candidates[]")
    ap.add_argument("--name", default="submission", help="label for leaderboard row")
    ap.add_argument("--stereo", action="store_true", help="score full InChIKey")
    args = ap.parse_args()
    STEREO = args.stereo

    ext = {}
    for line in open(args.predictions):
        row = json.loads(line)
        ext[row["qid"]] = row.get("candidates", [])

    random.seed(0)
    rows = load_cohort(ext)
    if len(rows) < 194:
        print(f"warning: {194 - len(rows)} / 194 benchmark compounds missing")
    R = metrics(rows)
    if not R:
        print("error: no compounds scored — check qid overlap with benchmark")
        sys.exit(1)

    def rate(rs, key):
        return 100 * sum(r[key] for r in rs) / len(rs)

    p, lo, hi = boot(R, lambda s: rate(s, "top1"))
    pr, rlo, rhi = boot(R, lambda s: rate(s, "rec"))
    scaf = 100 * sum(r["tani"] >= 0.45 for r in R) / len(R)
    mt = sum(r["tani"] for r in R) / len(R)
    layer = "full InChIKey" if STEREO else "InChIKey connectivity"
    print(f"# {args.name}")
    print(f"n={len(R)}  scoring={layer}")
    print(f"top1={p:.1f}% [{lo:.0f}-{hi:.0f}]  recall={pr:.1f}% [{rlo:.0f}-{rhi:.0f}]")
    print(f"scaffold>=0.45={scaf:.1f}%  mean_tanimoto={mt:.2f}")


if __name__ == "__main__":
    main()
