#!/usr/bin/env python3
"""Graphical abstract / table-of-contents graphic, authored at RSC's printed size.

RSC prints the TOC entry in an 8 cm x 4 cm box. This was drawn 6.30 in (16 cm) wide,
so the journal scaled it to half and its 5-8 pt labels landed at 2.5-4 pt on the page.
It is now authored at exactly 8 cm x 4 cm, which is a hard constraint rather than a
stylistic one: at that size the frame holds a title, one row of chemistry and one line
of result, and NOTHING may be set below 7 pt. Anything that did not survive that budget
is in the paper, not squeezed in here at 4 pt.

What survives: the real picolinamide/nicotinamide pair the method actually separates,
the observed 13C it is matched against, the two chamfer distances, and the figures of
merit. The narrative captions ("indistinguishable to the inverse task") went; the
image already shows two candidates and one verdict.

  python scripts/make_graphical_abstract.py  -> docs/figures/graphical_abstract.png
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np, io
from PIL import Image, ImageChops
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import figstyle as fs

fs.apply()
OBS = [28.9, 51.0, 121.9, 126.0, 137.9, 147.9, 151.0, 163.6]

CM = 1 / 2.54
W_IN, H_IN = 8 * CM, 4 * CM      # RSC's table-of-contents box, exactly
MIN_PT = 7                       # nothing in this graphic may be smaller
STRUCT_W_IN = 1.24               # printed width of each structure
CANVAS = (760, 430)


def _draw(smi, font_px):
    d = rdMolDraw2D.MolDraw2DCairo(*CANVAS)
    o = d.drawOptions(); o.useBWAtomPalette(); o.bondLineWidth = 2; o.padding = 0.04
    o.fixedFontSize = int(max(1, font_px))
    rdMolDraw2D.PrepareAndDrawMolecule(d, Chem.MolFromSmiles(smi))
    d.FinishDrawing()
    im = Image.open(io.BytesIO(d.GetDrawingText())).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 8
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    return np.asarray(im)


def molimg(smi):
    """Monochrome structure (colour is reserved for the selected/rejected coding) with
    its heteroatom labels solved onto MIN_PT *as printed*. An OffsetImage maps one
    canvas pixel to zoom/72 inch, so a glyph drawn at F canvas px prints at F * zoom
    points; the crop changes the width, so solve the font against the cropped image."""
    font = MIN_PT * CANVAS[0] / (STRUCT_W_IN * 72)
    for _ in range(2):
        arr = _draw(smi, round(font))
        font = MIN_PT / (STRUCT_W_IN * 72 / arr.shape[1])
    arr = _draw(smi, round(font))
    return arr, STRUCT_W_IN * 72 / arr.shape[1]


fig = plt.figure(figsize=(W_IN, H_IN))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

# Figures of merit are the whole-benchmark ones (n=194), matching the results section.
ax.text(50, 97.5, "28% top-1 on blind, real IR + NMR spectra", ha="center", va="top",
        fontsize=8, fontweight="bold", color=fs.INK)

ax.text(2, 87.5, "observed \u00b9\u00b3C,  C10H14N2O", ha="left", va="top",
        fontsize=MIN_PT, color=fs.NOTE)
xa, xb, PPM = 40.0, 98.0, 175.0
px = lambda p: xb - (p / PPM) * (xb - xa)
for p in OBS:
    ax.plot([px(p), px(p)], [70, 84], color=fs.INK, lw=fs.STICK_LW,
            solid_capstyle="butt")
ax.plot([xa - 1, xb + 1], [70, 70], color=fs.GHOST, lw=0.75)

for smi, xc, col, dist, verdict in [
        ("CC(C)(C)NC(=O)c1ccccn1", 26, fs.GREEN,  "0.42 ppm", "selected"),
        ("CC(C)(C)NC(=O)c1cccnc1", 74, fs.VERMIL, "1.30 ppm", "rejected")]:
    img, zoom = molimg(smi)
    ax.add_artist(AnnotationBbox(OffsetImage(img, zoom=zoom), (xc, 43),
                  frameon=True, box_alignment=(0.5, 0.5),
                  bboxprops=dict(edgecolor=col, lw=0.95, boxstyle="round,pad=0.18")))
    ax.text(xc, 14, f"{dist}  {verdict}", ha="center", va="center",
            fontsize=MIN_PT, fontweight="bold", color=col)

ax.text(50, 1.0, "recall (34%), not verification (89%), is the wall",
        ha="center", va="bottom", fontsize=MIN_PT, color=fs.INK)

fs.save("docs/figures/graphical_abstract.png")
print(f"wrote docs/figures/graphical_abstract.png  ({W_IN*2.54:.0f} x {H_IN*2.54:.0f} cm)")