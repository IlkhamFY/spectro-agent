#!/usr/bin/env python3
"""Fig 3 — Data distribution + technical validation (NMRexp Fig. 3 + Fig. 4 analogue).

Panels A–E: horizontal bar distributions (NMRexp Fig 3 style)
Panel F: validation histograms with median/rate elbow annotations (NMRexp Fig 4 style)
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import nature_design as nd  # noqa: E402

nd.apply()
OUT = ROOT / "docs/scientific_data/figures"
OUT.mkdir(parents=True, exist_ok=True)

STATS = json.loads((ROOT / "data/irexp/irexp_stats.json").read_text())
QC = json.loads((ROOT / "docs/scientific_data/qc_structure_nmr.json").read_text())
CHEM = json.loads((ROOT / "data/audit/chemist_proxy_audit.json").read_text())["summary"]
QUAR = json.loads((ROOT / "data/audit/structure_nmr_quarantine_summary.json").read_text())
FULL_QUAD = 33_201
TOTAL = STATS["records"]
RECALL = QC["extraction_recall_proxy"]
N200 = QC["transcription_fidelity"]["n200"]


def _band_histogram() -> tuple[list[int], list[int]]:
    counts = Counter()
    with gzip.open(ROOT / "data/irexp/irexp.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            counts[len(r.get("ir_bands_cm-1", []) or [])] += 1
    xs = sorted(counts.keys())
    # bin to 2-cm groups for readability
    binned = Counter()
    for k, v in counts.items():
        binned[(k // 2) * 2] += v
    bx = sorted(binned.keys())
    by = [binned[k] for k in bx]
    return bx, by


def _element_counts() -> tuple[list[str], list[int]]:
    from rdkit import Chem
    els = Counter()
    with gzip.open(ROOT / "data/irexp/irexp.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("has_structure"):
                continue
            sm = r.get("smiles")
            if not sm:
                continue
            m = Chem.MolFromSmiles(sm)
            if not m:
                continue
            for sym in set(a.GetSymbol() for a in m.GetAtoms()):
                els[sym] += 1
    common = ["C", "O", "N", "S", "F", "Cl", "Br", "Si", "P"]
    rare = ["I", "B", "Se", "Fe", "Te", "Sn", "Ge", "Na", "K"]
    labels = common + rare
    vals = [els.get(s, 0) for s in labels]
    return labels, vals


def _load_transcription_errors() -> np.ndarray:
    data = json.loads((ROOT / "data/audit/extraction_audit_n200.json").read_text())
    errs = []
    for r in data["records"]:
        if r.get("bands", 0) > 0:
            errs.append(1.0 - r["confirmed"] / r["bands"])
    return np.array(errs)


def _load_paper_recall_rates() -> np.ndarray:
    data = json.loads((ROOT / "data/audit/extraction_recall_proxy_n120.json").read_text())
    rates = []
    for r in data["records"]:
        rb = r.get("released_bands", 0)
        if rb > 0:
            rates.append(r["released_bands_in_reextract"] / rb)
    return np.array(rates)


def _load_paper_list_match() -> np.ndarray:
    data = json.loads((ROOT / "data/audit/extraction_recall_proxy_n120.json").read_text())
    rates = []
    for r in data["records"]:
        n_rel = r.get("n_released_rows", 0)
        if n_rel > 0:
            rates.append(r["reextract_lists_matched"] / n_rel)
    return np.array(rates)


def _load_chemist_fail_counts() -> np.ndarray:
    counts = []
    with open(ROOT / "data/audit/chemist_proxy_audit.jsonl") as f:
        for line in f:
            r = json.loads(line)
            counts.append(len(r.get("fail_reasons", [])))
    return np.array(counts)


def _validation_histogram(ax, title: str, data: np.ndarray, aggregate: float,
                           xlabel: str, xmax: float, agg_label: str = "Rate"):
    """NMRexp Fig 4 style histogram with dashed elbow annotations (real audit data)."""
    bins = np.linspace(0, xmax, min(25, max(10, len(np.unique(data)) + 2)))
    ax.hist(data, bins=bins, color=nd.NMREXP_BLUE, edgecolor="white",
            linewidth=0.3, zorder=2)
    ax.set_xlim(0, xmax)
    ax.set_xlabel(xlabel, fontsize=nd.FS_AXIS, fontweight="bold")
    ax.set_title(title, fontsize=nd.FS_TITLE, fontweight="bold", pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", left=False, labelleft=False)
    med = float(np.median(data))
    ymax = ax.get_ylim()[1]
    ax.plot([med, med], [0, ymax * 0.55], color=nd.NOTE, lw=0.7, ls=(0, (3, 2)), zorder=4)
    ax.plot([med, med + xmax * 0.08], [ymax * 0.55, ymax * 0.55],
            color=nd.NOTE, lw=0.7, ls=(0, (3, 2)), zorder=4)
    ax.text(med + xmax * 0.02, ymax * 0.62, f"Median {med:.3f}",
            va="center", ha="left", fontsize=nd.FS_BODY - 1, fontweight="bold")
    ax.plot([aggregate, aggregate], [0, ymax * 0.82], color=nd.NOTE,
            lw=0.7, ls=(0, (3, 2)), zorder=4)
    ax.plot([aggregate, min(aggregate + xmax * 0.06, xmax * 0.92)], [ymax * 0.82, ymax * 0.82],
            color=nd.NOTE, lw=0.7, ls=(0, (3, 2)), zorder=4)
    ax.text(min(aggregate + xmax * 0.07, xmax * 0.85), ymax * 0.82,
            f"{agg_label} {aggregate:.3f}",
            va="center", ha="left", fontsize=nd.FS_BODY - 1, fontweight="bold")


def main() -> None:
    fig = plt.figure(figsize=(nd.COL_FULL, 7.4))
    gs_top = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.15], hspace=0.62, wspace=0.48,
                               top=0.96, bottom=0.07, left=0.09, right=0.98)

    # ---- Row 1: A, B, C (NMRexp Fig 3 horizontal bars) ------------------------
    ax_a = fig.add_subplot(gs_top[0, 0])
    nd.panel(ax_a, "a", x=-0.22, y=1.10)
    nd.hbar_panel(ax_a,
                  ["PMC OA", "Chemotion"],
                  [STATS["provenance_pmc"], STATS["provenance_chemotion"]],
                  title="Source", color=nd.NMREXP_BLUE)

    ax_b = fig.add_subplot(gs_top[0, 1])
    nd.panel(ax_b, "b", x=-0.12, y=1.10)
    pool_labels = ["commercial", "non-commercial", "empty / unknown",
                   "ShareAlike", "other (ND)"]
    pool_vals = [STATS["licence_pool_commercial"], STATS["licence_pool_non_commercial"],
                 STATS["licence_pool_empty_unknown"], STATS["licence_pool_sharealike"],
                 STATS["licence_pool_other"]]
    nd.hbar_panel(ax_b, pool_labels, pool_vals, title="Licence pool",
                  color=nd.NMREXP_BLUE)

    ax_c = fig.add_subplot(gs_top[0, 2])
    nd.panel(ax_c, "c", x=-0.14, y=1.10)
    mod_labels = ["all records", "+ NMR string", "structure-linked",
                  "IR+¹H+¹³C+structure"]
    mod_vals = [STATS["records"], STATS["with_co_reported_NMR"],
                STATS["with_structure"], FULL_QUAD]
    nd.hbar_panel(ax_c, mod_labels, mod_vals, title="Modality linkage",
                  color=nd.NMREXP_BLUE)

    # ---- Row 2: D (histogram), E (elements two-column), F (validation 2×2) ---
    gs_bot = gs_top[1, :].subgridspec(1, 3, width_ratios=[1.0, 1.35, 1.65], wspace=0.38)

    ax_d = fig.add_subplot(gs_bot[0, 0])
    nd.panel(ax_d, "d", x=-0.22, y=1.08)
    bx, by = _band_histogram()
    ax_d.bar(bx, by, width=1.8, color=nd.NMREXP_BLUE, edgecolor="white", linewidth=0.3)
    ax_d.set_xlabel("IR bands per record", fontsize=nd.FS_AXIS, fontweight="bold")
    ax_d.set_title("Band-count distribution", fontsize=nd.FS_TITLE, fontweight="bold", pad=4)
    ax_d.spines["top"].set_visible(False)
    ax_d.spines["right"].set_visible(False)
    nd.ygrid(ax_d)
    ax_d.set_xlim(0, 42)
    med = QC["provenance_counts"]["median_bands_pmc"]
    ax_d.axvline(med, color=nd.NOTE, lw=0.7, ls=(0, (3, 2)))
    ax_d.text(med + 0.5, max(by) * 0.9, f"PMC median {med}", fontsize=nd.FS_BODY - 1,
              color=nd.NOTE)

    ax_e = fig.add_subplot(gs_bot[0, 1])
    nd.panel(ax_e, "e", x=-0.08, y=1.08)
    el_labels, el_vals = _element_counts()
    mid = 9
    left_labels, left_vals = el_labels[:mid], el_vals[:mid]
    right_labels, right_vals = el_labels[mid:], el_vals[mid:]
    gap = max(left_vals) * 1.22
    y_all = np.arange(len(left_labels) + len(right_labels))
    ax_e.barh(y_all[:mid], left_vals, color=nd.NMREXP_BLUE, height=0.58,
              edgecolor="white", linewidth=0.4)
    ax_e.barh(y_all[mid:], right_vals, left=gap, color=nd.NMREXP_BLUE, height=0.58,
              edgecolor="white", linewidth=0.4)
    ax_e.set_yticks(y_all)
    ax_e.set_yticklabels(left_labels + right_labels, fontsize=nd.FS_BODY)
    ax_e.invert_yaxis()
    nd.ygrid(ax_e)
    ax_e.spines["left"].set_visible(True)
    ax_e.spines["left"].set_linewidth(0.6)
    ax_e.spines["bottom"].set_visible(False)
    ax_e.tick_params(axis="x", labelbottom=False, length=0)
    ax_e.tick_params(axis="y", length=0)
    ax_e.set_title("Elemental distribution (structure-linked)",
                   fontsize=nd.FS_TITLE, fontweight="bold", pad=4, loc="center")
    ax_e.set_xlim(0, gap + max(right_vals) * 1.25)
    for i, v in enumerate(left_vals):
        ax_e.text(v + max(left_vals) * 0.015, i, f"{v:,}", va="center", ha="left",
                  fontsize=nd.FS_BODY - 1, color=nd.INK)
    for i, v in enumerate(right_vals):
        ax_e.text(gap + v + max(right_vals) * 0.06, mid + i, f"{v:,}", va="center", ha="left",
                  fontsize=nd.FS_BODY - 1, color=nd.INK)
    ax_e.axvline(gap * 0.96, color=nd.INK, lw=0.6)

    # Panel F: 2×2 validation histograms (real audit-derived distributions)
    gs_f = gs_bot[0, 2].subgridspec(2, 2, hspace=0.72, wspace=0.48)
    nd.panel(fig.add_subplot(gs_bot[0, 2]), "f", x=-0.06, y=1.08)

    tx_err = _load_transcription_errors()
    paper_recall = _load_paper_recall_rates()
    list_match = _load_paper_list_match()
    fail_ct = _load_chemist_fail_counts()

    ax_f1 = fig.add_subplot(gs_f[0, 0])
    _validation_histogram(ax_f1, "Transcription error (n=200)",
                          tx_err, 1.0 - N200["band_fidelity"],
                          "per-record error rate", 1.05, agg_label="MAE proxy")

    ax_f2 = fig.add_subplot(gs_f[0, 1])
    _validation_histogram(ax_f2, "Band recall (n=120 papers)",
                          paper_recall, RECALL["released_bands_confirmed_in_reextract"]["rate"],
                          "per-paper band rate", 1.05, agg_label="Pool")

    ax_f3 = fig.add_subplot(gs_f[1, 0])
    _validation_histogram(ax_f3, "List match (n=120 papers)",
                          list_match, RECALL["list_level_recall_proxy"],
                          "per-paper list rate", 1.05, agg_label="Pool")

    ax_f4 = fig.add_subplot(gs_f[1, 1])
    _validation_histogram(ax_f4, "Chemist-proxy fails (n=280)",
                          fail_ct, 1.0 - CHEM["pass_rate"],
                          "fail-reason count", 2.5, agg_label="Fail rate")

    fig.text(0.01, 0.01,
             "Panel F: audit-derived per-record / per-paper distributions — automated checks only",
             fontsize=nd.FS_BODY - 1, color=nd.NOTE, style="italic")

    nd.save(OUT / "fig_irexp_distribution.png", fig)
    plt.close(fig)
    print(f"wrote {OUT / 'fig_irexp_distribution.png'}")


if __name__ == "__main__":
    main()
