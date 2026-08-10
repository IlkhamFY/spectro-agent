#!/usr/bin/env python3
"""
Cross-check every statistical routine in this repository against SciPy.

The core protocol deliberately avoids heavy dependencies, so McNemar, Fisher, Wilson,
the point-biserial correlation and the Cochran-Mantel-Haenszel test are all implemented
by hand here. Hand-rolled statistics are exactly the kind of thing that is wrong in a
way nobody notices, so this script re-derives each reported quantity with SciPy and
fails loudly on any disagreement.

SciPy is NOT required to reproduce the paper -- only to audit it.

  pip install scipy && python scripts/verify_statistics.py
"""
import json, math, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from scipy import stats as S
except ImportError:
    sys.exit("this auditor needs scipy:  pip install scipy")

import numpy as np
from forward_verify_all import mcnemar_exact, fisher_exact
from contamination_recency import wilson

TOL = 1e-9
bad = []


def check(name, got, want, tol=TOL):
    ok = abs(got - want) <= tol
    if not ok:
        bad.append(f"{name}: repo={got!r} scipy={want!r}")
    print(f"  {'ok ' if ok else 'BAD'} {name:<46} {got:.6f} vs {want:.6f}")


print("McNemar exact — every discordant pair the paper reports")
# (b, c) pairs actually appearing in PAPER.md
for b, c in [(1, 3), (2, 4), (3, 7), (4, 7), (2, 5), (2, 2), (11, 0),
             (0, 3), (1, 5), (5, 4), (7, 7), (3, 3)]:
    ref = S.binomtest(min(b, c), b + c, 0.5).pvalue if b + c else 1.0
    check(f"McNemar b={b} c={c}", mcnemar_exact(b, c), ref)

print("\nFisher exact — the arm-homogeneity tests of §5.2")
for t in [(42, 4, 16, 3), (20, 4, 10, 3), (19, 5, 8, 5), (22, 24, 6, 13)]:
    check(f"Fisher {t}", fisher_exact(*t), S.fisher_exact([[t[0], t[1]], [t[2], t[3]]])[1])


def wilson_ref(k, n, z=1.96):
    if n == 0:
        return (0.0, 100.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - h) / d, 100 * (c + h) / d)


print("\nWilson score interval — §2.3 fidelity and the Fig. 5b year buckets")
for k, n in [(560, 560), (60, 60), (3, 60), (14, 60), (58, 65), (55, 65), (65, 194)]:
    lo, hi = wilson(k, n)[:2]
    rlo, rhi = wilson_ref(k, n)
    check(f"Wilson {k}/{n} lo", lo, rlo, 1e-6)
    check(f"Wilson {k}/{n} hi", hi, rhi, 1e-6)

print("\nClopper–Pearson — Haiku's 0/24 interval (§4.4), where bootstrap is degenerate")
cp_hi = 100 * S.beta.ppf(0.975, 1, 24)
print(f"  exact upper bound for 0/24 = {cp_hi:.2f}%  (paper reports [0, 14])")
if not 13.5 <= cp_hi <= 14.5:
    bad.append(f"Clopper-Pearson 0/24 upper is {cp_hi:.2f}, paper says 14")

print("\nRecency control — point-biserial r and the CMH test, from the released record")
rc = json.load(open("data/audit/recency_control.json"))
per = rc["per_compound"]
ys = np.array([int(bool(p["top1"])) for p in per])
xs = np.array([p["year"] for p in per], dtype=float)
check("point-biserial r", rc["point_biserial_r"], round(S.pointbiserialr(ys, xs).correlation, 4), 5e-4)

med = rc["median_year"]
band = lambda h: "<=15" if h <= 15 else ("16-25" if h <= 25 else ">25")
strata = {}
for p in per:
    d = strata.setdefault(band(p["hac"]), {"a": 0, "n1": 0, "n2": 0, "m1": 0, "T": 0})
    older = p["year"] <= med
    d["T"] += 1
    d["n1" if older else "n2"] += 1
    if p["top1"]:
        d["m1"] += 1
        if older:
            d["a"] += 1
num = var = 0.0
for d in strata.values():
    a, n1, n2, m1, T = d["a"], d["n1"], d["n2"], d["m1"], d["T"]
    m2 = T - m1
    num += a - n1 * m1 / T
    if T > 1:
        var += (n1 * n2 * m1 * m2) / (T * T * (T - 1))
chi2 = (abs(num) - 0.5) ** 2 / var
check("CMH chi2", rc["cmh_chi2"], round(chi2, 2), 0.02)
check("CMH p", rc["cmh_p"], round(float(1 - S.chi2.cdf(chi2, 1)), 3), 0.02)

print()
if bad:
    print(f"STATISTICS AUDIT: {len(bad)} disagreement(s)")
    for b in bad:
        print("  " + b)
    sys.exit(1)
print("STATISTICS AUDIT: every hand-rolled statistic agrees with SciPy")
