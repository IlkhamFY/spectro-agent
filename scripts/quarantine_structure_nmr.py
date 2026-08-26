#!/usr/bin/env python3
"""Full-corpus structure–formula consistency quarantine for irexp_resolved.

Adapts spectro_scraper.quality gates to the released IRexp schema
(h_nmr / c_nmr author strings + ir_bands_cm-1 + smiles), writes:

  data/audit/structure_nmr_quarantine.jsonl.gz   — failing rows (+ reasons)
  data/audit/structure_nmr_quarantine_summary.json
  docs/scientific_data/qc_structure_nmr.json     — merged into TV summary

Hard failure reasons (physically impossible / gross parse):
  - c13_peaks_gt_carbons
  - h1_integration_gt_formula_plus_2
  - ir_band_out_of_range (350–4000 cm⁻¹)
  - smiles_unparseable

  python3 scripts/quarantine_structure_nmr.py
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spectro_scraper.extract import parse_c_peaks, parse_h_peaks  # noqa: E402
from spectro_scraper.quality import IR_MAX, IR_MIN, _carbon_and_h_counts  # noqa: E402

CORPUS = Path("data/irexp_resolved/irexp_resolved.jsonl.gz")
OUT_Q = Path("data/audit/structure_nmr_quarantine.jsonl.gz")
OUT_S = Path("data/audit/structure_nmr_quarantine_summary.json")
C13_WINDOW = (-10.0, 235.0)


def _c13_count(c_nmr: str | None) -> int | None:
    if not c_nmr:
        return None
    peaks = parse_c_peaks(c_nmr)
    # Keep only tokens whose leading float is in a physical 13C window
    n = 0
    for p in peaks:
        try:
            v = float(re.findall(r"-?\d+\.?\d*", p.shift or "")[0])
        except (IndexError, ValueError):
            continue
        if C13_WINDOW[0] <= v <= C13_WINDOW[1]:
            n += 1
    return n


def _h1_integral(h_nmr: str | None) -> int | None:
    if not h_nmr:
        return None
    peaks = parse_h_peaks(h_nmr)
    vals = [p.nuclei for p in peaks if p.nuclei]
    if not vals:
        return None
    return sum(vals)


def gate_record(rec: dict) -> list[str]:
    reasons: list[str] = []
    smi = rec.get("smiles")
    if not smi:
        reasons.append("no_smiles")
        return reasons
    counts = _carbon_and_h_counts(smi)
    if not counts:
        reasons.append("smiles_unparseable")
        return reasons
    nC, nH, _ = counts

    n_c13 = _c13_count(rec.get("c_nmr"))
    if n_c13 is not None and n_c13 > nC:
        reasons.append(f"c13_peaks_gt_carbons:{n_c13}>{nC}")

    obs_h = _h1_integral(rec.get("h_nmr"))
    if obs_h is not None and obs_h > nH + 2:
        reasons.append(f"h1_integration_gt_formula_plus_2:{obs_h}>{nH}+2")

    bands = rec.get("ir_bands_cm-1") or []
    bad_ir = sum(1 for b in bands if not (IR_MIN <= float(b) <= IR_MAX))
    if bad_ir:
        reasons.append(f"ir_band_out_of_range:{bad_ir}")

    return reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--out-quarantine", type=Path, default=OUT_Q)
    ap.add_argument("--out-summary", type=Path, default=OUT_S)
    args = ap.parse_args()

    n = 0
    with_c = with_h = 0
    c_fail = h_fail = ir_fail = unparse = 0
    reason_counts: Counter[str] = Counter()
    failed_ids: list[str] = []

    args.out_quarantine.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.corpus, "rt") as inp, gzip.open(args.out_quarantine, "wt") as out:
        for line in inp:
            rec = json.loads(line)
            n += 1
            if rec.get("c_nmr"):
                with_c += 1
            if rec.get("h_nmr"):
                with_h += 1
            reasons = gate_record(rec)
            if not reasons:
                continue
            for r in reasons:
                key = r.split(":", 1)[0]
                reason_counts[key] += 1
                if key == "c13_peaks_gt_carbons":
                    c_fail += 1
                elif key == "h1_integration_gt_formula_plus_2":
                    h_fail += 1
                elif key == "ir_band_out_of_range":
                    ir_fail += 1
                elif key == "smiles_unparseable":
                    unparse += 1
            row = {
                "id": rec.get("id"),
                "source_doi": rec.get("source_doi"),
                "inchikey": rec.get("inchikey"),
                "smiles": rec.get("smiles"),
                "license_pool": rec.get("license_pool"),
                "reasons": reasons,
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            failed_ids.append(str(rec.get("id")))

    n_fail = len(failed_ids)
    # Rates among rows that have the relevant modality
    c_denom = with_c  # scored when c_nmr present (gate only fires if peaks parsed)
    h_denom = with_h
    summary = {
        "description": "Full-corpus structure–NMR/IR consistency quarantine on irexp_resolved",
        "date": "2026-08-26",
        "corpus": str(args.corpus),
        "n_records": n,
        "n_with_c_nmr": with_c,
        "n_with_h_nmr": with_h,
        "n_quarantined": n_fail,
        "quarantine_rate_of_resolved": round(n_fail / n, 4) if n else None,
        "c13_peaks_gt_carbons": {
            "count": c_fail,
            "among_with_c_nmr": with_c,
            "rate": round(c_fail / with_c, 4) if with_c else None,
        },
        "h1_integration_gt_formula_plus_2": {
            "count": h_fail,
            "among_with_h_nmr": with_h,
            "rate": round(h_fail / with_h, 4) if with_h else None,
        },
        "ir_band_out_of_range": ir_fail,
        "smiles_unparseable": unparse,
        "reason_counts": dict(reason_counts),
        "quarantine_file": str(args.out_quarantine),
        "method": (
            "parse_h_peaks/parse_c_peaks on author strings; RDKit C/H counts; "
            "fail if 13C peak count > carbons, or 1H integral sum > formula H+2, "
            "or any IR band outside [350,4000] cm-1, or SMILES unparseable"
        ),
        "note": (
            "Quarantine is diagnostic — release files are unchanged. "
            "Re-users should filter these IDs before supervised training."
        ),
    }
    args.out_summary.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"\nwrote {n_fail} quarantined rows -> {args.out_quarantine}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
