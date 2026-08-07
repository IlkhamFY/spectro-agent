#!/usr/bin/env python3
"""
Leakage check for the two *trained* verifiers of §5.4 (the HOSE lookup and the GNN),
both of which learn from nmrshiftdb2. The question a reviewer must be able to settle
mechanically: does any candidate structure they re-rank also appear in their training
database, and if so does it touch a reported number?

Reports, over the candidate sets scored in Table 8:
  - EXACT overlap: InChIKey-14 against the ENTIRE nmrshiftdb2 dump (not just the 13C
    subset), and for each hit whether it is the true structure and whether its compound
    is recall-positive (i.e. whether it enters the conditional analysis at all)
  - ANALOG overlap: Morgan(2, 2048) Tanimoto to the nearest training molecule, which
    exact matching cannot catch -- a near-duplicate would leak almost as well

  python scripts/verifier_leakage.py          # 60-compound arm
  python scripts/verifier_leakage.py --all    # whole benchmark
"""
import json, sys
from collections import defaultdict
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SDF = "data/nmrshiftdb/nmrshiftdb2.sd"
ARMS = ["data/fverify"] + (["data/fverify_main"] if "--all" in sys.argv else [])


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None


def main():
    rows, comps = [], defaultdict(list)
    for arm in ARMS:
        for l in open(f"{arm}/candidates.jsonl"):
            r = json.loads(l); r["arm"] = arm
            rows.append(r); comps[(arm, r["qid"])].append(r)
    by_key = defaultdict(list)
    for r in rows:
        k = ik14(r["smiles"])
        if k: by_key[k].append(r)
    print(f"arms: {', '.join(ARMS)}")
    print(f"candidates: {len(rows)}   distinct InChIKey-14: {len(by_key)}")

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    cand_fps = {}
    for k, rs in by_key.items():
        m = Chem.MolFromSmiles(rs[0]["smiles"])
        if m is not None:
            cand_fps[k] = gen.GetFingerprint(m)
    best = {k: 0.0 for k in cand_fps}

    train = set()
    n = 0
    for m in Chem.SDMolSupplier(SDF, removeHs=True, sanitize=True):
        if m is None: continue
        n += 1
        try: train.add(Chem.MolToInchiKey(m)[:14])
        except Exception: pass
        try: tfp = gen.GetFingerprint(m)
        except Exception: continue
        for k, fp in cand_fps.items():
            s = DataStructs.TanimotoSimilarity(fp, tfp)
            if s > best[k]: best[k] = s
    print(f"nmrshiftdb2: {n} molecules parsed, {len(train)} distinct InChIKey-14")

    overlap = sorted(set(by_key) & train)
    print(f"\nOVERLAP: {len(overlap)}/{len(by_key)} candidate structures "
          f"({100*len(overlap)/len(by_key):.1f}%)")
    consequential = 0
    for k in overlap:
        for r in by_key[k]:
            rp = any(c["is_true"] for c in comps[(r["arm"], r["qid"])])
            flag = "IS TRUE STRUCTURE" if r["is_true"] else "distractor"
            note = "recall-positive -> ENTERS the conditional analysis" if rp else \
                   "recall-negative -> excluded from the conditional analysis"
            if rp: consequential += 1
            print(f"  {k}  {r['qid']:>8}  {flag:<18}  {note}")
            print(f"      {r['smiles']}")
    print(f"\n=> {consequential} overlapping candidate(s) sit on a recall-positive "
          f"compound; only those could affect a Table 8 number.")
    true_leak = sum(1 for k in overlap for r in by_key[k] if r["is_true"])
    print(f"=> {true_leak} benchmark ANSWER(s) appear in nmrshiftdb2.")

    # analog overlap: how close is the NEAREST training molecule, structurally?
    vals = sorted(best.values())
    q = lambda f: vals[min(len(vals) - 1, int(f * len(vals)))]
    print(f"\nANALOG OVERLAP — Morgan(2,2048) Tanimoto to nearest training molecule "
          f"(n={len(vals)} candidates)")
    print(f"  median {q(0.50):.2f}   90th pct {q(0.90):.2f}   max {max(vals):.2f}")
    for t in (1.00, 0.95, 0.90, 0.80):
        print(f"  >= {t:.2f}: {sum(1 for v in vals if v >= t)}")
    truth = [best[k] for k in best if any(r["is_true"] for r in by_key[k])]
    if truth:
        truth.sort()
        print(f"  true structures only (n={len(truth)}): median "
              f"{truth[len(truth)//2]:.2f}, max {max(truth):.2f}")


if __name__ == "__main__":
    main()
