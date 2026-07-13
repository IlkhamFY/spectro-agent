#!/usr/bin/env python3
"""Hero figure (Fig 1) — the diagnosis as an icon array of the 60 forward-verify
compounds, so the DENOMINATORS are shown, not asserted. Of 60 real spectra:
41 the true structure is never proposed ("the wall"), 3 are recalled but mis-ranked,
16 are recalled AND verified (16/60 = 26% exact top-1 end-to-end; 16/19 = 84% of
recalled). This avoids the two-bar 31%-vs-84% chart, whose different denominators
(19/60 vs 16/19) misread as a single shared rate. Full-column width."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs

fs.apply()
NCOL = 10
# bottom-to-top fill: 41 never-proposed (grey), 3 mis-ranked (vermilion), 16 verified (green)
colours = [fs.MUTED] * 41 + [fs.VERMIL] * 3 + [fs.GREEN] * 16
xs = [i % NCOL for i in range(60)]
ys = [i // NCOL for i in range(60)]

fig = plt.figure(figsize=(fs.COL2, 2.5))
ax = fig.add_axes([0, 0, 1, 1])          # fill the frame; no default subplot margins
ax.scatter(xs, ys, s=250, c=colours, marker="s", edgecolor="white", linewidth=0.9, zorder=3)
# data box aspect (17.6 : 7.0 = 2.51) matches the figure aspect (6.30 : 2.50) so the
# equal-aspect squares fill the frame with only a thin uniform margin
ax.set_xlim(-0.9, 16.7); ax.set_ylim(-0.6, 6.4)
ax.set_aspect("equal"); ax.axis("off")

# direct, colour-matched labels on the right, aligned to each band (no legend box)
lx = 10.6
tx = lx + 0.95
ax.text(lx, 5.0, "16", color=fs.GREEN, fontsize=fs.FS_EMPH, fontweight="bold", va="center")
ax.text(tx, 5.15, "recalled and verified", color=fs.GREEN, fontsize=fs.FS_BODY, va="center")
ax.text(tx, 4.55, "16/60 = 26% exact top-1", color=fs.GREEN, fontsize=fs.FS_SMALL, va="center")
ax.text(lx, 3.7, "3", color=fs.VERMIL, fontsize=fs.FS_EMPH, fontweight="bold", va="center")
ax.text(tx, 3.7, "recalled but mis-ranked", color=fs.VERMIL, fontsize=fs.FS_BODY, va="center")
ax.text(lx, 1.7, "41", color=fs.MUTED, fontsize=fs.FS_EMPH, fontweight="bold", va="center")
ax.text(tx, 2.1, "never proposed", color=fs.INK, fontsize=fs.FS_BODY, va="center")
ax.text(tx, 1.5, "“the wall”", color=fs.INK, fontsize=fs.FS_BODY, fontweight="bold", va="center")
ax.text(tx, 0.85, "recall 31%; of those, 84% verify", color=fs.MUTED,
        fontsize=fs.FS_SMALL, va="center")

ax.text(-0.4, 5.85, "60 real spectra", color=fs.INK, fontsize=fs.FS_SMALL, va="bottom", ha="left")

plt.savefig("docs/figures/fig_wall.png")
print("wrote docs/figures/fig_wall.png")
