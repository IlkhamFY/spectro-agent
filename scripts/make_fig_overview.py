#!/usr/bin/env python3
"""Figure 1 - study pipeline. Minimal horizontal schematic: four stages, thin arrows,
numbered discs for presence — no boxes, no banner, no in-figure stats."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

stages = [
    ("IRexp", "experimental\nIR + ¹H + ¹³C"),
    ("Benchmark", "194 compounds,\ncomplexity-stratified"),
    ("LLM solver", "decoupled,\nclosed-book"),
    ("Forward-verify", "predict ¹³C,\nre-rank candidates"),
]

fig = plt.figure(figsize=(fs.COL2, 1.28))
ax = fig.add_axes([0.01, 0.05, 0.98, 0.90])
ax.set_xlim(0, 100); ax.set_ylim(8, 92); ax.axis("off")
xs = [12.5, 37.5, 62.5, 87.5]

for i, ((title, sub), x) in enumerate(zip(stages, xs), start=1):
    # Marker size is in POINTS so the disc stays circular regardless of data aspect.
    ax.scatter([x], [84], s=90, c=fs.INK, zorder=3, clip_on=False, linewidths=0)
    ax.text(x, 84, str(i), ha="center", va="center", fontsize=fs.FS_BODY,
            fontweight="bold", color="white", zorder=4)
    ax.text(x, 62, title, ha="center", va="center", fontsize=fs.FS_EMPH,
            fontweight="bold", color=fs.INK)
    ax.text(x, 44, sub, ha="center", va="top", fontsize=fs.FS_BODY, color=fs.NOTE,
            linespacing=1.35)

for x0, x1 in zip(xs[:-1], xs[1:]):
    m = (x0 + x1) / 2
    ax.add_patch(FancyArrowPatch((m - 3.4, 62), (m + 3.4, 62), arrowstyle="-|>",
                 mutation_scale=9, lw=1.05, color=fs.INK, shrinkA=0, shrinkB=0))

fs.save("docs/figures/fig0_overview.png")
print("wrote docs/figures/fig0_overview.png")
