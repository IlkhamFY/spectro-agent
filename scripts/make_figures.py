#!/usr/bin/env python3
"""Benchmark figures (difficulty, size, inference ladder, dataset funnel) in the shared
Nature-grade style. One message per figure, direct labels, restrained colour."""
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
fig, ax = plt.subplots(figsize=(fs.COL1, 2.5)); fs.ygrid(ax)
x = np.arange(len(groups)); c = 0.34; bw = 0.31   # 0.03 surface gap between the pair
for i, (key, col, lab) in enumerate([("top1", fs.BLUE, "exact top-1"),
                                     ("rec", fs.SKY, "recovered (top-3)")]):
    pts, los, his = [], [], []
    for _, sub in groups:
        p, lo, hi = boot(sub, lambda s: rate(s, key)); pts.append(p); los.append(p-lo); his.append(hi-p)
    ax.bar(x+(i-0.5)*c, pts, bw, yerr=[los, his], capsize=1.8,
           error_kw=dict(lw=0.6, ecolor=fs.INK, capthick=0.6), color=col, label=lab, zorder=3)
ax.set_xticks(x); ax.set_xticklabels([f"{g[0]}\n(n={len(g[1])})" for g in groups])
ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 70)
ax.legend(loc="upper right", handlelength=1.0)
# message in caption (Nature style); no in-panel title
plt.tight_layout(); plt.savefig("docs/figures/fig1_difficulty.png"); plt.close()

# Fig 2 - accuracy vs molecular size. Both lines descend left->right, so the
# upper-right corner is empty: put the legend there (direct labels on such steep,
# converging lines can't avoid crossing them).
buckets = ["≤15", "16-25", ">25"]
sub = lambda b: [r for r in R if r['hac'] == ("<=15" if b == "≤15" else b)]
t1 = [rate(sub(b), 'top1') for b in buckets]; rc = [rate(sub(b), 'rec') for b in buckets]
fig, ax = plt.subplots(figsize=(fs.COL1, 2.5))
ax.plot(buckets, rc, "s--", color=fs.SKY, mfc="white", mec=fs.SKY, label="recovered (top-3)")
ax.plot(buckets, t1, "o-", color=fs.BLUE, label="exact top-1")
ax.legend(loc="upper right", handlelength=1.8, borderaxespad=0.4)
ax.set_xticks(range(len(buckets)))
ax.set_xticklabels([f"{b}\n(n={len(sub(b))})" for b in buckets])
ax.set_xlabel("heavy atoms", labelpad=1); ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 78)
ax.margins(x=0.10)
# message in caption; no in-panel title
plt.tight_layout(); plt.savefig("docs/figures/fig2_size.png"); plt.close()

# Fig 3 - inference-time scaling on the same 60 compounds (one metric -> one accent)
labels = ["solver\nself-rank", "+ forward-\nverify", "+ generate-\nwide"]
vals = [23, 27, 30]      # 14/60, 16/60, 18/60 -- rounded, as Table 7
fig, ax = plt.subplots(figsize=(fs.COL1, 2.6)); fs.ygrid(ax)
cols = [fs.MUTED, fs.MUTED, fs.BLUE]
bars = ax.bar(labels, vals, width=0.6, color=cols, zorder=3)
fs.barlabels(ax, bars, fmt="{:.0f}%", dy=0.6)
ax.set_ylabel("exact top-1 (%)"); ax.set_ylim(0, 38)
# message in caption; no in-panel title
plt.tight_layout(); plt.savefig("docs/figures/fig3_method.png"); plt.close()

# Fig 4 - IRexp funnel (horizontal, k-formatted, payload bar highlighted)
cats = ["IR records", "+ NMR", "+ structure", "full quad"]
v = [121233, 87075, 43060, 33201]
fig, ax = plt.subplots(figsize=(fs.COL1, 2.5))
y = np.arange(len(cats))[::-1]
cols = [fs.MUTED, fs.MUTED, fs.MUTED, fs.BLUE]
ax.barh(y, v, height=0.62, color=cols, zorder=3)
ax.set_axisbelow(True); ax.xaxis.grid(True, color=fs.FAINT, linewidth=0.6); ax.yaxis.grid(False)
for yi, val in zip(y, v):
    ax.text(val + 2500, yi, f"{val/1000:.0f}k", va="center", ha="left", fontsize=7, color=fs.INK)
ax.set_yticks(y); ax.set_yticklabels(cats)
ax.set_xlim(0, 140000); ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
# message in caption; no in-panel title
plt.tight_layout(); plt.savefig("docs/figures/fig4_dataset.png"); plt.close()
print("wrote fig1_difficulty, fig2_size, fig3_method, fig4_dataset")
