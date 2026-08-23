#!/usr/bin/env python3
"""Figure 1 - study pipeline. Minimal horizontal schematic: four stages, thin arrows,
one accent on the forward-verify step. No boxes, no banner, no in-figure stats
(those live in the caption)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import figstyle as fs

fs.apply()

# All four stage names are set in INK. "Forward-verify" used to be the one accent
# colour, but nothing in the figure or its caption said what the colour meant, and an
# unexplained colour in a four-box schematic reads as a fifth variable. The palette
# reserves ORANGE for a hero element whose meaning is stated; here it was not, so it
# goes rather than being explained in a strip 0.75 in tall.
stages = [
    ("IRexp", "experimental\nIR + ¹H + ¹³C"),
    ("Benchmark", "194 compounds,\ncomplexity-stratified"),
    ("LLM solver", "decoupled,\nclosed-book"),
    ("Forward-verify", "predict ¹³C,\nre-rank candidates"),
]

# At 1.5 in with ylim 0-100 the top and bottom thirds of the frame were empty, and the
# PDF places this at native size. Crop to the content band, keeping the data unit at the
# original 0.015 in/unit (height / y-span) so the title-to-subtitle gap is unchanged.
fig = plt.figure(figsize=(fs.COL2, 0.80))
ax = fig.add_axes([0, 0, 1, 1])           # fill the frame; no tight-crop margins
ax.set_xlim(0, 100); ax.set_ylim(23.5, 73.5); ax.axis("off")
xs = [10, 36.7, 63.3, 90]
for (title, sub), x in zip(stages, xs):
    ax.text(x, 62, title, ha="center", va="center", fontsize=fs.FS_EMPH,
            fontweight="bold", color=fs.INK)
    # Body size in NOTE grey, not 6 pt in MUTED: these descriptors carry what each stage
    # actually is, and at 6 pt / 34% black they were the faintest marks in the paper.
    ax.text(x, 44, sub, ha="center", va="top", fontsize=fs.FS_BODY, color=fs.NOTE,
            linespacing=1.35)
# arrows of fixed length centred in each gap, so all three read identically and
# clear the (variable-width) stage labels
for x0, x1 in zip(xs[:-1], xs[1:]):
    m = (x0 + x1) / 2
    ax.add_patch(FancyArrowPatch((m - 3.5, 62), (m + 3.5, 62), arrowstyle="-|>",
                 mutation_scale=10, lw=1.1, color=fs.INK, shrinkA=0, shrinkB=0))

plt.savefig("docs/figures/fig0_overview.png")
print("wrote docs/figures/fig0_overview.png")
