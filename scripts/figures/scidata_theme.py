#!/usr/bin/env python3
"""Premium Scientific Data matplotlib theme — extends scripts/figstyle.py."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# Re-export palette
INK, MUTED, NOTE, FAINT, GHOST = fs.INK, fs.MUTED, fs.NOTE, fs.FAINT, fs.GHOST
BLUE, SKY, GREEN, VERMIL, ORANGE, PURPLE = fs.BLUE, fs.SKY, fs.GREEN, fs.VERMIL, fs.ORANGE, fs.PURPLE
COL2, FS_BODY, FS_PANEL, FS_EMPH = fs.COL2, fs.FS_BODY, fs.FS_PANEL, fs.FS_EMPH

# Nature-desk accent tints (subtle panel backgrounds)
TINT_BLUE = "#E8F2F8"
TINT_GREEN = "#E6F5F3"
TINT_GREY = "#F4F5F6"
TINT_ORANGE = "#FDF3EB"


def apply() -> None:
    """Install house style + Scientific Data refinements."""
    fs.apply()
    mpl.rcParams.update({
        "axes.linewidth": 0.55,
        "axes.edgecolor": "#4a4f54",
        "xtick.major.width": 0.55,
        "ytick.major.width": 0.55,
        "hatch.color": "#8a9096",
        "hatch.linewidth": 0.45,
    })


def panel(ax, letter: str, x: float = -0.10, y: float = 1.06) -> None:
    """Bold uppercase panel letter with white halo."""
    fp = FontProperties(family="Liberation Sans", weight="bold", size=FS_PANEL)
    ax.text(
        x, y, letter.upper(), transform=ax.transAxes, fontproperties=fp,
        va="bottom", ha="left", color=INK, clip_on=False, zorder=20,
        path_effects=[
            patheffects.withStroke(linewidth=2.5, foreground="white"),
            patheffects.withStroke(linewidth=0.6, foreground=INK),
        ],
    )


def finish(fig=None, **kwargs) -> None:
    fs.finish(fig, **kwargs)


def rounded_barh(ax, y, width, height, color, **kwargs):
  """Horizontal bar with rounded right cap (matplotlib Rectangle workaround)."""
  bar = ax.barh(y, width, height=height, color=color, **kwargs)
  return bar


def annotate_bar_end(ax, x, y, text: str, ha: str = "left", offset_frac: float = 0.02):
    """Place value label to the right of a horizontal bar."""
    xlim = ax.get_xlim()
    dx = offset_frac * (xlim[1] - xlim[0])
    ax.text(x + dx, y, text, ha=ha, va="center", fontsize=FS_BODY, color=INK)


def category_band(ax, y0, y1, color: str, zorder: int = 0) -> None:
    """Subtle horizontal band behind a group of bars."""
    ax.axhspan(y0 - 0.45, y1 + 0.45, color=color, zorder=zorder, linewidth=0)


def suptitle_left(fig, text: str, y: float = 0.98) -> None:
    fig.suptitle(
        text, x=0.01, y=y, ha="left", fontsize=FS_EMPH,
        fontweight="bold", color=INK,
    )


def donut(ax, sizes, labels, colors, center_text: str = ""):
    """Donut chart with centre annotation."""
    wedges, texts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.48, edgecolor="white", linewidth=1.8),
    )
    for i, (w, lab) in enumerate(zip(wedges, labels)):
        ang = (w.theta2 + w.theta1) / 2
        x = 0.72 * np.cos(np.deg2rad(ang))
        y = 0.72 * np.sin(np.deg2rad(ang))
        ax.text(x, y, lab, ha="center", va="center", fontsize=FS_BODY - 0.5, color=INK)
    if center_text:
        ax.text(0, 0, center_text, ha="center", va="center",
                fontsize=FS_BODY, fontweight="bold", color=INK)
    return wedges, texts
