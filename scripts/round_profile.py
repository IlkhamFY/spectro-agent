#!/usr/bin/env python3
"""Compare benchmark rounds on the properties that set task difficulty.

A later round is only a fair extension of an earlier one if it is drawn from the same
place. This reports the comparison from the QUESTION files alone -- formula, IR band
count, 13C peak count -- so a round that has not been scored yet, and whose answer key
is still withheld, can be profiled without touching the key.

    python scripts/round_profile.py
    python scripts/round_profile.py data/benchmark_expand
"""
import collections, json, os, re, statistics as st, sys

HEADLINE = [("main round (spectrally clean)", "data/benchmark_main",
             "data/benchmark_main/clean_qids.json"),
            ("controlled v3", "data/benchmark_v3", None),
            ("within-compound control", "data/benchmark_v2_ctrl", None)]


def heavy_atoms(formula):
    """Heavy-atom count from an RDKit-style formula string.

    Charge suffixes are stripped first, or the '+' in 'C9H12NO2+' would be read as an
    element boundary and the charge silently counted as an atom.
    """
    f = re.split(r"[+-]", formula)[0]
    return sum(int(c) if c else 1
               for el, c in re.findall(r"([A-Z][a-z]?)(\d*)", f) if el and el != "H")


def n_c13(c_nmr):
    return len(re.findall(r'(-?\d+\.?\d*)\s*\(', c_nmr or ""))


def profile(label, d, cleanf=None):
    keep = set(json.load(open(cleanf))) if cleanf and os.path.exists(cleanf) else None
    qs = [json.loads(l) for l in open(f"{d}/questions2.jsonl")]
    if keep is not None:
        qs = [q for q in qs if q["qid"] in keep]
    if not qs:
        return []
    ha = [heavy_atoms(q["formula"]) for q in qs]
    nc = [n_c13(q["c_nmr"]) for q in qs]
    nb = [len(q["ir_bands_cm-1"]) for q in qs]
    diff = collections.Counter(q["difficulty"] for q in qs)
    lo, _, hi = st.quantiles(ha) if len(ha) > 3 else (min(ha), None, max(ha))
    print(f"  {label:<32} {len(qs):>4}   {st.median(ha):>5.0f} ({lo:.0f}-{hi:.0f})"
          f"   {st.median(nc):>5.1f}   {st.median(nb):>5.1f}"
          f"   {diff['simple']:>3}/{diff['complex']:<3}")
    return ha


def main():
    extra = sys.argv[1:] or [d for d in sorted(
        __import__("glob").glob("data/benchmark_expand*")) if os.path.isdir(d)]
    print(f"\n  {'round':<32} {'n':>4}   {'heavy (IQR)':>13}   {'13C':>5}   {'IR':>5}"
          f"   {'s/c':>7}")
    print("  " + "-" * 76)
    pooled = []
    for label, d, cleanf in HEADLINE:
        pooled += profile(label, d, cleanf)
    print("  " + "-" * 76)
    lo, _, hi = st.quantiles(pooled)
    print(f"  {'HEADLINE COHORT, pooled':<32} {len(pooled):>4}   "
          f"{st.median(pooled):>5.0f} ({lo:.0f}-{hi:.0f})")
    for d in extra:
        if not os.path.exists(f"{d}/questions2.jsonl"):
            sys.exit(f"{d}: no questions2.jsonl")
        print()
        profile(os.path.basename(d), d, f"{d}/clean_qids.json")


if __name__ == "__main__":
    main()
