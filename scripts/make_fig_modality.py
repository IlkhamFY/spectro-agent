#!/usr/bin/env python3
"""Modality ablation figure — leave-one-out top-1 / recovered, house style.

Produces NOTHING if results are absent (so a placeholder figure can never ship).

  python scripts/make_fig_modality.py            # from data/modality/out_*.json
  python scripts/make_fig_modality.py <dir>      # alternate results dir
"""
import json, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import figstyle as fs

CONDS = [("full", "full\n(IR+¹H+¹³C)"), ("noIR", "−IR"), ("noH", "−¹H"), ("noC", "−¹³C")]

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def main(d="data/modality"):
    key_path = f"{d}/key.json"
    if not os.path.exists(key_path):
        print(f"missing {key_path} — run the ablation first (see docs/MODALITY_ABLATION.md). "
              f"No figure written.")
        return
    key = json.load(open(key_path))
    truth = {m: ik(v["true_smiles"]) for m, v in key.items()}
    outs = {c: (json.load(open(f"{d}/out_{c}.json")) if os.path.exists(f"{d}/out_{c}.json") else None)
            for c, _ in CONDS}
    if any(outs[c] is None for c, _ in CONDS):
        missing = [c for c, _ in CONDS if outs[c] is None]
        print(f"missing solver outputs {missing} in {d}/out_*.json — run the full "
              f"leave-one-out set first (see docs/MODALITY_ABLATION.md). No figure written.")
        return
    ids = [m for m in truth if all(m in outs[c] for c, _ in CONDS)]
    if not ids:
        print(f"no compounds present in all four conditions in {d}/ — no figure written.")
        return
    t1, rec = [], []
    for c, _ in CONDS:
        t1.append(np.mean([(lambda cs: bool(cs) and cs[0] == truth[m])
                           ([ik(s) for s in (outs[c].get(m) or [])[:1]]) for m in ids]) * 100)
        rec.append(np.mean([truth[m] in [ik(s) for s in (outs[c].get(m) or [])[:3]] for m in ids]) * 100)

    fs.apply()
    x = np.arange(len(CONDS)); c = fs.GROUP_C; bw = fs.GROUP_W
    # Highlight the full condition; ablations share the secondary/primary pair.
    col_t = [fs.BLUE if i == 0 else fs.MUTED for i in range(len(CONDS))]
    col_r = [fs.SKY  if i == 0 else fs.GHOST for i in range(len(CONDS))]
    fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.ygrid(ax)
    b1 = ax.bar(x - c/2, t1, bw, color=col_t, label="exact top-1", zorder=3)
    b2 = ax.bar(x + c/2, rec, bw, color=col_r, label="recovered (top-3)", zorder=3)
    fs.barlabels(ax, b1, fmt="{:.0f}", dy=1.0)
    fs.barlabels(ax, b2, fmt="{:.0f}", dy=1.0)
    ax.set_xticks(x); ax.set_xticklabels([l for _, l in CONDS])
    ax.set_ylabel("accuracy (%)")
    ax.set_ylim(0, max(rec + t1) * 1.22)
    fs.legend(ax, loc="upper right")
    fs.finish()
    fs.save("docs/figures/fig_modality.png")
    print(f"wrote docs/figures/fig_modality.png  (n={len(ids)}; full top-1 {t1[0]:.0f}%)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/modality")
