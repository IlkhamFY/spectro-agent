#!/usr/bin/env python3
"""Is verification actually better than generation, per vendor? Test it, don't eyeball it.

The cross-vendor table reports generation recall and verification precision with a
confidence interval on each, and the manuscript originally read the two intervals against
one another: only Claude's were disjoint, so only Claude's gap was called resolved.

Overlapping marginal intervals do not mean a difference is unresolved. Recall and
precision here are measured on the *same compounds*, so the quantity with a claim attached
is the paired difference, and it has a much tighter interval than either margin implies.
Bootstrapping compounds (not the two statistics independently) gives it:

    resample 60 compounds with replacement
    -> recall on the resample, precision-conditional-on-recall on the resample
    -> their difference

Grok stays unresolved on this test. Gemini and GPT-5.6 Sol do not: both intervals exclude
zero, so the inequality the paper claims is separated for them and directional only for
Grok -- the opposite of what reading the marginal intervals suggested.

  python scripts/cross_vendor_gap.py
"""
import json
import random
import sys

sys.path.insert(0, "scripts")
from cross_vendor_sweep import _canon, chamfer, ik14        # noqa: E402

OUT = "data/cross_vendor"
B = 10000


def rows_for(vendor, key, k):
    """per compound: (true structure present?, did the verifier pick it?)"""
    solve = json.load(open(f"{OUT}/solve_{vendor}.json"))
    pred = json.load(open(f"{OUT}/verify_{vendor}.json"))
    amap = json.load(open(f"{OUT}/anon_{vendor}.json"))
    out = []
    for mid, info in key.items():
        cands = [c for c in (_canon(s) for s in (solve.get(mid) or [])[:k]) if c]
        iks = [ik14(c) for c in cands]
        picked = None
        if cands:
            dist = [chamfer(pred.get(amap.get(c)), info["obs_c13"]) for c in cands]
            picked = int(iks[min(range(len(cands)), key=lambda i: dist[i])] == info["true_ik"])
        out.append((int(info["true_ik"] in iks), picked))
    return out


def gap(sample):
    recall = sum(a for a, _ in sample) / len(sample)
    hits = [p for a, p in sample if a and p is not None]
    return (sum(hits) / len(hits) - recall) if hits else None


def main():
    meta = json.load(open(f"{OUT}/key.json"))
    key, k = meta["key"], meta["k"]
    rng = random.Random(0)
    print(f"{'vendor':<18}{'recall':>8}{'prec|rec':>10}{'gap':>8}"
          f"   95% CI of the paired difference")
    for v in ("grok-4.6", "gemini-3.7-flash", "gpt-5.6-sol"):
        rows = rows_for(v, key, k)
        n = len(rows)
        point = gap(rows)
        bs = sorted(g for g in (gap([rows[rng.randrange(n)] for _ in range(n)])
                                for _ in range(B)) if g is not None)
        lo, hi = bs[int(.025 * len(bs))], bs[int(.975 * len(bs))]
        recall = sum(a for a, _ in rows) / n
        hits = [p for a, p in rows if a and p is not None]
        print(f"{v:<18}{100 * recall:7.1f}%{100 * sum(hits) / len(hits):9.1f}%"
              f"{100 * point:+7.1f}   [{100 * lo:+.1f}, {100 * hi:+.1f}]  "
              f"{'resolved' if lo > 0 else 'directional'}")


if __name__ == "__main__":
    main()
