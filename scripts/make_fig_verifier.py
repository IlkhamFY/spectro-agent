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
fig, (axA, axB) = plt.subplots(1, 2, figsize=(fs.COL2, 2.9))

# Panel A — conditional-on-recall top-1 (n=19), the four verifiers
labelsA = ["solver\nself-rank", "HOSE\nlookup (§5.4)", "learned\nGNN", "LLM\nverifier"]
top1    = [73, 73, 84, 84]
colsA   = [fs.MUTED, fs.MUTED, fs.ORANGE, fs.BLUE]  # baselines; GNN=hero; LLM=reference
xA = range(4)
bA = axA.bar(xA, top1, width=0.62, color=colsA, zorder=3)
fs.ygrid(axA); fs.barlabels(axA, bA, fmt="{:.0f}", dy=1.2, size=fs.FS_BODY)
axA.axhline(73, ls="--", lw=0.6, color=fs.MUTED, zorder=1)
axA.set_xticks(xA); axA.set_xticklabels(labelsA)
axA.set_ylim(0, 100); axA.set_yticks([0, 25, 50, 75, 100])
axA.set_ylabel("top-1 | recall (%)")   # n and set stated in the caption
fs.panel(axA, "a")

# Panel B — held-out 13C MAE (lower is better): the mechanism
labelsB = ["HOSE\nlookup", "learned\nGNN"]
mae     = [3.23, 1.70]
colsB   = [fs.MUTED, fs.ORANGE]   # HOSE lookup baseline; learned GNN = hero (as panel a)
xB = range(2)
bB = axB.bar(xB, mae, width=0.5, color=colsB, zorder=3)
fs.ygrid(axB); fs.barlabels(axB, bB, fmt="{:.2f}", dy=0.06, size=fs.FS_BODY)
axB.set_xticks(xB); axB.set_xticklabels(labelsB)
axB.set_ylim(0, 4.0); axB.set_yticks([0, 1, 2, 3, 4])
axB.set_ylabel("held-out $^{13}$C MAE (ppm)")
axB.text(0.97, 0.96, "lower = better", transform=axB.transAxes, ha="right",
         va="top", fontsize=fs.FS_SMALL, color=fs.MUTED)
fs.panel(axB, "b")

plt.tight_layout()
plt.savefig("docs/figures/fig_verifier.png")
print("wrote docs/figures/fig_verifier.png")
