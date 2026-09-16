#!/usr/bin/env python3
"""Fig 1 — diagnosis plate (the leading figure).

Design rules for this plate (it is the paper's first visual):
  • The grey mass is the claim. Do not decorate around it.
  • Counts live once — inside the segments (white).
  • Category names live once — centred under each segment on one baseline.
    Colours are learned from the bar; the key does not repeat swatches.
  • One bracket names the recalled pool. Nothing else floats.
  • n and the 89% verification rate belong in the caption, not here.

Counts come from data/diagnosis.json, written by scripts/forward_verify_all.py. They
were literals here until the cohort could grow, which would have left the paper's first
visual quietly disagreeing with the numbers underneath it.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import figstyle as fs

fs.apply()

D = json.load(open("data/diagnosis.json"))
N = D["n"]
VERIFIED, MISRANKED, WALL = D["verified"], D["misranked"], D["wall"]
RECALLED = VERIFIED + MISRANKED
assert VERIFIED + MISRANKED + WALL == N, f"segments do not sum to n={N}"

# Wall fill is darker than MUTED chart baselines: it must carry white type and read
# as the dominant mass, not as a de-emphasised series.
WALL_FILL = "#5f6670"
GAP = 0.6
segs = [
    (0,        VERIFIED,  fs.GREEN,  str(VERIFIED)),
    (VERIFIED, MISRANKED, fs.VERMIL, str(MISRANKED)),
    (RECALLED, WALL,      WALL_FILL, str(WALL)),
]
labels = ["verified", "mis-ranked", "never proposed"]

fig = plt.figure(figsize=(fs.COL2, 1.42))
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
ax.text((bx0 + bx1) / 2, by + 0.022, f"{RECALLED} recalled ({100*RECALLED/N:.0f}%)",
        ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.INK,
        zorder=3, clip_on=False)

# ---- labels: one under each segment (equal columns left "mis-ranked" under the wall)
for (x0, w, _col, _num), lab in zip(segs, labels):
    ax.text(x0 + w / 2, 0.12, lab, ha="center", va="center",
            fontsize=fs.FS_BODY, color=fs.NOTE, clip_on=False)

fs.save("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
