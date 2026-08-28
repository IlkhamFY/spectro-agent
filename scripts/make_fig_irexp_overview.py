#!/usr/bin/env python3
"""IRexp overview — NMRexp Fig. 3 style multi-panel composition.

Panel A: provenance donut
Panel B: licence pool horizontal bars
Panel C: modality cascade waterfall
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import nature_design as nd  # noqa: E402

nd.apply()
OUT = ROOT / "docs/scientific_data/figures"
OUT.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
FULL_QUAD = 33_201
TOTAL = STATS["records"]


def _fmt(n: int) -> str:
    return f"{n:,}"


fig = plt.figure(figsize=(nd.COL_FULL, 3.20))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.45, 1.30], wspace=0.42)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[0, 2])

# ---- (A) Provenance donut ----------------------------------------------------
nd.panel(ax_a, "a", x=-0.18, y=1.12)
prov_labels = ["PMC OA", "Chemotion"]
prov_vals = [STATS["provenance_pmc"], STATS["provenance_chemotion"]]
prov_cols = [nd.HERO, nd.GREEN]
nd.donut(ax_a, prov_vals, prov_labels, prov_cols,
         center_text=f"{TOTAL:,}\nrecords")
ax_a.set_title("Provenance", loc="left", pad=8, fontsize=nd.FS_TITLE, fontweight="bold")
ax_a.set_aspect("equal")

# ---- (B) Licence pools -------------------------------------------------------
nd.panel(ax_b, "b", x=-0.10, y=1.12)
pools = [
    ("commercial (CC-BY/CC0)", STATS["licence_pool_commercial"], nd.HERO),
    ("non-commercial (NC*)", STATS["licence_pool_non_commercial"], nd.SAND),
    ("empty / unknown", STATS["licence_pool_empty_unknown"], nd.VIEW_ONLY),
    ("ShareAlike", STATS["licence_pool_sharealike"], nd.GREEN),
    ("other (ND)", STATS["licence_pool_other"], nd.NOTE),
]
ylabels = [p[0] for p in pools]
yvals = [p[1] for p in pools]
ycols = [p[2] for p in pools]
y = np.arange(len(pools))
bars = ax_b.barh(y, yvals, color=ycols, height=0.58, edgecolor="white", linewidth=0.8, zorder=3)
ax_b.set_yticks(y)
ax_b.set_yticklabels(ylabels, fontsize=nd.FS_BODY - 0.5)
ax_b.invert_yaxis()
nd.xgrid(ax_b)
ax_b.set_xlabel("records", fontsize=nd.FS_AXIS)
ax_b.set_xlim(0, max(yvals) * 1.22)
ax_b.spines["left"].set_visible(False)
ax_b.tick_params(axis="y", length=0)
for b, v in zip(bars, yvals):
    ax_b.text(b.get_width() + max(yvals) * 0.015, b.get_y() + b.get_height() / 2,
              _fmt(v), ha="left", va="center", fontsize=nd.FS_BODY,
              fontweight="bold", color=nd.INK)
ax_b.set_title("Licence pools (Crossref-recovered)", loc="left", pad=8,
               fontsize=nd.FS_TITLE, fontweight="bold")

# ---- (C) Modality cascade waterfall ------------------------------------------
nd.panel(ax_c, "c", x=-0.14, y=1.12)
steps = [
    ("all records", STATS["records"], nd.VIEW_ONLY),
    ("+ NMR string", STATS["with_co_reported_NMR"], nd.TEAL),
    ("structure-linked", STATS["with_structure"], nd.HERO),
    ("IR+¹H+¹³C+structure", FULL_QUAD, nd.GREEN),
]
clabels = [s[0] for s in steps]
cvals = [s[1] for s in steps]
ccols = [s[2] for s in steps]
xs = np.arange(len(steps))
bars = ax_c.bar(xs, cvals, color=ccols, width=0.62, edgecolor="white", linewidth=1.0, zorder=3)
# Waterfall connectors
for i in range(len(cvals) - 1):
    ax_c.plot([xs[i] + 0.31, xs[i + 1] - 0.31], [cvals[i], cvals[i + 1]],
              color=nd.NOTE, lw=0.7, ls=(0, (3, 3)), zorder=2)
    drop = cvals[i] - cvals[i + 1]
    if drop > 0:
        mid_x = (xs[i] + xs[i + 1]) / 2
        ax_c.annotate(f"−{_fmt(drop)}", xy=(mid_x, (cvals[i] + cvals[i + 1]) / 2),
                      fontsize=nd.FS_BODY - 1, color=nd.NOTE, ha="center", va="center")
ax_c.set_xticks(xs)
ax_c.set_xticklabels(clabels, rotation=28, ha="right", fontsize=nd.FS_BODY - 0.5)
nd.ygrid(ax_c)
ax_c.set_ylabel("records", fontsize=nd.FS_AXIS)
ax_c.set_ylim(0, max(cvals) * 1.14)
for b, v in zip(bars, cvals):
    ax_c.text(b.get_x() + b.get_width() / 2, b.get_height() + max(cvals) * 0.012,
              _fmt(v), ha="center", va="bottom", fontsize=nd.FS_BODY - 0.5,
              fontweight="bold", color=nd.INK)
ax_c.set_title("Modality linkage", loc="left", pad=8, fontsize=nd.FS_TITLE, fontweight="bold")

# Unified colour key (below panels, clear of x-tick labels)
legend_elements = [
    Patch(facecolor=nd.HERO, edgecolor="white", label="IRexp / commercial"),
    Patch(facecolor=nd.TEAL, edgecolor="white", label="PMC / co-modality"),
    Patch(facecolor=nd.GREEN, edgecolor="white", label="Chemotion / quadruples"),
    Patch(facecolor=nd.SAND, edgecolor="white", label="non-commercial"),
    Patch(facecolor=nd.VIEW_ONLY, edgecolor="white", label="baseline / unknown"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.06),
           fontsize=nd.FS_BODY - 0.5, frameon=False)

nd.suptitle(fig, f"IRexp release overview (n = {TOTAL:,})")
nd.finish(fig, pad=0.52, left=0.08, top=0.88, w_pad=2.5, h_pad=3.0)
nd.save(OUT / "fig_irexp_overview.png", fig)
plt.close(fig)
print(f"wrote {OUT / 'fig_irexp_overview.png'}")
