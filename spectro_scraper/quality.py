"""
Data-quality audit for harvested spectra.

Scraped spectral data is only useful if it is *correct*. This module quantifies
quality on several independent axes, the strongest being a **physics-based
cross-check against the resolved structure**: a molecule's ``13C`` signal count
can never exceed its carbon count, and its ``1H`` integration sum can never
exceed its hydrogen count. Where OPSIN gave us a structure, those bounds turn
the molecule itself into ground truth for the scraped NMR.

Axes
----
* completeness   -- coverage of 1H / 13C / IR / structure
* shift validity -- fraction of peaks inside physical ppm windows
* structure check-- 13C<=C, 13C/symmetry-unique ratio, 1H-integration vs HC,
                    SELFIES->SMILES round-trip
* duplicates     -- residual InChIKey collisions
* field hygiene  -- multiplicity vocabulary, coupling-constant sanity

Run::

    python -m spectro_scraper.quality data/output/spectra.jsonl
"""

from __future__ import annotations

import json
import re
from collections import Counter

# Physical windows (generous, to flag only true parse errors, not edge chemistry
# like chelated enols ~16 ppm or metal hydrides <0).
H_MIN, H_MAX = -5.0, 17.5
C_MIN, C_MAX = -10.0, 235.0
IR_MIN, IR_MAX = 350.0, 4000.0

_KNOWN_MULT = {
    "s", "d", "t", "q", "p", "m", "h", "dd", "ddd", "dddd", "dt", "td", "tt",
    "dq", "qd", "ddt", "dtd", "tdd", "dddd", "hept", "sext", "sept", "quint",
    "br", "brs", "brd", "brt", "brm", "br.s", "br.d", "tq", "qt", "spt", "oct",
}

try:
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    _HAVE_RDKIT = True
except Exception:  # pragma: no cover
    _HAVE_RDKIT = False

try:
    import selfies as _sf
    _HAVE_SELFIES = True
except Exception:  # pragma: no cover
    _HAVE_SELFIES = False


def _peak_values(peak: dict) -> list[float]:
    """Numeric ppm value(s) of a peak; a 'a-b' range yields both endpoints."""
    return [float(x) for x in re.findall(r"\d+\.?\d*", peak.get("shift", ""))]


def _carbon_and_h_counts(smiles: str):
    """(total C, total H, symmetry-unique C) from a SMILES, or None."""
    if not _HAVE_RDKIT:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    nC = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == "C")
    nH = sum(a.GetTotalNumHs() for a in mol.GetAtoms())
    ranks = list(Chem.CanonicalRankAtoms(mol, breakTies=False))
    uniqC = len({ranks[a.GetIdx()] for a in mol.GetAtoms() if a.GetSymbol() == "C"})
    return nC, nH, uniqC


def audit(records: list[dict]) -> dict:
    n = len(records)
    rep: dict = {"n_records": n}
    if n == 0:
        return rep

    # -- completeness --
    hasH = sum(1 for r in records if r.get("h_peaks"))
    hasC = sum(1 for r in records if r.get("c_peaks"))
    hasBoth = sum(1 for r in records if r.get("h_peaks") and r.get("c_peaks"))
    hasIR = sum(1 for r in records if r.get("ir_bands"))
    hasSMI = sum(1 for r in records if r.get("smiles"))
    rep["completeness"] = {
        "h_nmr": hasH, "c_nmr": hasC, "both": hasBoth,
        "ir": hasIR, "structure": hasSMI,
        "pct_both": round(100 * hasBoth / n, 1),
        "pct_ir": round(100 * hasIR / n, 1),
    }

    # -- shift validity --
    h_tot = h_bad = c_tot = c_bad = ir_tot = ir_bad = 0
    for r in records:
        for p in r.get("h_peaks", []):
            for v in _peak_values(p):
                h_tot += 1
                if not (H_MIN <= v <= H_MAX):
                    h_bad += 1
        for p in r.get("c_peaks", []):
            for v in _peak_values(p):
                c_tot += 1
                if not (C_MIN <= v <= C_MAX):
                    c_bad += 1
        for b in r.get("ir_bands", []):
            ir_tot += 1
            if not (IR_MIN <= b <= IR_MAX):
                ir_bad += 1
    rep["shift_validity"] = {
        "h_peaks": h_tot, "h_out_of_range": h_bad,
        "h_bad_pct": round(100 * h_bad / max(h_tot, 1), 2),
        "c_peaks": c_tot, "c_out_of_range": c_bad,
        "c_bad_pct": round(100 * c_bad / max(c_tot, 1), 2),
        "ir_bands": ir_tot, "ir_out_of_range": ir_bad,
    }

    # -- structure cross-check --
    c_ok = c_impossible = h_match = h_over = h_under = 0
    sel_ok = sel_tot = checked = 0
    ratios = []
    for r in records:
        smi = r.get("smiles")
        if not smi:
            continue
        counts = _carbon_and_h_counts(smi)
        if not counts:
            continue
        checked += 1
        nC, nH, uniqC = counts
        obsC = len(r.get("c_peaks", []))
        if obsC:
            if obsC > nC:
                c_impossible += 1
            else:
                c_ok += 1
            ratios.append(obsC / max(uniqC, 1))
        obsH = sum(p["nuclei"] for p in r.get("h_peaks", []) if p.get("nuclei"))
        if obsH:
            if obsH > nH + 1:
                h_over += 1
            elif obsH < nH - 2:
                h_under += 1
            else:
                h_match += 1
        sel = r.get("selfies")
        if sel and _HAVE_SELFIES and _HAVE_RDKIT:
            sel_tot += 1
            try:
                back = _sf.decoder(sel)
                if Chem.MolToSmiles(Chem.MolFromSmiles(back)) == \
                        Chem.MolToSmiles(Chem.MolFromSmiles(smi)):
                    sel_ok += 1
            except Exception:
                pass
    rep["structure_check"] = {
        "checked": checked,
        "c13_within_carbon_count": c_ok,
        "c13_impossible": c_impossible,
        "c13_obs_over_unique_median": round(sorted(ratios)[len(ratios) // 2], 2)
        if ratios else None,
        "h1_integration_matches_formula": h_match,
        "h1_over_formula": h_over,
        "h1_under_formula_exchangeable": h_under,
        "selfies_roundtrip": f"{sel_ok}/{sel_tot}",
    }

    # -- duplicates --
    iks = [r["inchikey"] for r in records if r.get("inchikey")]
    dup = sum(c - 1 for c in Counter(iks).values() if c > 1)
    rep["duplicates"] = {"inchikey_collisions": dup}

    # -- field hygiene --
    bad_mult = Counter()
    big_j = 0
    for r in records:
        for p in r.get("h_peaks", []):
            mlt = (p.get("multiplicity") or "").lower()
            if mlt and mlt not in _KNOWN_MULT:
                bad_mult[mlt] += 1
        for p in r.get("h_peaks", []) + r.get("c_peaks", []):
            for j in p.get("j", []):
                if j > 300:
                    big_j += 1
    rep["field_hygiene"] = {
        "unknown_multiplicities": sum(bad_mult.values()),
        "unknown_multiplicity_examples": dict(bad_mult.most_common(5)),
        "implausible_J_over_300Hz": big_j,
    }

    # -- single headline score (0-100): clean shifts, no impossible structures --
    shift_clean = 1 - (h_bad + c_bad) / max(h_tot + c_tot, 1)
    struct_clean = 1 - (c_impossible + h_over) / max(checked, 1) if checked else 1.0
    rep["quality_score"] = round(100 * (0.6 * shift_clean + 0.4 * struct_clean), 1)
    return rep


def format_report(rep: dict) -> str:
    if rep.get("n_records", 0) == 0:
        return "no records"
    c = rep["completeness"]; s = rep["shift_validity"]
    sc = rep["structure_check"]; fh = rep["field_hygiene"]
    L = []
    L.append(f"records           : {rep['n_records']}")
    L.append(f"completeness      : 1H={c['h_nmr']} 13C={c['c_nmr']} both={c['both']} "
             f"({c['pct_both']}%) IR={c['ir']} ({c['pct_ir']}%) structure={c['structure']}")
    L.append(f"shift validity    : 1H bad {s['h_bad_pct']}%  13C bad {s['c_bad_pct']}%  "
             f"IR out-of-range {s['ir_out_of_range']}/{s['ir_bands']}")
    L.append(f"structure x-check : 13C<=C {sc['c13_within_carbon_count']} ok / "
             f"{sc['c13_impossible']} impossible | 13C obs/unique median "
             f"{sc['c13_obs_over_unique_median']} | 1H vs formula "
             f"{sc['h1_integration_matches_formula']} match/{sc['h1_over_formula']} over/"
             f"{sc['h1_under_formula_exchangeable']} under | SELFIES rt {sc['selfies_roundtrip']}")
    L.append(f"duplicates        : {rep['duplicates']['inchikey_collisions']} InChIKey collisions")
    L.append(f"field hygiene     : {fh['unknown_multiplicities']} odd multiplicities "
             f"{fh['unknown_multiplicity_examples']} | J>300Hz {fh['implausible_J_over_300Hz']}")
    L.append(f"QUALITY SCORE     : {rep['quality_score']}/100")
    return "\n".join(L)


def main(argv=None) -> int:
    import sys
    path = (argv or sys.argv[1:])[0] if (argv or sys.argv[1:]) else "data/output/spectra.jsonl"
    records = [json.loads(line) for line in open(path)]
    rep = audit(records)
    print(format_report(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
