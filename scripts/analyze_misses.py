#!/usr/bin/env python3
"""
What does a top-1 miss actually look like?

§4 originally asserted that the model fails "predominantly on regiochemistry — which
position a substituent occupies". That is a chemical claim about 139 specific failures,
and the expert-chemist audit (§7) was designed partly to test it. Most of it is
mechanically decidable, so it should be measured rather than asserted, leaving the panel
a narrower question.

Three nested descriptions of a miss, from weakest to strongest:
  * constitutional isomer  — exactly the right atoms, wrong connectivity
  * same Murcko scaffold   — the ring/linker skeleton is right, so the error is
                             genuinely positional: a substituent in the wrong place
  * high Tanimoto          — near-identical structures

  python scripts/analyze_misses.py
"""
import json, glob
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, DataStructs, rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

GEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
ROUNDS = [("data/benchmark_main", "data/benchmark_main/clean_qids.json", "M-"),
          ("data/benchmark_v3", None, None),
          ("data/benchmark_v2_ctrl", None, None)]


def ik14(m):
    return Chem.MolToInchiKey(m)[:14] if m else None


def scaffold(m):
    try:
        return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception:
        return None


def collect():
    misses, unparseable, hits = [], 0, 0
    for d, cleanf, prefix in ROUNDS:
        keep = set(json.load(open(cleanf))) if cleanf else None
        ans = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        pred = {}
        if prefix:
            for f in glob.glob(f"{d}/raw/*.json"):
                pred.update(json.load(open(f)))
            pred = {k[len(prefix):]: v for k, v in pred.items()}
        else:
            for l in open(f"{d}/predictions2.jsonl"):
                r = json.loads(l); pred[r["qid"]] = r.get("candidates", [])
        for q, a in ans.items():
            if keep is not None and q not in keep:
                continue
            top = pred.get(q, [])[:1]
            truth = Chem.MolFromSmiles(a.get("smiles") or "")
            if truth is None or not top:
                continue
            cand = Chem.MolFromSmiles(top[0] or "")
            if cand is None:
                unparseable += 1
                continue
            if ik14(cand) == ik14(truth):
                hits += 1
                continue
            misses.append({
                "same_formula": (rdMolDescriptors.CalcMolFormula(cand)
                                 == rdMolDescriptors.CalcMolFormula(truth)),
                "same_scaffold": scaffold(cand) is not None
                                 and scaffold(cand) == scaffold(truth),
                "tanimoto": DataStructs.TanimotoSimilarity(
                    GEN.GetFingerprint(cand), GEN.GetFingerprint(truth)),
            })
    return misses, unparseable, hits


def main():
    misses, unparseable, hits = collect()
    n = len(misses)
    total = n + unparseable
    iso = [m for m in misses if m["same_formula"]]
    pos = [m for m in iso if m["same_scaffold"]]
    print(f"top-1 correct: {hits}    top-1 misses: {total} "
          f"({unparseable} unparseable, {n} analysable)\n")
    row = lambda k, lab: print(f"  {lab:<52}{k:>4}/{n}  {100*k/n:5.1f}%")
    row(len(iso), "constitutional isomer (right formula, wrong bonds)")
    row(len(pos), "…and the same Murcko scaffold → positional error")
    for t in (0.85, 0.70, 0.55):
        row(sum(1 for m in iso if m["tanimoto"] >= t), f"…and Tanimoto ≥ {t:.2f}")
    row(n - len(iso), "wrong molecular formula (a different compound)")
    if iso:
        ts = sorted(m["tanimoto"] for m in iso)
        print(f"\n  Tanimoto(miss, truth) over the isomer misses: "
              f"median {ts[len(ts)//2]:.2f}  min {ts[0]:.2f}  max {ts[-1]:.2f}")
    print("\nReading: the composition is usually right and the connectivity is not.\n"
          "'Which position a substituent occupies' describes the scaffold-preserving\n"
          "row only — a minority of misses, not the predominant failure mode.")


if __name__ == "__main__":
    main()
