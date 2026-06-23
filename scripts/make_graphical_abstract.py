#!/usr/bin/env python3
"""Graphical abstract / TOC graphic. Compact horizontal flow on the real
picolinamide/nicotinamide example: observed spectrum -> LLM proposes both regioisomers
-> forward-predict 13C and match -> the true one wins. Clean shared style, no banner."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import figstyle as fs

fs.apply()
OBS = [28.9, 51.0, 121.9, 126.0, 137.9, 147.9, 151.0, 163.6]

def molimg(smi, sz=(200, 150)):
    return np.asarray(Draw.MolToImage(Chem.MolFromSmiles(smi), size=sz))

fig, ax = plt.subplots(figsize=(7.2, 3.0))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

ax.text(50, 96, "Structure elucidation from real IR + NMR spectra with a frontier LLM",
        ha="center", va="top", fontsize=10, fontweight="bold", color=fs.INK)

# block 1 - observed 13C stick spectrum
ax.text(16, 80, "observed $^{13}$C,  C$_{10}$H$_{14}$N$_2$O", ha="center", fontsize=7.5,
        color=fs.INK, fontweight="bold")
x0, x1, pm = 4.0, 30.0, 175.0
px = lambda p: x1 - (p/pm)*(x1-x0)
for p in OBS: ax.plot([px(p), px(p)], [46, 70], color=fs.INK, lw=1.2)
ax.plot([x0-0.5, x1+0.5], [46, 46], color=fs.MUTED, lw=0.8)
for tk in (150, 100, 50, 0):
    ax.text(px(tk), 41, str(tk), ha="center", fontsize=5.5, color=fs.MUTED)
ax.text(16, 33, "real literature spectrum,\nformula given, fully blind", ha="center",
        fontsize=6.5, color=fs.MUTED)

# block 2 - two proposed regioisomers
ax.text(50, 80, "LLM proposes regioisomers", ha="center", fontsize=7.5,
        color=fs.INK, fontweight="bold")
for smi, y, col in [("CC(C)(C)NC(=O)c1ccccn1", 62, fs.GREEN),
                    ("CC(C)(C)NC(=O)c1cccnc1", 36, fs.VERMIL)]:
    ax.add_artist(AnnotationBbox(OffsetImage(molimg(smi), zoom=0.26), (50, y),
                  frameon=True, box_alignment=(0.5, 0.5), bboxprops=dict(edgecolor=col, lw=1.0)))
ax.text(50, 17, "indistinguishable to the inverse task", ha="center", fontsize=6.5, color=fs.MUTED)

# block 3 - forward-verify result
ax.text(85, 80, "forward-predict $^{13}$C,\nmatch to observed", ha="center",
        fontsize=7.5, color=fs.INK, fontweight="bold")
ax.text(85, 60, "0.42 ppm\nselected", ha="center", fontsize=8, color=fs.GREEN, fontweight="bold")
ax.text(85, 34, "1.30 ppm\nrejected", ha="center", fontsize=8, color=fs.VERMIL, fontweight="bold")

for xa, xb in [(31, 38), (64, 71)]:
    ax.add_patch(FancyArrowPatch((xa, 55), (xb, 55), arrowstyle="-|>",
                 mutation_scale=9, lw=1.0, color=fs.INK))

ax.text(50, 5, "28% top-1 on blind, real spectra — recall (31%), not verification (84%), "
        "is the wall", ha="center", va="center", fontsize=7.5, color=fs.INK)

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
plt.savefig("docs/figures/graphical_abstract.png")
print("wrote docs/figures/graphical_abstract.png")
