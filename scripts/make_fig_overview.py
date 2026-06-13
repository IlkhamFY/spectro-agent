#!/usr/bin/env python3
"""Figure 1 — study-design schematic (pipeline overview), Nature-style.
Four stages left->right, each with a result chip; a training-free banner below."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY="#013a63"; BLUE="#2a6f97"; MID="#468faf"; SKY="#89c2d9"; PALE="#e9f3f8"
INK="#102a37"; GREY="#5b6b75"

fig, ax = plt.subplots(figsize=(11.6, 5.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.axis("off")

XS = [2, 27, 52, 77]; W = 21
BTOP, BBOT = 47.5, 26.5            # box vertical extent

def box(x, y, w, h, fc, ec=INK, lw=1.2, r=2.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.2,rounding_size={r}",
                 fc=fc, ec=ec, lw=lw, zorder=2))
def head(x, y, t, s=12.5):
    ax.text(x, y, t, ha="left", va="top", fontsize=s, fontweight="bold", color=NAVY, zorder=4)
def bullet(x, y, t, s=9.3):
    ax.text(x, y, t, ha="left", va="top", fontsize=s, color=INK, zorder=4)

STAGES = [
    ("1  DATA", "IRexp mining",
     ["• PMC-OA + Chemotion full text\n  (open, CC-BY / CC-BY-SA)",
      "• browser-free parser →\n  IR bands + ¹H/¹³C lists",
      "• OPSIN / RDKit / PubChem\n  structure resolution"],
     "121k IR · 42,842 structures"),
    ("2  BENCHMARK", "IRSpectra-Bench",
     ["• complexity-stratified\n  (simple / complex)",
      "• spectral audit (57/60 clean)",
      "• 194 blind problems:\n  formula + IR + ¹H + ¹³C"],
     "+48 electrolyte subset"),
    ("3  BLIND SOLVING", "Decoupled LLM agents",
     ["• closed-book, no web,\n  fresh context per compound",
      "• ≤3 ranked candidate SMILES",
      "• RDKit InChIKey scoring\n  + bootstrap 95% CIs"],
     "top-1 28.4% · scaffold 67%"),
    ("4  FORWARD VERIFICATION", "Generate–verify",
     ["• forward-predict each\n  candidate's ¹³C (blind)",
      "• match predicted ↔ observed\n  (chamfer distance)",
      "• re-rank → best match\n  (NMR-crystallography analog)"],
     "84% conditional · recall-bound"),
]

for x, (chip, title, bullets, result) in zip(XS, STAGES):
    ax.text(x + 0.4, 50.4, chip, fontsize=9.3, fontweight="bold", color=BLUE, va="top")
    box(x, BBOT, W, BTOP - BBOT, PALE)
    head(x + 1.2, 46.2, title)
    yy = 42.3
    for b in bullets:
        bullet(x + 1.2, yy, b)
        yy -= 4.7
    # result chip below the box
    box(x + 0.6, 21.5, W - 1.2, 3.3, NAVY, ec="none", r=1.6)
    ax.text(x + W/2, 23.15, result, ha="center", va="center", fontsize=8.6,
            color="white", fontweight="bold", zorder=4)

# flow arrows between boxes
for x in XS[:-1]:
    ax.add_patch(FancyArrowPatch((x + W + 0.2, 37), (x + 25 - 0.2, 37),
                 arrowstyle="-|>", mutation_scale=20, lw=2.4, color=BLUE, zorder=3))

# training-free banner
ax.add_patch(FancyBboxPatch((2, 10.5), 96, 6.0, boxstyle="round,pad=0.2,rounding_size=2.5",
             fc=SKY, ec="none", zorder=1))
ax.text(50, 13.5, "Training-free  ·  no fine-tuning  ·  no paid API  —  LLM agents under one "
        "subscription, fully reproducible", ha="center", va="center", fontsize=10.6,
        color=NAVY, fontweight="bold")

ax.text(2, 4.2, "Figure 1.  Study design: open multimodal data → blind, stratified benchmark → "
        "decoupled blind solving → forward-verification re-ranking.",
        fontsize=9.2, color=GREY)

plt.tight_layout()
plt.savefig("docs/figures/fig0_overview.png", dpi=170, bbox_inches="tight")
print("wrote docs/figures/fig0_overview.png")
