#!/usr/bin/env python3
"""Shared figure system — one typographic + colour language for every panel.

Design brief (Nature / Cell / Science grade):
  • One typeface, one type scale, one ink weight everywhere.
  • Paul Tol *Vibrant* qualitative scheme (SRON; colourblind-safe, print-tuned) —
    not raw Okabe–Ito. Wong 2011 is the accessibility textbook; Tol Vibrant is what
    high-end Nature/Science figure desks actually favour: deeper blue, teal good-
    mark, print-friendly orange/red, less "default colourblind Excel" sheen.
  • No top/right spines; ticks out; whisper-faint reference grid on the VALUE axis only.
  • Direct labels preferred over legends; when a legend is needed, identical styling.
  • Fixed column widths so on-page type size never drifts between figures.
  • One save path (standard bbox + fixed pad) so whitespace is coherent.

SEMANTIC PALETTE — never reassign by convenience:
  BLUE    primary series / main metric (exact top-1; reference model)
  SKY     secondary / broader series (recovered top-3; candidate-recall pool)
  ORANGE  the single highlighted "hero" element per figure
  GREEN   CORRECT / true / selected / verified  (Tol teal)
  VERMIL  WRONG / rejected / failure-mode
  MUTED   baseline / de-emphasised / gated-out
  NOTE    in-plot explanatory text (~57% black; survives print)
  GHOST   reference overlay behind coloured marks (spectra, baselines)

Import, call apply(), use palette + helpers. Prefer save() over raw plt.savefig.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.font_manager import FontProperties

# ---- Paul Tol Vibrant core + Nature-desk secondary ---------------------------
# Primary/hero/good/bad from Tol Vibrant (SRON). Secondary is a *same-hue* light
# companion to BLUE rather than Tol's neon cyan (#33BBEE): paired bars then read as
# one family at two weights, which is what high-end Nature/Science plates do.
INK    = "#1a1a1a"   # text / spines (near-black, not pure #000)
MUTED  = "#9aa0a6"   # de-emphasised bars (darker than Tol's #BBB so bars hold on white)
NOTE   = "#5c636a"   # in-plot annotations (readable grey)
FAINT  = "#e0e0e0"   # whisper gridlines only
GHOST  = "#c5c9cd"   # reference overlays (ghosted spectra, soft rules)
BLUE   = "#0077BB"   # primary   (Tol vibrant blue)
SKY    = "#6BAFD4"   # secondary (same-hue light companion — not neon cyan)
GREEN  = "#009988"   # correct   (Tol vibrant teal)
VERMIL = "#CC3311"   # wrong     (Tol vibrant red)
ORANGE = "#EE7733"   # hero      (Tol vibrant orange)
PURPLE = "#EE3377"   # spare     (Tol vibrant magenta)

PRIMARY, SECONDARY, ACCENT, GOOD, BAD = BLUE, SKY, ORANGE, GREEN, VERMIL

# ---- canonical sizes (inches) ------------------------------------------------
# Author EVERY chart at exactly one of these so type prints at one physical size.
COL1 = 3.30          # single column (~85 mm)
COL2 = 6.30          # full text width
H1   = 2.70          # default single-panel height
H2   = 3.15          # default two-panel height
SINGLE = (COL1, H1)
DOUBLE = (COL2, H2)

# ---- type scale (points) — nothing below the print floor ---------------------
# Printed at authored COL width (no downscaling). 8 pt body survives photocopy;
# panel letters are a full step above so a/b/c read as letters, not tick labels.
FS_BODY  = 8         # axis labels, ticks, most text
FS_SMALL = 8         # secondary annotations (role via NOTE colour, not size)
FS_PANEL = 12        # bold panel letters (a, b, c) — one step above body, stroked
FS_EMPH  = 10        # rare emphasised figure hierarchy

# ---- geometry tokens (shared bar / mark / dash language) ---------------------
BAR_W       = 0.58   # single-series vertical bar width
BAR_H       = 0.58   # single-series horizontal bar height
GROUP_C     = 0.38   # centre-to-centre of a paired group
GROUP_W     = 0.34   # width of each bar in a paired group
ERR         = dict(lw=0.85, ecolor=INK, capthick=0.85, capsize=2.4)
REF_LS      = (0, (3.2, 2.4))   # dashed reference lines
REF_LW      = 0.75
STICK_LW    = 1.70   # NMR stick spectra
MARKER      = 5.5
LINE_W      = 1.50
PAD_INCHES  = 0.05   # identical outer whitespace on every saved PNG
DPI_SAVE    = 600


def apply():
    """Install the house style. Self-contained — no SciencePlots dependency."""
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": DPI_SAVE,
        # "standard" = fixed figsize (Nature-grade: type size stays honest across figures).
        # Pass this ONLY via rcParams — savefig(bbox_inches="standard") raises on mpl≥3.8.
        "savefig.bbox": "standard",
        "savefig.pad_inches": PAD_INCHES,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "font.family": "sans-serif",
        # Liberation Sans: Helvetica metric-compatible, full Regular/Bold/Italic, and
        # the ≤ ≥ − glyphs the tick labels need (Noto Sans is missing those codepoints).
        "font.sans-serif": [
            "Liberation Sans", "Noto Sans", "Helvetica", "Arial", "DejaVu Sans",
        ],
        "mathtext.fontset": "custom",
        "mathtext.rm": "Liberation Sans",
        "mathtext.it": "Liberation Sans:italic",
        "mathtext.bf": "Liberation Sans:bold",
        "mathtext.default": "regular",
        "mathtext.fallback": "stix",
        "axes.prop_cycle": mpl.cycler(
            color=[BLUE, ORANGE, GREEN, SKY, VERMIL, PURPLE]),
        "font.size": FS_BODY,
        "axes.titlesize": FS_BODY,
        "axes.labelsize": FS_BODY,
        "xtick.labelsize": FS_BODY,
        "ytick.labelsize": FS_BODY,
        "legend.fontsize": FS_BODY,
        "axes.edgecolor": INK,
        "axes.linewidth": 0.70,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlelocation": "left",
        "axes.titlepad": 4.5,
        "axes.titleweight": "normal",
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.labelpad": 3.0,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.top": False,
        "ytick.right": False,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "xtick.major.pad": 2.8,
        "ytick.major.pad": 2.8,
        "axes.grid": False,
        "grid.color": FAINT,
        "grid.linewidth": 0.55,
        "legend.frameon": False,
        "legend.handlelength": 1.15,
        "legend.handletextpad": 0.45,
        "legend.labelspacing": 0.32,
        "legend.borderaxespad": 0.35,
        "legend.columnspacing": 1.0,
        "lines.linewidth": LINE_W,
        "lines.markersize": MARKER,
        "lines.solid_capstyle": "round",
        "patch.linewidth": 0,
        "hatch.linewidth": 0.55,
        "pdf.fonttype": 42,                  # editable text in Illustrator
        "ps.fonttype": 42,
    })


def ygrid(ax):
    """Whisper-faint y-only reference lines (for vertical-value charts)."""
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=FAINT, linewidth=0.55)
    ax.xaxis.grid(False)


def xgrid(ax):
    """Whisper-faint x-only reference lines (for horizontal-value charts)."""
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=FAINT, linewidth=0.55)
    ax.yaxis.grid(False)


def panel(ax, letter, x=0.02, y=0.98, ha="left", va="top"):
    """Heavy panel letter, *inside* the axes (top-left by default).

    Letters placed in negative axes-fraction were clipped by savefig.bbox='standard'
    — only a sliver of the glyph survived, which read as a faint un-bold 'a'.
    """
    fp = FontProperties(family="Liberation Sans", weight="bold", size=FS_PANEL)
    ax.text(x, y, letter, transform=ax.transAxes, fontproperties=fp,
            va=va, ha=ha, color=INK, clip_on=False, zorder=10,
            path_effects=[patheffects.withStroke(linewidth=0.85, foreground=INK)])


def barlabels(ax, bars, fmt="{:.0f}", dy=1.0, size=FS_BODY, color=None):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + dy,
                fmt.format(b.get_height()),
                ha="center", va="bottom", fontsize=size, color=color or INK)


def legend(ax, **kwargs):
    """Identical legend chrome everywhere (callers only pick loc / ncol / handles)."""
    kw = dict(frameon=False, handlelength=1.15, handletextpad=0.45,
              labelspacing=0.32, borderaxespad=0.35, fontsize=FS_BODY)
    kw.update(kwargs)
    return ax.legend(**kw)


def refline(ax, y=None, x=None, **kwargs):
    """Muted dashed reference rule (shared dash pattern + weight)."""
    kw = dict(color=MUTED, lw=REF_LW, ls=REF_LS, zorder=2)
    kw.update(kwargs)
    if y is not None:
        return ax.axhline(y, **kw)
    if x is not None:
        return ax.axvline(x, **kw)
    raise ValueError("refline requires y= or x=")


def finish(fig=None, pad=0.35, w_pad=None, h_pad=None):
    """Standard outer padding before save — one tight_layout call everywhere."""
    fig = fig or plt.gcf()
    kw = dict(pad=pad)
    if w_pad is not None:
        kw["w_pad"] = w_pad
    if h_pad is not None:
        kw["h_pad"] = h_pad
    fig.tight_layout(**kw)


def key_row(ax, labels, y, x0=0, x1=1, transform=None, **text_kw):
    """Place labels in equal columns on one baseline (Fig 1 key-row language)."""
    n = len(labels)
    transform = transform or ax.transAxes
    defaults = dict(ha="center", va="center", fontsize=FS_BODY, color=NOTE)
    defaults.update(text_kw)
    for i, lab in enumerate(labels):
        x = x0 + (x1 - x0) * (2 * i + 1) / (2 * n)
        ax.text(x, y, lab, transform=transform, **defaults)


def reflabel(ax, y, text, x=0.99, ha="right", va="bottom", color=None, dy_frac=0.012):
    """Inline label on a horizontal reference — no leader line."""
    y0, y1 = ax.get_ylim()
    ax.text(x, y + dy_frac * (y1 - y0), text, transform=ax.get_yaxis_transform(),
            ha=ha, va=va, fontsize=FS_BODY, color=color or NOTE, clip_on=False)


def barlabels_inside(ax, bars, fmt="{:.0f}", color="white", min_h_frac=0.08):
    """White in-bar value labels (Fig 1 segment language). Skips bars too thin."""
    y0, y1 = ax.get_ylim()
    thresh = y0 + min_h_frac * (y1 - y0)
    for b in bars:
        h = b.get_height()
        if h < thresh:
            continue
        ax.text(b.get_x() + b.get_width() / 2, h / 2, fmt.format(h),
                ha="center", va="center", fontsize=FS_BODY, fontweight="bold",
                color=color, zorder=5)


def twin_panel(figsize=None, width_ratios=None, w_pad=1.4):
    """Two-panel row with shared height token and consistent inter-panel gap."""
    kw = dict(figsize=figsize or (COL2, H2))
    if width_ratios:
        kw["gridspec_kw"] = {"width_ratios": width_ratios}
    fig, axes = plt.subplots(1, 2, **kw)
    return fig, axes[0], axes[1]


def save(path, fig=None):
    """One save path: fixed pad, no tight crop, 600 dpi PNG + vector PDF twin.

    Do not pass bbox_inches here — mpl≥3.8 rejects the rc alias "standard" as a
    kwarg. apply() sets savefig.bbox='standard' so the authored figsize is preserved.

    The PDF twin is what LaTeX embeds (crisp type at any zoom). The PNG stays for
    Overleaf preview and markdown viewers that cannot render PDF images.
    """
    fig = fig or plt.gcf()
    fig.savefig(path, dpi=DPI_SAVE, pad_inches=PAD_INCHES, facecolor="white")
    if path.lower().endswith(".png"):
        fig.savefig(path[:-4] + ".pdf", pad_inches=PAD_INCHES, facecolor="white")
