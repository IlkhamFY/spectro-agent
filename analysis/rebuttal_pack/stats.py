"""Wilson intervals, paired bootstrap, exact McNemar, Holm."""
from __future__ import annotations

import math
from math import exp, lgamma, log

import numpy as np

from paperstyle import wilson_ci


def wilson(k, n):
    """Return (p, lo, hi) on the probability scale. p is k/n, not the Wilson centre."""
    k = int(k)
    n = int(n)
    if n <= 0:
        return (float("nan"), float("nan"), float("nan"))
    lo, hi = wilson_ci(k, n)
    lo = float(np.asarray(lo).reshape(-1)[0])
    hi = float(np.asarray(hi).reshape(-1)[0])
    return (k / n, max(0.0, lo), min(1.0, hi))


def pct(k, n, digits=1):
    p, lo, hi = wilson(k, n)
    return f"{100 * p:.{digits}f}% ({k}/{n}), 95% CI {100 * lo:.{digits}f} to {100 * hi:.{digits}f}"


def mcnemar_p(b, c):
    """Two-sided exact McNemar p. b and c are the discordant counts."""
    b, c = int(b), int(c)
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    logs = []
    for i in range(k + 1):
        logs.append(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) - n * log(2))
    m = max(logs)
    cdf = exp(m) * sum(exp(v - m) for v in logs)
    return float(min(1.0, 2.0 * cdf))


def paired_diff(a, b, B=10000, seed=0):
    """Paired bootstrap of mean(a) - mean(b). a, b are 0/1 arrays aligned on items."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) != len(b) or len(a) == 0:
        raise ValueError("paired_diff needs two equal non-empty vectors")
    rng = np.random.default_rng(seed)
    point = float(a.mean() - b.mean())
    idx = rng.integers(0, len(a), size=(B, len(a)))
    diffs = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    lo, hi = np.quantile(diffs, [0.025, 0.975])
    return point, float(lo), float(hi)


def holm(rows):
    """rows: list of dicts with key 'p'. Adds 'holm'. Monotone from the smallest p."""
    order = sorted(range(len(rows)), key=lambda i: rows[i]["p"])
    m = len(rows)
    running = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, rows[i]["p"] * (m - rank))
        running = max(running, adj)
        rows[i]["holm"] = running
    return rows


def discordance(a, b):
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    b_only_a = int(np.sum(a & ~b))
    c_only_b = int(np.sum(~a & b))
    return b_only_a, c_only_b
