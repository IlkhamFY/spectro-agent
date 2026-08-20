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

fig, (ax, bx) = plt.subplots(1, 2, figsize=(fs.COL2, 2.9),
                             gridspec_kw={"width_ratios": [1.25, 1]})

# ---- (a) generation recall, gated by whether the output contract was met -----
order = sorted(MODELS, key=lambda m: m[1])
ys = range(len(order))
cols = [fs.MUTED if (m[2] is not None and m[2] < GATE) else
        (fs.ORANGE if m[0] == "Claude Opus" else fs.BLUE) for m in order]
ax.barh(list(ys), [100 * m[1] / 60 for m in order], color=cols, height=0.62, zorder=3)
ax.set_yticks(list(ys)); ax.set_yticklabels([m[0] for m in order])
for y, m in zip(ys, order):
    ax.text(100 * m[1] / 60 + 1.2, y, f"{m[1]}/60",
            va="center", fontsize=fs.FS_SMALL, color=fs.INK)
ax.set_xlabel("generation recall (%)", labelpad=1)
ax.set_xlim(0, 68)
ax.grid(axis="x", color=fs.FAINT, lw=0.5, zorder=0); ax.set_axisbelow(True)
ax.text(0.40, 0.12, "grey: below the formula-adherence floor —\n"
        "recall is not a chemistry result",
        transform=ax.transAxes, fontsize=fs.FS_SMALL, color=fs.MUTED, va="bottom")
ax.text(-0.42, 1.04, "a", transform=ax.transAxes,
        fontsize=fs.FS_PANEL, fontweight="bold", color=fs.INK)

# ---- (b) the claim: precision above recall ----------------------------------
# Both axes run the full 0-100%: they are the same unit, and the whole panel is a
# comparison against y = x. Cropping to (2-70, 42-100) -- as this panel used to --
# stretches the vertical gaps between models about twice as far as the horizontal
# ones and makes the distance above the diagonal look larger than it is.
bx.plot([0, 100], [0, 100], color=fs.MUTED, lw=0.7, ls="--", zorder=1)
for name, r, _adh, p in MODELS:
    if p is None:
        continue
    x = 100 * r / 60
    c = fs.ORANGE if name == "Claude Opus" else fs.BLUE
    partial = name.startswith("DeepSeek")          # 18/60 answered: a lower bound
    bx.scatter([x], [p], s=26, zorder=4, linewidth=0.9,
               facecolor="white" if partial else c, edgecolor=c)
    if partial:
        bx.annotate("", (x + 5.5, p), (x + 0.8, p),
                    arrowprops=dict(arrowstyle="->", color=fs.MUTED, lw=0.7))
    # Offsets keep every label off the diagonal and off its neighbours' markers:
    # Grok and GPT-5.6 Sol label to the LEFT because the space to their right is
    # where the y = x rule passes.
    OFF = {"Grok 4.6": (-5, -2, "right"), "Gemini 3.7 Flash": (-5, 4, "right"),
           "GPT-5.6 Sol": (-5, 3, "right"), "Claude Opus": (5, 2, "left"),
           "DeepSeek V4 Pro": (7, -11, "center")}
    dx, dy, ha = OFF.get(name, (4, 4, "left"))
    bx.annotate(name, (x, p), textcoords="offset points", xytext=(dx, dy),
                fontsize=fs.FS_SMALL, color=fs.INK, ha=ha)
bx.set_xlabel("generation recall (%)", labelpad=1)
bx.set_ylabel("verification precision | recall (%)", labelpad=2)
bx.set_xlim(0, 100); bx.set_ylim(0, 100)
bx.set_xticks([0, 25, 50, 75, 100]); bx.set_yticks([0, 25, 50, 75, 100])
bx.text(-0.30, 1.04, "b", transform=bx.transAxes,
        fontsize=fs.FS_PANEL, fontweight="bold", color=fs.INK)
bx.text(0.03, 0.04, "above the line: verification beats generation\n"
        "hollow: incomplete arm, recall is a lower bound",
        transform=bx.transAxes, fontsize=fs.FS_SMALL, color=fs.MUTED, va="bottom")

plt.tight_layout(w_pad=1.6)

# The diagonal's on-screen angle depends on the final axes box, so label it only after
# tight_layout has settled -- a hardcoded rotation silently goes wrong when it moves.
fig.canvas.draw()
(x0, y0), (x1, y1) = bx.transData.transform([(20, 20), (80, 80)])
bx.text(78, 71, "precision = recall", fontsize=fs.FS_SMALL, color=fs.MUTED,
        rotation=np.degrees(np.arctan2(y1 - y0, x1 - x0)), rotation_mode="anchor",
        ha="center", va="center")
plt.savefig("docs/figures/fig7_crossvendor.png")
print("wrote docs/figures/fig7_crossvendor.png")
