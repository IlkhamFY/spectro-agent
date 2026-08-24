#!/usr/bin/env python3
"""Fig 6: structure-elucidation accuracy by battery-electrolyte chemical class."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json, glob
from collections import defaultdict
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import figstyle as fs
fs.apply()

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

a = {json.loads(l)["qid"]: json.loads(l)
     for l in open("data/benchmark_electrolyte/answers2.jsonl")}
pred = {}
for f in glob.glob("data/benchmark_electrolyte/raw/*.json"):
    try:
        for k, v in json.load(open(f)).items():
            pred[k.replace("E-", "")] = v
    except Exception:
        pass

by = defaultdict(lambda: [0, 0, 0])
N = t1 = rec = 0
for qid, ans in a.items():
    cands = pred.get(qid)
    if cands is None:
        continue
    t = ans["inchikey"][:14]; cs = cands[:3]; cl = ans["eclass"]
    a1 = bool(cs) and ik(cs[0]) == t
    ar = any(ik(s) == t for s in cs)
    N += 1; t1 += a1; rec += ar
    by[cl][0] += 1; by[cl][1] += a1; by[cl][2] += ar

NICE = {"carbonate": "carbonate", "sulfonyl": "sulfonyl",
        "nitrile": "nitrile", "fluorinated": "sp³-C–F",
        "phosphoryl": "phosphoryl", "glyme": "glyme"}
order = sorted(by, key=lambda c: (100 * by[c][1] / by[c][0]) if by[c][0] else 0)
labels = [NICE.get(c, c) for c in order]
top1 = [100 * by[c][1] / by[c][0] if by[c][0] else 0 for c in order]
recov = [100 * by[c][2] / by[c][0] if by[c][0] else 0 for c in order]
ns = [by[c][0] for c in order]

fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.xgrid(ax)
y = np.arange(len(order)); c = fs.GROUP_C; bh = fs.GROUP_W
ax.barh(y + c/2, recov, bh, color=fs.SKY, label="recovered (top-3)", zorder=3)
ax.barh(y - c/2, top1, bh, color=fs.BLUE, label="exact top-1", zorder=3)
ax.set_yticks(y); ax.set_yticklabels([f"{lab}  (n={n})" for lab, n in zip(labels, ns)])
ax.set_xlabel("accuracy (%)"); ax.set_xlim(0, 60)
fs.legend(ax, loc="lower right")
plt.tight_layout(pad=0.35); fs.save("docs/figures/fig6_electrolyte.png")
plt.close()
ov1 = round(100*t1/max(N, 1)); ovr = round(100*rec/max(N, 1))
print(f"wrote docs/figures/fig6_electrolyte.png  (n={N}, top-1 {ov1}%, recovered {ovr}%)")
