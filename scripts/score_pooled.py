#!/usr/bin/env python3
"""Pool complete, validate-clean Opus rounds without rewriting score_main.py.

The n=194 lock in scripts/score_main.py is intentional and is not edited here.
This script is the extension named in docs/EXPANSION_PREREGISTRATION_500.md:
after (and only after) a pre-registered expansion is 100% deposited, validated,
and scored in isolation, it reports how that round would combine with the
locked headline.

It refuses to run against an unfinished raw/ tree, a missing answer key, or a
missing predictions2.jsonl. It never reads raw_fable/ or predictions2_fable.jsonl.
It does not invent numbers: every count is InChIKey-14 connectivity on deposited
candidates vs the key, the same rule as score2 / score_main.

  python scripts/score_pooled.py                  # n=194 only
  python scripts/score_pooled.py --expand         # + +106 validate-clean
  python scripts/score_pooled.py --expand --expand-500

A missing --expand-500 flag is the correct state until that round is complete.
Do not pass --expand-500 to force a partial into the headline.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs

RDLogger.DisableLog("rdApp.*")


def ik14(s):
    m = Chem.MolFromSmiles(s) if s else None
    if not m:
        return None
    return Chem.MolToInchiKey(m)[:14]


def fp(s):
    m = Chem.MolFromSmiles(s) if s else None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048) if m else None


def load_main_194():
    """Identical cohort construction to scripts/score_main.py (n=194)."""
    rows = []
    a = {json.loads(l)["qid"]: json.loads(l) for l in open("data/benchmark_main/answers2.jsonl")}
    clean = set(json.load(open("data/benchmark_main/clean_qids.json")))
    pred = {}
    for f in glob.glob("data/benchmark_main/raw/*.json"):
        try:
            for k, v in json.load(open(f)).items():
                pred[k] = v
        except Exception:
            pass
    n_main = 0
    for qid, ans in a.items():
        if qid not in clean:
            continue
        cands = pred.get(f"M-{qid}")
        if cands is None:
            continue
        rows.append((ans, cands[:3], "main"))
        n_main += 1
    n_ctrl = 0
    for d in ["data/benchmark_v3", "data/benchmark_v2_ctrl"]:
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        p = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/predictions2.jsonl")}
        for qid, ans in a.items():
            rows.append((ans, p[qid].get("candidates", [])[:3], os.path.basename(d)))
            n_ctrl += 1
    if n_main + n_ctrl != 194:
        sys.exit(f"score_main cohort drifted: {n_main} main + {n_ctrl} ctrl = {n_main+n_ctrl}, expected 194")
    return rows


def load_expansion(round_dir: str, label: str):
    """Validate-clean Opus deposits only. Refuses partials and Fable files."""
    qfile = os.path.join(round_dir, "questions2.jsonl")
    afile = os.path.join(round_dir, "answers2.jsonl")
    pfile = os.path.join(round_dir, "predictions2.jsonl")
    cfile = os.path.join(round_dir, "clean_qids.json")
    if not os.path.exists(qfile):
        sys.exit(f"{label}: no {qfile}")
    if not os.path.exists(afile):
        sys.exit(f"{label}: answer key withheld or missing at {afile}. "
                 f"Restore locally for a complete-round pooling pass; do not commit it "
                 f"while any arm is incomplete. Refusing to score.")
    if not os.path.exists(pfile):
        raw = sorted(glob.glob(os.path.join(round_dir, "raw", "*.json")))
        sys.exit(f"{label}: no {pfile}. collect_round.py writes it only at 100% deposit. "
                 f"{len(raw)} raw batch file(s) present — this is an unfinished round, "
                 f"not a result. Do not pass it to the paper.")
    qs = {json.loads(l)["qid"] for l in open(qfile)}
    ans = {json.loads(l)["qid"]: json.loads(l) for l in open(afile)}
    preds = {json.loads(l)["qid"]: json.loads(l) for l in open(pfile)}
    missing = sorted(qs - set(preds))
    extra = sorted(set(preds) - qs)
    if missing or extra or set(ans) != qs:
        sys.exit(f"{label}: INCOMPLETE or key/question mismatch "
                 f"(questions={len(qs)} answers={len(ans)} predictions={len(preds)} "
                 f"missing={missing[:8]} extra={extra[:8]}). Refusing to score a partial.")
    if not os.path.exists(cfile):
        sys.exit(f"{label}: no {cfile}. Run scripts/validate_benchmark.py before pooling "
                 f"so 13C-overread flags are set before any clean-subset total.")
    clean = set(json.load(open(cfile)))
    rows = []
    for qid in sorted(qs):
        if qid not in clean:
            continue
        rows.append((ans[qid], preds[qid].get("candidates", [])[:3], label))
    return rows, len(qs), len(clean)


def metrics(rows):
    out = []
    for ans, cands, src in rows:
        t = ik14(ans["smiles"])
        cs = cands[:3]
        top1 = bool(cs) and t is not None and ik14(cs[0]) == t
        rec = t is not None and any(ik14(s) == t for s in cs)
        af, best = fp(ans["smiles"]), 0.0
        for s in cs:
            pf = fp(s)
            if af and pf:
                best = max(best, DataStructs.TanimotoSimilarity(af, pf))
        out.append({"top1": top1, "rec": rec, "tani": best,
                    "diff": ans.get("difficulty", "?"), "src": src})
    return out


def boot(vals, f, n=2000):
    if not vals:
        return (0, 0, 0)
    pt = f(vals)
    bs = [f([vals[random.randrange(len(vals))] for _ in vals]) for _ in range(n)]
    bs.sort()
    return (pt, bs[int(0.025 * n)], bs[int(0.975 * n)])


def report(title, rows, with_ci=False):
    R = metrics(rows)
    n = len(R)
    t1 = sum(r["top1"] for r in R)
    rec = sum(r["rec"] for r in R)
    print(f"\n=== {title}  n={n}  (InChIKey-14 constitution) ===")
    print(f"  top-1  {t1}/{n} ({100*t1/n:.1f}%)" if n else "  empty")
    if n:
        print(f"  recall {rec}/{n} ({100*rec/n:.1f}%)")
    for diff in ("simple", "complex"):
        sub = [r for r in R if r["diff"] == diff]
        if not sub:
            continue
        t1d = sum(r["top1"] for r in sub)
        recd = sum(r["rec"] for r in sub)
        print(f"  {diff:8} n={len(sub):3}  top-1 {t1d}/{len(sub)} ({100*t1d/len(sub):.0f}%)  "
              f"recall {recd}/{len(sub)} ({100*recd/len(sub):.0f}%)")
    if with_ci and n:
        random.seed(0)
        def rate(rs, key):
            return 100 * sum(r[key] for r in rs) / len(rs)
        p, lo, hi = boot(R, lambda s: rate(s, "top1"))
        pr, rlo, rhi = boot(R, lambda s: rate(s, "rec"))
        print(f"  bootstrap 95% CI (seed 0, 2000 resamples; not a paper figure until signed off):")
        print(f"    top-1  {p:.1f}% [{lo:.0f}-{hi:.0f}]   recall {pr:.1f}% [{rlo:.0f}-{rhi:.0f}]")
    return n, t1, rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expand", action="store_true",
                    help="include data/benchmark_expand validate-clean Opus deposits")
    ap.add_argument("--expand-500", action="store_true", dest="expand_500",
                    help="include data/benchmark_expand_500 validate-clean Opus deposits")
    ap.add_argument("--ci", action="store_true",
                    help="print bootstrap 95% CIs (computed, not invented). Off by default.")
    a = ap.parse_args()

    print("score_pooled.py — does not rewrite score_main.py; does not read Fable arms.")
    print("Paper headline stays n=295 until --expand-500 is legal (100% deposited).")

    all_rows = load_main_194()
    report("locked n=194 (score_main cohort)", all_rows, with_ci=a.ci)

    if a.expand:
        rows, drawn, clean = load_expansion("data/benchmark_expand", "expand+106")
        report(f"expand +106  validate-clean {clean}/{drawn}", rows, with_ci=a.ci)
        all_rows = all_rows + rows
        report("pooled n=194 + expand-clean", all_rows, with_ci=a.ci)

    if a.expand_500:
        rows, drawn, clean = load_expansion("data/benchmark_expand_500", "expand_500")
        report(f"expand_500  validate-clean {clean}/{drawn}", rows, with_ci=a.ci)
        all_rows = all_rows + rows
        report("pooled headline (194 + included expansions, validate-clean)", all_rows, with_ci=a.ci)

    if not a.expand_500:
        print("\n--expand-500 not set. data/benchmark_expand_500 is not in the pool.")
        print("That is required until every drawn compound has an Opus response.")


if __name__ == "__main__":
    main()
