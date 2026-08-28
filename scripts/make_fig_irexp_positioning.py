#!/usr/bin/env python3
"""IRexp positioning vs peer IR/NMR resources (NMRexp Fig. 1 analogue).

Honest scale comparison: band lists vs absorbance spectra; redistributable vs view-only.
Output: docs/scientific_data/figures/fig_irexp_positioning.{png,pdf}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

fs.apply()

OUT_DIR = ROOT / "docs/scientific_data/figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())

# External comparators (cite in caption — not IRexp counts)
NMRexp_TOTAL = 3_370_987  # Wang et al. 2025 Sci Data sum of all nuclei
SDBS_FTIR = 54_100  # AIST SDBS introduction, May 2015 (approx.)

ROWS = [
    ("IRexp\n(band lists,\nbulk DL)", STATS["records"], fs.BLUE, False, "left"),
    ("IRexp commercial\npool (CC-BY/CC0)", STATS["licence_pool_commercial"], fs.SKY, False, "left"),
    ("NMRexp\n(NMR lists,\nbulk DL)", NMRexp_TOTAL, fs.GREEN, False, "left"),
    ("SDBS FT-IR\n(absorbance,\nview-only)", SDBS_FTIR, fs.MUTED, True, "left"),
]

fig, ax = plt.subplots(figsize=(fs.COL2, 2.55))
vals = [r[1] for r in ROWS]
labels = [r[0] for r in ROWS]
colors = [r[2] for r in ROWS]
hatches = ["///" if r[3] else None for r in ROWS]
y = np.arange(len(ROWS))

bars = ax.barh(y, vals, color=colors, height=0.62, edgecolor=fs.INK, linewidth=0.35)
for bar, hatch in zip(bars, hatches):
    if hatch:
        bar.set_hatch(hatch)
        bar.set_edgecolor(fs.NOTE)
        bar.set_linewidth(0.55)

ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xscale("log")
fs.xgrid(ax)
ax.set_xlabel("records / spectra (log scale)")
ax.set_xlim(3e3, 6e6)

for bar, v in zip(bars, vals):
    ax.text(
        v * 1.12,
        bar.get_y() + bar.get_height() / 2,
        f"{v:,}",
        ha="left",
        va="center",
        fontsize=fs.FS_BODY,
        color=fs.INK,
    )

ax.text(
    0.99,
    0.03,
    "Hatched = view-only (no bulk redistribution)",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=fs.FS_BODY,
    color=fs.NOTE,
)

fig.suptitle(
    "Open IR and NMR spectral data — scale and redistribution",
    x=0.01,
    y=0.98,
    ha="left",
    fontsize=fs.FS_EMPH,
    fontweight="bold",
    color=fs.INK,
)
fs.finish(fig, pad=0.42, left=0.22)
fs.save(str(OUT_DIR / "fig_irexp_positioning.png"), fig)
plt.close(fig)
print(f"wrote {OUT_DIR / 'fig_irexp_positioning.png'}")
