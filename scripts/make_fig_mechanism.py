#!/usr/bin/env python3
"""Mechanism figure - forward-verification on a real benchmark regioisomer pair
(picolinamide / nicotinamide). The inverse task proposes both; forward-predicting each
candidate's 13C and matching to the observed spectrum selects the true one
(chamfer 0.42 vs 1.30 ppm). Clean single-font style; explainer lives in the caption.

Three stacked small-multiples on ONE shared ppm axis: observed (a), then each
candidate's predicted sticks over a ghost of the observed (b, c). A predicted stick
either lands on an observed guide (match) or drifts off it (mismatch).

Structures are drawn ACS-bold (thick bonds, clear heteroatoms) with the regioisomer
nitrogen tinted in the panel colour so the 2- vs 3-pyridyl distinction reads at a glance.
"""
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

INSET_W_IN  = 1.48    # printed width of the structure inset
ATOM_LABEL_PT = 8.5   # printed size of heteroatom glyphs
CANVAS = (900, 520)
BOND_LW = 4.0         # with scaleBondWidth → ACS-bold at print size


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _pyridyl_n_idx(mol):
    """Ring nitrogen that distinguishes the 2- vs 3-pyridyl regioisomer."""
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7 and atom.IsInRing():
            return atom.GetIdx()
    return None


def _draw(smi, font_px, accent=None):
    mol = Chem.MolFromSmiles(smi)
    d = rdMolDraw2D.MolDraw2DCairo(*CANVAS)
    o = d.drawOptions()
    o.useBWAtomPalette()
    o.bondLineWidth = BOND_LW
    o.scaleBondWidth = True
    o.padding = 0.08
    o.fixedFontSize = int(max(1, font_px))
    o.additionalAtomLabelPadding = 0.12
    o.multipleBondOffset = 0.20

    highlight, colors = [], {}
    if accent is not None:
        n_idx = _pyridyl_n_idx(mol)
        if n_idx is not None:
            highlight = [n_idx]
            # Soft wash of the panel colour on the distinguishing N.
            r, g, b = _hex_rgb(accent)
            colors[n_idx] = (0.55 * r + 0.45, 0.55 * g + 0.45, 0.55 * b + 0.45)

    rdMolDraw2D.PrepareAndDrawMolecule(
        d, mol, highlightAtoms=highlight, highlightAtomColors=colors,
    )
    d.FinishDrawing()
    im = Image.open(io.BytesIO(d.GetDrawingText())).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 18
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    return np.asarray(im)


def molimg(smi, accent=None):
    """Bold monochrome structure; optional accent tint on the regioisomer N."""
    font = ATOM_LABEL_PT * CANVAS[0] / (INSET_W_IN * 72)
    for _ in range(2):
        arr = _draw(smi, round(font), accent=accent)
        zoom = INSET_W_IN * 72 / arr.shape[1]
        font = ATOM_LABEL_PT / zoom
    arr = _draw(smi, round(font), accent=accent)
    return arr, INSET_W_IN * 72 / arr.shape[1]


fig = plt.figure(figsize=(fs.COL2, 3.85))
gs = fig.add_gridspec(3, 1, hspace=0.34, left=0.38, right=0.985, top=0.88, bottom=0.115)
axes = [fig.add_subplot(gs[i]) for i in range(3)]
XMAX = 172
PRED_LW = 2.15

for ax in axes:
    for o in OBS:
        ax.axvline(o, color=fs.FAINT, lw=0.40, zorder=0)

axes[0].vlines(OBS, 0, 1, color=fs.INK, lw=PRED_LW, zorder=3)
axes[0].set_title("observed spectrum", fontsize=fs.FS_BODY, color=fs.INK, loc="left")
# Formula card — same left column language as the structure frames below.
axes[0].text(
    -0.255, 0.5, "unknown\nC\u2081\u2080H\u2081\u2084N\u2082O",
    transform=axes[0].transAxes, ha="center", va="center",
    fontsize=fs.FS_EMPH, fontweight="bold", color=fs.INK, linespacing=1.35,
    bbox=dict(boxstyle="square,pad=0.45", facecolor="white",
              edgecolor=fs.INK, linewidth=1.35),
)
fs.panel(axes[0], "a", x=-0.08, y=1.08)

for ax, lett, (pred, smi, name, dist), col, mark in [
        (axes[1], "b", TRUE,  fs.GREEN,  "selected"),
        (axes[2], "c", FALSE, fs.VERMIL, "rejected")]:
    ax.vlines(OBS, 0, 1, color=fs.GHOST, lw=3.6, zorder=1)
    ax.vlines(pred, 0, 1, color=col, lw=PRED_LW, zorder=3)
    ax.set_title(f"{name} ({mark})", fontsize=fs.FS_BODY, color=col, loc="left")
    ax.text(0.995, 0.90, f"{dist:.2f} ppm", transform=ax.transAxes,
            ha="right", va="top", fontsize=fs.FS_BODY, fontweight="bold",
            color=col, clip_on=False)
    img, zoom = molimg(smi, accent=col)
    ax.add_artist(AnnotationBbox(
        OffsetImage(img, zoom=zoom), (-0.255, 0.5),
        xycoords="axes fraction", frameon=True, box_alignment=(0.5, 0.5),
        pad=0.22, bboxprops=dict(edgecolor=col, lw=1.85,
                                 facecolor="white", boxstyle="square,pad=0.22"),
    ))
    fs.panel(ax, lett, x=-0.08, y=1.08)

for i, ax in enumerate(axes):
    ax.set_xlim(XMAX, 0); ax.set_ylim(0, 1.18); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)
    if i < 2:
        ax.set_xticklabels([])
axes[2].set_xlabel("\u00b9\u00b3C chemical shift (ppm)", labelpad=2)

fig.legend(handles=[Line2D([0], [0], color=fs.INK, lw=PRED_LW, label="observed"),
                    Line2D([0], [0], color=fs.GHOST, lw=3.6, label="observed, ghosted"),
                    Line2D([0], [0], color=fs.GREEN, lw=PRED_LW, label="predicted, true"),
                    Line2D([0], [0], color=fs.VERMIL, lw=PRED_LW, label="predicted, wrong")],
           loc="upper left", bbox_to_anchor=(0.36, 0.995), ncol=4, fontsize=fs.FS_BODY,
           handlelength=1.2, columnspacing=1.1, handletextpad=0.4, borderaxespad=0)

fs.save("docs/figures/fig_mechanism.png")
print("wrote docs/figures/fig_mechanism.png")
