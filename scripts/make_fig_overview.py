#!/usr/bin/env python3
"""Figure 1 - study pipeline. Minimal horizontal schematic: four stages, thin arrows,
one accent on the forward-verify step. No boxes, no banner, no in-figure stats
(those live in the caption)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

stages = [
    ("IRexp", "experimental\nIR + ¹H + ¹³C", fs.INK),
    ("Benchmark", "194 compounds,\ncomplexity-stratified", fs.INK),
    ("LLM solver", "decoupled,\nclosed-book", fs.INK),
    ("Forward-verify", "predict ¹³C,\nre-rank candidates", fs.ACCENT),
]

fig, ax = plt.subplots(figsize=(7.0, 1.7))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
xs = [12, 38, 63, 88]
for (title, sub, col), x in zip(stages, xs):
    ax.text(x, 60, title, ha="center", va="center", fontsize=9, fontweight="bold", color=col)
    ax.text(x, 38, sub, ha="center", va="top", fontsize=6.8, color=fs.MUTED)
for x0, x1 in zip(xs[:-1], xs[1:]):
    ax.add_patch(FancyArrowPatch((x0 + 12, 60), (x1 - 12, 60), arrowstyle="-|>",
                 mutation_scale=9, lw=1.0, color=fs.INK, shrinkA=0, shrinkB=0))

plt.savefig("docs/figures/fig0_overview.png")
print("wrote docs/figures/fig0_overview.png")
