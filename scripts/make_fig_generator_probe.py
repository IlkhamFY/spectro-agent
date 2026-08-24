#!/usr/bin/env python3
"""Fig S5 - trained-generator probe on the 194-compound benchmark."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import figstyle as fs
fs.apply()

pools  = ["Claude\nonly", "+ scaffold\nenumeration", "+ trained\ngenerator"]
recall = [33.5, 41.8, 54.1]
top1   = [28.4, 16.0, 35.1]

x = np.arange(len(pools)); c = fs.GROUP_C; bw = fs.GROUP_W
fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.ygrid(ax)
b1 = ax.bar(x - c/2, recall, bw, color=fs.SKY, zorder=3, label="candidate recall")
b2 = ax.bar(x + c/2, top1,  bw, color=fs.BLUE, zorder=3, label="HOSE top-1")
# White pad under values so the Claude-only baseline does not cut digits.
for bars in (b1, b2):
    for b in bars:
        ax.text(
            b.get_x() + b.get_width() / 2, b.get_height() + 1.0,
            f"{b.get_height():.1f}", ha="center", va="bottom",
            fontsize=fs.FS_BODY, color=fs.INK, zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.12),
        )

# Dashed baseline at Claude-only top-1 — explained in the legend, not overlaid on bars.
fs.refline(ax, y=28.4)

ax.set_xticks(x); ax.set_xticklabels(pools)
ax.set_ylabel("% of 194 compounds"); ax.set_ylim(0, 64); ax.set_yticks([0, 20, 40, 60])
fs.legend(ax, loc="upper left", handles=[
    b1, b2,
    Line2D([0], [0], color=fs.MUTED, lw=fs.REF_LW, ls=fs.REF_LS,
           label="Claude-only top-1"),
])
fs.finish()
fs.save("docs/figures/fig_generator_probe.png")
print("wrote docs/figures/fig_generator_probe.png")
