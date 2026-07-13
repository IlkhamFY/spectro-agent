#!/usr/bin/env python3
"""Hero figure (Fig 1) — the diagnosis as an icon array of the 60 forward-verify
compounds, so the DENOMINATORS are shown, not asserted. Of 60 real spectra:
41 the true structure is never proposed ("the wall"), 3 are recalled but mis-ranked,
16 are recalled AND verified (16/60 = 26% exact top-1 end-to-end; 16/19 = 84% of
recalled). This avoids the two-bar 31%-vs-84% chart, whose different denominators
(19/60 vs 16/19) misread as a single shared rate."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()
NCOL = 10
# bottom-to-top fill: 41 never-proposed (grey), 3 mis-ranked (vermilion), 16 verified (green)
colours = [fs.MUTED] * 41 + [fs.VERMIL] * 3 + [fs.GREEN] * 16
xs = [i % NCOL for i in range(60)]
ys = [i // NCOL for i in range(60)]

fig, ax = plt.subplots(figsize=(4.6, 2.7))
ax.scatter(xs, ys, s=62, c=colours, marker="s", edgecolor="white", linewidth=0.7, zorder=3)
ax.set_xlim(-0.8, 20.4); ax.set_ylim(-0.9, 6.0)
ax.set_aspect("equal"); ax.axis("off")

# direct, colour-matched labels on the right, aligned to each band (no legend box)
lx = 11.2
ax.text(lx, 5.0, "16", color=fs.GREEN, fontsize=11, fontweight="bold", va="center")
ax.text(lx + 1.35, 5.15, "recalled and verified", color=fs.GREEN, fontsize=7, va="center")
ax.text(lx + 1.35, 4.55, "16/60 = 26% exact top-1", color=fs.GREEN, fontsize=6, va="center")
ax.text(lx, 3.7, "3", color=fs.VERMIL, fontsize=10, fontweight="bold", va="center")
ax.text(lx + 1.35, 3.7, "recalled but mis-ranked", color=fs.VERMIL, fontsize=7, va="center")
ax.text(lx, 1.85, "41", color=fs.MUTED, fontsize=11, fontweight="bold", va="center")
ax.text(lx + 1.35, 2.25, "never proposed", color=fs.INK, fontsize=7, va="center")
ax.text(lx + 1.35, 1.55, "“the wall”", color=fs.INK, fontsize=8.5, fontweight="bold", va="center")
ax.text(lx + 1.35, 0.85, "recall 31%; of those, 84% verify", color=fs.MUTED, fontsize=6, va="center")

ax.text(-0.4, 5.85, "60 real spectra", color=fs.INK, fontsize=6.5, va="bottom", ha="left")

plt.tight_layout()
plt.savefig("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
