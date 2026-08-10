#!/usr/bin/env python3
"""
Extend forward-verification (scripts/forward_verify.py, §5.2) from the 60-compound
v3+v2-control set to the 134 main-round compounds, so that the recall-conditional
claim rests on the whole n=194 benchmark rather than on n=19.

Protocol is deliberately IDENTICAL to the original arm: candidates are canonicalised
and de-duplicated per compound, the unique SMILES pool is shuffled and anonymised,
and blind agents predict 13C shift lists from the anonymous SMILES alone -- never
seeing the observed spectrum, the compound identity, or which candidates belong
together. Only the seed and the compound set differ.

  prep : build data/fverify_main/candidates.jsonl + anon_map.json + batch prompts
  score: this arm alone (the pooled n=194 number comes from forward_verify_all.py)
"""
import json, glob, re, random, sys, os
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

OUT   = "data/fverify_main"
SRC   = "data/benchmark_main"
CAND  = f"{OUT}/candidates.jsonl"
AMAP  = f"{OUT}/anon_map.json"
BATCH = 17          # same batch size as the original arm


def obs_c13(c_nmr):                      # shifts are the number before each "("
    return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', c_nmr or "")]


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def _predictions():
    """Main-round solver output: raw/*.json map 'M-<qid>' -> [smiles, ...]."""
    pred = {}
    for f in sorted(glob.glob(f"{SRC}/raw/*.json")):
        pred.update(json.load(open(f)))
    return pred


def prep():
    os.makedirs(f"{OUT}/raw", exist_ok=True)
    q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{SRC}/questions2.jsonl")}
    a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{SRC}/answers2.jsonl")}
    clean = json.load(open(f"{SRC}/clean_qids.json"))
    pred = _predictions()

    rows = []
    for qid in clean:
        ans = a[qid]
        tik = ans["inchikey"][:14]
        obs = obs_c13(q[qid].get("c_nmr"))
        seen = set()
        for rank, smi in enumerate(pred.get("M-" + qid, [])[:3]):
            cs = canon(smi)
            if not cs or cs in seen:      # skip invalid / duplicate candidates
                continue
            seen.add(cs)
            rows.append({"cid": f"main:{qid}:{rank}", "dir": SRC, "qid": qid,
                         "smiles": cs, "self_rank": rank,
                         "is_true": ik14(cs) == tik, "obs_c13": obs,
                         "difficulty": ans["difficulty"]})
    open(CAND, "w").write("\n".join(json.dumps(r) for r in rows) + "\n")

    uniq = sorted({r["smiles"] for r in rows})
    random.seed(11); random.shuffle(uniq)
    amap = {s: f"Q{i:03d}" for i, s in enumerate(uniq)}
    json.dump(amap, open(AMAP, "w"))
    print(f"{len(rows)} candidates over {len({r['qid'] for r in rows})} compounds; "
          f"{len(uniq)} unique SMILES to forward-predict")

    for bi in range((len(uniq) + BATCH - 1) // BATCH):
        chunk = uniq[bi * BATCH:(bi + 1) * BATCH]
        body = "\n".join(f"{amap[s]}  {s}" for s in chunk)
        open(f"{OUT}/fbatch_{bi+1}.txt", "w").write(body + "\n")
    print(f"wrote {bi+1} batch files to {OUT}/fbatch_*.txt")


def chamfer(pred, obs):
    if not pred or not obs: return 999.0
    a = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    b = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (a + b) / 2


def score():
    rows = [json.loads(l) for l in open(CAND)]
    amap = json.load(open(AMAP))
    pred = {}
    for f in sorted(glob.glob(f"{OUT}/raw/*.json")):
        pred.update(json.load(open(f)))
    print(f"forward predictions loaded: {len(pred)}/{len(amap)} unique SMILES")

    comps = {}
    for r in rows: comps.setdefault(r["qid"], []).append(r)
    self1 = ver1 = ceil = n = 0
    cond_self = cond_ver = cond_n = 0
    multi_self = multi_ver = multi_n = 0
    for qid, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            c["pred"] = pred.get(amap.get(c["smiles"]))
            c["dist"] = chamfer(c["pred"], obs) if c["pred"] else 999.0
        n += 1
        has = any(c["is_true"] for c in cands); ceil += has
        s = sorted(cands, key=lambda c: c["self_rank"])[0]["is_true"]; self1 += s
        v = min(cands, key=lambda c: c["dist"])["is_true"];            ver1 += v
        if has:
            cond_n += 1; cond_self += s; cond_ver += v
            if len(cands) > 1:
                multi_n += 1; multi_self += s; multi_ver += v
    print(f"compounds: {n}")
    print(f"  recall (true in candidate set): {ceil}/{n} ({100*ceil/n:.0f}%)")
    print(f"  top-1, solver self-rank:        {self1}/{n} ({100*self1/n:.0f}%)")
    print(f"  top-1, forward-verified rerank: {ver1}/{n} ({100*ver1/n:.0f}%)")
    print(f"  conditional on recall (n={cond_n}): self {cond_self}/{cond_n} "
          f"({100*cond_self/cond_n:.0f}%) | verify {cond_ver}/{cond_n} "
          f"({100*cond_ver/cond_n:.0f}%)")
    print(f"  multi-candidate only  (n={multi_n}): self {multi_self}/{multi_n} "
          f"| verify {multi_ver}/{multi_n}")


if __name__ == "__main__":
    prep() if sys.argv[1] == "prep" else score()
