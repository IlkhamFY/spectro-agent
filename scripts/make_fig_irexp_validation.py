#!/usr/bin/env python3
"""IRexp Technical Validation summary (NMRexp Table 2 / Fig 3 analogue).

Reads frozen audit JSON — no fabricated human expert results.
Output: docs/scientific_data/figures/fig_irexp_validation.{png,pdf}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import figstyle as fs  # noqa: E402

fs.apply()

OUT_DIR = ROOT / "docs/scientific_data/figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QC = json.loads((ROOT / "docs/scientific_data/qc_structure_nmr.json").read_text())
CHEM = json.loads((ROOT / "data/audit/chemist_proxy_audit.json").read_text())["summary"]
QUAR = json.loads((ROOT / "data/audit/structure_nmr_quarantine_summary.json").read_text())
RECALL = QC["extraction_recall_proxy"]

fig, axes = plt.subplots(2, 2, figsize=(fs.COL2, 4.35))
(ax_a, ax_b), (ax_c, ax_d) = axes


def pct_label(rate: float) -> str:
    return f"{rate * 100:.1f}%"


# (a) Transcription fidelity
fs.panel(ax_a, "a")
n60 = QC["transcription_fidelity"]["n60"]
n200 = QC["transcription_fidelity"]["n200"]
metrics = ["bands\n(n=60)", "records\n(n=60)", "bands\n(n=200)", "records\n(n=200)"]
rates = [n60["band_fidelity"], n60["record_fidelity"], n200["band_fidelity"], n200["record_fidelity"]]
xs = np.arange(4)
bars = ax_a.bar(xs, rates, color=[fs.BLUE, fs.SKY, fs.BLUE, fs.SKY], width=0.62)
ax_a.set_xticks(xs)
ax_a.set_xticklabels(metrics, fontsize=fs.FS_BODY - 0.5)
fs.ygrid(ax_a)
ax_a.set_ylim(0.94, 1.01)
ax_a.set_ylabel("confirmed rate")
ax_a.set_title("Transcription fidelity (PMC re-fetch)", loc="left", pad=2)
for b, r in zip(bars, rates):
    ax_a.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.002,
              pct_label(r), ha="center", va="bottom", fontsize=fs.FS_BODY - 0.5)


# (b) Recall proxy with Wilson CI
fs.panel(ax_b, "b")
labels = ["band confirm", "list recall", "paper recovery"]
rates = [
    RECALL["released_bands_confirmed_in_reextract"]["rate"],
    RECALL["list_level_recall_proxy"],
    RECALL["papers_all_released_lists_recovered"]["rate"],
]
ci_lo = [
    RECALL["released_bands_confirmed_in_reextract"]["wilson95"][0],
    RECALL["list_level_recall_proxy_wilson95"][0],
    RECALL["papers_all_released_lists_recovered"]["wilson95"][0],
]
ci_hi = [
    RECALL["released_bands_confirmed_in_reextract"]["wilson95"][1],
    RECALL["list_level_recall_proxy_wilson95"][1],
    RECALL["papers_all_released_lists_recovered"]["wilson95"][1],
]
xs = np.arange(3)
yerr = np.array([np.array(rates) - np.array(ci_lo), np.array(ci_hi) - np.array(rates)])
bars = ax_b.bar(xs, rates, color=fs.BLUE, width=0.58, yerr=yerr, capsize=3,
                error_kw=dict(lw=0.85, ecolor=fs.INK, capthick=0.85))
ax_b.set_xticks(xs)
ax_b.set_xticklabels(labels)
fs.ygrid(ax_b)
ax_b.set_ylim(0.88, 1.02)
ax_b.set_ylabel("rate (Wilson 95% CI)")
ax_b.set_title(f"Extraction-recall proxy (n={RECALL['n']} papers)", loc="left", pad=2)
for b, r in zip(bars, rates):
    ax_b.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015,
              pct_label(r), ha="center", va="bottom", fontsize=fs.FS_BODY - 0.5)


# (c) Chemist-proxy by stratum
fs.panel(ax_c, "c")
strata = [
    ("All", CHEM["pass_rate"], CHEM["wilson95_pass"]),
    ("Chemotion", CHEM["by_stratum"]["chemotion"]["pass_rate"],
     CHEM["by_stratum"]["chemotion"]["wilson95"]),
    ("PMC IR-only", CHEM["by_stratum"]["pmc_ir_only"]["pass_rate"],
     CHEM["by_stratum"]["pmc_ir_only"]["wilson95"]),
    ("PMC struct.\ncommercial", CHEM["by_stratum"]["pmc_struct_commercial"]["pass_rate"],
     CHEM["by_stratum"]["pmc_struct_commercial"]["wilson95"]),
    ("PMC struct.\nother lic.", CHEM["by_stratum"]["pmc_struct_other_licence"]["pass_rate"],
     CHEM["by_stratum"]["pmc_struct_other_licence"]["wilson95"]),
]
slabels = [s[0] for s in strata]
srates = [s[1] for s in strata]
sci_lo = [s[2][0] for s in strata]
sci_hi = [s[2][1] for s in strata]
ys = np.arange(len(strata))
yerr = np.array([np.array(srates) - np.array(sci_lo), np.array(sci_hi) - np.array(srates)])
bars = ax_c.barh(ys, srates, color=fs.GREEN, height=0.58, xerr=yerr, capsize=3,
                 error_kw=dict(lw=0.85, ecolor=fs.INK, capthick=0.85))
ax_c.set_yticks(ys)
ax_c.set_yticklabels(slabels)
ax_c.invert_yaxis()
fs.xgrid(ax_c)
ax_c.set_xlim(0.82, 1.03)
ax_c.set_xlabel("joint pass rate (Wilson 95% CI)")
ax_c.set_title(f"Automated chemist-proxy (n={CHEM['n_scored']})", loc="left", pad=2)
for b, r in zip(bars, srates):
    ax_c.text(b.get_width() + 0.004, b.get_y() + b.get_height() / 2,
              pct_label(r), ha="left", va="center", fontsize=fs.FS_BODY - 0.5)


# (d) Quarantine on resolved corpus
fs.panel(ax_d, "d")
n_res = QUAR["n_records"]
n_quar = QUAR["n_quarantined"]
n_pass = n_res - n_quar
sizes = [n_pass, n_quar]
labels_pie = [f"pass\n({n_pass:,})", f"quarantined\n({n_quar:,})"]
colors_pie = [fs.GREEN, fs.VERMIL]
wedges, texts = ax_d.pie(
    sizes,
    labels=labels_pie,
    colors=colors_pie,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.2),
    textprops=dict(fontsize=fs.FS_BODY - 0.5, color=fs.INK),
)
ax_d.set_title(
    f"Structure–NMR quarantine (n={n_res:,} resolved)",
    loc="left",
    pad=2,
)
ax_d.text(
    0,
    -1.35,
    f"4.37% flagged (diagnostic; release unchanged)",
    ha="center",
    fontsize=fs.FS_BODY - 0.5,
    color=fs.NOTE,
)

fig.suptitle(
    "Technical validation summary (automated checks only)",
    x=0.01,
    y=0.99,
    ha="left",
    fontsize=fs.FS_EMPH,
    fontweight="bold",
    color=fs.INK,
)
fig.text(
    0.01,
    0.01,
    "Not NMRexp-parity human expert audits. Chemist-proxy = automated multi-check surrogate.",
    fontsize=fs.FS_BODY - 0.5,
    color=fs.NOTE,
)
fs.finish(fig, pad=0.38, left=0.10, top=0.93, h_pad=1.8, w_pad=1.6)
fs.save(str(OUT_DIR / "fig_irexp_validation.png"), fig)
plt.close(fig)
print(f"wrote {OUT_DIR / 'fig_irexp_validation.png'}")
