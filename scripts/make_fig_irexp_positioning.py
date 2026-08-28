#!/usr/bin/env python3
"""Fig 1 — Summary of major IR / spectral list resources (NMRexp Fig. 1 analogue).

3D isometric bar comparison + sidebar callout box.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, FancyBboxPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import nature_design as nd  # noqa: E402

nd.apply()
OUT = ROOT / "docs/scientific_data/figures"
OUT.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
NMRexp = 3_370_987
SDBS = 54_100  # approximate; AIST introduction 2015

# (label, access_tag, stacks: [(name, value, color), ...])
# stacks drawn left-to-right per cluster; total is tallest back bar
DATABASES = [
    ("SDBS", "View-only", [
        ("Total", SDBS, nd.NMREXP_BLUE),
    ], True),
    ("NIST\nWebBook", "View-only", [
        ("Total", 17_000, nd.NMREXP_BLUE),  # ~gas-phase IR spectra; approximate
    ], True),
    ("NMRexp", "Open-access", [
        ("Total", NMRexp, nd.NMREXP_BLUE),
    ], False),
    ("IRexp", "This Work", [
        ("Total", STATS["records"], nd.NMREXP_BLUE),
        ("Structure-linked", STATS["with_structure"], nd.NMREXP_PEACH),
        ("CC-BY/CC0 pool", STATS["licence_pool_commercial"], nd.NMREXP_NAVY),
    ], False),
]

STACK_LEGEND = [
    ("Total", nd.NMREXP_BLUE),
    ("Structure-linked", nd.NMREXP_PEACH),
    ("CC-BY/CC0 pool", nd.NMREXP_NAVY),
]

Y_MAX = 3.8e6
Y_TICKS = [0, 0.5e6, 1.0e6, 1.5e6, 2.0e6, 2.5e6, 3.0e6, 3.5e6]
Y_LABELS = ["0", "0.5M", "1.0M", "1.5M", "2.0M", "2.5M", "3.0M", "3.5M"]


def _fmt_m(n: float) -> str:
    if n >= 1e6:
        return f"{n/1e6:.1f}M"
    if n >= 1e3:
        return f"{n/1e3:.0f}k"
    return f"{int(n)}"


def _y_to_ax(y_val: float, y_base: float, y_top: float) -> float:
    return y_base + (y_val / Y_MAX) * (y_top - y_base)


def main() -> None:
    fig, ax = plt.subplots(figsize=(nd.COL_FULL, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Chart area
    chart_l, chart_r = 0.55, 6.85
    chart_b, chart_t = 1.35, 8.55
    chart_w = chart_r - chart_l
    chart_h = chart_t - chart_b

    # Back wall grid (NMRexp 3D floor)
    for frac in np.linspace(0, 1, 9):
        yg = chart_b + frac * chart_h
        ax.plot([chart_l, chart_r], [yg, yg], color=nd.FAINT, lw=0.5, zorder=0)
    for frac in np.linspace(0, 1, 8):
        xg = chart_l + frac * chart_w
        ax.plot([xg, xg + 0.35], [chart_b, chart_b + 0.22],
                color=nd.FAINT, lw=0.4, zorder=0)

    # Back wall
    wall = Polygon(
        [(chart_l, chart_b), (chart_r, chart_b), (chart_r + 0.35, chart_b + 0.22),
         (chart_l + 0.35, chart_b + 0.22)],
        closed=True, facecolor="#F7F8F9", edgecolor=nd.GHOST, linewidth=0.5, zorder=0,
    )
    ax.add_patch(wall)

    # Y-axis labels on back wall
    for tick, lab in zip(Y_TICKS, Y_LABELS):
        yp = _y_to_ax(tick, chart_b, chart_t)
        ax.text(chart_l - 0.12, yp, lab, ha="right", va="center",
                fontsize=nd.FS_BODY - 0.5, color=nd.NOTE)
    ax.text(chart_l - 0.55, (chart_b + chart_t) / 2, "Number of records",
            rotation=90, ha="center", va="center", fontsize=nd.FS_AXIS,
            fontweight="bold", color=nd.INK)

    n_db = len(DATABASES)
    cluster_w = chart_w / n_db
    bar_w = cluster_w * 0.14
    bar_d = cluster_w * 0.10

    for i, (label, access, stacks, view_only) in enumerate(DATABASES):
        cx = chart_l + (i + 0.5) * cluster_w
        n_stacks = len(stacks)
        offsets = np.linspace(-(n_stacks - 1) * bar_w * 0.55,
                              (n_stacks - 1) * bar_w * 0.55, n_stacks)
        for j, (sname, val, col) in enumerate(stacks):
            bx = cx + offsets[j]
            h_ax = _y_to_ax(val, chart_b, chart_t) - chart_b
            alpha = 0.55 if view_only and j > 0 else (0.75 if view_only else 1.0)
            nd.draw_iso_bar(ax, bx, chart_b, bar_w, bar_d, h_ax, col,
                            zorder=3 + j, alpha=alpha)
            if view_only:
                # hatch overlay on top face
                pass

        # Access label
        tag_color = nd.NMREXP_BLUE if access in ("Open-access", "This Work") else nd.INK
        tag_weight = "bold" if access == "This Work" else "normal"
        ax.text(cx, chart_t + 0.35, access, ha="center", va="bottom",
                fontsize=nd.FS_BODY, color=tag_color, fontweight=tag_weight)
        # X label
        ax.text(cx, chart_b - 0.28, label, ha="center", va="top",
                fontsize=nd.FS_BODY, color=nd.INK, linespacing=1.1)

        if access == "This Work":
            # Star above IRexp
            star_y = chart_t + 0.75
            ax.text(cx, star_y, "*", ha="center", va="center",
                    fontsize=28, color=nd.NMREXP_BLUE_DARK, fontweight="bold", zorder=10)

    ax.text((chart_l + chart_r) / 2, chart_b - 0.75, "Spectral resource",
            ha="center", va="top", fontsize=nd.FS_AXIS, fontweight="bold", color=nd.INK)

    # Legend (top-left of chart)
    leg_x, leg_y = chart_l + 0.05, chart_t - 0.15
    for k, (name, col) in enumerate(STACK_LEGEND):
        lx = leg_x + k * 1.55
        nd.draw_iso_bar(ax, lx, leg_y, 0.12, 0.08, 0.18, col, zorder=6)
        ax.text(lx + 0.18, leg_y + 0.09, name, ha="left", va="center",
                fontsize=nd.FS_BODY - 1, color=nd.INK)

    # Honest footnote
    ax.text(chart_l, chart_b - 1.05,
            "SDBS ≈54k FT-IR spectra (AIST 2015); NIST ≈17k gas-phase IR (approx.); "
            "band lists ≠ absorbance traces",
            ha="left", va="top", fontsize=nd.FS_BODY - 1, color=nd.NOTE, style="italic")

    # Sidebar callout (NMRexp Fig 1 right panel)
    nd.sidebar_callout(
        ax, 0.70, 0.15, 0.28, 0.55,
        header="IRexp  (IR: an experimental database)",
        bullets=[
            f"Large:  {STATS['records']:,} band lists",
            f"Redistributable:  {STATS['licence_pool_commercial']:,} CC-BY/CC0",
            "Traceable:  DOI + licence pools per record",
        ],
    )

    nd.save(OUT / "fig_irexp_positioning.png", fig)
    plt.close(fig)
    print(f"wrote {OUT / 'fig_irexp_positioning.png'}")


if __name__ == "__main__":
    main()
