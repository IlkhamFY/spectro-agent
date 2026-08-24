#!/usr/bin/env python3
"""Fig S5 - trained-generator probe on the 194-compound benchmark."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
fs.barlabels(ax, b1, fmt="{:.1f}", dy=1)
fs.barlabels(ax, b2, fmt="{:.1f}", dy=1)

fs.refline(ax, y=28.4)
fs.reflabel(ax, 28.4, "Claude-only top-1", x=0.99, ha="right")

ax.set_xticks(x); ax.set_xticklabels(pools)
ax.set_ylabel("% of 194 compounds"); ax.set_ylim(0, 64); ax.set_yticks([0, 20, 40, 60])
fs.legend(ax, loc="upper left")
fs.finish(); fs.save("docs/figures/fig_generator_probe.png")
print("wrote docs/figures/fig_generator_probe.png")
