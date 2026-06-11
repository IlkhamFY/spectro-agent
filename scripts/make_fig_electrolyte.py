#!/usr/bin/env python3
"""Fig 6: structure-elucidation accuracy by battery-electrolyte chemical class."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json, glob
from collections import defaultdict
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

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

by = defaultdict(lambda: [0, 0, 0])     # class -> [n, top1, recovered]
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

# pretty class labels
NICE = {"carbonate": "carbonate", "sulfonyl": "sulfonyl/\nsulfonate",
        "nitrile": "nitrile", "fluorinated": "sp3-fluorinated",
        "phosphoryl": "phosphoryl", "glyme": "glyme/\noligoether"}
order = sorted(by, key=lambda c: -(100 * by[c][1] / by[c][0]) if by[c][0] else 0)
labels = [NICE.get(c, c) for c in order]
top1 = [100 * by[c][1] / by[c][0] if by[c][0] else 0 for c in order]
recov = [100 * by[c][2] / by[c][0] if by[c][0] else 0 for c in order]
ns = [by[c][0] for c in order]

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})
fig, ax = plt.subplots(figsize=(6.2, 3.8))
y = np.arange(len(order)); h = 0.38
ax.barh(y + h / 2, recov, h, color="#89c2d9", label="recovered (top-3)")
ax.barh(y - h / 2, top1, h, color="#2a6f97", label="exact top-1")
for i, (n, p) in enumerate(zip(ns, top1)):
    ax.text(1, y[i] - h / 2, f" n={n}", va="center", fontsize=8, color="white")
ax.set_yticks(y); ax.set_yticklabels(labels)
ax.set_xlabel("accuracy (%)"); ax.set_xlim(0, 80)
ax.invert_yaxis()
ax.legend(frameon=False, fontsize=9, loc="lower right")
ax.set_title(f"Elucidation by electrolyte class (n={N})")
plt.tight_layout(); plt.savefig("docs/figures/fig6_electrolyte.png", dpi=150)
plt.close()
ov1 = 100 * t1 // max(N, 1); ovr = 100 * rec // max(N, 1)
print(f"wrote docs/figures/fig6_electrolyte.png  (n={N}, top-1 {ov1}%, recovered {ovr}%)")
