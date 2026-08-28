#!/usr/bin/env python3
"""Nature / NMRexp design system — locked palette, typography, export for IRexp Sci Data.

Reference: Wang et al., NMRexp, Sci Data 12:1954 (2025).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

# ---- Nature dimensions (inches) -----------------------------------------------
MM_PER_IN = 25.4
COL_SINGLE = 89 / MM_PER_IN
COL_FULL = 183 / MM_PER_IN
MAX_HEIGHT = 247 / MM_PER_IN

# ---- NMRexp-matched palette (Fig 1–4 reference) ------------------------------
INK = "#1a1a1a"
MUTED = "#7a7f85"
NOTE = "#5c636a"
FAINT = "#e8eaec"
GHOST = "#c5c9cd"

# NMRexp bar blues (Fig 1 & 3)
NMREXP_BLUE = "#4A7EBB"       # primary horizontal bars / histograms
NMREXP_BLUE_DARK = "#2E5F8F"  # 3D total bar / header navy
NMREXP_BLUE_LIGHT = "#A8C8E8" # stack: structure-linked / ¹H analogue
NMREXP_PEACH = "#E8B48C"      # stack: commercial / ¹³C analogue
NMREXP_NAVY = "#1B3D5C"       # ¹⁹F / accent dark
NMREXP_PINK = "#D4A0B8"       # ³¹P analogue
NMREXP_MAROON = "#8B3A3A"     # ¹¹B analogue
NMREXP_RED = "#C44E52"        # ²⁹Si / emphasis

HERO = NMREXP_BLUE
SECONDARY = NMREXP_BLUE_LIGHT
TEAL = "#66A8C8"
SAND = "#CCBB44"
ROSE = "#AA3377"
GREEN = "#3D8B5E"
GREY = "#BBBBBB"
ORANGE = "#D97B32"
VIEW_ONLY = GREY
FAIL = NMREXP_RED
PASS = GREEN

TINT_BLUE = "#EEF3F8"
TINT_GREEN = "#EAF4EE"
TINT_GREY = "#F3F4F5"
TINT_SAND = "#FAF6E8"

# ---- Typography --------------------------------------------------------------
FONT = "Liberation Sans"
FS_MIN = 5
FS_BODY = 7
FS_AXIS = 7
FS_LABEL = 7
FS_PANEL = 8
FS_TITLE = 8
FS_EMPH = 8

LINE_AXIS = 0.50
LINE_GRID = 0.40
LINE_DATA = 1.00
PAD_INCHES = 0.04
DPI_PNG = 600

COL1 = fs.COL1
COL2 = fs.COL2


def apply() -> None:
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
        "axes.prop_cycle": mpl.cycler(color=[HERO, TEAL, SAND, GREEN, ROSE, ORANGE]),
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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = fig or plt.gcf()
    stem = path.with_suffix("")
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=DPI_PNG, pad_inches=PAD_INCHES, facecolor="white")
    fig.savefig(pdf, pad_inches=PAD_INCHES, facecolor="white")
    return png


def hbar_panel(ax, labels, values, *, title: str = "", xlabel: str = "",
               color=HERO, label_fmt: str = "{:,}", invert: bool = True) -> None:
    """NMRexp Fig 3 style horizontal bar chart — counts at bar ends, faint y-grid."""
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=color, height=0.62, edgecolor="white",
                   linewidth=0.6, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=FS_BODY)
    if invert:
        ax.invert_yaxis()
    ygrid(ax)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(INK)
    ax.spines["left"].set_linewidth(0.6)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.set_xlim(0, max(values) * 1.18)
    for b, v in zip(bars, values):
        ax.text(b.get_width() + max(values) * 0.012,
                b.get_y() + b.get_height() / 2,
                label_fmt.format(v), ha="left", va="center",
                fontsize=FS_BODY - 0.5, color=INK)
    if title:
        ax.set_title(title, loc="center", pad=6, fontsize=FS_TITLE, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FS_AXIS)


def _shade(hex_color: str, factor: float) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_iso_bar(ax, cx: float, base_y: float, w: float, d: float, h: float,
                 color: str, zorder: int = 2, alpha: float = 1.0) -> None:
    """Fake-isometric 3D bar (NMRexp Fig 1 style) in 2D axes coords."""
    hw, hd = w / 2, d / 2
    # floor diamond corners
    bl = (cx - hw, base_y)
    br = (cx + hw, base_y)
    fr = (cx + hw + hd, base_y + hd * 0.55)
    fl = (cx - hw + hd, base_y + hd * 0.55)
    top_off = h  # h already in axis data coordinates

    def lift(pt, dz):
        return (pt[0], pt[1] + dz)

    bl_t, br_t, fr_t, fl_t = [lift(p, top_off) for p in (bl, br, fr, fl)]

    # right face (darker)
    ax.add_patch(Polygon([br, fr, lift(fr, top_off), lift(br, top_off)],
                         closed=True, facecolor=_shade(color, 0.72),
                         edgecolor=_shade(color, 0.55), linewidth=0.4,
                         zorder=zorder, alpha=alpha))
    # left face (medium)
    ax.add_patch(Polygon([bl, fl, fl_t, bl_t],
                         closed=True, facecolor=_shade(color, 0.85),
                         edgecolor=_shade(color, 0.65), linewidth=0.4,
                         zorder=zorder + 1, alpha=alpha))
    # top face (lightest)
    ax.add_patch(Polygon([bl_t, br_t, fr_t, fl_t],
                         closed=True, facecolor=color,
                         edgecolor=_shade(color, 0.75), linewidth=0.5,
                         zorder=zorder + 2, alpha=alpha))


def annotation_elbow(ax, x_val: float, y_frac: float, label: str, *,
                     xlim: tuple, color: str = NOTE, fontsize: float | None = None):
    """NMRexp Fig 4 dashed elbow annotation to x-axis value."""
    fontsize = fontsize or FS_BODY - 0.5
    x0, x1 = xlim
    x_norm = (x_val - x0) / (x1 - x0)
    ax.plot([x_val, x_val], [0, y_frac * ax.get_ylim()[1]], color=color,
            lw=0.6, ls=(0, (3, 2)), zorder=4, clip_on=False)
    ax.text(x_val, y_frac * ax.get_ylim()[1] * 1.02, label,
            ha="left", va="bottom", fontsize=fontsize, fontweight="bold",
            color=INK, zorder=5)


def forest_row(ax, y, rate, lo, hi, *, color=HERO, marker="o", label="", n_text=""):
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


def sidebar_callout(ax, x: float, y: float, w: float, h: float, *,
                    header: str, bullets: list[str], header_color=NMREXP_BLUE_DARK):
    """NMRexp Fig 1 sidebar highlight box."""
    shadow = FancyBboxPatch(
        (x + 0.008, y - 0.012), w, h,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=ax.transAxes, facecolor="#D0D5DA", edgecolor="none",
        linewidth=0, zorder=8, clip_on=False,
    )
    ax.add_patch(shadow)
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        transform=ax.transAxes, facecolor="white", edgecolor=GHOST,
        linewidth=0.8, zorder=9, clip_on=False,
    )
    ax.add_patch(box)
    hdr_h = 0.055
    ax.add_patch(FancyBboxPatch(
        (x, y + h - hdr_h), w, hdr_h,
        boxstyle="square,pad=0", transform=ax.transAxes,
        facecolor=header_color, edgecolor="none", zorder=10, clip_on=False,
    ))
    ax.text(x + w / 2, y + h - hdr_h / 2, header, transform=ax.transAxes,
            ha="center", va="center", fontsize=FS_BODY, fontweight="bold",
            color="white", zorder=11)
    for i, bullet in enumerate(bullets):
        ax.text(x + 0.02, y + h - hdr_h - 0.04 - i * 0.065, "+",
                transform=ax.transAxes, ha="left", va="top",
                fontsize=FS_BODY, fontweight="bold", color=header_color, zorder=11)
        ax.text(x + 0.04, y + h - hdr_h - 0.04 - i * 0.065, bullet,
                transform=ax.transAxes, ha="left", va="top",
                fontsize=FS_BODY - 0.5, color=INK, linespacing=1.3, zorder=11)
