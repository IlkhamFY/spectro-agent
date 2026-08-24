#!/usr/bin/env python3
"""Fig. 7 — every model measured, on one axis where they share a compound set.

(a) ranks by generation recall on the 60-compound arm; formula-adherence gate in colour.
(b) recall against verification precision, with the diagonal.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.path.insert(0, "scripts")
import figstyle as fs

fs.apply()

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
GATE = 78
PARTIAL = "DeepSeek V4 Pro"

fig, (ax, bx) = plt.subplots(1, 2, figsize=(fs.COL2, 3.45),
                             gridspec_kw={"width_ratios": [0.92, 1]})

order = sorted(MODELS, key=lambda m: m[1])
ys = range(len(order))
cols = [fs.MUTED if (m[2] is not None and m[2] < GATE) else
        (fs.ORANGE if m[0] == "Claude Opus" else fs.BLUE) for m in order]
for y, m, c in zip(ys, order, cols):
    part = m[0] == PARTIAL
    ax.barh(y, 100 * m[1] / 60, height=fs.BAR_H, zorder=3,
            color="white" if part else c, edgecolor=c,
            linewidth=0.9 if part else 0, hatch="////" if part else None)
ax.set_yticks(list(ys))
ax.set_yticklabels([m[0] for m in order], ha="right")
ax.tick_params(axis="y", pad=4)
for y, m in zip(ys, order):
    ax.text(100 * m[1] / 60 + 1.4, y, f"{m[1]}/60",
            va="center", fontsize=fs.FS_BODY, color=fs.INK)
ax.set_xlabel("generation recall (%)", labelpad=2)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_ylim(-0.7, 8.35)
fs.xgrid(ax)
fs.legend(ax, handles=[
    Patch(facecolor="white", edgecolor=fs.BLUE, hatch="////", linewidth=0.9,
          label="partial formula gate"),
], loc="lower right")
fs.panel(ax, "a")

bx.plot([0, 100], [0, 100], color=fs.MUTED, lw=fs.REF_LW, ls=fs.REF_LS, zorder=1)
bx.set_axisbelow(True)
bx.yaxis.grid(True, color=fs.FAINT, linewidth=0.55)
bx.xaxis.grid(True, color=fs.FAINT, linewidth=0.55)
# Per-point offsets keep labels off the diagonal and each other (no shared dx).
LBL = {
    "Grok 4.6":         (8, -10),
    "Gemini 3.7 Flash": (-8, 8),
    "GPT-5.6 Sol":      (8,  8),
    "Claude Opus":      (-8, 0),
    "DeepSeek V4 Pro":  (8, -10),
}
for name, r, _adh, p in MODELS:
    if p is None:
        continue
    x = 100 * r / 60
    c = fs.ORANGE if name == "Claude Opus" else fs.BLUE
    partial = name == PARTIAL
    bx.scatter([x], [p], s=42, zorder=4, linewidth=1.05,
               facecolor="white" if partial else c, edgecolor=c,
               hatch="////" if partial else None)
    dx, dy = LBL.get(name, (7, 0))
    ha = "right" if dx < 0 else "left"
    bx.annotate(name, (x, p), textcoords="offset points", xytext=(dx, dy),
                fontsize=fs.FS_BODY, color=fs.INK, ha=ha, va="center", zorder=5,
                bbox=dict(fc="white", ec="none", pad=0.6))
bx.set_xlabel("generation recall (%)", labelpad=2)
bx.set_ylabel("verification precision | recall (%)", labelpad=2)
bx.set_xlim(0, 100); bx.set_ylim(0, 100)
bx.set_xticks([0, 25, 50, 75, 100]); bx.set_yticks([0, 25, 50, 75, 100])
fs.panel(bx, "b")

fs.finish(w_pad=1.8)

fig.canvas.draw()
(x0, y0), (x1, y1) = bx.transData.transform([(20, 20), (80, 80)])
bx.text(38, 32, "precision = recall", fontsize=fs.FS_BODY, color=fs.NOTE,
        rotation=np.degrees(np.arctan2(y1 - y0, x1 - x0)), rotation_mode="anchor",
        ha="center", va="center")
fs.save("docs/figures/fig7_crossvendor.png")
print("wrote docs/figures/fig7_crossvendor.png")
