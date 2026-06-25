#!/usr/bin/env python3
"""Generator probe (proposed §5.6): a trained generator breaks the recall wall AND the
recall converts. Panel A: truth-in-candidate-set recall. Panel B: HOSE top-1 on the same
pools — enumeration lifts recall but CRATERS top-1 (near-degenerate), the generator lifts
both. (Strong LLM forward-verifier lifts +generator top-1 to 46%; see caption.)"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()
fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.0, 3.1))

labels = ["Claude\nalone", "+ scaffold\nenumeration", "+ trained\ngenerator"]
cols   = [fs.MUTED, fs.ORANGE, fs.BLUE]
x = range(3)

# Panel A — recall (truth in candidate set), n=194
recall = [33.5, 41.8, 54.1]
bA = axA.bar(x, recall, width=0.64, color=cols, zorder=3)
fs.ygrid(axA); fs.barlabels(axA, bA, fmt="{:.1f}", dy=1.0, size=7)
axA.set_xticks(x); axA.set_xticklabels(labels)
axA.set_ylim(0, 70); axA.set_yticks([0, 20, 40, 60])
axA.set_ylabel("truth in candidate set (%)")
axA.set_title("Recall: the wall breaks")
axA.text(0.97, 0.04, "n=194", transform=axA.transAxes, ha="right", va="bottom",
         fontsize=6.5, color=fs.MUTED)
fs.panel(axA, "A")

# Panel B — HOSE top-1 on the same pools, n=194
top1 = [28.4, 16.0, 35.1]
bB = axB.bar(x, top1, width=0.64, color=cols, zorder=3)
fs.ygrid(axB); fs.barlabels(axB, bB, fmt="{:.1f}", dy=1.0, size=7)
axB.axhline(28.4, ls="--", lw=0.8, color=fs.MUTED, zorder=1)
axB.set_xticks(x); axB.set_xticklabels(labels)
axB.set_ylim(0, 70); axB.set_yticks([0, 20, 40, 60])
axB.set_ylabel("top-1 exact constitution (%)")
axB.set_title("Conversion: only the generator's converts")
# annotate the two mechanisms
axB.annotate("craters\nthe verifier", xy=(1, 16.0), xytext=(1.0, 44),
             ha="center", va="bottom", fontsize=6.3, color=fs.VERMIL,
             arrowprops=dict(arrowstyle="->", color=fs.VERMIL, lw=0.8))
axB.text(0.97, 0.04, "n=194 · HOSE verifier", transform=axB.transAxes, ha="right",
         va="bottom", fontsize=6.5, color=fs.MUTED)
fs.panel(axB, "B")

plt.tight_layout()
plt.savefig("docs/figures/fig_generator.png")
print("wrote docs/figures/fig_generator.png")
