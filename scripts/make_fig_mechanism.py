#!/usr/bin/env python3
"""Mechanism figure - forward-verification on a real benchmark regioisomer pair
(picolinamide / nicotinamide). The inverse task proposes both; forward-predicting each
candidate's 13C and matching to the observed spectrum selects the true one
(chamfer 0.42 vs 1.30 ppm). Clean single-font style; explainer lives in the caption."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.lines import Line2D
import numpy as np, io
from PIL import Image
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import figstyle as fs

fs.apply()
OBS  = [28.9, 51.0, 121.9, 126.0, 137.9, 147.9, 151.0, 163.6]
TRUE = ([28.7, 51.5, 122.0, 126.5, 137.0, 148.0, 150.0, 163.5], "CC(C)(C)NC(=O)c1ccccn1",
        "picolinamide (2-pyridyl)", 0.42)
FALSE= ([28.6, 51.6, 123.5, 130.5, 135.5, 148.5, 151.5, 164.5], "CC(C)(C)NC(=O)c1cccnc1",
        "nicotinamide (3-pyridyl)", 1.30)

def molimg(smi):
    """Monochrome structure — no default red-O/blue-N, so colour is reserved for the
    true/wrong (green/vermilion) coding of this figure."""
    mol = Chem.MolFromSmiles(smi)
    d = rdMolDraw2D.MolDraw2DCairo(320, 210)
    o = d.drawOptions(); o.useBWAtomPalette(); o.bondLineWidth = 1; o.padding = 0.06
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    return np.asarray(Image.open(io.BytesIO(d.GetDrawingText())))

fig = plt.figure(figsize=(6.6, 4.6))
gs = fig.add_gridspec(3, 1, hspace=0.55, left=0.30, right=0.97, top=0.90, bottom=0.12)
axes = [fig.add_subplot(gs[i]) for i in range(3)]
XMAX = 175

# faint vertical guides at each observed shift -> the stack reads as true small-multiples:
# a predicted stick either lands on a guide (matches) or drifts off it (mismatch)
for ax in axes:
    for o in OBS:
        ax.axvline(o, color="#ededed", lw=0.5, zorder=0)

# panel a - observed
axes[0].vlines(OBS, 0, 1, color=fs.INK, lw=1.6)
axes[0].set_title("observed $^{13}$C,  C$_{10}$H$_{14}$N$_2$O", fontsize=7, loc="left")
fs.panel(axes[0], "a", x=-0.30, y=1.04)

# panels b, c - predicted vs observed ghost
for ax, lett, (pred, smi, name, dist), col, mark in [
        (axes[1], "b", TRUE,  fs.GREEN,  "selected"),
        (axes[2], "c", FALSE, fs.VERMIL, "rejected")]:
    ax.vlines(OBS, 0, 1, color=fs.FAINT, lw=4.0)          # observed reference
    ax.vlines(pred, 0, 1, color=col, lw=1.6)
    # name + chamfer in the title bar (above the sticks), so no label overlaps the data
    ax.set_title(f"{name}   ·   chamfer {dist:.2f} ppm, {mark}",
                 fontsize=7, color=col, loc="left")
    ax.add_artist(AnnotationBbox(OffsetImage(molimg(smi), zoom=0.42), (-0.155, 0.5),
                  xycoords="axes fraction", frameon=True, box_alignment=(0.5, 0.5),
                  bboxprops=dict(edgecolor=col, lw=1.2)))
    fs.panel(ax, lett, x=-0.30, y=1.04)

for i, ax in enumerate(axes):
    ax.set_xlim(XMAX, 0); ax.set_ylim(0, 1.2); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)
    if i < 2:
        ax.set_xticklabels([])
axes[2].set_xlabel("$^{13}$C chemical shift (ppm)")

fig.legend(handles=[Line2D([0], [0], color=fs.FAINT, lw=4, label="observed"),
                    Line2D([0], [0], color=fs.GREEN, lw=1.6, label="predicted, true"),
                    Line2D([0], [0], color=fs.VERMIL, lw=1.6, label="predicted, wrong")],
           loc="upper left", bbox_to_anchor=(0.30, 1.0), ncol=3, fontsize=6.5,
           handlelength=1.2, columnspacing=1.2)

plt.savefig("docs/figures/fig_mechanism.png")
print("wrote docs/figures/fig_mechanism.png")
