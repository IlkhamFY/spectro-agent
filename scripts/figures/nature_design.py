#!/usr/bin/env python3
"""Nature Portfolio design system — locked palette, typography, export for IRexp Sci Data.

Single source of truth for figure dimensions, colours, panel labels, and save settings.
Import after matplotlib Agg backend selection.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# ---- Nature dimensions (inches) -----------------------------------------------
MM_PER_IN = 25.4
COL_SINGLE = 89 / MM_PER_IN      # 3.504 in — single column
COL_FULL = 183 / MM_PER_IN       # 7.205 in — double column
MAX_HEIGHT = 247 / MM_PER_IN

# ---- Locked Nature-muted palette (Paul Tol Muted + desk accents) --------------
INK = "#1a1a1a"
MUTED = "#7a7f85"
NOTE = "#5c636a"
FAINT = "#e8eaec"
GHOST = "#c5c9cd"

# Primary series (Tol Muted — colourblind-safe, Nature-desk restrained)
BLUE = "#4477AA"       # hero / IRexp / commercial
TEAL = "#66CCEE"        # secondary / PMC / co-modality
SAND = "#CCBB44"        # highlight / non-commercial
ROSE = "#AA3377"        # accent / quarantine
GREEN = "#228833"       # positive / pass
GREY = "#BBBBBB"        # view-only / baseline
ORANGE = "#EE7733"      # sparing hero accent (Tol vibrant orange)

# Semantic aliases
HERO = BLUE
SECONDARY = TEAL
OPEN = GREEN
VIEW_ONLY = GREY
FAIL = ROSE
PASS = GREEN

# Panel background tints
TINT_BLUE = "#EEF3F8"
TINT_GREEN = "#EAF4EE"
TINT_GREY = "#F3F4F5"
TINT_SAND = "#FAF6E8"

# ---- Typography (pt at final print size) ------------------------------------
FONT = "Liberation Sans"
FS_MIN = 5
FS_BODY = 7
FS_AXIS = 7
FS_LABEL = 7
FS_PANEL = 8
FS_TITLE = 8
FS_EMPH = 8

# ---- Geometry tokens ---------------------------------------------------------
LINE_AXIS = 0.50
LINE_GRID = 0.40
LINE_DATA = 1.00
LINE_SCHEMATIC = 1.20
PAD_INCHES = 0.04
DPI_PNG = 600

# Re-export figstyle column widths for compat
COL1 = fs.COL1
COL2 = fs.COL2


def apply() -> None:
    """Install Nature Portfolio matplotlib rcParams."""
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": DPI_PNG,
        "savefig.bbox": "standard",
        "savefig.pad_inches": PAD_INCHES,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "sans-serif",
        "font.sans-serif": [FONT, "Helvetica", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "custom",
        "mathtext.rm": FONT,
        "mathtext.it": f"{FONT}:italic",
        "mathtext.bf": f"{FONT}:bold",
        "font.size": FS_BODY,
        "axes.titlesize": FS_TITLE,
        "axes.labelsize": FS_AXIS,
        "xtick.labelsize": FS_LABEL,
        "ytick.labelsize": FS_LABEL,
        "legend.fontsize": FS_BODY,
        "axes.prop_cycle": mpl.cycler(color=[BLUE, TEAL, SAND, GREEN, ROSE, ORANGE]),
        "axes.edgecolor": "#4a4f54",
        "axes.linewidth": LINE_AXIS,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlelocation": "left",
        "axes.titlepad": 5,
        "axes.titleweight": "bold",
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.major.width": LINE_AXIS,
        "ytick.major.width": LINE_AXIS,
        "axes.grid": False,
        "grid.color": FAINT,
        "grid.linewidth": LINE_GRID,
        "legend.frameon": False,
        "lines.linewidth": LINE_DATA,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "hatch.color": NOTE,
        "hatch.linewidth": 0.40,
    })


def panel(ax, letter: str, x: float = -0.14, y: float = 1.08) -> None:
    """8 pt bold uppercase panel label, top-left, white halo."""
    fp = FontProperties(family=FONT, weight="bold", size=FS_PANEL)
    ax.text(
        x, y, letter.upper(), transform=ax.transAxes, fontproperties=fp,
        va="bottom", ha="left", color=INK, clip_on=False, zorder=30,
        path_effects=[
            patheffects.withStroke(linewidth=2.0, foreground="white"),
            patheffects.withStroke(linewidth=0.5, foreground=INK),
        ],
    )


def ygrid(ax) -> None:
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=FAINT, linewidth=LINE_GRID)
    ax.xaxis.grid(False)


def xgrid(ax) -> None:
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=FAINT, linewidth=LINE_GRID)
    ax.yaxis.grid(False)


def finish(fig=None, *, pad=0.42, left=0.14, top=0.92, w_pad=None, h_pad=None) -> None:
    fig = fig or plt.gcf()
    kw = {"pad": pad}
    if w_pad is not None:
        kw["w_pad"] = w_pad
    if h_pad is not None:
        kw["h_pad"] = h_pad
    fig.tight_layout(**kw)
    p = fig.subplotpars
    fig.subplots_adjust(left=max(p.left, left), top=min(p.top, top))


def save(path: str | Path, fig=None) -> Path:
    """Save PNG (600 dpi) + PDF vector twin."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = fig or plt.gcf()
    stem = path.with_suffix("")
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=DPI_PNG, pad_inches=PAD_INCHES, facecolor="white")
    fig.savefig(pdf, pad_inches=PAD_INCHES, facecolor="white")
    return png


def callout_box(ax, x, y, text: str, *, width=0.36, height=0.10, facecolor="#FFF8E8",
                edgecolor=ORANGE, fontsize=FS_BODY - 0.5, transform=None):
    """Rounded annotation callout in axes fraction coords."""
    transform = transform or ax.transAxes
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        transform=transform,
        facecolor=facecolor, edgecolor=edgecolor, linewidth=0.8,
        clip_on=False, zorder=25,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2, y + height / 2, text,
        transform=transform, ha="center", va="center",
        fontsize=fontsize, color=INK, linespacing=1.25, zorder=26,
    )


def donut(ax, sizes, labels, colors, *, center_text: str = "", startangle=90):
    """Publication donut with external percent labels."""
    wedges, _ = ax.pie(
        sizes, labels=None, colors=colors,
        startangle=startangle, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.5),
    )
    total = sum(sizes)
    for w, lab, val in zip(wedges, labels, sizes):
        ang = np.deg2rad((w.theta2 + w.theta1) / 2)
        r = 0.78
        ax.text(r * np.cos(ang), r * np.sin(ang), f"{lab}\n{val:,}",
                ha="center", va="center", fontsize=FS_BODY - 0.5, color=INK)
    if center_text:
        ax.text(0, 0, center_text, ha="center", va="center",
                fontsize=FS_BODY, fontweight="bold", color=INK)
    return wedges


def forest_row(ax, y, rate, lo, hi, *, color=BLUE, marker="o", label="", n_text=""):
    """Single forest-plot row with Wilson CI."""
    ax.plot([lo, hi], [y, y], color=INK, lw=1.0, zorder=2)
    ax.plot(rate, y, marker=marker, color=color, markersize=5.5, zorder=3,
            markeredgecolor="white", markeredgewidth=0.6)
    if label:
        ax.text(-0.005, y, label, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=FS_BODY - 0.5, color=INK)
    if n_text:
        ax.text(max(hi, rate) + 0.006, y, n_text, transform=ax.transData,
                ha="left", va="center", fontsize=FS_BODY - 0.5, color=NOTE)


def watermark(fig, text: str = "Automated checks only — not human expert audit") -> None:
    fig.text(0.01, 0.008, text, fontsize=FS_BODY - 1, color=NOTE, style="italic")


def suptitle(fig, text: str, y: float = 0.98) -> None:
    fig.suptitle(text, x=0.01, y=y, ha="left", fontsize=FS_EMPH,
                 fontweight="bold", color=INK)
