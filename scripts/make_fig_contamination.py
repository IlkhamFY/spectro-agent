#!/usr/bin/env python3
"""Contamination controls: (a) formula-only ablation, (b) accuracy vs publication year."""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()

fo = json.load(open("data/modality/formulaonly_control.json"))
rc = json.load(open("data/audit/recency_control.json"))

YMAX = 52
fig, (axA, axB) = plt.subplots(1, 2, figsize=(fs.COL2, fs.H2), sharey=True)

# ---- (a) ------------------------------------------------------------------
labels = ["formula\nonly", "formula + IR\n+ \u00b9H + \u00b9\u00b3C"]
vals = [5.0, 23.3]
cols = [fs.MUTED, fs.BLUE]
bars = axA.bar([0, 1], vals, width=fs.BAR_W, color=cols, zorder=3)
fs.ygrid(axA)
for b, v, k in zip(bars, vals, ["3/60", "14/60"]):
    axA.text(b.get_x() + b.get_width() / 2, v + 1.6, f"{v:.0f}%",
             ha="center", va="bottom", fontsize=fs.FS_BODY, fontweight="bold",
             color=fs.INK)
    axA.text(b.get_x() + b.get_width() / 2, v + 5.0, k,
             ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.NOTE)
axA.set_xticks([0, 1])
axA.set_xticklabels(labels)
axA.set_ylabel("exact top-1 (%)")
axA.set_ylim(0, YMAX)
fs.panel(axA, "a")

# ---- (b) ------------------------------------------------------------------
bk = rc["buckets"]
xs = list(range(len(bk)))
pts = [b["pct"] for b in bk]
lo = [b["pct"] - b["ci"][0] for b in bk]
hi = [b["ci"][1] - b["pct"] for b in bk]
axB.errorbar(xs, pts, yerr=[lo, hi], fmt="o", ms=fs.MARKER, color=fs.BLUE,
             ecolor=fs.BLUE, elinewidth=fs.ERR["lw"], capsize=fs.ERR["capsize"],
             capthick=fs.ERR["capthick"], zorder=3)
fs.ygrid(axB)
pooled = 100 * sum(b["top1"] for b in bk) / sum(b["n"] for b in bk)
fs.refline(axB, y=pooled)
# Both labels outside the axes (top edge) — every CI crosses the pooled
# line, so any in-panel / on-line label collides with an error bar.
axB.text(-0.04, 1.04, f"r = {rc['point_biserial_r']:+.3f}".replace("-", "\u2212"),
         transform=axB.transAxes, ha="left", va="bottom",
         fontsize=fs.FS_BODY, color=fs.NOTE, clip_on=False)
axB.text(0.98, 1.04, f"pooled {pooled:.0f}%",
         transform=axB.transAxes, ha="right", va="bottom",
         fontsize=fs.FS_BODY, color=fs.NOTE, clip_on=False)

def tick(lab):
    return lab.replace(">=", "\u2265").replace("<=", "\u2264").replace("-", "\u2013")
axB.set_xticks(xs)
axB.set_xticklabels([f"{tick(b['label'])}\n(n={b['n']})" for b in bk])
axB.set_xlim(-0.5, len(bk) - 0.5)
axB.set_ylim(0, YMAX)
axB.set_xlabel("source publication year", labelpad=2)
fs.panel(axB, "b")

fs.finish(w_pad=1.6, left=0.13, top=0.90)
fs.save("docs/figures/fig_contamination.png")
print("wrote docs/figures/fig_contamination.png")
