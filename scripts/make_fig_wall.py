#!/usr/bin/env python3
"""Fig 1 — diagnosis plate (the leading figure).

Design rules for this plate (it is the paper's first visual):
  • The grey mass is the claim. Do not decorate around it.
  • Counts live once — inside the segments (white).
  • Category names live once — three equal columns on one baseline below.
    Colours are learned from the bar; the key does not repeat swatches.
  • One bracket names the recalled pool. Nothing else floats.
  • n=194 and the 89% verification rate belong in the caption, not here.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import figstyle as fs

fs.apply()

N = 194
VERIFIED, MISRANKED, WALL = 58, 7, 129
RECALLED = VERIFIED + MISRANKED

# Wall fill is darker than MUTED chart baselines: it must carry white type and read
# as the dominant mass, not as a de-emphasised series.
WALL_FILL = "#5f6670"
GAP = 0.6
segs = [
    (0,        VERIFIED,  fs.GREEN,  "58"),
    (VERIFIED, MISRANKED, fs.VERMIL, "7"),
    (RECALLED, WALL,      WALL_FILL, "129"),
]
labels = ["verified", "mis-ranked", "never proposed"]

fig = plt.figure(figsize=(fs.COL2, 1.28))
ax = fig.add_axes([0.025, 0.02, 0.95, 0.94])
ax.set_xlim(0, N)
ax.set_ylim(0, 1)
ax.axis("off")

# ---- bar --------------------------------------------------------------------
BAR_Y, BAR_H = 0.36, 0.38
for x0, w, col, num in segs:
    ax.add_patch(Rectangle((x0 + GAP / 2, BAR_Y), max(w - GAP, 0.25), BAR_H,
                 facecolor=col, edgecolor="none", linewidth=0, zorder=2))
    xc = x0 + w / 2
    size = fs.FS_BODY if w < 15 else fs.FS_EMPH
    ax.text(xc, BAR_Y + BAR_H / 2, num, ha="center", va="center",
            fontsize=size, fontweight="bold", color="white",
            zorder=5, clip_on=False)

# ---- recall bracket ---------------------------------------------------------
bx0, bx1 = GAP / 2, RECALLED - GAP / 2
by = BAR_Y + BAR_H + 0.06
tick = 0.032
ax.plot([bx0, bx0, bx1, bx1], [by - tick, by, by, by - tick],
        color=fs.INK, lw=0.9, solid_capstyle="butt", solid_joinstyle="miter",
        zorder=3, clip_on=False)
ax.text((bx0 + bx1) / 2, by + 0.022, "65 recalled (34%)",
        ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.INK,
        zorder=3, clip_on=False)

# ---- labels: three equal columns, one baseline ------------------------------
fs.key_row(ax, labels, y=0.12, x0=0, x1=N, transform=ax.transData)

fs.save("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
