#!/usr/bin/env python3
"""Forward-verification diagnostics (deterministic, uses the stored LLM 13C predictions):

  A. Permutation negative-control (Y-randomization analog): re-pair, as a DERANGEMENT
     (no compound keeps its own spectrum), which observed spectrum each candidate set
     is scored against; the verifier's conditional-on-recall precision should collapse
     toward chance, proving it exploits real predicted-vs-observed agreement.

  B. Accuracy-at-coverage (applicability-domain -> selective-prediction analog): use
     the chamfer margin (2nd-best minus best) as a confidence score and answer only
     the most-confident fraction. Compounds with a single candidate have NO margin
     signal and are excluded (otherwise they spuriously dominate the confident end).

Default: the 60-compound §5.2 arm (data/fverify/), i.e. the numbers §5.5 reports.
`--all`: pools in the 134 main-round compounds (data/fverify_main/) for the n=194 set.
"""
import json, glob, random, sys
from collections import defaultdict
from specmetrics import chamfer

ARMS = ["data/fverify"]
if "--all" in sys.argv:
    ARMS.append("data/fverify_main")

# group: compound -> [(smiles, is_true, pred13c)], plus its observed 13C
comp = defaultdict(list)
obs = {}
for arm in ARMS:
    cands = [json.loads(l) for l in open(f"{arm}/candidates.jsonl")]
    amap = json.load(open(f"{arm}/anon_map.json"))
    pred = {}
    for f in glob.glob(f"{arm}/raw/*.json"):
        pred.update(json.load(open(f)))
    for c in cands:
        k = (arm, c["dir"], c["qid"])
        comp[k].append((c["smiles"], c["is_true"], pred.get(amap.get(c["smiles"]))))
        obs[k] = c["obs_c13"]
print(f"arms: {', '.join(ARMS)}  ({len(comp)} compounds with candidates)\n")

keys = sorted(comp)
recall_pos = [k for k in keys if any(t for _, t, _ in comp[k])]   # true is in candidate set

def precision_given_obs(obs_map):
    """fraction of recall-positive compounds whose min-chamfer candidate is the true one."""
    hit = tot = 0
    for k in recall_pos:
        scored = [(chamfer(p, obs_map[k]), t) for _, t, p in comp[k] if p]
        if not any(t for _, t in scored):   # true had no prediction -> not selectable
            continue
        tot += 1
        scored.sort(key=lambda x: x[0])
        hit += scored[0][1]
    return hit, tot

def deranged(idx, rng):
    """return a permutation of idx with no fixed point (rejection sampling)."""
    n = len(idx)
    while True:
        p = idx[:]; rng.shuffle(p)
        if all(p[i] != idx[i] for i in range(n)):
            return p

# ---- A. permutation control (derangement) ----
h, t = precision_given_obs(obs)
real = h / t
rng = random.Random(0)
N = 1000
perm_scores = []
order = list(range(len(keys)))
vals = [obs[k] for k in keys]
for _ in range(N):
    perm = deranged(order, rng)
    pmap = {keys[i]: vals[perm[i]] for i in order}    # each compound gets ANOTHER's spectrum
    hh, tt = precision_given_obs(pmap)
    perm_scores.append(hh / tt if tt else 0)
perm_scores.sort()
mean_perm = sum(perm_scores) / N
ge = sum(s >= real for s in perm_scores)
p_one = (ge + 1) / (N + 1)                              # one-sided: real beats chance
p_two = min(1.0, 2 * p_one)
print("A. PERMUTATION NEGATIVE-CONTROL (derangement, forward-verification)")
print(f"   real conditional-on-recall precision : {real:.3f}  ({h}/{t})")
print(f"   permuted (n={N})                      : {mean_perm:.3f}  "
      f"[{perm_scores[int(.025*N)]:.3f}-{perm_scores[int(.975*N)]:.3f}]")
print(f"   empirical p: one-sided {p_one:.4f}  two-sided {p_two:.4f}")
print(f"   => verifier signal is real: {real:.0%} vs chance {mean_perm:.0%}\n")

# ---- B. accuracy-at-coverage (margin defined only for >=2 candidates) ----
rows = []
single = 0
for k in keys:
    scored = sorted([(chamfer(p, obs[k]), t) for _, t, p in comp[k] if p])
    if len(scored) < 2:
        single += 1
        continue                                       # no margin signal -> excluded
    margin = scored[1][0] - scored[0][0]
    rows.append((margin, scored[0][1]))
rows.sort(key=lambda r: -r[0])                          # most confident (largest margin) first
n = len(rows)
print("B. ACCURACY-AT-COVERAGE (chamfer-margin confidence; >=2-candidate compounds)")
print(f"   {'coverage':>9} {'n':>4} {'top-1 acc':>10}")
for cov in (1.00, 0.75, 0.50, 0.25):
    m = max(1, int(round(cov * n)))
    acc = sum(t for _, t in rows[:m]) / m
    print(f"   {cov*100:7.0f}%  {m:4} {acc:9.1%}")
print(f"   (n={n} multi-candidate compounds; {single} single-candidate compounds excluded)")
