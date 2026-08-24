#!/usr/bin/env python3
"""Contamination controls figure: (a) formula-only ablation, (b) accuracy vs publication year.

Two independent tests of whether the headline number is memorisation.
(a) Remove the spectra: accuracy collapses 23% -> 5%, and the outcomes are nested (every
    formula-only success is also solved from spectra; none the reverse).
(b) Vary how long the source paper has been available to a training corpus: accuracy is
    flat in publication year (point-biserial r = -0.007), which recall from pretraining
    would not predict.
Numbers come from data/modality/formulaonly_control.json and data/audit/recency_control.json.
"""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()

fo = json.load(open("data/modality/formulaonly_control.json"))
rc = json.load(open("data/audit/recency_control.json"))

# ONE y-scale for both panels. They carry the same label and the same unit -- "exact
# top-1 (%)" -- and sit side by side, so a reader compares bar heights across the pair
# at a glance. Running (a) to 42 and (b) to 68 made that comparison false. The range is
# set by the taller demand: (b)'s widest Wilson interval reaches 59.
YMAX = 68

fig, (axA, axB) = plt.subplots(1, 2, figsize=(fs.COL2, 2.5))

# ---- (a) formula-only ablation -------------------------------------------------
labels = ["formula\nonly", "formula + IR\n+ ¹H + ¹³C"]
vals = [5.0, 23.3]
cols = [fs.MUTED, fs.BLUE]
bars = axA.bar([0, 1], vals, width=0.55, color=cols, zorder=3)
fs.ygrid(axA)
# Offsets are fractions of the shared y-range, so the value and its denominator keep
# the same printed gap now that both panels run to YMAX.
for b, v, k in zip(bars, vals, ["3/60", "14/60"]):
    axA.text(b.get_x() + b.get_width()/2, v + 0.019 * YMAX, f"{v:.0f}%",
             ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.INK)
    axA.text(b.get_x() + b.get_width()/2, v + 0.081 * YMAX, k,
             ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.NOTE)
axA.set_xticks([0, 1]); axA.set_xticklabels(labels)
axA.set_ylabel("exact top-1 (%)"); axA.set_ylim(0, YMAX)
# The in-panel note ("11 compounds solved only with the spectra, 0 only without
# (McNemar exact p=0.001)") is gone: the caption already carries that sentence, word for
# word, at 10 pt. Repeating it inside the panel at 6 pt added no fact and cost the
# reader a second, smaller reading of the same thing.
fs.panel(axA, "a", x=-0.20)

# ---- (b) accuracy vs publication year ------------------------------------------
bk = rc["buckets"]
xs = list(range(len(bk)))
pts = [b["pct"] for b in bk]
lo = [b["pct"] - b["ci"][0] for b in bk]
hi = [b["ci"][1] - b["pct"] for b in bk]
axB.errorbar(xs, pts, yerr=[lo, hi], fmt="o", ms=5, color=fs.BLUE, ecolor=fs.BLUE,
             elinewidth=1.0, capsize=2.5, capthick=0.9, zorder=3)
fs.ygrid(axB)
# the pooled rate, for reference
pooled = 100 * sum(b["top1"] for b in bk) / sum(b["n"] for b in bk)
axB.axhline(pooled, color=fs.MUTED, lw=0.7, ls=(0, (4, 3)), zorder=2)
# Every bucket's interval spans the pooled rate, so a label sitting ON the rule crosses
# an error bar wherever it is put: right-aligned near the right spine, its white halo
# cut a gap in the >=2024 bar. It now sits in the one empty column of the panel (between
# the last two buckets, above the rules they reach) with a hairline back down to the
# rule it names -- nothing is drawn over, and the label is still attached.
LX = len(bk) - 1.5
axB.plot([LX, LX], [pooled + 0.6, 39.2], color=fs.MUTED, lw=0.5, zorder=2)
axB.text(LX, 40.0, f"pooled {pooled:.0f}%", ha="center", va="bottom",
         fontsize=fs.FS_BODY, color=fs.NOTE)
axB.set_xticks(xs)
# The bucket keys in the JSON are ASCII (">=2024", "2015-2019"); the printed ticks use
# the same glyphs the prose does -- U+2265 and U+2013 -- so figure and text agree.
def tick(lab):
    return lab.replace(">=", "\u2265").replace("<=", "\u2264").replace("-", "\u2013")
axB.set_xticklabels([f"{tick(b['label'])}\n(n={b['n']})" for b in bk],
                    fontsize=fs.FS_BODY)
axB.set_xlim(-0.5, len(bk) - 0.5); axB.set_ylim(0, YMAX)
axB.set_ylabel("exact top-1 (%)"); axB.set_xlabel("source publication year", labelpad=2)
# U+2212 MINUS, not a hyphen: the caption prints "r = \u22120.007" and the figure must match
r_txt = f"r = {rc['point_biserial_r']:+.3f}".replace("-", "\u2212")
axB.text(0.02, 0.96, r_txt, transform=axB.transAxes,
         ha="left", va="top", fontsize=fs.FS_BODY, color=fs.INK)
fs.panel(axB, "b", x=-0.20)

plt.tight_layout()
plt.savefig("docs/figures/fig_contamination.png")
print("wrote docs/figures/fig_contamination.png")
