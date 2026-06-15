#!/usr/bin/env python3
"""Graphical abstract / TOC graphic for the RSC Digital Discovery submission.
Compact horizontal flow on the real picolinamide/nicotinamide example:
observed spectrum -> LLM proposes regioisomers -> forward-predict 13C, match ->
pick the true one. Bottom banner carries the headline result. All drawn in one
data-coordinate axis (0-100) to avoid inset/figure-fraction collisions."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

NAVY="#013a63"; BLUE="#2a6f97"; GREEN="#2e8b57"; RED="#c1442e"; INK="#102a37"; SKY="#cfe6f2"
OBS=[28.9,51.0,121.9,126.0,137.9,147.9,151.0,163.6]

def molimg(smi, sz=(200,150)):
    return np.asarray(Draw.MolToImage(Chem.MolFromSmiles(smi), size=sz))

fig, ax = plt.subplots(figsize=(8.6, 3.7))
ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")

ax.text(50, 94, "Structure elucidation from real IR + NMR spectra with a frontier LLM",
        ha="center", va="center", fontsize=11.5, fontweight="bold", color=NAVY)

# ---- block 1: observed 13C stick spectrum (data coords) ----
ax.text(16.5, 80, "observed $^{13}$C  ·  C$_{10}$H$_{14}$N$_2$O", ha="center",
        fontsize=8.2, color=INK, fontweight="bold")
x0,x1,ppm_max = 4.0, 30.0, 175.0
def px(ppm): return x1 - (ppm/ppm_max)*(x1-x0)     # high ppm on the left
base, top = 46, 70
for p in OBS: ax.plot([px(p),px(p)],[base,top], color=INK, lw=1.4)
ax.plot([x0-0.5,x1+0.5],[base,base], color="#888", lw=0.8)
for tick in (150,100,50,0):
    ax.text(px(tick), 42, str(tick), ha="center", fontsize=6, color="#888")
ax.text(16.5, 33, "real literature spectrum\n(formula given, fully blind)",
        ha="center", fontsize=7.3, color="#5b6b75")

# ---- block 2: LLM proposes regioisomers ----
ax.text(50, 80, "LLM proposes regioisomers", ha="center", fontsize=8.4,
        color=NAVY, fontweight="bold")
for smi, y, col in [("CC(C)(C)NC(=O)c1ccccn1", 62, GREEN),
                    ("CC(C)(C)NC(=O)c1cccnc1", 37, RED)]:
    ax.add_artist(AnnotationBbox(OffsetImage(molimg(smi), zoom=0.27), (50, y),
                  frameon=True, box_alignment=(0.5,0.5),
                  bboxprops=dict(edgecolor=col, lw=1.2)))
ax.text(50, 20, "inverse task: ambiguous", ha="center", fontsize=7.3,
        color="#5b6b75", style="italic")

# ---- block 3: forward-verify result ----
ax.text(85, 80, "forward-predict $^{13}$C,\nmatch to observed", ha="center",
        fontsize=8.4, color=NAVY, fontweight="bold")
ax.text(85, 62, "0.42 ppm  ✓", ha="center", fontsize=10, color=GREEN, fontweight="bold")
ax.text(85, 37, "1.30 ppm  ✗", ha="center", fontsize=10, color=RED, fontweight="bold")
ax.text(85, 20, "verification picks the\ntrue isomer", ha="center", fontsize=7.3,
        color="#5b6b75", style="italic")

# arrows
for xa,xb in [(31.5,37.5),(64.5,71.0)]:
    ax.add_patch(FancyArrowPatch((xa,53),(xb,53), arrowstyle="-|>",
                 mutation_scale=13, lw=2, color=BLUE))

# ---- bottom headline banner ----
ax.add_patch(FancyBboxPatch((1,0.5), 98, 8.5, boxstyle="round,pad=0.3,rounding_size=2",
             fc=SKY, ec="none"))
ax.text(50, 4.7, "28% top-1 on blind, real spectra   ·   the wall is candidate recall "
        "(31%), not verification (84%)   ·   training-free",
        ha="center", va="center", fontsize=8.4, color=NAVY, fontweight="bold")

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
plt.savefig("docs/figures/graphical_abstract.png", dpi=200, bbox_inches="tight")
print("wrote docs/figures/graphical_abstract.png")
