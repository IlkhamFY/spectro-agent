#!/usr/bin/env python3
"""Learned-verifier probe: GNN vs HOSE vs LLM on identical recall set."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()
fig, (axA, axB) = plt.subplots(1, 2, figsize=(fs.COL2, fs.H2))

labelsA = ["solver\nself-rank", "HOSE\nlookup (§5.4)", "learned\nGNN", "LLM\nverifier"]
top1    = [84.6, 84.6, 90.8, 89.2]
colsA   = [fs.MUTED, fs.MUTED, fs.ORANGE, fs.BLUE]
xA = range(4)
bA = axA.bar(xA, top1, width=fs.BAR_W, color=colsA, zorder=3)
fs.ygrid(axA); fs.barlabels(axA, bA, fmt="{:.0f}", dy=1.2, size=fs.FS_BODY)
fs.refline(axA, y=84.6)
axA.set_xticks(xA); axA.set_xticklabels(labelsA)
axA.set_ylim(0, 100); axA.set_yticks([0, 25, 50, 75, 100])
axA.set_ylabel("top-1 | recall (%)")
fs.panel(axA, "a")

labelsB = ["HOSE\nlookup", "learned\nGNN"]
mae     = [3.23, 1.70]
colsB   = [fs.MUTED, fs.ORANGE]
xB = range(2)
bB = axB.bar(xB, mae, width=0.52, color=colsB, zorder=3)
fs.ygrid(axB); fs.barlabels(axB, bB, fmt="{:.2f}", dy=0.06, size=fs.FS_BODY)
axB.set_xticks(xB); axB.set_xticklabels(labelsB)
axB.set_ylim(0, 4.0); axB.set_yticks([0, 1, 2, 3, 4])
axB.set_ylabel("held-out \u00b9\u00b3C MAE (ppm)")
# NOTE grey, not MUTED: this reads the axis for the reader (the only panel in the paper
# where a smaller bar is the better result), and at ~34% black it was the faintest mark
# in the figure.
axB.text(0.97, 0.86, "lower = better", transform=axB.transAxes, ha="right",
         va="top", fontsize=fs.FS_BODY, color=fs.NOTE)
fs.panel(axB, "b")

fs.finish(w_pad=1.4)
fs.save("docs/figures/fig_verifier.png")
print("wrote docs/figures/fig_verifier.png")
