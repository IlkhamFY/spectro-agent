#!/usr/bin/env python3
"""Figure for the modality ablation. Reads the harness outputs
(data/modality/out_<cond>.json + key.json) and renders a grouped-bar chart of top-1
and recovered accuracy by leave-one-out condition. Produces NOTHING if results are
absent (so a placeholder figure can never ship). Run after modality_ablation.py score.

  python scripts/make_fig_modality.py            # render from data/modality/out_*.json
  python scripts/make_fig_modality.py <dir>      # render from an alternate results dir
"""
import json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

CONDS = [("full", "full\n(IR+¹H+¹³C)"), ("noIR", "−IR"), ("noH", "−¹H"), ("noC", "−¹³C")]
COL_T = ["#013a63", "#2a6f97", "#2a6f97", "#2a6f97"]   # full highlighted
COL_R = ["#6fb1cc", "#a9d6e5", "#a9d6e5", "#a9d6e5"]

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def main(d="data/modality"):
    key = json.load(open(f"{d}/key.json"))
    truth = {m: ik(v["true_smiles"]) for m, v in key.items()}
    outs = {c: (json.load(open(f"{d}/out_{c}.json")) if os.path.exists(f"{d}/out_{c}.json") else None)
            for c, _ in CONDS}
    if outs["full"] is None or all(outs[c] is None for c, _ in CONDS[1:]):
        print(f"no solver outputs in {d}/out_*.json yet — run the experiment first "
              f"(see docs/MODALITY_ABLATION.md). No figure written."); return
    ids = [m for m in truth if all(outs[c] is not None and m in outs[c] for c, _ in CONDS)]
    t1, rec = [], []
    for c, _ in CONDS:
        t1.append(np.mean([(lambda cs: bool(cs) and cs[0] == truth[m])
                           ([ik(s) for s in (outs[c].get(m) or [])[:1]]) for m in ids]) * 100)
        rec.append(np.mean([truth[m] in [ik(s) for s in (outs[c].get(m) or [])[:3]] for m in ids]) * 100)
    x = np.arange(len(CONDS)); w = 0.38
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.bar(x - w/2, t1, w, color=COL_T, label="top-1")
    ax.bar(x + w/2, rec, w, color=COL_R, label="recovered (top-3)")
    for i, (a, b) in enumerate(zip(t1, rec)):
        ax.text(i - w/2, a + 1, f"{a:.0f}", ha="center", fontsize=8)
        ax.text(i + w/2, b + 1, f"{b:.0f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([l for _, l in CONDS], fontsize=9)
    ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, max(rec + t1) * 1.25)
    ax.set_title(f"Modality ablation (leave-one-out, n={len(ids)})", fontsize=11)
    ax.legend(frameon=False, fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig("docs/figures/fig_modality.png", dpi=170, bbox_inches="tight")
    print(f"wrote docs/figures/fig_modality.png  (n={len(ids)}; full top-1 {t1[0]:.0f}%)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/modality")
