#!/usr/bin/env python3
"""Mechanism figure - forward-verification on a real benchmark regioisomer pair
(picolinamide / nicotinamide). The inverse task proposes both; forward-predicting each
candidate's 13C and matching to the observed spectrum selects the true one
(chamfer 0.42 vs 1.30 ppm). Clean single-font style; explainer lives in the caption.

Three stacked small-multiples on ONE shared ppm axis: observed (a), then each
candidate's predicted sticks over a ghost of the observed (b, c). A predicted stick
either lands on an observed guide (match) or drifts off it (mismatch)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.lines import Line2D
import numpy as np, io
from PIL import Image, ImageChops
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
    """Monochrome structure (no default red-O/blue-N, so colour stays reserved for the
    true/wrong coding), rendered then tightly cropped so the framed box hugs the atoms."""
    mol = Chem.MolFromSmiles(smi)
    d = rdMolDraw2D.MolDraw2DCairo(340, 200)
    o = d.drawOptions(); o.useBWAtomPalette(); o.bondLineWidth = 1; o.padding = 0.04
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    im = Image.open(io.BytesIO(d.GetDrawingText())).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()      # trim white margin
    if bbox:
        pad = 6
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    return np.asarray(im)

fig = plt.figure(figsize=(fs.COL2, 3.7))
gs = fig.add_gridspec(3, 1, hspace=0.42, left=0.27, right=0.98, top=0.88, bottom=0.13)
axes = [fig.add_subplot(gs[i]) for i in range(3)]
XMAX = 172

# faint vertical guides at each observed shift -> the stack reads as small-multiples
for ax in axes:
    for o in OBS:
        ax.axvline(o, color=fs.FAINT, lw=0.5, zorder=0)

# panel a - observed. Left column carries the formula, matching the b/c structure column.
axes[0].vlines(OBS, 0, 1, color=fs.INK, lw=1.5)
axes[0].set_title("observed spectrum", fontsize=7, color=fs.INK, loc="left")
axes[0].text(-0.26, 0.5, "unknown\nC$_{10}$H$_{14}$N$_2$O", transform=axes[0].transAxes,
             ha="center", va="center", fontsize=7, color=fs.INK)
fs.panel(axes[0], "a", x=-0.30, y=1.06)

# panels b, c - predicted (coloured) over a ghost of the observed (grey)
for ax, lett, (pred, smi, name, dist), col, mark in [
        (axes[1], "b", TRUE,  fs.GREEN,  "selected"),
        (axes[2], "c", FALSE, fs.VERMIL, "rejected")]:
    ax.vlines(OBS, 0, 1, color=fs.FAINT, lw=3.4)          # observed reference (ghost)
    ax.vlines(pred, 0, 1, color=col, lw=1.5)
    # name + chamfer in the title bar (above the sticks), so no label overlaps the data
    ax.set_title(f"{name}   ·   chamfer {dist:.2f} ppm, {mark}",
                 fontsize=7, color=col, loc="left")
    img = molimg(smi)
    zoom = 0.224 * 100 / img.shape[0]                     # normalise to a common height
    ax.add_artist(AnnotationBbox(OffsetImage(img, zoom=zoom), (-0.26, 0.5),
                  xycoords="axes fraction", frameon=True, box_alignment=(0.5, 0.5),
                  pad=0.25, bboxprops=dict(edgecolor=col, lw=0.9, boxstyle="round,pad=0.22")))
    fs.panel(ax, lett, x=-0.30, y=1.06)

for i, ax in enumerate(axes):
    ax.set_xlim(XMAX, 0); ax.set_ylim(0, 1.18); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)
    if i < 2:
        ax.set_xticklabels([])
axes[2].set_xlabel("$^{13}$C chemical shift (ppm)", labelpad=2)

fig.legend(handles=[Line2D([0], [0], color=fs.FAINT, lw=3.4, label="observed"),
                    Line2D([0], [0], color=fs.GREEN, lw=1.5, label="predicted, true"),
                    Line2D([0], [0], color=fs.VERMIL, lw=1.5, label="predicted, wrong")],
           loc="upper left", bbox_to_anchor=(0.30, 0.985), ncol=3, fontsize=6.5,
           handlelength=1.2, columnspacing=1.4, borderaxespad=0)

plt.savefig("docs/figures/fig_mechanism.png")
print("wrote docs/figures/fig_mechanism.png")
