#!/usr/bin/env python3
"""Figure 2 — forward-verification mechanism, on a REAL worked example from the
benchmark (R25): the picolinamide / nicotinamide regioisomer pair. The inverse
direction cannot separate them; forward-predicting each candidate's 13C and matching
to the observed spectrum does (chamfer 0.42 vs 1.30 ppm)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

NAVY="#013a63"; BLUE="#2a6f97"; GREEN="#2e8b57"; RED="#c1442e"; GREY="#9aa7 af".replace(" ","")
INK="#102a37"

OBS  = [28.9, 51.0, 121.9, 126.0, 137.9, 147.9, 151.0, 163.6]
TRUE = ([28.7, 51.5, 122.0, 126.5, 137.0, 148.0, 150.0, 163.5], "CC(C)(C)NC(=O)c1ccccn1",
        "picolinamide (2-pyridyl)", 0.42)
FALSE= ([28.6, 51.6, 123.5, 130.5, 135.5, 148.5, 151.5, 164.5], "CC(C)(C)NC(=O)c1cccnc1",
        "nicotinamide (3-pyridyl)", 1.30)

def molimg(smi):
    m = Chem.MolFromSmiles(smi)
    return np.asarray(Draw.MolToImage(m, size=(220, 150)))

fig = plt.figure(figsize=(10.4, 6.6))
gs = fig.add_gridspec(3, 1, hspace=0.42, left=0.30, right=0.97, top=0.87, bottom=0.20)
axes = [fig.add_subplot(gs[i]) for i in range(3)]
XMAX = 175

def sticks(ax, peaks, color, lw=2.0, label=None):
    ax.vlines(peaks, 0, 1, color=color, lw=lw, label=label)

# --- panel 0: observed reference ---
ax = axes[0]
sticks(ax, OBS, INK, lw=2.4)
ax.set_title("Observed $^{13}$C spectrum  —  benchmark compound, formula C$_{10}$H$_{14}$N$_2$O",
             fontsize=11, color=NAVY, fontweight="bold", loc="left", pad=6)
ax.text(0.5, 0.78, "the inverse task proposes BOTH regioisomers below;\n"
        "their $^1$H/$^{13}$C shifts are too similar to rank by inspection",
        transform=ax.transAxes, ha="center", fontsize=8.8, color=INK, style="italic")

# --- panels 1,2: candidates with observed ghost ---
for ax, (pred, smi, name, dist), col, verdict in [
        (axes[1], TRUE,  GREEN, "SELECTED  ✓"),
        (axes[2], FALSE, RED,   "rejected")]:
    ax.vlines(OBS, 0, 1, color="#c9d4db", lw=4.5)              # observed ghost
    sticks(ax, pred, col, lw=2.0)
    ax.set_title(f"forward-predict $^{{13}}$C of  {name}", fontsize=10,
                 color=col, fontweight="bold", loc="left", pad=4)
    ax.text(0.992, 0.80, f"chamfer to observed = {dist:.2f} ppm\n{verdict}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9.4,
            color=col, fontweight="bold")
    ab = AnnotationBbox(OffsetImage(molimg(smi), zoom=0.62), (-0.165, 0.5),
                        xycoords="axes fraction", frameon=True, box_alignment=(0.5, 0.5),
                        bboxprops=dict(edgecolor=col, lw=1.4))
    ax.add_artist(ab)

for i, ax in enumerate(axes):
    ax.set_xlim(XMAX, 0); ax.set_ylim(0, 1.25)
    ax.set_yticks([]);
    ax.spines[["left","right","top"]].set_visible(False)
    if i < 2:
        ax.set_xticklabels([])
    ax.tick_params(axis="x", labelsize=8)
axes[2].set_xlabel("$^{13}$C chemical shift (ppm)", fontsize=10, labelpad=4)

# legend for ghost vs predicted
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([0],[0],color="#c9d4db",lw=4.5,label="observed (reference)"),
                    Line2D([0],[0],color=GREEN,lw=2,label="predicted, true isomer"),
                    Line2D([0],[0],color=RED,lw=2,label="predicted, wrong isomer")],
           loc="upper left", bbox_to_anchor=(0.30,0.99), ncol=3, frameon=False, fontsize=8.6)

fig.text(0.30, 0.045,
         "Figure 2.  Forward-verification breaks a regiochemistry tie the inverse task cannot — "
         "the LLM analog of NMR-crystallography.",
         fontsize=8.8, color="#5b6b75")

plt.savefig("docs/figures/fig_mechanism.png", dpi=170, bbox_inches="tight")
print("wrote docs/figures/fig_mechanism.png")
