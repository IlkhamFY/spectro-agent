#!/usr/bin/env python3
"""
Generator-verifier elucidation: re-rank the solver agents' candidate structures
by how well each candidate's FORWARD-predicted 13C spectrum matches the OBSERVED
13C spectrum. Forward prediction is the model's easy direction (Anthropic: ~1.4
ppm 13C); regioisomers differ in predicted shifts, so forward verification can
break the regiochemistry ties that defeat single-pass inverse elucidation.

  prep : build data/fverify/candidates.jsonl (cid, qid, smiles, is_true, obs_c13)
         + shuffled, anonymized SMILES batches for blind forward-prediction agents
  score: load predicted 13C per SMILES -> chamfer distance to observed ->
         re-rank candidates -> compare self-rank top-1 vs verified top-1 vs ceiling
"""
import json, glob, re, random, sys
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

DIRS = ["data/benchmark_v3", "data/benchmark_v2_ctrl"]
CAND = "data/fverify/candidates.jsonl"

def obs_c13(c_nmr):                      # shifts are the number before each "("
    return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', c_nmr or "")]

def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None

def prep():
    rows = []
    for d in DIRS:
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        p = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/predictions2.jsonl")}
        for qid, ans in a.items():
            tik = ans["inchikey"][:14]; obs = obs_c13(q[qid]["c_nmr"])
            seen = set()
            for rank, smi in enumerate(p.get(qid, {}).get("candidates", [])[:3]):
                cs = canon(smi)
                if not cs or cs in seen:  # skip invalid / duplicate candidates
                    continue
                seen.add(cs)
                rows.append({"cid": f"{d.split('_')[-1]}:{qid}:{rank}", "dir": d,
                             "qid": qid, "smiles": cs, "self_rank": rank,
                             "is_true": ik14(cs) == tik, "obs_c13": obs,
                             "difficulty": ans["difficulty"]})
    open(CAND, "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
    # unique SMILES -> anon ids, shuffled
    uniq = sorted({r["smiles"] for r in rows})
    random.seed(5); random.shuffle(uniq)
    amap = {s: f"P{i:03d}" for i, s in enumerate(uniq)}
    json.dump(amap, open("data/fverify/anon_map.json", "w"))
    print(f"{len(rows)} candidates over {len({r['qid'] for r in rows})} compounds; "
          f"{len(uniq)} unique SMILES to forward-predict")
    B = 17
    for bi in range((len(uniq)+B-1)//B):
        print(f"\n##### FWD BATCH {bi+1} #####")
        for s in uniq[bi*B:(bi+1)*B]:
            print(f"{amap[s]}  {s}")

def chamfer(pred, obs):
    if not pred or not obs: return 999.0
    a = sum(min(abs(p-o) for o in obs) for p in pred)/len(pred)
    b = sum(min(abs(o-p) for p in pred) for o in obs)/len(obs)
    return (a+b)/2

def score():
    rows = [json.loads(l) for l in open(CAND)]
    amap = json.load(open("data/fverify/anon_map.json"))
    pred = {}
    for f in glob.glob("data/fverify/raw/*.json"):
        pred.update(json.load(open(f)))               # {anon_id: [shifts]}
    # group candidates by compound
    comps = {}
    for r in rows: comps.setdefault(r["qid"]+r["dir"], []).append(r)
    self1=ver1=ceil=n=0; cal=[]; cond_self=cond_ver=cond_n=0
    for key, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            pid = amap.get(c["smiles"]); c["pred"] = pred.get(pid)
            c["dist"] = chamfer(c["pred"], obs) if c["pred"] else 999.0
        n += 1
        has = any(c["is_true"] for c in cands); ceil += has
        s = sorted(cands, key=lambda c:c["self_rank"])[0]["is_true"]; self1 += s
        best = min(cands, key=lambda c:c["dist"]); ver1 += best["is_true"]
        if has:                                    # recall-conditional accuracy
            cond_n += 1; cond_self += s; cond_ver += best["is_true"]
        if any(c["pred"] for c in cands):
            cal.append((best["dist"], best["is_true"]))
    print(f"compounds: {n}")
    print(f"  ceiling (true in candidate set): {ceil}/{n} ({round(100*ceil/n)}%)  <- generation recall")
    print(f"  top-1, solver self-rank:         {self1}/{n} ({round(100*self1/n)}%)")
    print(f"  top-1, FORWARD-VERIFIED rerank:  {ver1}/{n} ({round(100*ver1/n)}%)")
    print(f"\n  CONDITIONAL on true-in-set (the verifier's actual job, n={cond_n}):")
    print(f"    solver self-rank picks it: {cond_self}/{cond_n} ({round(100*cond_self/cond_n)}%)")
    print(f"    forward-verify picks it:   {cond_ver}/{cond_n} ({round(100*cond_ver/cond_n)}%)  <- the generator-verifier gap")
    # calibration: accuracy of the verified pick by match-distance bin
    cal.sort()
    print("\ncalibration (verified pick correctness vs forward-match distance):")
    for lo,hi in [(0,2),(2,4),(4,8),(8,999)]:
        b=[t for d,t in cal if lo<=d<hi]
        if b: print(f"  match dist {lo}-{hi} ppm: {sum(b)}/{len(b)} correct ({round(100*sum(b)/len(b))}%)")

if __name__ == "__main__":
    prep() if sys.argv[1]=="prep" else score()
