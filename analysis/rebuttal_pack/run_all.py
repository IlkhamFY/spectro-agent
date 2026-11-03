#!/usr/bin/env python3
"""Rerun the rebuttal pack. Reads locked deposits. Writes only under outputs/."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from analyze import score  # noqa: E402
from cohort import load  # noqa: E402
from plots import before_after, fig_breakdowns, fig_main  # noqa: E402
from report import build  # noqa: E402

OUT = HERE / "outputs"


def _write_rows(path, rows, fields):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    print("loading deposits...")
    bundle = load()
    print(f"headline {len(bundle['headline'])}  ablation conditions {sorted(bundle['ablation'])}")
    for cond, raw in sorted(bundle["ablation"].items()):
        print(f"  ablation {cond}: {len(raw)} ids")
    print("scoring...")
    result = score(bundle)

    locks = {
        "n500_top1": 227,
        "n500_top3": 249,
        "n524": (result["pool_524_n"], result["pool_524_top"], result["pool_524_rec"]),
        "n530": (result["pool_530_n"], result["pool_530_top"], result["pool_530_rec"]),
    }
    if locks["n524"] != (524, 245, 268):
        raise SystemExit(f"n=524 sensitivity drifted: {locks['n524']}")
    if locks["n530"] != (530, 247, 271):
        raise SystemExit(f"n=530 sensitivity drifted: {locks['n530']}")
    if result["nmr_mismatch"]:
        raise SystemExit(f"NMRTrans rescore disagrees with hits.jsonl on {result['nmr_mismatch']} tasks")

    OUT.mkdir(exist_ok=True)
    _write_rows(
        OUT / "headline_wilson.csv",
        result["headline_rows"] + result["extra_props"],
        ["name", "metric", "k", "n", "p", "lo", "hi"],
    )
    _write_rows(
        OUT / "paired_tests.csv",
        result["paired"],
        ["family", "a", "b", "n", "metric", "diff", "lo", "hi", "b_only_a", "c_only_b", "p", "holm"],
    )
    _write_rows(OUT / "models_n60.csv", result["model60_rows"], ["name", "metric", "k", "n", "p", "lo", "hi"])
    _write_rows(OUT / "ladder24.csv", result["ladder_rows"], ["name", "metric", "k", "n", "p", "lo", "hi", "covered"])
    _write_rows(OUT / "modality.csv", result["ablation_rows"], ["set", "name", "metric", "k", "n", "p", "lo", "hi"])
    _write_rows(OUT / "by_heavy_atoms.csv", result["heavy"], ["name", "k", "n", "p", "lo", "hi"])
    _write_rows(OUT / "by_ring_class.csv", result["rings"], ["name", "k", "n", "p", "lo", "hi"])
    _write_rows(OUT / "by_functional_group.csv", result["fg"], ["name", "k", "n", "p", "lo", "hi"])

    with open(OUT / "per_item.csv", "w", newline="") as fh:
        fields = ["uid", "arm", "difficulty", "hac", "hac_bin", "ring",
                  "opus_top1", "opus_rec", "nmr_top1", "nmr_rec", "opus_formula_ok", "tani"]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for it in bundle["headline"]:
            w.writerow(it)

    near = {k: v for k, v in result["near"].items() if k not in ("tanis", "mces_sims", "mces_dists")}
    summary = {
        "expand_sha": bundle["expand_sha"],
        "nmr_mismatch": result["nmr_mismatch"],
        "repeats": result["repeats"],
        "modality_availability": result["modality_avail"],
        "near_miss": near,
        "wall_locked": bundle["wall"],
        "sensitivity": {
            "n524": locks["n524"],
            "n530": locks["n530"],
        },
    }
    json.dump(summary, open(OUT / "summary.json", "w"), indent=2)
    print("near-miss", json.dumps(near))

    print("drawing...")
    fig_main(bundle, result, str(OUT / "fig_main_results"))
    fig_breakdowns(bundle, result, str(OUT / "fig_breakdowns"))
    before = HERE / "inputs" / "before"
    before_after(
        before / "fig1_lead_overview.png",
        OUT / "fig_main_results.png",
        OUT / "before_after_overview.png",
        "Before: submitted overview (point estimates, no interval)",
        "After: same headline, with intervals, slices, and the other deposited model",
    )
    before_after(
        before / "fig_robustness.png",
        OUT / "fig_main_results.png",
        OUT / "before_after_robustness.png",
        "Before: submitted robustness figure (interval on one panel)",
        "After: rescored models, Wilson intervals on every accuracy",
    )
    text = build(bundle, result)
    (OUT / "REPORT.md").write_text(text)
    (HERE / "REPORT.md").write_text(text)
    print("wrote", OUT)
    print(text.split("## 1.")[0])


if __name__ == "__main__":
    main()
