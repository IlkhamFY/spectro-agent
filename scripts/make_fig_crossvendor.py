#!/usr/bin/env python3
"""Fig. 7 — every model measured, on one axis where they share a compound set.

Two panels, because two things have to be seen at once and only one of them is the
headline. (a) ranks the models by generation recall on the 60-compound arm and encodes the
formula-adherence gate in the bar colour: a model below the floor is not being measured
on chemistry at all, so its recall is greyed rather than ranked. (b) is the claim itself — recall against
verification precision, with the diagonal. Every point above the line is a vendor for
which verification is better than generation, which is what the paper says and what the
sweep set out to falsify.

The four Claude models of §4.4 are deliberately absent: they ran a different
24-compound subset, and putting them on this axis would imply a comparison that was
never made.

  python scripts/make_fig_crossvendor.py     -> docs/figures/fig7_crossvendor.png
"""
import json, sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "scripts")
import figstyle as fs

fs.apply()

# (label, recall/60, formula-adherence %, precision|recall or None)
MODELS = [
    ("Grok 4.6",          32, 95,  62),
    ("Gemini 3.7 Flash",  30, 94,  73),
    ("GPT-5.6 Sol",       25, 100, 68),
    ("Claude Opus",       19, None, 84),
    ("Composer 2.5",      12, 67,  None),
    ("GPT-5.6 Luna",       9, 76,  None),
    ("DeepSeek V4 Pro",    8, 94,  62),
    ("Nemotron 3.5",       0,  2,  None),
]
GATE = 78          # bottom of Claude's own adherence band (§3)

# Panel (b) carries five direct point labels on a 0-100 square, so it needs the wider
# box: at the old 1.25:1 a 6 pt name spanned half the data range and no single label
# offset could be made to clear both the neighbouring markers and the diagonal.
fig, (ax, bx) = plt.subplots(1, 2, figsize=(fs.COL2, 2.86),
                             gridspec_kw={"width_ratios": [0.82, 1]})

# ---- (a) generation recall, gated by whether the output contract was met -----
PARTIAL = "DeepSeek V4 Pro"        # 18/60 answered: this recall is a lower bound
order = sorted(MODELS, key=lambda m: m[1])
ys = range(len(order))
cols = [fs.MUTED if (m[2] is not None and m[2] < GATE) else
        (fs.ORANGE if m[0] == "Claude Opus" else fs.BLUE) for m in order]
# The incomplete arm is drawn hollow in BOTH panels. It used to be solid here and
# hollow only in (b) -- and (a) is the panel the recall number is actually read off,
# so the caveat has to be attached where the reading happens.
for y, m, c in zip(ys, order, cols):
    part = m[0] == PARTIAL
    ax.barh(y, 100 * m[1] / 60, height=0.62, zorder=3,
            color="white" if part else c, edgecolor=c,
            linewidth=0.9 if part else 0, hatch="////" if part else None)
ax.set_yticks(list(ys)); ax.set_yticklabels([m[0] for m in order])
for y, m in zip(ys, order):
    ax.text(100 * m[1] / 60 + 1.2, y, f"{m[1]}/60",
            va="center", fontsize=fs.FS_SMALL, color=fs.INK)
ax.set_xlabel("generation recall (%)", labelpad=1)
# The same axis label appears under both panels, so it has to mean the same thing in
# both: (a) ran 0-68 while (b) ran 0-100, and a reader who reads a bar's length in (a)
# against the same model's x-position in (b) was reading two different rulers. Same
# range, same ticks.
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.grid(axis="x", color=fs.FAINT, lw=0.5, zorder=0); ax.set_axisbelow(True)
ax.text(-0.42, 1.04, "a", transform=ax.transAxes,
        fontsize=fs.FS_PANEL, fontweight="bold", color=fs.INK)

# ---- (b) the claim: precision above recall ----------------------------------
# Both axes run the full 0-100%: they are the same unit, and the whole panel is a
# comparison against y = x. Cropping to (2-70, 42-100) -- as this panel used to --
# stretches the vertical gaps between models about twice as far as the horizontal
# ones and makes the distance above the diagonal look larger than it is.
bx.plot([0, 100], [0, 100], color=fs.MUTED, lw=0.7, ls="--", zorder=1)
# ONE offset for every point -- 6 pt to the right, vertically centred. The labels
# used to sit right, left and below their markers, with a leader arrow on the
# DeepSeek point that ran into its own label; five different placements read as five
# different meanings. The five models are far enough apart in y that a single
# rightward offset clears every neighbouring marker; where a label crosses the
# y = x rule a white halo keeps both readable.
LBL_DX = 6
for name, r, _adh, p in MODELS:
    if p is None:
        continue
    x = 100 * r / 60
    c = fs.ORANGE if name == "Claude Opus" else fs.BLUE
    partial = name == PARTIAL
    bx.scatter([x], [p], s=26, zorder=4, linewidth=0.9,
               facecolor="white" if partial else c, edgecolor=c,
               hatch="////" if partial else None)
    bx.annotate(name, (x, p), textcoords="offset points", xytext=(LBL_DX, 0),
                fontsize=fs.FS_SMALL, color=fs.INK, ha="left", va="center", zorder=5,
                bbox=dict(fc="white", ec="none", pad=0.8))
bx.set_xlabel("generation recall (%)", labelpad=1)
bx.set_ylabel("verification precision | recall (%)", labelpad=2)
bx.set_xlim(0, 100); bx.set_ylim(0, 100)
bx.set_xticks([0, 25, 50, 75, 100]); bx.set_yticks([0, 25, 50, 75, 100])
bx.text(-0.30, 1.04, "b", transform=bx.transAxes,
        fontsize=fs.FS_PANEL, fontweight="bold", color=fs.INK)

plt.tight_layout(w_pad=1.6)

# The footnote strip that used to run under the panels is gone. Both of its lines said
# what the caption already says -- grey marks a model below the formula-adherence floor
# whose recall is not a chemistry result; hollow/hatched marks an incomplete arm whose
# recall is a lower bound; every point above the line is a vendor where verification
# beats generation -- and the caption says it at 10 pt on the full measure. A 7 pt grey
# restatement under the figure is a second, worse copy of the same key. The 0.34 in the
# strip occupied comes off the figure height, so the panels keep their printed size.

# The diagonal's on-screen angle depends on the final axes box, so label it only after
# tight_layout has settled -- a hardcoded rotation silently goes wrong when it moves.
fig.canvas.draw()
(x0, y0), (x1, y1) = bx.transData.transform([(20, 20), (80, 80)])
# Below the rule, low down: the upper-right stretch is now under the Gemini label.
bx.text(38, 32, "precision = recall", fontsize=fs.FS_SMALL, color=fs.NOTE,
        rotation=np.degrees(np.arctan2(y1 - y0, x1 - x0)), rotation_mode="anchor",
        ha="center", va="center")
plt.savefig("docs/figures/fig7_crossvendor.png")
print("wrote docs/figures/fig7_crossvendor.png")
