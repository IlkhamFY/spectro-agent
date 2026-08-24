#!/usr/bin/env python3
"""Hero figure — the diagnosis as a single part-to-whole bar of the WHOLE
194-compound benchmark. Of 194 real spectra the true structure is verified top-1
for 58 (green), recalled but mis-ranked for 7 (vermilion), and never proposed for
129 (grey) — "the wall", 66% of the bar."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

N = 194
VERIFIED, MISRANKED, WALL = 58, 7, 129
RECALLED = VERIFIED + MISRANKED

GAP = 0.55
segs = [(0, VERIFIED, fs.GREEN),
        (VERIFIED, MISRANKED, fs.VERMIL),
        (RECALLED, WALL, fs.MUTED)]

fig = plt.figure(figsize=(fs.COL2, 1.72))
ax = fig.add_axes([0.02, 0.04, 0.96, 0.92])
ax.set_xlim(-1.5, N + 1.5); ax.set_ylim(-1.2, 2.25); ax.axis("off")

Y0, H = 0.0, 1.0
for x, w, col in segs:
    ax.add_patch(plt.Rectangle((x + GAP, Y0), w - GAP, H,
                 facecolor=col, edgecolor="none", linewidth=0))

bx0, bx1, by = 0 + GAP, RECALLED, 1.32
ax.plot([bx0, bx0, bx1, bx1], [by - 0.14, by, by, by - 0.14],
        color=fs.INK, lw=0.85, solid_capstyle="butt", solid_joinstyle="miter")
ax.text((bx0 + bx1) / 2, by + 0.1, "65 recalled = 34% \u2013 of these, 89% verify",
        ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.INK)

def below(xc, n, word, col, y1=-0.22):
    ax.text(xc, y1, n, ha="center", va="top", fontsize=fs.FS_EMPH,
            fontweight="bold", color=col)
    ax.text(xc, y1 - 0.58, word, ha="center", va="top", fontsize=fs.FS_BODY, color=col)

below(VERIFIED / 2, "58", "verified — 30% top-1", fs.GREEN)
below(RECALLED + WALL / 2, "129", "never proposed — “the wall”", fs.INK)

ax.add_patch(FancyArrowPatch((RECALLED - MISRANKED / 2, 1.0), (RECALLED + 13, 1.68),
             arrowstyle="-", lw=0.65, color=fs.VERMIL, shrinkA=0, shrinkB=2))
ax.text(RECALLED + 14.5, 1.72, "7 mis-ranked", ha="left", va="center",
        fontsize=fs.FS_BODY, color=fs.VERMIL)

ax.text(-0.5, 2.18, "194 real spectra", ha="left", va="top",
        fontsize=fs.FS_BODY, color=fs.NOTE)

fs.save("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
