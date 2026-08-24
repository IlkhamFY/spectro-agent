#!/usr/bin/env python3
"""Score the cross-model comparison on the fixed 24-compound subset and
regenerate Fig 5. Models: Claude Opus / Sonnet / Haiku / Fable 5 (all via the
Agent tool under one subscription; no API). InChIKey-connectivity scoring,
identical blind protocol per model."""
import json, glob, sys, math, random
from itertools import combinations
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SUBSET = ['R01','R02','R04','R05','R06','R07','R08','R09','R10','R11','R12','R13',
          'R15','R16','R17','R18','R19','R20','R21','R22','R23','R24','R25','R26']

SRC = {                                   # model -> glob of raw {M-qid:[smiles]}
    "Opus":   "data/benchmark_main/raw/*.json",
    "Sonnet": "data/benchmark_main/sonnet/*.json",
    "Haiku":  "data/benchmark_main/haiku/*.json",
    "Fable":  "data/benchmark_main/fable/*.json",
}

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def load(glb):
    d = {}
    for f in glob.glob(glb):
        try:
            for k, v in json.load(open(f)).items():
                d.setdefault(k.replace("M-", ""), v)
        except Exception:
            pass
    return d

def _mcnemar(b, c):
    """exact two-sided McNemar p on discordant counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))

def stats(vec, B=10000, seed=0):
    """Reproduce the §4.4 bootstrap 95% CIs and pairwise McNemar/Holm p-values."""
    rng = random.Random(seed)
    n = len(next(iter(vec.values())))
    order = [m for m in ["Fable", "Opus", "Sonnet", "Haiku"] if m in vec]
    print(f"\nBootstrap 95% CI (top-1, {B} resamples of {n} compounds):")
    for m in order:
        v = vec[m]
        boots = sorted(sum(v[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
        lo, hi = boots[int(.025 * B)], boots[int(.975 * B)]
        print(f"  {m:7} {100*sum(v)/n:5.1f}%  [{100*lo:.0f}, {100*hi:.0f}]")
    print("Pairwise McNemar (exact two-sided) + Holm:")
    pairs = []
    for a, b in combinations(order, 2):
        va, vb = vec[a], vec[b]
        bcell = sum(x and not y for x, y in zip(va, vb))   # a right, b wrong
        ccell = sum(y and not x for x, y in zip(va, vb))   # a wrong, b right
        pairs.append((a, b, bcell, ccell, _mcnemar(bcell, ccell)))
    # Holm-Bonferroni
    pairs.sort(key=lambda r: r[4])
    M = len(pairs)
    for i, (a, b, bc, cc, p) in enumerate(pairs):
        holm = min(1.0, p * (M - i))
        print(f"  {a:6} vs {b:6}  b={bc} c={cc}  p={p:.4f}  Holm={holm:.4f}")

def main():
    ans = {json.loads(l)["qid"]: json.loads(l)
           for l in open("data/benchmark_main/answers2.jsonl")}
    gold = {q: ans[q]["inchikey"][:14] for q in SUBSET if q in ans}
    res = {}
    vec = {}                                # model -> per-compound top-1 bool vector
    for model, glb in SRC.items():
        pred = load(glb)
        if not any(q in pred for q in SUBSET):
            continue                       # model not yet collected
        v = []
        rec = 0
        for q in SUBSET:
            cs = (pred.get(q) or [])[:3]
            v.append(bool(cs) and ik(cs[0]) == gold[q])
            rec += any(ik(s) == gold[q] for s in cs)
        vec[model] = v
        res[model] = [sum(v), rec]
        n = len(SUBSET)
        # Round, do not floor. // truncates, so 11/24 = 45.8% printed as "45%" while
        # the figure below annotates the same fraction as 46 -- the caption and the plot
        # of one figure disagreed, and Table 3 understated two of the four models.
        pct = lambda k: round(100 * k / n)
        print(f"{model:7} n={n}  top-1 {sum(v)}/{n} ({pct(sum(v))}%)  recovered {rec}/{n} ({pct(rec)}%)")
    json.dump({"n": len(SUBSET), "results": res},
              open("data/benchmark_main/model_comparison.json", "w"))

    if "--stats" in sys.argv and vec:
        stats(vec)

    if "--fig" in sys.argv and vec:
        # Dot + bootstrap-95%-CI forest (NOT bars): at n=24 the CIs overlap heavily, so
        # the plot must show that adjacent models are not separable, not imply a ranking.
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import figstyle as fs
        fs.apply()
        order = [m for m in ["Fable", "Opus", "Sonnet", "Haiku"] if m in vec]
        n = len(SUBSET); rng = random.Random(0); B = 10000
        def _ci(v):
            """Bootstrap, with an exact fallback at the boundary.

            A model that scores 0/24 (or 24/24) has an identical value in every resample,
            so the bootstrap interval collapses to a point and the weakest model in the
            figure is drawn as the most certain one. That is backwards. At the boundary
            the bootstrap has no information and Clopper-Pearson does: 0/24 is [0, 14.2%],
            which is the honest statement -- not measurably above zero, and not pinned to
            it either."""
            k = sum(v)
            p = 100 * k / n
            if k in (0, n):
                from scipy.stats import beta
                lo = 0.0 if k == 0 else 100 * beta.ppf(.025, k, n - k + 1)
                hi = 100.0 if k == n else 100 * beta.ppf(.975, k + 1, n - k)
                return p, lo, hi
            bs = sorted(100 * sum(v[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
            return p, bs[int(.025 * B)], bs[int(.975 * B)]
        t1 = {m: _ci(vec[m]) for m in order}
        rc = {m: 100 * res[m][1] / n for m in order}
        ys = list(range(len(order) - 1, -1, -1))          # Fable at top
        fig, ax = plt.subplots(figsize=(fs.COL1, fs.H1)); fs.xgrid(ax)
        for y, m in zip(ys, order):
            p, lo, hi = t1[m]
            col = fs.ORANGE if m == "Fable" else fs.BLUE
            ax.errorbar(p, y, xerr=[[p - lo], [hi - p]], fmt="o", ms=fs.MARKER,
                        color=col, ecolor=col, elinewidth=fs.ERR["lw"],
                        capsize=fs.ERR["capsize"], capthick=fs.ERR["capthick"], zorder=3)
            ax.plot(rc[m], y, "o", ms=fs.MARKER, mfc="white", mec=fs.SKY, mew=1.1, zorder=2)
            ax.text(p, y + 0.26, f"{p:.0f}", ha="center", va="bottom",
                    fontsize=fs.FS_SMALL, color=fs.INK)
        ax.set_yticks(ys); ax.set_yticklabels(order)
        ax.set_xlabel("accuracy (%)"); ax.set_xlim(-4, 72); ax.set_ylim(-0.6, len(order) - 0.4)
        ax.plot([], [], "o", ms=fs.MARKER, color=fs.BLUE, label="exact top-1 (95% CI)")
        ax.plot([], [], "o", ms=fs.MARKER, mfc="white", mec=fs.SKY, mew=1.1,
                label="recovered (top-3)")
        fs.legend(ax, loc="lower right")
        fs.finish(); fs.save("docs/figures/fig5_models.png")
        print("wrote docs/figures/fig5_models.png")
if __name__ == "__main__":
    main()
