#!/usr/bin/env python3
"""IRexp positioning vs peer IR/NMR resources (NMRexp Fig. 1 analogue).

Honest scale comparison: band lists vs absorbance spectra; redistributable vs view-only.
Output: docs/scientific_data/figures/fig_irexp_positioning.{svg,pdf,png}
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

NMRexp_TOTAL = 3_370_987
SDBS_FTIR = 54_100

ROWS = [
    ("IRexp", "band lists · bulk DL", STATS["records"], fs.BLUE, False, "Redistributable"),
    ("IRexp commercial pool", "CC-BY / CC0", STATS["licence_pool_commercial"], fs.SKY, False, "Redistributable"),
    ("NMRexp", "NMR lists · bulk DL", NMRexp_TOTAL, fs.GREEN, False, "Redistributable"),
    ("SDBS FT-IR", "absorbance · view-only", SDBS_FTIR, fs.MUTED, True, "View-only"),
]

fig, ax = plt.subplots(figsize=(st.COL2, 2.85))
vals = [r[2] for r in ROWS]
colors = [r[3] for r in ROWS]
hatches = ["////" if r[4] else None for r in ROWS]
groups = [r[5] for r in ROWS]
y = np.arange(len(ROWS))

# Category bands
for gname, tint in [("Redistributable", st.TINT_BLUE), ("View-only", st.TINT_GREY)]:
    idx = [i for i, g in enumerate(groups) if g == gname]
    if idx:
        st.category_band(ax, min(idx), max(idx), tint)

bars = ax.barh(y, vals, color=colors, height=0.58, edgecolor="white", linewidth=0.8, zorder=3)
for bar, hatch in zip(bars, hatches):
    if hatch:
        bar.set_hatch(hatch)
        bar.set_edgecolor(fs.NOTE)
        bar.set_linewidth(0.7)
        bar.set_facecolor("#D8DCDE")

# Two-line y labels
ytick_labels = []
for name, sub, *_ in ROWS:
    ytick_labels.append(f"{name}\n{sub}")
ax.set_yticks(y)
ax.set_yticklabels(ytick_labels, fontsize=fs.FS_BODY - 0.5)
ax.invert_yaxis()
ax.set_xscale("log")
fs.xgrid(ax)
ax.set_xlabel("records / spectra (log scale)")
ax.set_xlim(3e3, 8e6)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)

for bar, v in zip(bars, vals):
    ax.text(
        v * 1.15,
        bar.get_y() + bar.get_height() / 2,
        f"{v:,}",
        ha="left",
        va="center",
        fontsize=fs.FS_BODY,
        fontweight="bold",
        color=fs.INK,
        zorder=4,
    )

# Legend row
legend_y = -0.72
ax.text(0.01, legend_y, "■", transform=ax.transAxes, color=fs.BLUE, fontsize=10, va="center")
ax.text(0.04, legend_y, "Redistributable (bulk download)", transform=ax.transAxes,
        fontsize=fs.FS_BODY - 0.5, color=fs.NOTE, va="center")
ax.add_patch(plt.Rectangle((0.52, legend_y - 0.012), 0.025, 0.024,
                            transform=ax.transAxes, facecolor="#D8DCDE",
                            hatch="////", edgecolor=fs.NOTE, linewidth=0.5))
ax.text(0.56, legend_y, "View-only (no bulk redistribution)", transform=ax.transAxes,
        fontsize=fs.FS_BODY - 0.5, color=fs.NOTE, va="center")

st.suptitle_left(fig, "Open IR and NMR spectral data — scale and redistribution")
st.finish(fig, pad=0.48, left=0.26, top=0.90)
save_figure(OUT_DIR / "fig_irexp_positioning.png", fig)
plt.close(fig)
print(f"wrote {OUT_DIR / 'fig_irexp_positioning.png'}")
