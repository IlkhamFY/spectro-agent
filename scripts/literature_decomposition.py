#!/usr/bin/env python3
"""Apply the recall/verification decomposition to every published system, not just ours.

The decomposition this paper reports -- how often the true structure is *proposed*, against
how often it is *ranked first once proposed* -- is not something the field measures. Papers
report top-1, and often top-k, and stop. But top-k is not silent about the split, and the
arithmetic that recovers it needs no data beyond what is already printed.

For a system that returns a ranked list and reports top-1 = a and top-k = b:

    recall >= b            the true structure was in the candidate set at least as often as
                           it reached the top k, so top-k is a floor on recall
    precision | recall
        <= a / b           if recall were exactly b then precision would be a/b; any recall
                           above b divides the same a by a larger number, so a/b is a ceiling
    ranking loss >= b - a  the compounds where the truth was found and then not ranked first

Both are one-sided, and that is the point: a *ceiling* on conditional precision is what
decides whether ranking can be the dominant loss. Where the ceiling is high the question is
open; where it is low, ranking is provably not where the accuracy went.

One thing the ceiling is *not*. It bounds the ranking the reported pipeline already does,
and a system can exceed it only by adding something that re-orders the candidates. This
paper's own numbers show the gap: the solver's own ranking puts the truth first for 55 of
the 65 compounds where it was proposed (84.6%, and 28.4/33.5 = 84.8% recovers that from the
published top-1 and top-3 alone), while forward-verification re-ranking reaches 58/65 =
89.2%. So a/b measures how well a system already orders what it has found, and the distance
from a/b to 100% is the room a re-ranker has. Reading the ceiling as if it bounded any
possible verifier would be wrong.

Every row carries its correctness criterion, because mixing a stereochemistry-strict number
with a connectivity-only one would make the table worse than nothing. Rows are only
comparable within a criterion, and the printout says so.

  python scripts/literature_decomposition.py
  python scripts/literature_decomposition.py --check   # fail if a row lacks provenance
"""
import sys

# Each row: what was run, on what, and the numbers as printed. `top_k` is (k, value).
# `criterion` is the correctness test, because a stereo-strict number and a connectivity
# number are not on the same axis. `where` is the provenance -- table or section in the
# cited work -- and no row may enter this table without one.
ROWS = [
    dict(system="This work, solver alone", data="IRexp literature IR + 1H/13C",
         realism="literature-reported", n=194, formula=True,
         criterion="InChIKey connectivity",
         top1=28.4, top_k=(3, 33.5),
         recall=33.5, precision=84.6,
         where="Tables 2 and 7 of this paper; scripts/score_main.py",
         note="recall and its own ranking measured directly (65/194 and 55/65); the bound "
              "from the published top-1 and top-3 alone would give >=33.5% and <=84.8%, "
              "which is how every other row here is read"),
    dict(system="This work, + forward-verification", data="IRexp literature IR + 1H/13C",
         realism="literature-reported", n=194, formula=True,
         criterion="InChIKey connectivity",
         top1=29.9, top_k=(3, 33.5),
         recall=33.5, precision=89.2,
         where="Table 7 of this paper; scripts/forward_verify_main.py",
         note="the re-ranker exceeds the solver's own ceiling: 58/65 against 55/65"),
    dict(system="This work, stereo-strict", data="IRexp literature IR + 1H/13C",
         realism="literature-reported", n=194, formula=True,
         criterion="full InChIKey (stereochemistry)",
         top1=21.1, top_k=(3, 25.8),
         recall=None, precision=None,
         where="Section 3 of this paper; scripts/score_main.py",
         note="the same runs scored strictly, for comparison with stereo-strict work"),
]


def bound(row):
    """-> (recall floor, conditional-precision ceiling, ranking-loss floor) or None."""
    if not row.get("top_k") or row.get("top1") is None:
        return None
    k, b = row["top_k"]
    a = row["top1"]
    if not b:
        return None
    return b, 100.0 * a / b, b - a


def fmt(x, suffix="%"):
    return "—" if x is None else f"{x:.1f}{suffix}"


def main():
    strict = "--check" in sys.argv
    missing = [r["system"] for r in ROWS if not r.get("where")]
    if strict and missing:
        print("rows without provenance:", ", ".join(missing))
        return 1

    by_criterion = {}
    for r in ROWS:
        by_criterion.setdefault(r["criterion"], []).append(r)

    for criterion, rows in by_criterion.items():
        print(f"\n=== correctness criterion: {criterion} "
              f"— rows are comparable only within this block ===\n")
        print(f"{'system':<34}{'data':<22}{'n':>5}{'top-1':>8}{'top-k':>15}"
              f"{'recall':>13}{'prec|rec':>13}")
        for r in rows:
            bd = bound(r)
            if r.get("recall") is not None:
                rec, prec = f"{r['recall']:.1f}%", f"{r['precision']:.1f}%"
            elif bd:
                rec, prec = f">= {bd[0]:.1f}%", f"<= {bd[1]:.1f}%"
            else:
                rec = prec = "not reported"
            kv = f"{r['top_k'][1]:.1f}% (k={r['top_k'][0]})" if r.get("top_k") else "—"
            print(f"{r['system']:<34}{r['realism']:<22}{r['n']:>5}"
                  f"{fmt(r['top1']):>8}{kv:>15}{rec:>13}{prec:>13}")

    print("\nprovenance")
    for r in ROWS:
        print(f"  {r['system']}: {r['where']}")
        if r.get("note"):
            print(f"      {r['note']}")
    print("\nBounds are one-sided: top-k floors recall, and top-1/top-k ceilings the")
    print("conditional precision. A low ceiling is the informative case -- it shows that")
    print("ranking cannot be where the accuracy went.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
