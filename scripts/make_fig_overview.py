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

# At 1.5 in with ylim 0-100 the top and bottom thirds of the frame were empty, and the
# PDF places this at native size. Crop to the content band, keeping the data unit at the
# original 0.015 in/unit (height / y-span) so the title-to-subtitle gap is unchanged.
fig = plt.figure(figsize=(fs.COL2, 0.75))
ax = fig.add_axes([0, 0, 1, 1])           # fill the frame; no tight-crop margins
ax.set_xlim(0, 100); ax.set_ylim(23.5, 73.5); ax.axis("off")
xs = [10, 36.7, 63.3, 90]
for (title, sub, col), x in zip(stages, xs):
    ax.text(x, 62, title, ha="center", va="center", fontsize=fs.FS_EMPH,
            fontweight="bold", color=col)
    ax.text(x, 44, sub, ha="center", va="top", fontsize=fs.FS_SMALL, color=fs.MUTED)
# arrows of fixed length centred in each gap, so all three read identically and
# clear the (variable-width) stage labels
for x0, x1 in zip(xs[:-1], xs[1:]):
    m = (x0 + x1) / 2
    ax.add_patch(FancyArrowPatch((m - 3.5, 62), (m + 3.5, 62), arrowstyle="-|>",
                 mutation_scale=10, lw=1.1, color=fs.INK, shrinkA=0, shrinkB=0))

plt.savefig("docs/figures/fig0_overview.png")
print("wrote docs/figures/fig0_overview.png")
