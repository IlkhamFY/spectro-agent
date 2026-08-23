#!/usr/bin/env python3
"""Shared figure style — SciencePlots' Nature base (garrettj403) plus a strict,
colourblind-safe Okabe-Ito semantic palette, so every figure in the paper reads as one
system. Import, call apply(), use the palette + helpers.

SEMANTIC PALETTE — one colour means ONE thing, everywhere (Wong, Nat. Methods 2011;
Okabe-Ito). Never assign these colours by any other logic:
  BLUE   primary series / main metric (exact top-1; the reference model in a comparison)
  SKY    secondary/broader series (recovered top-3; candidate-recall pool)
  ORANGE the single highlighted "hero" element per figure (Fable; the GNN result)
  GREEN  a CORRECT / true / selected / verified outcome
  VERMIL a WRONG / rejected / failure-mode outcome
  MUTED  baseline / reference / de-emphasised steps
  NOTE   in-plot explanatory text (a darker grey than MUTED: a 7 pt annotation set
         in MUTED is ~34% black and dissolves on paper; NOTE is ~57%)
Rules: sans-serif (Helvetica-class), 7 pt text and nothing smaller, no top/right
spines, ticks out, whisper-faint y-grid for bars only, direct labels over legends,
no in-panel titles."""
import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe-Ito, colourblind-safe (hex per Wong 2011)
INK    = "#222222"   # text / spines (never pure black)
MUTED  = "#9aa0a6"   # de-emphasised text, n= labels, baseline series
NOTE   = "#5f6368"   # in-plot annotations: grey, but >=50% black so it survives print
FAINT  = "#e6e6e6"   # barely-there gridlines
BLUE   = "#0072B2"   # primary series / main metric
SKY    = "#56B4E9"   # secondary / broader series
GREEN  = "#009E73"   # correct / selected / verified
VERMIL = "#D55E00"   # wrong / rejected
ORANGE = "#E69F00"   # the one hero highlight per figure
PURPLE = "#CC79A7"   # spare 5th category

# semantic aliases
PRIMARY, SECONDARY, ACCENT, GOOD, BAD = BLUE, SKY, ORANGE, GREEN, VERMIL

# ---- canonical column widths (inches) -------------------------------------
# Every figure is authored at exactly ONE of these so, placed 1:1 in the PDF,
# their type renders at an identical physical size. No in-between widths.
COL1 = 3.30    # single column (~85 mm)
COL2 = 6.30    # full width  (== \textwidth at 1-in margins)
SINGLE  = (3.30, 2.5)
DOUBLE  = (6.30, 3.0)

# ---- type scale (points) --------------------------------------------------
# The ONLY sizes any figure may use, so text is coherent across the whole set.
FS_BODY  = 7    # axis labels, tick labels, most text
# The "secondary" tier is a role, not a smaller size. Every figure is placed 1:1, so a
# 6 pt annotation printed at 6 pt -- under the 7 pt floor for this page, below the 10 pt
# captions and smaller than the tick labels beside it. Secondary marks are now separated
# by COLOUR (NOTE grey) and position, never by dropping below the floor.
FS_SMALL = 7    # secondary annotations, n= notes -- at the print floor, same as body
FS_PANEL = 8    # bold panel letters (a, b, c)
FS_EMPH  = 9    # a single emphasised figure where hierarchy genuinely helps

def apply():
    # Cutting-edge journal base: SciencePlots' Nature style (thin lines, 7 pt, tight),
    # then our Helvetica-class font + Okabe-Ito overrides on top.
    try:
        import scienceplots  # noqa: F401
        plt.style.use(["science", "nature", "no-latex"])
    except Exception:
        pass
    mpl.rcParams.update({
        # Force "standard" (NOT "tight") to override SciencePlots' nature style, which
        # sets bbox=tight. A tight bbox trims each figure to its own content, so the
        # placed width — and thus on-page type size — drifts per figure. With "standard"
        # the saved size == figsize exactly, so authoring at COL1/COL2 gives identical
        # on-page type everywhere.
        "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "standard",
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "Helvetica", "Arial", "FreeSans"],
        "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans",
        "mathtext.it": "Liberation Sans:italic", "mathtext.bf": "Liberation Sans:bold",
        "axes.prop_cycle": mpl.cycler(color=[BLUE, ORANGE, GREEN, SKY, VERMIL, PURPLE]),
        "font.size": 7,
        "axes.titlesize": 7, "axes.labelsize": 7,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": FS_BODY,
        "axes.edgecolor": INK, "axes.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlelocation": "left", "axes.titlepad": 5, "axes.titleweight": "normal",
        "axes.labelcolor": INK, "axes.titlecolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.top": False, "ytick.right": False,          # SciencePlots turns these on
        "xtick.minor.visible": False, "ytick.minor.visible": False,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.major.pad": 2.5, "ytick.major.pad": 2.5,
        "axes.grid": False, "legend.frameon": False, "legend.handlelength": 1.1,
        "legend.handletextpad": 0.5, "legend.labelspacing": 0.35,
        "lines.linewidth": 1.2, "lines.markersize": 4, "patch.linewidth": 0,
    })

def ygrid(ax):
    """Whisper-faint y-only reference lines behind bars (Nature: minimal)."""
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=FAINT, linewidth=0.4)
    ax.xaxis.grid(False)

def panel(ax, letter, x=-0.16, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=FS_PANEL, fontweight="bold",
            va="bottom", ha="left", color=INK)

def barlabels(ax, bars, fmt="{:.0f}", dy=1.0, size=FS_BODY, color=None):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + dy, fmt.format(b.get_height()),
                ha="center", va="bottom", fontsize=size, color=color or INK)
