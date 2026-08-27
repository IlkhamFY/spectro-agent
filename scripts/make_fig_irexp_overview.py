#!/usr/bin/env python3
"""IRexp Sci Data overview: provenance + licence pools (frozen counts).

Output (real files, no symlinks — Overleaf-safe):
  docs/scientific_data/figures/fig_irexp_overview.{png,pdf}
"""
from __future__ import annotations

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

# Frozen post-Crossref counts (LICENCE_REMEDIATION.md / pmc_licence_summary.json)
PROVENANCE = [("PMC OA", 119_345), ("Chemotion", 1_888)]
POOLS = [
    ("commercial\n(CC-BY/CC0)", 88_545, fs.BLUE),
    ("non-commercial\n(NC*)", 21_823, fs.ORANGE),
    ("empty /\nunknown", 8_963, fs.MUTED),
    ("ShareAlike", 1_897, fs.GREEN),
    ("other\n(ND)", 5, fs.NOTE),
]
COMPOSITION = [
    ("all records", 121_233),
    ("+ NMR string", 87_075),
    ("structure-linked", 43_060),
    ("IR+¹H+¹³C+structure", 33_201),
]


def _fmt(n: int) -> str:
    return f"{n:,}"


fig, axes = plt.subplots(
    1, 3, figsize=(fs.COL2 * 1.55, 2.35), gridspec_kw={"width_ratios": [1.0, 1.55, 1.35]}
)

# (a) Provenance
ax = axes[0]
fs.panel(ax, "a", x=-0.18, y=1.08)
labels, vals = zip(*PROVENANCE)
colors = [fs.BLUE, fs.GREEN]
bars = ax.bar(labels, vals, color=colors, width=0.62)
fs.ygrid(ax)
ax.set_ylabel("records")
ax.set_ylim(0, max(vals) * 1.18)
for b, v in zip(bars, vals):
    ax.text(
        b.get_x() + b.get_width() / 2,
        b.get_height(),
        _fmt(v),
        ha="center",
        va="bottom",
        fontsize=fs.FS_BODY,
        color=fs.INK,
    )
ax.set_title("Provenance", loc="left", pad=2)

# (b) Licence pools
ax = axes[1]
fs.panel(ax, "b", x=-0.08, y=1.08)
ylabels = [p[0] for p in POOLS]
yvals = [p[1] for p in POOLS]
ycols = [p[2] for p in POOLS]
y = np.arange(len(POOLS))
bars = ax.barh(y, yvals, color=ycols, height=0.68)
ax.set_yticks(y)
ax.set_yticklabels(ylabels)
ax.invert_yaxis()
fs.xgrid(ax)
ax.set_xlabel("records")
ax.set_xlim(0, max(yvals) * 1.22)
for b, v in zip(bars, yvals):
    ax.text(
        b.get_width() + max(yvals) * 0.015,
        b.get_y() + b.get_height() / 2,
        _fmt(v),
        ha="left",
        va="center",
        fontsize=fs.FS_BODY,
        color=fs.INK,
    )
ax.set_title("Licence pools (Crossref-recovered)", loc="left", pad=2)

# (c) Composition cascade
ax = axes[2]
fs.panel(ax, "c", x=-0.12, y=1.08)
clabels, cvals = zip(*COMPOSITION)
xs = np.arange(len(COMPOSITION))
# Step-down greys → blue for full quadruples
ccols = [fs.MUTED, "#7a8288", fs.SKY, fs.BLUE]
bars = ax.bar(xs, cvals, color=ccols, width=0.72)
ax.set_xticks(xs)
ax.set_xticklabels(clabels, rotation=28, ha="right")
fs.ygrid(ax)
ax.set_ylabel("records")
ax.set_ylim(0, max(cvals) * 1.18)
for b, v in zip(bars, cvals):
    ax.text(
        b.get_x() + b.get_width() / 2,
        b.get_height(),
        _fmt(v),
        ha="center",
        va="bottom",
        fontsize=fs.FS_BODY - 0.5,
        color=fs.INK,
    )
ax.set_title("Composition", loc="left", pad=2)

fig.suptitle(
    "IRexp release overview (n = 121,233)",
    x=0.01,
    y=0.98,
    ha="left",
    fontsize=fs.FS_EMPH,
    fontweight="bold",
    color=fs.INK,
)
fig.tight_layout(rect=[0, 0, 1, 0.93])

stem = OUT_DIR / "fig_irexp_overview"
fig.savefig(stem.with_suffix(".png"), dpi=fs.DPI_SAVE)
fig.savefig(stem.with_suffix(".pdf"))
plt.close(fig)
print(f"wrote {stem.with_suffix('.png')}")
print(f"wrote {stem.with_suffix('.pdf')}")
