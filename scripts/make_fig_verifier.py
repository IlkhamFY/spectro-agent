#!/usr/bin/env python3
"""Learned-verifier probe (proposed §5.7): a GNN trained on the SAME nmrshiftdb2 data as the
§5.4 HOSE lookup recovers the LLM verifier's precision the lookup could not. Panel A:
conditional-on-recall top-1 across the four verifiers on the identical n=19 set (GNN closes
the 73->84% HOSE->LLM gap). Panel B: the why — held-out 13C MAE (the learned model is ~2x
sharper, 1.70 vs 3.23 ppm), so it resolves environments the lookup degrades on."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()
fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.0, 3.1))

# Panel A — conditional-on-recall top-1 (n=19), the four verifiers
labelsA = ["solver\nself-rank", "HOSE\nlookup (§5.4)", "learned\nGNN", "LLM\nverifier"]
top1    = [73, 73, 84, 84]
colsA   = [fs.MUTED, fs.MUTED, fs.BLUE, fs.GREEN]
xA = range(4)
bA = axA.bar(xA, top1, width=0.66, color=colsA, zorder=3)
fs.ygrid(axA); fs.barlabels(axA, bA, fmt="{:.0f}", dy=1.2, size=7)
axA.axhline(73, ls="--", lw=0.8, color=fs.MUTED, zorder=1)
axA.set_xticks(xA); axA.set_xticklabels(labelsA)
axA.set_ylim(0, 100); axA.set_yticks([0, 25, 50, 75, 100])
axA.set_ylabel("top-1 | recall (%)")
axA.set_title("Learned predictor closes the gap")
axA.annotate("matches the\nLLM verifier", xy=(2, 84), xytext=(1.4, 96),
             ha="center", va="top", fontsize=6.3, color=fs.BLUE,
             arrowprops=dict(arrowstyle="->", color=fs.BLUE, lw=0.8))
axA.text(0.97, 0.04, "n=19 · same §5.2 set", transform=axA.transAxes, ha="right",
         va="bottom", fontsize=6.5, color=fs.MUTED)
fs.panel(axA, "A")

# Panel B — held-out 13C MAE (lower is better): the mechanism
labelsB = ["HOSE\nlookup", "learned\nGNN"]
mae     = [3.23, 1.70]
colsB   = [fs.MUTED, fs.BLUE]
xB = range(2)
bB = axB.bar(xB, mae, width=0.5, color=colsB, zorder=3)
fs.ygrid(axB); fs.barlabels(axB, bB, fmt="{:.2f}", dy=0.06, size=7)
axB.set_xticks(xB); axB.set_xticklabels(labelsB)
axB.set_ylim(0, 4.0); axB.set_yticks([0, 1, 2, 3, 4])
axB.set_ylabel("held-out $^{13}$C MAE (ppm)")
axB.set_title("Why: the learned model is sharper")
axB.text(0.97, 0.96, "lower = better", transform=axB.transAxes, ha="right",
         va="top", fontsize=6.5, color=fs.MUTED)
fs.panel(axB, "B")

plt.tight_layout()
plt.savefig("docs/figures/fig_verifier.png")
print("wrote docs/figures/fig_verifier.png")
