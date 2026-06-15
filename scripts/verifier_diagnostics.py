#!/usr/bin/env python3
"""Forward-verification diagnostics (deterministic, uses the stored LLM 13C predictions):

  A. Permutation negative-control (Y-randomization analog): shuffle which observed
     spectrum each compound's candidates are scored against; the verifier's
     conditional-on-recall precision should collapse to chance, proving it exploits
     real predicted-vs-observed agreement, not an artifact.

  B. Accuracy-at-coverage (applicability-domain -> selective-prediction analog): use
     the chamfer margin (2nd-best minus best) as a confidence score; report top-1
     accuracy when only the most-confident fraction of compounds is answered.
"""
import json, glob, random
from collections import defaultdict

def chamfer(p, o):
    if not p or not o: return 999.0
    a = sum(min(abs(x - y) for y in o) for x in p) / len(p)
    b = sum(min(abs(y - x) for x in p) for y in o) / len(o)
    return (a + b) / 2

cands = [json.loads(l) for l in open("data/fverify/candidates.jsonl")]
amap = json.load(open("data/fverify/anon_map.json"))
pred = {}
for f in glob.glob("data/fverify/raw/*.json"):
    pred.update(json.load(open(f)))

# group: compound -> [(smiles, is_true, pred13c)], plus its observed 13C
comp = defaultdict(list)
obs = {}
for c in cands:
    k = (c["dir"], c["qid"])
    comp[k].append((c["smiles"], c["is_true"], pred.get(amap.get(c["smiles"]))))
    obs[k] = c["obs_c13"]

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

# ---- A. permutation control ----
h, t = precision_given_obs(obs)
real = h / t
rng = random.Random(0)
N = 1000
perm_scores = []
vals = [obs[k] for k in keys]
for _ in range(N):
    shuf = vals[:]; rng.shuffle(shuf)
    pmap = {k: shuf[i] for i, k in enumerate(keys)}
    hh, tt = precision_given_obs(pmap)
    perm_scores.append(hh / tt if tt else 0)
perm_scores.sort()
mean_perm = sum(perm_scores) / N
ge = sum(s >= real for s in perm_scores)
pval = (ge + 1) / (N + 1)
print("A. PERMUTATION NEGATIVE-CONTROL (forward-verification)")
print(f"   real conditional-on-recall precision : {real:.3f}  ({h}/{t})")
print(f"   permuted (n={N})                      : {mean_perm:.3f}  "
      f"[{perm_scores[int(.025*N)]:.3f}-{perm_scores[int(.975*N)]:.3f}]")
print(f"   empirical p (perm >= real)            : {pval:.4f}")
print(f"   => verifier signal is real: {real:.0%} vs chance {mean_perm:.0%}\n")

# ---- B. accuracy-at-coverage ----
rows = []
for k in keys:
    scored = sorted([(chamfer(p, obs[k]), t) for _, t, p in comp[k] if p])
    if not scored:
        continue
    best_d, best_true = scored[0]
    margin = (scored[1][0] - scored[0][0]) if len(scored) > 1 else 999.0  # confident if alone
    rows.append((margin, best_true))
rows.sort(key=lambda r: -r[0])          # most confident (largest margin) first
n = len(rows)
print("B. ACCURACY-AT-COVERAGE (chamfer-margin confidence, all compounds, top-1)")
print(f"   {'coverage':>9} {'n':>4} {'top-1 acc':>10}")
for cov in (1.00, 0.75, 0.50, 0.25):
    m = max(1, int(round(cov * n)))
    acc = sum(t for _, t in rows[:m]) / m
    print(f"   {cov*100:7.0f}%  {m:4} {acc:9.1%}")
print(f"   (n={n} compounds with >=1 predicted candidate; full-coverage = standard top-1)")
