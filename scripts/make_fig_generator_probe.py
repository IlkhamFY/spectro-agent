#!/usr/bin/env python3
"""Fig S5 - trained-generator probe (a complement to the training-free protocol).
On the 194-compound benchmark, the generator raises candidate recall AND converts it
to top-1 under the deterministic HOSE verifier, whereas scaffold enumeration's
near-degenerate regioisomers instead collapse the verifier.
Numbers reproduce from scripts/closing_the_gap_gen.py (Tier A, no model needed)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import figstyle as fs
fs.apply()

pools  = ["Claude\nonly", "+ scaffold\nenumeration", "+ trained\ngenerator"]
recall = [33.5, 41.8, 54.1]
top1   = [28.4, 16.0, 35.1]          # deterministic HOSE re-rank (real, not projected)

x = np.arange(len(pools)); w = 0.38
fig, ax = plt.subplots(figsize=(4.2, 3.0)); fs.ygrid(ax)
b1 = ax.bar(x - w/2, recall, w, color=fs.SKY, zorder=3, label="candidate recall")
b2 = ax.bar(x + w/2, top1,  w, color=fs.BLUE, zorder=3, label="HOSE top-1")
fs.barlabels(ax, b1, fmt="{:.1f}", dy=1)
fs.barlabels(ax, b2, fmt="{:.1f}", dy=1)

# baseline + collapse/lift call-outs
ax.axhline(28.4, color=fs.MUTED, lw=0.7, ls=(0, (4, 3)), zorder=2)
ax.annotate("verifier collapses", xy=(1 + w/2, 16.0), xytext=(1 + w/2, 30),
            ha="center", va="bottom", fontsize=6.5, color=fs.VERMIL,
            arrowprops=dict(arrowstyle="->", color=fs.VERMIL, lw=0.9))
ax.annotate("recall converts", xy=(2 + w/2, 35.1), xytext=(2 - 0.02, 48),
            ha="center", va="bottom", fontsize=6.5, color=fs.GREEN,
            arrowprops=dict(arrowstyle="->", color=fs.GREEN, lw=0.9))

ax.set_xticks(x); ax.set_xticklabels(pools)
ax.set_ylabel("% of 194 compounds"); ax.set_ylim(0, 64); ax.set_yticks([0, 20, 40, 60])
ax.legend(loc="upper left", handlelength=1.0, fontsize=6.5)
ax.set_title("A trained generator converts recall into top-1")
plt.tight_layout(); plt.savefig("docs/figures/fig_generator_probe.png")
print("wrote docs/figures/fig_generator_probe.png")
