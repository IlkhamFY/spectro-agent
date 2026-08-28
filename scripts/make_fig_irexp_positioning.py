#!/usr/bin/env python3
"""IRexp positioning vs peer IR/NMR resources — NMRexp Fig. 1 style rebuild.

Honest scale comparison: band lists vs absorbance spectra; redistributable vs view-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import nature_design as nd  # noqa: E402

nd.apply()
OUT = ROOT / "docs/scientific_data/figures"
OUT.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
NMRexp = 3_370_987
SDBS = 54_100

# (name, subtitle, count, colour, view_only, group)
ROWS = [
    ("IRexp", "band lists · bulk download", STATS["records"], nd.HERO, False, "Band lists"),
    ("IRexp commercial", "CC-BY / CC0 pool", STATS["licence_pool_commercial"], nd.TEAL, False, "Band lists"),
    ("NMRexp", "NMR lists · bulk download", NMRexp, nd.GREEN, False, "NMR lists"),
    ("SDBS FT-IR", "absorbance spectra · view-only", SDBS, nd.VIEW_ONLY, True, "Spectra"),
]

fig, ax = plt.subplots(figsize=(nd.COL_FULL, 3.35))
vals = [r[2] for r in ROWS]
y = np.arange(len(ROWS))

# Category bands
groups = [r[5] for r in ROWS]
for gname, tint in [("Band lists", nd.TINT_BLUE), ("NMR lists", nd.TINT_GREEN), ("Spectra", nd.TINT_GREY)]:
    idx = [i for i, g in enumerate(groups) if g == gname]
    if idx:
        ax.axhspan(min(idx) - 0.48, max(idx) + 0.48, color=tint, zorder=0, linewidth=0)

# Bars
for i, (name, sub, val, col, view_only, _) in enumerate(ROWS):
    bar = ax.barh(i, val, height=0.52, color=col if not view_only else "#D5D8DB",
                  edgecolor="white", linewidth=0.9, zorder=3)
    if view_only:
        bar[0].set_hatch("////")
        bar[0].set_edgecolor(nd.NOTE)
        bar[0].set_linewidth(0.6)

# Y labels — two-line
ax.set_yticks(y)
ax.set_yticklabels([f"{r[0]}\n{r[1]}" for r in ROWS], fontsize=nd.FS_BODY)
ax.invert_yaxis()
ax.set_xscale("log")
nd.xgrid(ax)
ax.set_xlabel("records / spectra (log scale)", fontsize=nd.FS_AXIS)
ax.set_xlim(2.5e3, 9e6)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0, pad=4)

# Value labels at bar ends
for i, val in enumerate(vals):
    ax.text(val * 1.18, i, f"{val:,}", ha="left", va="center",
            fontsize=nd.FS_BODY, fontweight="bold", color=nd.INK, zorder=4)

# Legend row (below plot area)
box = FancyBboxPatch(
    (0.58, 0.04), 0.40, 0.14,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    transform=ax.transAxes, facecolor="#FFF8E8", edgecolor=nd.ORANGE,
    linewidth=0.8, zorder=10, clip_on=False,
)
ax.add_patch(box)
ax.text(0.78, 0.11,
        "Band lists ≠ absorbance spectra\nIRexp stores cm$^{-1}$ positions only",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=nd.FS_BODY - 0.5, color=nd.INK, linespacing=1.3, zorder=11)

# Legend row (below plot area)
leg_y = -0.22
ax.add_patch(Rectangle((0.02, leg_y - 0.008), 0.022, 0.016, transform=ax.transAxes,
                        facecolor=nd.HERO, edgecolor="none"))
ax.text(0.05, leg_y, "Bulk redistributable", transform=ax.transAxes,
        fontsize=nd.FS_BODY - 0.5, color=nd.NOTE, va="center")
ax.add_patch(Rectangle((0.28, leg_y - 0.008), 0.022, 0.016, transform=ax.transAxes,
                        facecolor="#D5D8DB", hatch="////", edgecolor=nd.NOTE, linewidth=0.4))
ax.text(0.31, leg_y, "View-only (no bulk redistribution)", transform=ax.transAxes,
        fontsize=nd.FS_BODY - 0.5, color=nd.NOTE, va="center")

nd.suptitle(fig, "Open IR and NMR spectral data — scale and redistribution")
nd.finish(fig, pad=0.55, left=0.30, top=0.90, h_pad=2.0)
nd.save(OUT / "fig_irexp_positioning.png", fig)
plt.close(fig)
print(f"wrote {OUT / 'fig_irexp_positioning.png'}")
