#!/usr/bin/env python3
"""IRexp harvest provenance pipeline (NMRexp Fig. 2A analogue).

Output: docs/scientific_data/figures/fig_irexp_pipeline.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

fs.apply()

OUT_DIR = ROOT / "docs/scientific_data/figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STAGES = [
    ("1", "Discover", "NCBI esearch\n+ OA filter"),
    ("2", "Fetch", "PMC-OA S3\nplain text"),
    ("3", "Extract", "Regex band lists\n+ NMR strings"),
    ("4", "Resolve", "OPSIN / RDKit\n→ SMILES"),
    ("5", "Licence", "Europe PMC join\n+ Crossref recovery"),
    ("6", "Release", "JSONL pools\n+ HF / Zenodo"),
]

CHEMO = ("C", "Chemotion\nRADAR4Chem", "ELN band lists\n+ structures")

fig = plt.figure(figsize=(fs.COL2, 2.15))
ax = fig.add_axes([0.01, 0.08, 0.98, 0.82])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

xs = [7, 23, 39, 55, 71, 87]
y_main = 58
box_w, box_h = 13.5, 28


def draw_box(x, y, num, title, sub, color=fs.BLUE, width=box_w):
    patch = FancyBboxPatch(
        (x - width / 2, y - box_h / 2),
        width,
        box_h,
        boxstyle="round,pad=0.02,rounding_size=1.2",
        facecolor="white",
        edgecolor=color,
        linewidth=1.1,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.scatter([x], [y + box_h / 2 - 4.5], s=120, c=fs.INK, zorder=4, linewidths=0)
    ax.text(x, y + box_h / 2 - 4.5, num, ha="center", va="center", fontsize=fs.FS_BODY,
            fontweight="bold", color="white", zorder=5)
    ax.text(x, y + 5, title, ha="center", va="center", fontsize=fs.FS_EMPH,
            fontweight="bold", color=fs.INK, zorder=3)
    ax.text(x, y - 7, sub, ha="center", va="top", fontsize=fs.FS_BODY - 0.5,
            color=fs.NOTE, linespacing=1.25, zorder=3)


for (num, title, sub), x in zip(STAGES, xs):
    col = fs.BLUE if num in ("3", "6") else fs.SKY if num in ("2", "5") else fs.MUTED
    draw_box(x, y_main, num, title, sub, color=col)

for x0, x1 in zip(xs[:-1], xs[1:]):
    ax.add_patch(
        FancyArrowPatch(
            (x0 + box_w / 2 + 0.5, y_main),
            (x1 - box_w / 2 - 0.5, y_main),
            arrowstyle="-|>",
            mutation_scale=10,
            lw=1.0,
            color=fs.INK,
            zorder=1,
        )
    )

# Chemotion branch merges at Extract
cx, cy = 39, 22
draw_box(cx, cy, CHEMO[0], CHEMO[1], CHEMO[2], color=fs.GREEN, width=15)
ax.add_patch(
    FancyArrowPatch(
        (cx, cy + box_h / 2),
        (cx, y_main - box_h / 2 - 1),
        arrowstyle="-|>",
        mutation_scale=10,
        lw=1.0,
        color=fs.GREEN,
        zorder=1,
    )
)
ax.text(cx + 9, (cy + y_main) / 2, "same extractor", fontsize=fs.FS_BODY - 0.5,
        color=fs.GREEN, rotation=90, va="center")

ax.text(
    50,
    94,
    "IRexp construction pipeline (released corpus)",
    ha="center",
    va="top",
    fontsize=fs.FS_EMPH,
    fontweight="bold",
    color=fs.INK,
)
ax.text(
    50,
    6,
    "Outputs: irexp.jsonl.gz, licence pools, irexp_resolved — numeric fields only (no PDFs / figures)",
    ha="center",
    va="bottom",
    fontsize=fs.FS_BODY,
    color=fs.NOTE,
)

fs.save(str(OUT_DIR / "fig_irexp_pipeline.png"), fig)
plt.close(fig)
print(f"wrote {OUT_DIR / 'fig_irexp_pipeline.png'}")
