#!/usr/bin/env python3
"""Hero figure - the diagnosis in one glance: the model can VERIFY the right structure
(84% when shown it) but rarely PROPOSES it (31% recall). Recall is the wall."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()
fig, ax = plt.subplots(figsize=(3.5, 2.9))

x = [0, 1]
vals = [31, 84]
cols = [fs.VERMIL, fs.GREEN]
bars = ax.bar(x, vals, width=0.62, color=cols, zorder=3)
fs.ygrid(ax)

for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 2, f"{v}%", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=b.get_facecolor())

# the gap = "the wall"
ax.annotate("", xy=(0, 84), xytext=(0, 31),
            arrowprops=dict(arrowstyle="<->", color=fs.INK, lw=1.0))
ax.text(0.08, 57.5, "the wall\n53-point gap", ha="left", va="center",
        fontsize=7.5, color=fs.INK, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(["Proposes it\n(generation recall)", "Verifies it\n(precision | recall)"])
ax.set_ylim(0, 100)
ax.set_ylabel("% of compounds")
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_title("Recall is the wall, not verification")

plt.tight_layout()
plt.savefig("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
