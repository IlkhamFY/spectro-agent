#!/usr/bin/env python3
"""IRexp Sci Data overview: provenance + licence pools + composition cascade.

Reads frozen counts from data/irexp/irexp_stats.json.
Output: docs/scientific_data/figures/fig_irexp_overview.{pdf,png}
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
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import figstyle as fs  # noqa: E402
import scidata_theme as st  # noqa: E402
from scidata_export import save_figure  # noqa: E402

st.apply()
OUT_DIR = ROOT / "docs/scientific_data/figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
FULL_QUAD = 33_201

PROVENANCE = [
    ("PMC OA", STATS["provenance_pmc"], fs.BLUE),
    ("Chemotion", STATS["provenance_chemotion"], fs.GREEN),
]
POOLS = [
    ("commercial\n(CC-BY/CC0)", STATS["licence_pool_commercial"], fs.BLUE),
    ("non-commercial\n(NC*)", STATS["licence_pool_non_commercial"], fs.ORANGE),
    ("empty /\nunknown", STATS["licence_pool_empty_unknown"], fs.MUTED),
    ("ShareAlike", STATS["licence_pool_sharealike"], fs.GREEN),
    ("other\n(ND)", STATS["licence_pool_other"], fs.NOTE),
]
COMPOSITION = [
    ("all records", STATS["records"]),
    ("+ NMR string", STATS["with_co_reported_NMR"]),
    ("structure-linked", STATS["with_structure"]),
    ("IR+¹H+¹³C+structure", FULL_QUAD),
]
TOTAL = STATS["records"]


def _fmt(n: int) -> str:
    return f"{n:,}"


fig, axes = plt.subplots(
    1, 3, figsize=(st.COL2 * 1.55, 2.55),
    gridspec_kw={"width_ratios": [1.0, 1.55, 1.35], "wspace": 0.38},
)

# (a) Provenance — donut-style paired bars with icons
ax = axes[0]
st.panel(ax, "a")
labels, vals, cols = zip(*PROVENANCE)
x = np.arange(len(labels))
bars = ax.bar(x, vals, color=cols, width=0.55, edgecolor="white", linewidth=1.2, zorder=3)
fs.ygrid(ax)
ax.set_ylabel("records")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(0, max(vals) * 1.15)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(vals) * 0.02,
            _fmt(v), ha="center", va="bottom", fontsize=fs.FS_BODY, fontweight="bold", color=fs.INK)
ax.set_title("Provenance", loc="left", pad=6, fontweight="bold")
ax.set_facecolor("#F8F9FA")

# (b) Licence pools
ax = axes[1]
st.panel(ax, "b", x=-0.06)
ylabels = [p[0] for p in POOLS]
yvals = [p[1] for p in POOLS]
ycols = [p[2] for p in POOLS]
y = np.arange(len(POOLS))
bars = ax.barh(y, yvals, color=ycols, height=0.62, edgecolor="white", linewidth=0.8, zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(ylabels, fontsize=fs.FS_BODY - 0.5)
ax.invert_yaxis()
fs.xgrid(ax)
ax.set_xlabel("records")
ax.set_xlim(0, max(yvals) * 1.28)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
for b, v in zip(bars, yvals):
    ax.text(b.get_width() + max(yvals) * 0.02, b.get_y() + b.get_height() / 2,
            _fmt(v), ha="left", va="center", fontsize=fs.FS_BODY, fontweight="bold", color=fs.INK)
ax.set_title("Licence pools (Crossref-recovered)", loc="left", pad=6, fontweight="bold")

# (c) Composition cascade — waterfall-style
ax = axes[2]
st.panel(ax, "c", x=-0.10)
clabels, cvals = zip(*COMPOSITION)
xs = np.arange(len(COMPOSITION))
ccols = [fs.MUTED, "#6B8A9A", fs.SKY, fs.BLUE]
bars = ax.bar(xs, cvals, color=ccols, width=0.68, edgecolor="white", linewidth=1.0, zorder=3)
# Connecting steps
for i in range(len(cvals) - 1):
    ax.plot([xs[i] + 0.34, xs[i + 1] - 0.34],
            [cvals[i], cvals[i + 1]],
            color=fs.NOTE, lw=0.8, ls=(0, (4, 3)), zorder=2)
ax.set_xticks(xs)
ax.set_xticklabels(clabels, rotation=22, ha="right", fontsize=fs.FS_BODY - 0.5)
fs.ygrid(ax)
ax.set_ylabel("records")
ax.set_ylim(0, max(cvals) * 1.18)
for b, v in zip(bars, cvals):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(cvals) * 0.015,
            _fmt(v), ha="center", va="bottom", fontsize=fs.FS_BODY - 0.5,
            fontweight="bold", color=fs.INK)
ax.set_title("Composition", loc="left", pad=6, fontweight="bold")

st.suptitle_left(fig, f"IRexp release overview (n = {TOTAL:,})")
st.finish(fig, pad=0.42, left=0.08, top=0.90, w_pad=2.0)
save_figure(OUT_DIR / "fig_irexp_overview.png", fig)
plt.close(fig)
print(f"wrote {OUT_DIR / 'fig_irexp_overview.png'}")
