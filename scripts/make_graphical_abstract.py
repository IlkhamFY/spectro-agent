#!/usr/bin/env python3
"""RSC table-of-contents graphic — exactly 8 cm × 4 cm, nothing below 7 pt.

One clean composition (Nature desk, not a dashboard):
  title claim → observed ¹³C sticks → two framed candidates → one-line FOM.

Structures use ACS-bold bonds with the regioisomer nitrogen tinted so the
2- vs 3-pyridyl distinction reads at thumbnail size.
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
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
STRUCT_W_IN = 1.12
ATOM_PT = 7.5
CANVAS = (900, 520)
BOND_LW = 4.2         # with scaleBondWidth → bold at 8×4 cm thumbnail

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
    opts.padding = 0.08
    opts.fixedFontSize = int(max(1, font_px))
    opts.additionalAtomLabelPadding = 0.12
    opts.multipleBondOffset = 0.20

    highlight, colors = [], {}
    if accent is not None:
        n_idx = _pyridyl_n_idx(mol)
        if n_idx is not None:
            highlight = [n_idx]
            r, g, b = _hex_rgb(accent)
            colors[n_idx] = (0.55 * r + 0.45, 0.55 * g + 0.45, 0.55 * b + 0.45)

    rdMolDraw2D.PrepareAndDrawMolecule(
        drawer, mol, highlightAtoms=highlight, highlightAtomColors=colors,
    )
    drawer.FinishDrawing()
    im = Image.open(io.BytesIO(drawer.GetDrawingText())).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 18
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


def _ppm_x(ppm, x0, x1, ppm_max=175.0):
    return x1 - (ppm / ppm_max) * (x1 - x0)


def main():
    fig = plt.figure(figsize=(W_IN, H_IN))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # 1 — single headline claim
    ax.text(
        50, 97.0, "28% top-1 · real IR + NMR",
        ha="center", va="top", fontsize=8, fontweight="bold", color=fs.INK,
    )

    # 2 — observed ¹³C sticks (full width, bolder)
    ax.text(3.0, 80.5, "observed \u00b9\u00b3C", ha="left", va="bottom",
            fontsize=MIN_PT, color=fs.NOTE)
    spec_x0, spec_x1 = 3.0, 97.0
    stick_y0, stick_y1 = 58.0, 78.0
    for ppm in OBS:
        x = _ppm_x(ppm, spec_x0, spec_x1)
        ax.plot([x, x], [stick_y0, stick_y1], color=fs.INK, lw=2.35,
                solid_capstyle="butt", zorder=3)
    ax.plot([spec_x0, spec_x1], [stick_y0, stick_y0], color=fs.GHOST, lw=0.85, zorder=1)

    # 3 — two equal columns: bold framed structures + verdict line
    for (smi, col, caption), xc in zip(CANDIDATES, (25, 75)):
        img, zoom = molimg(smi, accent=col)
        ax.add_artist(AnnotationBbox(
            OffsetImage(img, zoom=zoom),
            (xc, 36),
            frameon=True,
            box_alignment=(0.5, 0.5),
            pad=0.28,
            bboxprops=dict(edgecolor=col, lw=1.65, facecolor="white",
                           boxstyle="square,pad=0.28"),
        ))
        ax.text(
            xc, 10.5, caption,
            ha="center", va="center", fontsize=MIN_PT, fontweight="bold", color=col,
        )

    # 4 — bottom FOM
    ax.text(
        50, 1.5,
        "recall 34% binds · verification 89% does not",
        ha="center", va="bottom", fontsize=MIN_PT, color=fs.INK,
    )

    fs.save("docs/figures/graphical_abstract.png")
    print(f"wrote docs/figures/graphical_abstract.png  ({W_IN * 2.54:.0f} × {H_IN * 2.54:.0f} cm)")


if __name__ == "__main__":
    main()
