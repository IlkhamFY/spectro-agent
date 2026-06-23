#!/usr/bin/env python3
"""Shared figure style — one restrained, Nature-grade look so every figure reads as
hand-crafted, not tool-default. Import, call apply(), use the palette + helpers.
Palette: Okabe-Ito colourblind-safe (Wong, Nat. Methods 2011). Font: Liberation Sans
(metric-compatible with Helvetica/Arial). Rules: no top/right spines, ticks out, faint
y-grid for bars only, direct labels over legends, generous whitespace."""
import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe-Ito, colourblind-safe
INK    = "#222222"   # text / spines (never pure black)
MUTED  = "#9aa0a6"   # de-emphasised text, n= labels, reference series
FAINT  = "#e6e6e6"   # barely-there gridlines
BLUE   = "#0072B2"   # PRIMARY: exact top-1 (the headline metric)
SKY    = "#56B4E9"   # secondary: recovered / top-3
GREEN  = "#009E73"   # correct / selected / verified
VERMIL = "#D55E00"   # wrong / rejected (pair with an X glyph)
ORANGE = "#E69F00"   # single highlight (the hero bar/point)
PURPLE = "#CC79A7"   # spare 5th category

# semantic aliases
PRIMARY, SECONDARY, ACCENT, GOOD, BAD = BLUE, SKY, ORANGE, GREEN, VERMIL

SINGLE  = (3.35, 2.6)
ONEHALF = (5.0, 3.0)
DOUBLE  = (7.0, 3.2)

def apply():
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "Helvetica", "Arial", "FreeSans"],
        "font.size": 7,
        "axes.titlesize": 8, "axes.labelsize": 7.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.5,
        "axes.edgecolor": INK, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlelocation": "left", "axes.titlepad": 7, "axes.titleweight": "bold",
        "axes.labelcolor": INK, "axes.titlecolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.8, "ytick.major.width": 0.8,
        "axes.grid": False, "legend.frameon": False,
        "lines.linewidth": 1.6, "lines.markersize": 5, "patch.linewidth": 0,
    })

def ygrid(ax):
    """Faint y-only gridline behind bars."""
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=FAINT, linewidth=0.6)
    ax.xaxis.grid(False)

def panel(ax, letter, x=-0.16, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=8, fontweight="bold",
            va="bottom", ha="left", color=INK)

def barlabels(ax, bars, fmt="{:.0f}", dy=1.0, size=6.5, color=None):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + dy, fmt.format(b.get_height()),
                ha="center", va="bottom", fontsize=size, color=color or INK)
