#!/usr/bin/env python3
"""Build isomer-separated forward-prediction batches: no two candidates of the SAME
benchmark compound share a batch (paper's safeguard so the predictor commits to each
structure absolutely, not by comparing co-listed isomers). Output data/fverify_gen/batches.json."""
import json, math
cands = [json.loads(l) for l in open("data/fverify_gen/candidates.jsonl")]
topredict = json.load(open("data/fverify_gen/to_predict.json"))   # {anon_id: smiles} (the NEW ones)
amap = json.load(open("data/fverify_gen/anon_map.json"))
sm2id = {s: amap[s] for s in {r["smiles"] for r in cands}}

# map each NEW smiles -> its compound key (qid,dir); group
sm2comp = {}
for r in cands:
    sm2comp.setdefault(r["smiles"], (r["qid"], r["dir"]))
new = list(topredict.values())                     # the 75 new SMILES
groups = {}
for s in new:
    groups.setdefault(sm2comp.get(s, ("?", s)), []).append(s)
maxg = max(len(v) for v in groups.values())
nb = max(maxg, math.ceil(len(new)/15))             # >= max per-compound, ~15/batch
batches = [dict() for _ in range(nb)]

# greedy: compounds with most candidates first; each candidate -> least-loaded batch w/o a sibling
for comp, smis in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    used = set()
    for s in smis:
        cand_b = sorted(range(nb), key=lambda b: len(batches[b]))
        for b in cand_b:
            if b not in used:
                batches[b][sm2id[s]] = s; used.add(b); break
json.dump(batches, open("data/fverify_gen/batches.json", "w"))
print(f"{len(new)} new SMILES; max candidates/compound = {maxg}; {nb} batches; "
      f"sizes {[len(b) for b in batches]}")
# verify constraint
bad = 0
for b in batches:
    comps = [sm2comp.get(s) for s in b.values()]
    bad += len(comps) - len(set(comps))
print(f"same-compound collisions within a batch: {bad} (must be 0)")
