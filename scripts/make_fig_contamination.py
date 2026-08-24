#!/usr/bin/env python3
"""Contamination controls: (a) formula-only ablation, (b) accuracy vs publication year."""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()

fo = json.load(open("data/modality/formulaonly_control.json"))
rc = json.load(open("data/audit/recency_control.json"))

# Shared y-scale so the two panels can be compared by eye. Ceiling is just above
# panel (b)'s upper CI, not a decorative 0–100.
YMAX = 52
fig, (axA, axB) = plt.subplots(1, 2, figsize=(fs.COL2, fs.H2), sharey=True)

# ---- (a) formula-only ablation -------------------------------------------------
labels = ["formula\nonly", "formula + IR\n+ \u00b9H + \u00b9\u00b3C"]
vals = [5.0, 23.3]
cols = [fs.MUTED, fs.BLUE]
bars = axA.bar([0, 1], vals, width=fs.BAR_W, color=cols, zorder=3)
fs.ygrid(axA)
# Counts sit above the bars: the 5% bar is too short to carry white in-bar type.
for b, v, k in zip(bars, vals, ["3/60", "14/60"]):
    axA.text(b.get_x() + b.get_width() / 2, v + 1.4, f"{v:.0f}%",
             ha="center", va="bottom", fontsize=fs.FS_BODY, fontweight="bold",
             color=fs.INK)
    axA.text(b.get_x() + b.get_width() / 2, v + 4.6, k,
             ha="center", va="bottom", fontsize=fs.FS_BODY, color=fs.INK)
axA.set_xticks([0, 1]); axA.set_xticklabels(labels)
axA.set_ylabel("exact top-1 (%)"); axA.set_ylim(0, YMAX)
fs.panel(axA, "a")

# ---- (b) accuracy vs publication year ------------------------------------------
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
fs.reflabel(axB, pooled, f"pooled {pooled:.0f}%", x=0.99, ha="right", dy_frac=0.035)
axB.set_xticks(xs)

def tick(lab):
    return lab.replace(">=", "\u2265").replace("<=", "\u2264").replace("-", "\u2013")
axB.set_xticklabels([f"{tick(b['label'])}\n(n={b['n']})" for b in bk])
axB.set_xlim(-0.5, len(bk) - 0.5); axB.set_ylim(0, YMAX)
axB.set_xlabel("source publication year", labelpad=2)
r_txt = f"r = {rc['point_biserial_r']:+.3f}".replace("-", "\u2212")
axB.text(0.02, 0.86, r_txt, transform=axB.transAxes,
         ha="left", va="top", fontsize=fs.FS_BODY, color=fs.INK)
fs.panel(axB, "b")

fs.finish(w_pad=1.6)
fs.save("docs/figures/fig_contamination.png")
print("wrote docs/figures/fig_contamination.png")
