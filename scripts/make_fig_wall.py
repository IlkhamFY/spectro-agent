#!/usr/bin/env python3
"""Hero figure (Fig 1) — the diagnosis as a single part-to-whole bar of the WHOLE
194-compound benchmark, so the denominators are shown, not asserted. Of 194 real
spectra the true structure is verified top-1 for 58 (green), recalled but mis-ranked
for 7 (vermilion), and never proposed for 129 (grey) — "the wall", 66% of the bar.
Recall is 65/194 = 34%; of those recalled, 89% verify -> 58/194 = 30% exact top-1.
The point is visual: the wall dominates, so recall (not verification) is the limit.
Numbers regenerate from `python scripts/forward_verify_all.py`."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

N = 194
VERIFIED, MISRANKED, WALL = 58, 7, 129
RECALLED = VERIFIED + MISRANKED

GAP = 0.45                     # white surface gap between segments (~2 px at 600 dpi)
segs = [(0, VERIFIED, fs.GREEN),
        (VERIFIED, MISRANKED, fs.VERMIL),
        (RECALLED, WALL, fs.MUTED)]

fig = plt.figure(figsize=(fs.COL2, 1.66))
ax = fig.add_axes([0.015, 0.02, 0.97, 0.96])
ax.set_xlim(-1.3, N + 1.3); ax.set_ylim(-1.12, 2.18); ax.axis("off")

Y0, H = 0.0, 1.0
for x, w, col in segs:
    ax.add_patch(plt.Rectangle((x + GAP, Y0), w - GAP, H, facecolor=col, edgecolor="none"))

# bracket over the 65 recalled (green + vermilion), the key sub-total
bx0, bx1, by = 0 + GAP, RECALLED, 1.28
ax.plot([bx0, bx0, bx1, bx1], [by - 0.12, by, by, by - 0.12], color=fs.INK, lw=0.8)
ax.text((bx0 + bx1) / 2, by + 0.08, "65 recalled = 34%   ·   of these, 89% verify",
        ha="center", va="bottom", fontsize=fs.FS_SMALL, color=fs.INK)

# segment labels below, aligned to each segment's centre
def below(xc, n, word, col, y1=-0.2):
    ax.text(xc, y1, n, ha="center", va="top", fontsize=fs.FS_EMPH, fontweight="bold", color=col)
    ax.text(xc, y1 - 0.62, word, ha="center", va="top", fontsize=fs.FS_BODY, color=col)

below(VERIFIED / 2, "58", "verified — 30% top-1", fs.GREEN)
below(RECALLED + WALL / 2, "129", "never proposed — “the wall”", fs.INK)

# the narrow mis-ranked segment: a short leader out to a clear label
ax.add_patch(FancyArrowPatch((RECALLED - MISRANKED / 2, 1.0), (RECALLED + 13, 1.62),
             arrowstyle="-", lw=0.6, color=fs.VERMIL, shrinkA=0, shrinkB=2))
ax.text(RECALLED + 14.3, 1.66, "7 mis-ranked", ha="left", va="center",
        fontsize=fs.FS_SMALL, color=fs.VERMIL)

ax.text(-0.7, 2.12, "194 real spectra", ha="left", va="top",
        fontsize=fs.FS_SMALL, color=fs.MUTED)

plt.savefig("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
