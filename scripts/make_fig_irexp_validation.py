#!/usr/bin/env python3
"""IRexp Technical Validation — forest plot + lollipop (no pie charts).

Reads frozen audit JSON — no fabricated human expert results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import nature_design as nd  # noqa: E402

nd.apply()
OUT = ROOT / "docs/scientific_data/figures"
OUT.mkdir(parents=True, exist_ok=True)

QC = json.loads((ROOT / "docs/scientific_data/qc_structure_nmr.json").read_text())
CHEM = json.loads((ROOT / "data/audit/chemist_proxy_audit.json").read_text())["summary"]
QUAR = json.loads((ROOT / "data/audit/structure_nmr_quarantine_summary.json").read_text())
RECALL = QC["extraction_recall_proxy"]
N60 = QC["transcription_fidelity"]["n60"]
N200 = QC["transcription_fidelity"]["n200"]


def pct(r: float) -> str:
    return f"{r * 100:.1f}%"


def _fmt(n: int) -> str:
    return f"{n:,}"


fig = plt.figure(figsize=(nd.COL_FULL, 4.60))
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], hspace=0.55, wspace=0.38)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 0])
ax_d = fig.add_subplot(gs[1, 1])

# ---- (A) Transcription fidelity — lollipop with 100% reference ---------------
nd.panel(ax_a, "a")
checks_a = [
    ("bands (n=60)", N60["band_fidelity"], None, None, "560/560"),
    ("records (n=60)", N60["record_fidelity"], None, None, "60/60"),
    ("bands (n=200)", N200["band_fidelity"], None, None, "2250/2261"),
    ("records (n=200)", N200["record_fidelity"], None, None, "196/200"),
]
ys = np.arange(len(checks_a))
for i, (lab, rate, lo, hi, ntxt) in enumerate(checks_a):
  ax_a.plot([0.94, rate], [i, i], color=nd.TEAL, lw=1.8, zorder=2)
  ax_a.plot(rate, i, "o", color=nd.HERO, markersize=6, zorder=3,
            markeredgecolor="white", markeredgewidth=0.5)
  ax_a.text(-0.01, i, lab, transform=ax_a.get_yaxis_transform(),
            ha="right", va="center", fontsize=nd.FS_BODY - 0.5)
  ax_a.text(rate + 0.003, i, f"{pct(rate)}  ({ntxt})", transform=ax_a.get_yaxis_transform(),
            ha="left", va="center", fontsize=nd.FS_BODY - 0.5, fontweight="bold")
nd.refline = lambda ax, x: ax.axvline(x, color=nd.NOTE, lw=0.7, ls=(0, (4, 3)), zorder=1)
ax_a.axvline(1.0, color=nd.NOTE, lw=0.7, ls=(0, (4, 3)), zorder=1)
ax_a.set_yticks(ys)
ax_a.set_yticklabels([""] * len(ys))
ax_a.invert_yaxis()
ax_a.set_xlim(0.935, 1.012)
ax_a.set_xlabel("confirmed rate", fontsize=nd.FS_AXIS)
ax_a.set_title("Transcription fidelity (PMC re-fetch)", loc="left", pad=6,
               fontsize=nd.FS_TITLE, fontweight="bold")
ax_a.spines["left"].set_visible(False)
ax_a.tick_params(axis="y", length=0)

# ---- (B) Recall proxy — forest plot with Wilson CI ---------------------------
nd.panel(ax_b, "b")
checks_b = [
    ("band confirm", RECALL["released_bands_confirmed_in_reextract"]["rate"],
     RECALL["released_bands_confirmed_in_reextract"]["wilson95"][0],
     RECALL["released_bands_confirmed_in_reextract"]["wilson95"][1],
     f"n={RECALL['released_bands_confirmed_in_reextract']['total']}"),
    ("list recall", RECALL["list_level_recall_proxy"],
     RECALL["list_level_recall_proxy_wilson95"][0],
     RECALL["list_level_recall_proxy_wilson95"][1],
     f"n={RECALL['released_lists_total']} lists"),
    ("paper recovery", RECALL["papers_all_released_lists_recovered"]["rate"],
     RECALL["papers_all_released_lists_recovered"]["wilson95"][0],
     RECALL["papers_all_released_lists_recovered"]["wilson95"][1],
     f"n={RECALL['n']} papers"),
]
ys = np.arange(len(checks_b))
for i, (lab, rate, lo, hi, ntxt) in enumerate(checks_b):
    nd.forest_row(ax_b, i, rate, lo, hi, color=nd.HERO, label=lab, n_text=f"{pct(rate)}  {ntxt}")
ax_b.axvline(0.95, color=nd.NOTE, lw=0.6, ls=(0, (3, 3)), zorder=1)
ax_b.text(0.951, -0.6, "95%", fontsize=nd.FS_BODY - 1, color=nd.NOTE)
ax_b.set_yticks(ys)
ax_b.set_yticklabels([""] * len(ys))
ax_b.invert_yaxis()
ax_b.set_xlim(0.86, 1.08)
ax_b.set_xlabel("rate (Wilson 95% CI)", fontsize=nd.FS_AXIS)
ax_b.set_title(f"Extraction-recall proxy (n={RECALL['n']} papers)", loc="left", pad=6,
               fontsize=nd.FS_TITLE, fontweight="bold")
ax_b.spines["left"].set_visible(False)
ax_b.tick_params(axis="y", length=0)

# ---- (C) Chemist-proxy — forest by stratum -----------------------------------
nd.panel(ax_c, "c")
strata = [
    ("All", CHEM["pass_rate"], CHEM["wilson95_pass"], CHEM["n_scored"]),
    ("Chemotion", CHEM["by_stratum"]["chemotion"]["pass_rate"],
     CHEM["by_stratum"]["chemotion"]["wilson95"], CHEM["by_stratum"]["chemotion"]["n"]),
    ("PMC IR-only", CHEM["by_stratum"]["pmc_ir_only"]["pass_rate"],
     CHEM["by_stratum"]["pmc_ir_only"]["wilson95"], CHEM["by_stratum"]["pmc_ir_only"]["n"]),
    ("PMC struct. commercial", CHEM["by_stratum"]["pmc_struct_commercial"]["pass_rate"],
     CHEM["by_stratum"]["pmc_struct_commercial"]["wilson95"],
     CHEM["by_stratum"]["pmc_struct_commercial"]["n"]),
    ("PMC struct. other lic.", CHEM["by_stratum"]["pmc_struct_other_licence"]["pass_rate"],
     CHEM["by_stratum"]["pmc_struct_other_licence"]["wilson95"],
     CHEM["by_stratum"]["pmc_struct_other_licence"]["n"]),
]
ys = np.arange(len(strata))
for i, (lab, rate, (lo, hi), n) in enumerate(strata):
    nd.forest_row(ax_c, i, rate, lo, hi, color=nd.GREEN, label=lab,
                  n_text=f"{pct(rate)}  (n={n})")
ax_c.axvline(0.95, color=nd.NOTE, lw=0.6, ls=(0, (3, 3)), zorder=1)
ax_c.set_yticks(ys)
ax_c.set_yticklabels([""] * len(ys))
ax_c.invert_yaxis()
ax_c.set_xlim(0.78, 1.10)
ax_c.set_xlabel("joint pass rate (Wilson 95% CI)", fontsize=nd.FS_AXIS)
ax_c.set_title(f"Automated chemist-proxy (n={CHEM['n_scored']})", loc="left", pad=6,
               fontsize=nd.FS_TITLE, fontweight="bold")
ax_c.spines["left"].set_visible(False)
ax_c.tick_params(axis="y", length=0)

# ---- (D) Quarantine — horizontal bar inset (not pie) ---------------------------
nd.panel(ax_d, "d")
n_res = QUAR["n_records"]
n_quar = QUAR["n_quarantined"]
n_pass = n_res - n_quar
rate = QUAR["quarantine_rate_of_resolved"]

ax_d.barh([1], [n_pass], color=nd.GREEN, height=0.45, edgecolor="white", linewidth=0.8, label="pass")
ax_d.barh([0], [n_quar], color=nd.ROSE, height=0.45, edgecolor="white", linewidth=0.8, label="quarantined")
nd.xgrid(ax_d)
ax_d.set_yticks([0, 1])
ax_d.set_yticklabels([f"quarantined\n({pct(rate)})", f"pass\n({pct(1-rate)})"],
                      fontsize=nd.FS_BODY - 0.5)
ax_d.invert_yaxis()
ax_d.set_xlim(0, n_res * 1.12)
ax_d.set_xlabel("records", fontsize=nd.FS_AXIS)
for yp, val in [(1, n_pass), (0, n_quar)]:
    ax_d.text(val + n_res * 0.02, yp, _fmt(val), va="center", ha="left",
              fontsize=nd.FS_BODY, fontweight="bold")
ax_d.set_title(f"Structure–NMR quarantine (n={n_res:,} resolved)", loc="left", pad=6,
               fontsize=nd.FS_TITLE, fontweight="bold")
ax_d.spines["left"].set_visible(False)
ax_d.tick_params(axis="y", length=0)

# Inset summary box
box = FancyBboxPatch(
    (0.55, 0.08), 0.42, 0.22,
    boxstyle="round,pad=0.01,rounding_size=0.02",
    transform=ax_d.transAxes, facecolor=nd.TINT_SAND, edgecolor=nd.ORANGE,
    linewidth=0.7, zorder=10,
)
ax_d.add_patch(box)
ax_d.text(0.76, 0.19, f"{pct(rate)} flagged\n(diagnostic only;\nrelease unchanged)",
          transform=ax_d.transAxes, ha="center", va="center",
          fontsize=nd.FS_BODY - 0.5, color=nd.INK, linespacing=1.25, zorder=11)

# Automated watermark
nd.suptitle(fig, "Technical validation summary", y=0.98)
nd.watermark(fig, "Automated checks only — not NMRexp-parity human expert audits")
nd.finish(fig, pad=0.42, left=0.28, top=0.90, h_pad=2.5, w_pad=2.5)
nd.save(OUT / "fig_irexp_validation.png", fig)
plt.close(fig)
print(f"wrote {OUT / 'fig_irexp_validation.png'}")
