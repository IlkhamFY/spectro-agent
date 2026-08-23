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

The floor on recall is *exact* when k equals the system's candidate budget: a system that
returns three candidates and reports top-3 has told you its recall outright, whether or not
it says so. Our own main arm is that case -- the solver returns at most three, and its
measured recall of 65/194 = 33.5% is identical to its published "recovered within top-3".
Where a system's pool is larger than the k it reports, the floor is a genuine lower bound
and the ceiling on precision correspondingly loose.

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
    # -- this work ---------------------------------------------------------------
    dict(system="This work, solver alone", realism="literature-reported", n=194,
         criterion="InChIKey connectivity", budget=3, top1=28.4, top_k=(3, 33.5),
         recall=33.5, precision=84.6, exact=True,
         where="Tables 2 and 7 of this paper; scripts/score_main.py",
         note="recall measured directly (65/194) and identical to recovered-within-top-3, "
              "because the solver emits at most three candidates; its own ranking is 55/65"),
    dict(system="This work, + forward-verification", realism="literature-reported", n=194,
         criterion="InChIKey connectivity", budget=3, top1=29.9, top_k=(3, 33.5),
         recall=33.5, precision=89.2, exact=True,
         where="Table 7 of this paper; scripts/forward_verify_main.py",
         note="the re-ranker exceeds the solver's own ceiling: 58/65 against 55/65"),
    dict(system="This work, stereo-strict", realism="literature-reported", n=194,
         criterion="full InChIKey (stereochemistry)", budget=3, top1=21.1, top_k=(3, 25.8),
         recall=25.8, precision=81.8, exact=True,
         where="Section 3 of this paper; scripts/score_main.py",
         note="the same runs scored strictly, for comparison with stereo-strict work"),

    # -- prior and concurrent systems, from their own published top-k -------------
    dict(system="NMR-Solver, real literature", realism="literature-reported", n=450,
         criterion="InChIKey connectivity", budget=1000, top1=52.89, top_k=(10, 67.33),
         recall=None, precision=None, exact=False,
         where="Jin et al., Supplementary Table 4 (titled 'stereochemistry ignored'); "
               "pool size num_pool=1000, Supplementary Table 3",
         note="pool far exceeds the reported k, so the recall floor is loose"),
    dict(system="NMR-Solver, simulated", realism="simulated", n=1000,
         criterion="full InChIKey (stereochemistry)", budget=1000,
         top1=66.90, top_k=(10, 89.90), recall=None, precision=None, exact=False,
         where="Jin et al., Table 1, 'exact molecular match with stereochemistry considered'",
         note="paired with the row below: one system, one criterion, two datasets"),
    dict(system="NMR-Solver, real literature", realism="literature-reported", n=450,
         criterion="full InChIKey (stereochemistry)", budget=1000,
         top1=31.56, top_k=(10, 53.78), recall=None, precision=None, exact=False,
         where="Jin et al., Supplementary Table 5 (titled 'stereochemistry preserved')",
         note="the same cells as the connectivity row above: 21 points of the difference "
              "between 52.89 and 31.56 is the criterion alone, on identical predictions"),
    dict(system="NMRAgent, Exp450", realism="literature-reported", n=450,
         criterion="InChIKey connectivity", budget=None, top1=61.60, top_k=(10, 70.00),
         recall=None, precision=None, exact=False,
         where="Fang et al., Table C, Exp450 row"),
    dict(system="Espejo Morales, AstraZeneca", realism="raw instrument files", n=34,
         criterion="full InChIKey (stereochemistry)", budget=10,
         top1=20.60, top_k=(5, 29.06), recall=None, precision=None, exact=False,
         where="Espejo Morales et al., Table 1, 'Ours (kimi-k2.6)'; Methods declare a "
               "ten-candidate output and the paper reports only k=1, 2 and 5",
         note="stereo retained: 'an incorrect stereochemical prediction results always in "
              "a zero hit'"),
    dict(system="Espejo Morales, education set", realism="curated educational", n=236,
         criterion="full InChIKey (stereochemistry)", budget=10,
         top1=80.87, top_k=(5, 90.00), recall=None, precision=None, exact=False,
         where="Espejo Morales et al., Table 1, 'Ours (kimi-k2.6)'",
         note="same agent, same backbone, same criterion as the row above; only the data "
              "differ"),
    dict(system="Alberts IR transformer, NIST 6-13 HA", realism="single-library experimental",
         n=3455, criterion="exact match, stereo handling unstated", budget=10,
         top1=63.25, top_k=(10, 83.56), recall=None, precision=None, exact=True,
         where="Alberts et al., Table 4; Methods 4.5 'ten ranked SMILES strings per sample "
               "are generated', so top-10 is the emitted list and the recall is exact",
         note="IR alone plus the formula, against IR + 1H + 13C here"),
    dict(system="Alberts IR transformer, NIST 5-35 HA", realism="single-library experimental",
         n=5024, criterion="exact match, stereo handling unstated", budget=10,
         top1=59.94, top_k=(10, 78.46), recall=None, precision=None, exact=True,
         where="Alberts et al., Table 4"),
    dict(system="SpecX transformer, random split", realism="simulated", n=99439,
         criterion="exact match, stereo handling unstated", budget=10,
         top1=59.04, top_k=(10, 81.77), recall=None, precision=None, exact=True,
         where="Xiang et al., multi-modal transformer, random split"),
    dict(system="SpecX transformer, scaffold split", realism="simulated", n=99439,
         criterion="exact match, stereo handling unstated", budget=10,
         top1=29.66, top_k=(10, 50.56), recall=None, precision=None, exact=True,
         where="Xiang et al., multi-modal transformer, scaffold split",
         note="paired with the row above: one system, one criterion, split changed"),
    dict(system="IR-Agent, experimental NIST IR", realism="single-library experimental",
         n=905, criterion="exact match, stereo handling unstated", budget=10,
         top1=10.3, top_k=(10, 21.6), recall=None, precision=None, exact=True,
         where="Noh et al., multi-agent with o3-mini; no formula supplied"),
    # Reported for one system, not spliced across two: the baseline HSQC matcher on the
    # analogue-seeded condition. Its 7/9 precision and 9/34 recall multiply to the 20.6%
    # top-1 of that same arm; the 23.5% quoted elsewhere is the reasoning-LLM re-rank, a
    # different system, and pairing it with 77.8% would break top-1 = recall x precision.
    # Not marked exact: the supplementary figures give conflicting denominators (8 against
    # 9 molecules) for the two conditions.
    dict(system="Priessner, analogue-seeded", realism="curated experimental",
         n=34, criterion="not stated", budget=None, top1=20.6, top_k=None,
         recall=26.5, precision=77.8, exact=False,
         where="Priessner et al., Supplementary Fig. 4 caption ('7 out of 9 molecules'), "
               "read in the ChemRxiv preprint; the version of record could not be opened",
         note="the one published system that reports candidate recall separately, once, "
              "in a caption"),
]


# Pairs that differ only in the data. Matched on (system, realism, criterion) -- the
# criterion is not optional: "NMR-Solver, real literature" appears twice, once scored on
# connectivity and once with stereochemistry preserved, and matching without it silently
# paired a stereo-strict simulated row against a connectivity real one. That is exactly the
# mixing the blocked table above exists to prevent, and it produced a wrong number.
STEREO = "full InChIKey (stereochemistry)"
UNSTATED = "exact match, stereo handling unstated"
PAIRS = [
    (("NMR-Solver, simulated", "simulated", STEREO),
     ("NMR-Solver, real literature", "literature-reported", STEREO)),
    (("SpecX transformer, random split", "simulated", UNSTATED),
     ("SpecX transformer, scaffold split", "simulated", UNSTATED)),
    (("Espejo Morales, education set", "curated educational", STEREO),
     ("Espejo Morales, AstraZeneca", "raw instrument files", STEREO)),
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


import math


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
        print(f"{'system':<38}{'data':<28}{'n':>5}{'top-1':>8}{'top-k':>15}"
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
            print(f"{r['system']:<38}{r['realism']:<28}{r['n']:>5}"
                  f"{fmt(r['top1']):>8}{kv:>15}{rec:>13}{prec:>13}")

    print("\nprovenance")
    for r in ROWS:
        print(f"  {r['system']}: {r['where']}")
        if r.get("note"):
            print(f"      {r['note']}")
    print("\nBounds are one-sided: top-k floors recall, and top-1/top-k ceilings the")
    print("conditional precision. A low ceiling is the informative case -- it shows that")
    print("ranking cannot be where the accuracy went.")

    # ---- the strongest evidence in the table: one system, one criterion, one k, --
    # ---- two datasets. Both terms move or only one does. -------------------------
    print("\n\n=== paired within-system controls ===")
    print("One system, one correctness criterion, one candidate budget; only the data")
    print("change. These are the only comparisons that need no cross-paper assumption.\n")
    # The absolute gap b - a is the wrong statistic for a paired comparison: it is bounded
    # above by b, so it compresses mechanically as recall falls and reads as "flat" when
    # ranking is in fact degrading. top-1 = recall x precision, so the honest split is
    # multiplicative -- log(top-1) = log(recall) + log(precision) -- and each term's share
    # of the collapse is its share of the log ratio.
    print(f"{'system':<38}{'dataset':<24}{'top-1':>7}{'recall':>8}"
          f"{'prec.':>7}{'1-a/b':>8}")
    for a, b in PAIRS:
        rows = []
        for r in (a, b):
            match = [x for x in ROWS if x["system"] == r[0] and x["realism"] == r[1]
                     and x["criterion"] == r[2]]
            if len(match) != 1:
                raise SystemExit(f"pair {r} matches {len(match)} rows, not one")
            row = match[0]
            k, tk = row["top_k"]
            rows.append(row)
            print(f"{row['system']:<38}{row['realism']:<24}{row['top1']:>6.1f}%"
                  f"{tk:>7.1f}%{100 * row['top1'] / tk:>6.1f}%"
                  f"{100 - 100 * row['top1'] / tk:>7.1f}%")
        (a1, b1), (a2, b2) = ((r["top1"], r["top_k"][1]) for r in rows)
        lr = math.log(b2 / b1)
        lp = math.log((a2 / b2) / (a1 / b1))
        print(f"{'':38}{'-> of the collapse, recall carries':<24}"
              f"{100 * lr / (lr + lp):>5.0f}%, ranking {100 * lp / (lr + lp):.0f}%")
        print()
    print("Both terms degrade; recall carries most of each collapse. The absolute gap")
    print("b - a looks flat only because it is bounded by b, which is why the share is")
    print("computed on the log ratio instead.")

    # ---- the same statistic within a single row -----------------------------------
    # -log(top-1) = -log(recall) - log(precision), so recall's share of a system's total
    # loss from perfection is log(recall)/log(top-1). Scale-free, and unlike the additive
    # miss:ranking ratio it is not driven by where the reported k happens to fall.
    print("\n\n=== recall's share of the total loss, where recall is exact ===\n")
    print(f"{'system':<38}{'data':<24}{'top-1':>7}{'recall share':>14}")
    for r in ROWS:
        if not r.get("exact") or not r.get("top_k") or r["top1"] <= 0:
            continue
        rec = r["recall"] if r.get("recall") is not None else r["top_k"][1]
        share = math.log(rec / 100) / math.log(r["top1"] / 100)
        print(f"{r['system']:<38}{r['realism']:<24}{r['top1']:>6.1f}%{100 * share:>13.0f}%")
    print("\nRecall's share rises with the realism and heterogeneity of the spectra.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
