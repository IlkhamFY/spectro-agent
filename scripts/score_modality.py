#!/usr/bin/env python3
"""Score the modality-ablation pilot. Reads the four solver outputs
(/tmp/modality/out_{full,noIR,noH,noC}.json, each {id:[smiles,...]}) against the
held-out key (/tmp/modality/key.json) by InChIKey-connectivity match, and reports
top-1 / recovered(top-3) per leave-one-out condition -> marginal value of each modality."""
import json, os
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

key = json.load(open("/tmp/modality/key.json"))
truth = {k: ik(v["true_smiles"]) for k, v in key.items()}
CONDS = [("full", "full (IR+1H+13C)"), ("noIR", "-IR"),
         ("noH", "-1H"), ("noC", "-13C")]
print(f"{'condition':<18}{'n':>4}{'top-1':>9}{'recovered':>11}")
base = None
for cond, label in CONDS:
    path = f"/tmp/modality/out_{cond}.json"
    if not os.path.exists(path):
        print(f"{label:<18}  (missing {path})"); continue
    preds = json.load(open(path))
    n = top1 = rec = 0
    for mid, t in truth.items():
        cs = [ik(s) for s in (preds.get(mid) or [])[:3]]
        if not cs:
            n += 1; continue
        n += 1
        top1 += (cs[0] == t)
        rec += (t in cs)
    print(f"{label:<18}{n:>4}{top1/n:>8.1%}{rec/n:>11.1%}")
    if cond == "full":
        base = (top1 / n, rec / n)
if base:
    print(f"\nfull-modality baseline: top-1 {base[0]:.1%}, recovered {base[1]:.1%}")
    print("marginal value of a modality = (full) - (leave-one-out condition).")
