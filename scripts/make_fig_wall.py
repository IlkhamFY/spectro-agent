#!/usr/bin/env python3
"""Hero figure (Fig 1) — the diagnosis as a single part-to-whole bar of all 60
forward-verify compounds, so the denominators are shown, not asserted. Of 60 real
spectra the true structure is verified top-1 for 16 (green), recalled but mis-ranked
for 3 (vermilion), and never proposed for 41 (grey) — "the wall", 68% of the bar.
Recall is 19/60 = 31%; of those recalled, 84% verify -> 16/60 = 26% exact top-1.
The point is visual: the wall dominates, so recall (not verification) is the limit."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

GAP = 0.14                     # white surface gap between segments (~2 px at 600 dpi)
segs = [(0, 16, fs.GREEN, "verified"),
        (16, 3, fs.VERMIL, "mis-ranked"),
        (19, 41, fs.MUTED, "never proposed")]

fig = plt.figure(figsize=(fs.COL2, 1.95))
ax = fig.add_axes([0.015, 0.06, 0.97, 0.9])
ax.set_xlim(-0.4, 60.4); ax.set_ylim(-1.65, 2.25); ax.axis("off")

Y0, H = 0.0, 1.0
for x, w, col, _ in segs:
    ax.add_patch(plt.Rectangle((x + GAP, Y0), w - GAP, H, facecolor=col, edgecolor="none"))

# bracket over the 19 recalled (green + vermilion), the key sub-total
bx0, bx1, by = 0 + GAP, 19, 1.28
ax.plot([bx0, bx0, bx1, bx1], [by - 0.12, by, by, by - 0.12], color=fs.INK, lw=0.8)
ax.text((bx0 + bx1) / 2, by + 0.08, "19 recalled = 31%   ·   of these, 84% verify",
        ha="center", va="bottom", fontsize=fs.FS_SMALL, color=fs.INK)

# segment labels below, aligned to each segment's centre
def below(xc, n, word, col, y1=-0.2):
    ax.text(xc, y1, n, ha="center", va="top", fontsize=fs.FS_EMPH, fontweight="bold", color=col)
    ax.text(xc, y1 - 0.62, word, ha="center", va="top", fontsize=fs.FS_BODY, color=col)

below(8, "16", "verified — 26% top-1", fs.GREEN)
below(39.5, "41", "never proposed — “the wall”", fs.INK)

# the narrow mis-ranked segment: a short leader out to a clear label
ax.add_patch(FancyArrowPatch((17.5, 1.0), (23.5, 1.62), arrowstyle="-",
             lw=0.6, color=fs.VERMIL, shrinkA=0, shrinkB=2))
ax.text(23.9, 1.66, "3 mis-ranked", ha="left", va="center",
        fontsize=fs.FS_SMALL, color=fs.VERMIL)

ax.text(-0.2, 2.12, "60 real spectra", ha="left", va="top", fontsize=fs.FS_SMALL, color=fs.MUTED)

plt.savefig("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
