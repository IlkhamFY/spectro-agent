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

# Claude-only baseline reference; the collapse-vs-convert story lives in the caption.
# Label sits in the clear band above the group-1 bars (below the legend), left of the
# scaffold recall bar, so it never collides with the 28.4 value label on its own bar.
ax.axhline(28.4, color=fs.MUTED, lw=0.6, ls=(0, (4, 3)), zorder=2)
ax.text(0.015, 44.5, "Claude-only top-1 (28.4%)", transform=ax.get_yaxis_transform(),
        fontsize=6, color=fs.MUTED, va="bottom", ha="left")

ax.set_xticks(x); ax.set_xticklabels(pools)
ax.set_ylabel("% of 194 compounds"); ax.set_ylim(0, 64); ax.set_yticks([0, 20, 40, 60])
ax.legend(loc="upper left", handlelength=1.0, fontsize=6.5)
# message in caption; no in-panel title
plt.tight_layout(); plt.savefig("docs/figures/fig_generator_probe.png")
print("wrote docs/figures/fig_generator_probe.png")
