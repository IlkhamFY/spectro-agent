#!/usr/bin/env python3
"""Robustness plate — contamination + cross-vendor controls on one Nature-style figure.

(a) formula-only ablation (60 compounds)
(b) accuracy vs source publication year (n=194)
(c) generation recall by vendor (60-compound arm)
(d) verification precision vs generation recall (numbered key)
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import figstyle as fs

fs.apply()

fo = json.load(open("data/modality/formulaonly_control.json"))
rc = json.load(open("data/audit/recency_control.json"))

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
SCATTER = [(n, r, a, p) for n, r, a, p in MODELS if p is not None]

YMAX = 52
fig, axes = plt.subplots(
    2, 2, figsize=(fs.COL2, 6.55),
    gridspec_kw={"height_ratios": [1.0, 1.08], "width_ratios": [1.0, 1.02]},
)
axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

# ---- (a) formula-only -------------------------------------------------------
labels = ["formula\nonly", "formula + IR\n+ \u00b9H + \u00b9\u00b3C"]
vals = [5.0, 23.3]
cols = [fs.MUTED, fs.BLUE]
bars = axA.bar([0, 1], vals, width=fs.BAR_W, color=cols, zorder=3)
fs.ygrid(axA)
for b, v, k in zip(bars, vals, ["3/60", "14/60"]):
    axA.text(b.get_x() + b.get_width() / 2, v + 1.6, f"{v:.0f}%",
             ha="center", va="bottom", fontsize=fs.FS_BODY, fontweight="bold",
             color=fs.INK)
    axA.text(b.get_x() + b.get_width() / 2, v + 5.0, k,
             ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.NOTE)
axA.set_xticks([0, 1])
axA.set_xticklabels(labels)
axA.set_ylabel("exact top-1 (%)")
axA.set_ylim(0, YMAX)
fs.panel(axA, "a")

# ---- (b) recency ------------------------------------------------------------
bk = rc["buckets"]
xs = list(range(len(bk)))
pts = [b["pct"] for b in bk]
lo = [b["pct"] - b["ci"][0] for b in bk]
hi = [b["ci"][1] - b["pct"] for b in bk]
axB.errorbar(xs, pts, yerr=[lo, hi], fmt="o", ms=fs.MARKER, color=fs.BLUE,
             ecolor=fs.BLUE, elinewidth=fs.ERR["lw"], capsize=fs.ERR["capsize"],
             capthick=fs.ERR["capthick"], zorder=3)
fs.ygrid(axB)
pooled = 100 * sum(b["top1"] for b in bk) / sum(b["n"] for b in bk)
fs.refline(axB, y=pooled)
axB.text(
    0.0, 1.06,
    f"r = {rc['point_biserial_r']:+.3f}".replace("-", "\u2212")
    + f"  \u00b7  pooled {pooled:.0f}%",
    transform=axB.transAxes, ha="left", va="bottom",
    fontsize=fs.FS_BODY, color=fs.NOTE, clip_on=False,
)

def tick(lab):
    return lab.replace(">=", "\u2265").replace("<=", "\u2264").replace("-", "\u2013")

axB.set_xticks(xs)
axB.set_xticklabels([f"{tick(b['label'])}\n(n={b['n']})" for b in bk])
axB.set_xlim(-0.5, len(bk) - 0.5)
axB.set_ylim(0, YMAX)
axB.set_xlabel("source publication year", labelpad=2)
axB.set_ylabel("exact top-1 (%)")
fs.panel(axB, "b")

# ---- (c) cross-vendor recall ------------------------------------------------
order = sorted(MODELS, key=lambda m: m[1])
ys = range(len(order))
cols = [fs.MUTED if (m[2] is not None and m[2] < GATE) else
        (fs.ORANGE if m[0] == "Claude Opus" else fs.BLUE) for m in order]
for y, m, c in zip(ys, order, cols):
    part = m[0] == PARTIAL
    axC.barh(y, 100 * m[1] / 60, height=fs.BAR_H, zorder=3,
             color="white" if part else c, edgecolor=c,
             linewidth=0.9 if part else 0, hatch="////" if part else None)
axC.set_yticks(list(ys))
axC.set_yticklabels([m[0] for m in order], ha="right")
axC.tick_params(axis="y", pad=4)
for y, m in zip(ys, order):
    axC.text(100 * m[1] / 60 + 1.4, y, f"{m[1]}/60",
             va="center", fontsize=fs.FS_BODY, color=fs.INK)
axC.set_xlabel("generation recall (%)", labelpad=2)
axC.set_xlim(0, 100)
axC.set_xticks([0, 25, 50, 75, 100])
axC.set_ylim(-0.7, 8.55)
fs.xgrid(axC)
fs.legend(axC, handles=[
    Patch(facecolor="white", edgecolor=fs.BLUE, hatch="////", linewidth=0.9,
          label="partial formula gate"),
], loc="lower right")
fs.panel(axC, "c")

# ---- (d) recall vs precision ------------------------------------------------
axD.plot([0, 100], [0, 100], color=fs.MUTED, lw=fs.REF_LW, ls=fs.REF_LS, zorder=1)
axD.set_axisbelow(True)
axD.yaxis.grid(True, color=fs.FAINT, linewidth=0.55)
axD.xaxis.grid(True, color=fs.FAINT, linewidth=0.55)

for i, (name, r, _adh, p) in enumerate(SCATTER, start=1):
    x = 100 * r / 60
    c = fs.ORANGE if name == "Claude Opus" else fs.BLUE
    partial = name == PARTIAL
    axD.scatter([x], [p], s=48, zorder=4, linewidth=1.05,
                facecolor="white" if partial else c, edgecolor=c,
                hatch="////" if partial else None)
    axD.text(x - 1.8, p - 3.2, str(i), fontsize=fs.FS_BODY, fontweight="bold",
             color=fs.INK, ha="right", va="top", zorder=5, clip_on=False)

key = "\n".join(f"{i}. {n}" for i, (n, *_rest) in enumerate(SCATTER, start=1))
axD.text(0.98, 0.04, key, transform=axD.transAxes, fontsize=fs.FS_BODY,
         color=fs.INK, ha="right", va="bottom", linespacing=1.35, zorder=6,
         bbox=dict(boxstyle="round,pad=0.30", facecolor="white",
                   edgecolor=fs.FAINT, linewidth=0.6))

axD.set_xlabel("generation recall (%)", labelpad=2)
axD.set_ylabel("verification precision | recall (%)", labelpad=2)
axD.set_xlim(0, 100)
axD.set_ylim(0, 100)
axD.set_xticks([0, 25, 50, 75, 100])
axD.set_yticks([0, 25, 50, 75, 100])
fs.panel(axD, "d")

fs.finish(w_pad=1.6, h_pad=2.0, left=0.13, top=0.94)

fig.canvas.draw()
(x0, y0), (x1, y1) = axD.transData.transform([(20, 20), (80, 80)])
axD.text(38, 32, "precision = recall", fontsize=fs.FS_BODY, color=fs.NOTE,
         rotation=np.degrees(np.arctan2(y1 - y0, x1 - x0)), rotation_mode="anchor",
         ha="center", va="center", zorder=2)

fs.save("docs/figures/fig_robustness.png")
print("wrote docs/figures/fig_robustness.png")
