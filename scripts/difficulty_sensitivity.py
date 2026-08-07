#!/usr/bin/env python3
"""
Is the simple/complex split's heavy-atom threshold load-bearing?

§3 stratifies a compound as *simple* iff it has <=2 rings, no fused/spiro/bridgehead
system, and <=22 heavy atoms. A reviewer is entitled to ask whether 22 was tuned to
produce the 48%/8% separation. This sweeps the threshold and reports the separation at
each value; if the gap is stable, the choice is not doing the work.

  python scripts/difficulty_sensitivity.py
"""
import json, glob
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

# (dir, clean-qid file or None, raw-prediction key prefix or None -> use predictions2)
ROUNDS = [("data/benchmark_main", "data/benchmark_main/clean_qids.json", "M-"),
          ("data/benchmark_v3", None, None),
          ("data/benchmark_v2_ctrl", None, None)]
THRESHOLDS = (18, 20, 22, 24, 26)


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None


def difficulty(mol, T):
    """scripts/benchmark_v2.py's rule with the heavy-atom threshold parameterised.
    The upper guard sits at T+2, mirroring the released 22/24 pair."""
    ri = mol.GetRingInfo()
    nr, hac = ri.NumRings(), mol.GetNumHeavyAtoms()
    fused = any(ri.NumAtomRings(a.GetIdx()) >= 2 for a in mol.GetAtoms())
    spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol) > 0
    bridge = rdMolDescriptors.CalcNumBridgeheadAtoms(mol) > 0
    if spiro or bridge or nr >= 3 or fused or hac > T + 2:
        return "complex"
    return "simple" if (nr <= 2 and hac <= T) else "complex"


def load():
    rows = []
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
            m = Chem.MolFromSmiles(a.get("smiles") or "")
            if m is None:
                continue
            cands = pred.get(q, [])[:3]
            t = a["inchikey"][:14]
            rows.append((m, bool(cands) and ik14(cands[0]) == t))
    return rows


def main():
    rows = load()
    print(f"compounds: {len(rows)}\n")
    print(f"{'threshold':>10} {'n simple':>9} {'simple top-1':>13} "
          f"{'n complex':>10} {'complex top-1':>14} {'gap (pts)':>10}")
    for T in THRESHOLDS:
        s = [c for m, c in rows if difficulty(m, T) == "simple"]
        x = [c for m, c in rows if difficulty(m, T) == "complex"]
        ps = 100 * sum(s) / len(s) if s else 0.0
        px = 100 * sum(x) / len(x) if x else 0.0
        star = "   <- released" if T == 22 else ""
        print(f"{T:>10} {len(s):>9} {ps:>12.1f}% {len(x):>10} {px:>13.1f}% "
              f"{ps - px:>9.1f}{star}")
    print("\nA gap that barely moves across the sweep means the threshold is not "
          "doing the work;\nthe separation is a property of the compounds, not of "
          "where the line was drawn.")


if __name__ == "__main__":
    main()
