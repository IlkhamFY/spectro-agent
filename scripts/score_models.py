#!/usr/bin/env python3
"""Score the cross-model comparison on the fixed 24-compound subset and
regenerate Fig 5. Models: Claude Opus / Sonnet / Haiku / Fable 5 (all via the
Agent tool under one subscription; no API). InChIKey-connectivity scoring,
identical blind protocol per model."""
import json, glob, sys
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SUBSET = ['R01','R02','R04','R05','R06','R07','R08','R09','R10','R11','R12','R13',
          'R15','R16','R17','R18','R19','R20','R21','R22','R23','R24','R25','R26']

SRC = {                                   # model -> glob of raw {M-qid:[smiles]}
    "Opus":   "data/benchmark_main/raw/*.json",
    "Sonnet": "data/benchmark_main/sonnet/*.json",
    "Haiku":  "data/benchmark_main/haiku/*.json",
    "Fable":  "data/benchmark_main/fable/*.json",
}

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def load(glb):
    d = {}
    for f in glob.glob(glb):
        try:
            for k, v in json.load(open(f)).items():
                d.setdefault(k.replace("M-", ""), v)
        except Exception:
            pass
    return d

def main():
    ans = {json.loads(l)["qid"]: json.loads(l)
           for l in open("data/benchmark_main/answers2.jsonl")}
    gold = {q: ans[q]["inchikey"][:14] for q in SUBSET if q in ans}
    res = {}
    for model, glb in SRC.items():
        pred = load(glb)
        if not any(q in pred for q in SUBSET):
            continue                       # model not yet collected
        t1 = rec = n = 0
        for q in SUBSET:
            cs = (pred.get(q) or [])[:3]
            n += 1
            t1 += bool(cs) and ik(cs[0]) == gold[q]
            rec += any(ik(s) == gold[q] for s in cs)
        res[model] = [t1, rec]
        print(f"{model:7} n={n}  top-1 {t1}/{n} ({100*t1//n}%)  recovered {rec}/{n} ({100*rec//n}%)")
    json.dump({"n": len(SUBSET), "results": res},
              open("data/benchmark_main/model_comparison.json", "w"))

    if "--fig" in sys.argv and res:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        order = [m for m in ["Opus", "Sonnet", "Fable", "Haiku"] if m in res]
        n = len(SUBSET)
        t1 = [100 * res[m][0] / n for m in order]
        rc = [100 * res[m][1] / n for m in order]
        x = np.arange(len(order)); w = 0.38
        plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        ax.bar(x - w/2, t1, w, color="#2a6f97", label="exact top-1")
        ax.bar(x + w/2, rc, w, color="#89c2d9", label="recovered (top-3)")
        for i, v in enumerate(t1): ax.text(x[i]-w/2, v+1, f"{v:.0f}", ha="center", fontsize=8)
        ax.set_xticks(x); ax.set_xticklabels(order)
        ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 55)
        ax.legend(frameon=False, fontsize=9)
        ax.set_title(f"Cross-model comparison (n={n}, identical blind protocol)")
        plt.tight_layout(); plt.savefig("docs/figures/fig5_models.png", dpi=150)
        print("wrote docs/figures/fig5_models.png")

if __name__ == "__main__":
    main()
