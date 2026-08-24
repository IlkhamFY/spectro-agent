#!/usr/bin/env python3
"""RSC table-of-contents graphic — exactly 8 cm × 4 cm, nothing below 7 pt.

One clean composition (Nature desk, not a dashboard):
  title claim → observed ¹³C sticks → two candidates → one-line FOM.

Structures use ACS-bold bonds with the regioisomer nitrogen tinted so the
2- vs 3-pyridyl distinction reads at thumbnail size. No card frames — colour
lives on the isomer N, a short rule, and the verdict type.
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Rectangle
from PIL import Image, ImageChops
from rdkit import Chem, RDLogger
from rdkit.Chem.Draw import rdMolDraw2D

import figstyle as fs

RDLogger.DisableLog("rdApp.*")
fs.apply()

# ---- hard constraints ---------------------------------------------------------
CM = 1 / 2.54
W_IN, H_IN = 8 * CM, 4 * CM
MIN_PT = 7
# Printed width chosen so molecule height (~0.58 in) clears the spectrum band.
STRUCT_W_IN = 1.20
ATOM_PT = 8.0               # heteroatoms stay ≥ 7 pt when printed
CANVAS = (1100, 620)
BOND_LW = 4.5               # with scaleBondWidth → bold at 8×4 cm thumbnail
STICK_LW = 3.20             # TOC sticks must dominate the upper band
PPM_MAX = 175.0

# ---- chemistry ----------------------------------------------------------------
OBS = [28.9, 51.0, 121.9, 126.0, 137.9, 147.9, 151.0, 163.6]
TRUE_SMI = "CC(C)(C)NC(=O)c1ccccn1"   # picolinamide (2-pyridyl)
FALSE_SMI = "CC(C)(C)NC(=O)c1cccnc1"  # nicotinamide (3-pyridyl)

CANDIDATES = (
    (TRUE_SMI, fs.GREEN, "0.42 ppm · selected"),
    (FALSE_SMI, fs.VERMIL, "1.30 ppm · rejected"),
)


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _pyridyl_n_idx(mol):
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7 and atom.IsInRing():
            return atom.GetIdx()
    return None


def _draw_mol(smi, font_px, accent=None):
    mol = Chem.MolFromSmiles(smi)
    drawer = rdMolDraw2D.MolDraw2DCairo(*CANVAS)
    opts = drawer.drawOptions()
    opts.useBWAtomPalette()
    opts.bondLineWidth = BOND_LW
    opts.scaleBondWidth = True
    opts.padding = 0.04
    opts.fixedFontSize = int(max(1, font_px))
    opts.additionalAtomLabelPadding = 0.10
    opts.multipleBondOffset = 0.22
    opts.atomHighlightsAreCircles = True
    opts.fillHighlights = True
    opts.highlightRadius = 0.62

    highlight, colors = [], {}
    if accent is not None:
        n_idx = _pyridyl_n_idx(mol)
        if n_idx is not None:
            highlight = [n_idx]
            r, g, b = _hex_rgb(accent)
            # Strong wash so the isomer N survives thumbnail shrink.
            colors[n_idx] = (0.78 * r + 0.22, 0.78 * g + 0.22, 0.78 * b + 0.22)

    rdMolDraw2D.PrepareAndDrawMolecule(
        drawer, mol, highlightAtoms=highlight, highlightAtomColors=colors,
    )
    drawer.FinishDrawing()
    im = Image.open(io.BytesIO(drawer.GetDrawingText())).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 10
        im = im.crop((
            max(0, bbox[0] - pad), max(0, bbox[1] - pad),
            min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad),
        ))
    return np.asarray(im)


def molimg(smi, accent=None):
    """Bold monochrome structure; heteroatom labels land near ATOM_PT when printed."""
    font = ATOM_PT * CANVAS[0] / (STRUCT_W_IN * 72)
    for _ in range(2):
        arr = _draw_mol(smi, round(font), accent=accent)
        zoom = STRUCT_W_IN * 72 / arr.shape[1]
        font = ATOM_PT / zoom
    arr = _draw_mol(smi, round(font), accent=accent)
    return arr, STRUCT_W_IN * 72 / arr.shape[1]


def _ppm_x(ppm, x0, x1, ppm_max=PPM_MAX):
    return x1 - (ppm / ppm_max) * (x1 - x0)


def main():
    fig = plt.figure(figsize=(W_IN, H_IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # 1 — headline claim
    ax.text(
        50, 98.0, "28% top-1 · real IR + NMR",
        ha="center", va="top", fontsize=8.5, fontweight="bold", color=fs.INK,
    )

    # 2 — observed ¹³C sticks (chemistry visual anchor)
    spec_x0, spec_x1 = 3.5, 96.5
    stick_y0, stick_y1 = 64.5, 87.5
    ax.text(
        spec_x0, 89.0, "observed \u00b9\u00b3C",
        ha="left", va="bottom", fontsize=MIN_PT, fontweight="bold", color=fs.NOTE,
    )
    ax.text(
        spec_x1, 89.0, "ppm",
        ha="right", va="bottom", fontsize=MIN_PT, color=fs.MUTED,
    )

    arom_lo, arom_hi = 100.0, 165.0
    ax.add_patch(Rectangle(
        (_ppm_x(arom_hi, spec_x0, spec_x1), stick_y0),
        _ppm_x(arom_lo, spec_x0, spec_x1) - _ppm_x(arom_hi, spec_x0, spec_x1),
        stick_y1 - stick_y0,
        facecolor="#eef1f2", edgecolor="none", zorder=0,
    ))

    for ppm in OBS:
        x = _ppm_x(ppm, spec_x0, spec_x1)
        ax.plot(
            [x, x], [stick_y0, stick_y1], color=fs.INK, lw=STICK_LW,
            solid_capstyle="butt", zorder=3,
        )
    ax.plot(
        [spec_x0, spec_x1], [stick_y0, stick_y0],
        color=fs.INK, lw=1.20, solid_capstyle="butt", zorder=2,
    )
    for ppm, ha, dx in ((PPM_MAX, "left", 0.4), (0.0, "right", -0.4)):
        x = _ppm_x(ppm, spec_x0, spec_x1)
        ax.plot([x, x], [stick_y0 - 1.4, stick_y0], color=fs.INK, lw=1.0, zorder=2)
        ax.text(
            x + dx, stick_y0 - 1.8, f"{ppm:.0f}",
            ha=ha, va="top", fontsize=MIN_PT, color=fs.NOTE,
        )

    # 3 — two candidates without card frames
    # Structure height ≈ 37 data units at STRUCT_W_IN=1.20 → centre 41 clears ppm labels.
    for (smi, col, caption), xc in zip(CANDIDATES, (26.5, 73.5)):
        img, zoom = molimg(smi, accent=col)
        ax.add_artist(AnnotationBbox(
            OffsetImage(img, zoom=zoom),
            (xc, 41.0),
            frameon=False,
            box_alignment=(0.5, 0.5),
            pad=0.0,
        ))
        # Short colour rule — selected/rejected cue without a box
        ax.add_patch(Rectangle(
            (xc - 11.5, 19.0), 23.0, 0.85,
            facecolor=col, edgecolor="none", zorder=4,
        ))
        ax.text(
            xc, 14.0, caption,
            ha="center", va="center", fontsize=MIN_PT,
            fontweight="bold", color=col,
        )

    # 4 — bottom FOM (wording gated by check_manuscript.py)
    ax.text(
        50, 1.8,
        "recall 34% binds · verification 89% does not",
        ha="center", va="bottom", fontsize=MIN_PT, color=fs.INK,
    )

    fs.save("docs/figures/graphical_abstract.png")
    print(f"wrote docs/figures/graphical_abstract.png  ({W_IN * 2.54:.0f} × {H_IN * 2.54:.0f} cm)")


if __name__ == "__main__":
    main()
