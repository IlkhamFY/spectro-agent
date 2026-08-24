#!/usr/bin/env python3
"""Benchmark figures (difficulty, size, inference ladder, dataset funnel) in the shared
premium style. One message per figure, direct labels, restrained colour."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, random
import figstyle as fs
from score_main import load, metrics, boot  # noqa

fs.apply()
random.seed(0)
R = metrics(load())
def rate(rs, k): return 100*sum(r[k] for r in rs)/len(rs) if rs else 0

# Fig 1 - accuracy by difficulty (top-1 & recovered, bootstrap CIs)
groups = [("All", R), ("Simple", [r for r in R if r['diff'] == 'simple']),
          ("Complex", [r for r in R if r['diff'] == 'complex'])]
fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.ygrid(ax)
x = np.arange(len(groups)); c = fs.GROUP_C; bw = fs.GROUP_W
for i, (key, col, lab) in enumerate([("top1", fs.BLUE, "exact top-1"),
                                     ("rec", fs.SKY, "recovered (top-3)")]):
    pts, los, his = [], [], []
    for _, sub in groups:
        p, lo, hi = boot(sub, lambda s: rate(s, key)); pts.append(p); los.append(p-lo); his.append(hi-p)
    ax.bar(x+(i-0.5)*c, pts, bw, yerr=[los, his],
           error_kw=fs.ERR, color=col, label=lab, zorder=3)
ax.set_xticks(x); ax.set_xticklabels([f"{g[0]}\n(n={len(g[1])})" for g in groups])
ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 70)
fs.legend(ax, loc="upper right")
fs.finish(); fs.save("docs/figures/fig1_difficulty.png"); plt.close()

# Fig 2 - accuracy vs molecular size
KEYS   = ["<=15", "16-25", ">25"]
LABELS = ["\u226415", "16\u201325", ">25"]
sub = lambda k: [r for r in R if r['hac'] == k]
t1 = [rate(sub(k), 'top1') for k in KEYS]; rc = [rate(sub(k), 'rec') for k in KEYS]
fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.ygrid(ax)
x = np.arange(len(KEYS))
ax.plot(x, rc, "s--", color=fs.SKY, mfc="white", mec=fs.SKY, mew=1.1,
        lw=fs.LINE_W, ms=fs.MARKER, label="recovered (top-3)")
ax.plot(x, t1, "o-", color=fs.BLUE, lw=fs.LINE_W, ms=fs.MARKER, label="exact top-1")
fs.legend(ax, loc="upper right", handlelength=1.8)
ax.set_xticks(x)
ax.set_xticklabels([f"{lab}\n(n={len(sub(k))})" for lab, k in zip(LABELS, KEYS)])
ax.set_xlabel("heavy atoms", labelpad=2); ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 78)
ax.margins(x=0.12)
fs.finish(); fs.save("docs/figures/fig2_size.png"); plt.close()

# Fig 3 - inference-time scaling on the same 60 compounds
labels = ["solver\nself-rank", "+ forward-\nverify", "+ generate-\nwide"]
vals = [23, 27, 30]
fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.ygrid(ax)
cols = [fs.MUTED, fs.MUTED, fs.BLUE]
bars = ax.bar(labels, vals, width=fs.BAR_W, color=cols, zorder=3)
fs.barlabels_inside(ax, bars, fmt="{:.0f}%")
ax.set_ylabel("exact top-1 (%)"); ax.set_ylim(0, 38)
fs.finish(); fs.save("docs/figures/fig3_method.png"); plt.close()

# Fig 4 - IRexp funnel
cats = ["IR records", "+ NMR", "+ structure", "full quad"]
v = [121233, 87075, 43060, 33201]
fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.xgrid(ax)
y = np.arange(len(cats))[::-1]
cols = [fs.MUTED, fs.MUTED, fs.MUTED, fs.BLUE]
ax.barh(y, v, height=fs.BAR_H, color=cols, zorder=3)
for yi, val in zip(y, v):
    ax.text(val + 2500, yi, f"{val/1000:.0f}k", va="center", ha="left",
            fontsize=fs.FS_BODY, color=fs.INK)
ax.set_yticks(y); ax.set_yticklabels(cats)
ax.set_xlim(0, 140000); ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
fs.finish(); fs.save("docs/figures/fig4_dataset.png"); plt.close()
print("wrote docs/figures/fig{1..4}_*.png")
