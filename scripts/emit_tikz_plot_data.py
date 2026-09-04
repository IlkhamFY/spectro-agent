#!/usr/bin/env python3
"""Emit TikZ/PGFPlots data snippets from frozen_plot_data.json."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/scientific_data/figures/tikz/frozen_plot_data.json"
OUT = ROOT / "docs/scientific_data/figures/tikz/plot_data.tex"


def main() -> None:
    d = json.loads(DATA.read_text())
    s = d["stats"]
    lines = [
        "% Auto-generated from frozen_plot_data.json — do not edit by hand.",
        f"\\newcommand{{\\IRexpTotal}}{{{s['records']}}}",
        f"\\newcommand{{\\IRexpStruct}}{{{s['with_structure']}}}",
        f"\\newcommand{{\\IRexpCommercial}}{{{s['licence_pool_commercial']}}}",
        f"\\newcommand{{\\IRexpNMR}}{{{s['with_co_reported_NMR']}}}",
        f"\\newcommand{{\\IRexpPMC}}{{{s['provenance_pmc']}}}",
        f"\\newcommand{{\\IRexpChemotion}}{{{s['provenance_chemotion']}}}",
        f"\\newcommand{{\\IRexpNC}}{{{s['licence_pool_non_commercial']}}}",
        f"\\newcommand{{\\IRexpEmpty}}{{{s['licence_pool_empty_unknown']}}}",
        f"\\newcommand{{\\IRexpSA}}{{{s['licence_pool_sharealike']}}}",
        f"\\newcommand{{\\IRexpOther}}{{{s['licence_pool_other']}}}",
        f"\\newcommand{{\\IRexpQuad}}{{{d['full_quad']}}}",
        f"\\newcommand{{\\NMRexpN}}{{{d['nmrexp']}}}",
        f"\\newcommand{{\\SDBSN}}{{{d['sdbs']}}}",
        f"\\newcommand{{\\NISTN}}{{{d['nist']}}}",
        f"\\newcommand{{\\BandMedian}}{{{d['band_hist']['median_pmc']}}}",
        f"\\newcommand{{\\TxMAE}}{{{d['validation']['aggregates']['tx_mae']}}}",
        f"\\newcommand{{\\BandRecallPool}}{{{d['validation']['aggregates']['band_recall_pool']}}}",
        f"\\newcommand{{\\ListMatchPool}}{{{d['validation']['aggregates']['list_match_pool']}}}",
        f"\\newcommand{{\\FailRate}}{{{d['validation']['aggregates']['fail_rate']}}}",
        "",
        "% Band histogram coordinates (x,y)",
        "\\newcommand{\\BandHistCoords}{",
    ]
    for x, y in d["band_hist"]["pairs"]:
        lines.append(f"({x},{y})")
    lines.append("}")
    lines.append("")
    lines.append("% Element bars")
    labels = d["elements"]["labels"]
    vals = d["elements"]["values"]
    lines.append("\\newcommand{\\ElementCommonCoords}{")
    for i, (lab, v) in enumerate(zip(labels[:9], vals[:9])):
        lines.append(f"({v},{8-i})% {lab}")
    lines.append("}")
    lines.append("\\newcommand{\\ElementRareCoords}{")
    for i, (lab, v) in enumerate(zip(labels[9:], vals[9:])):
        lines.append(f"({v},{8-i})% {lab}")
    lines.append("}")
    lines.append("\\newcommand{\\ElementCommonLabels}{" + ",".join(labels[:9]) + "}")
    lines.append("\\newcommand{\\ElementRareLabels}{" + ",".join(labels[9:]) + "}")
    for i, (lab, v) in enumerate(zip(labels, vals)):
        safe = lab.replace("+", "Plus")
        lines.append(f"\\newcommand{{\\El{safe}}}{{{v}}}")

    def hist_macro(name: str, key: str) -> None:
        h = d["validation"][key]
        lines.append(f"\\newcommand{{\\{name}Median}}{{{h['median']}}}")
        lines.append(f"\\newcommand{{\\{name}Coords}}{{")
        for c, ct in zip(h["centers"], h["counts"]):
            lines.append(f"({c:.4f},{ct})")
        lines.append("}")
        # also bin edges for ybar interval if needed
        w = (h["edges"][1] - h["edges"][0]) if len(h["edges"]) > 1 else 0.05
        lines.append(f"\\newcommand{{\\{name}BinWidth}}{{{w:.5f}}}")

    hist_macro("TxErr", "tx_err")
    hist_macro("PaperRecall", "paper_recall")
    hist_macro("ListMatch", "list_match")
    hist_macro("FailCt", "fail_ct")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
