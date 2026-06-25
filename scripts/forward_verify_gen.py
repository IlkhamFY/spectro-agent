#!/usr/bin/env python3
"""
Phase-2: forward-verify the NEURAL-GENERATOR pool with the SAME blind LLM forward
predictor as forward_verify.py (the paper's 84%/30% method) — the strong selector,
vs the weak HOSE one. Pools Claude candidates + our formula-filtered generator
candidates over the 60 controlled compounds (v3+v2_ctrl), reuses existing fverify
13C predictions, and emits only the NEW candidate SMILES that need forward-prediction.

  prep  : build data/fverify_gen/candidates.jsonl + anon_map.json; print FWD BATCHes
          of NEW (anon_id, SMILES) for the out-of-band Claude forward-predictor.
  score : load data/fverify/raw/*.json (existing) + data/fverify_gen/raw/*.json (new)
          -> chamfer rerank -> top-1, recall, conditional precision. vs paper 30%.
"""
import json, glob, os, re, random, sys
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
import importlib.util
_s = importlib.util.spec_from_file_location("fv", "scripts/forward_verify.py")
fv = importlib.util.module_from_spec(_s); _s.loader.exec_module(fv)   # reuse obs_c13/ik14/canon/chamfer

DIRS = ["data/benchmark_v3", "data/benchmark_v2_ctrl"]
GEN  = json.load(open("contrib/generator_probe/artifacts/gen_candidates.jsonl"))
OUT  = "data/fverify_gen"; os.makedirs(f"{OUT}/raw", exist_ok=True)

def formula(s):
    m = Chem.MolFromSmiles(s) if s else None
    return rdMolDescriptors.CalcMolFormula(m) if m else None

def prep():
    rows = []
    for d in DIRS:
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        p = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/predictions2.jsonl")}
        for qid, ans in a.items():
            tik = ans["inchikey"][:14]; obs = fv.obs_c13(q[qid]["c_nmr"]); tf = formula(ans["smiles"])
            seen = set()
            def add(smi, src):
                cs = fv.canon(smi)
                if not cs or cs in seen: return
                seen.add(cs)
                rows.append({"cid": f"{d.split('_')[-1]}:{qid}:{src}", "dir": d, "qid": qid,
                             "smiles": cs, "src": src, "is_true": fv.ik14(cs) == tik,
                             "obs_c13": obs, "difficulty": ans["difficulty"]})
            for smi in p.get(qid, {}).get("candidates", [])[:3]:        # Claude candidates
                add(smi, "claude")
            for smi in GEN.get(f"{d}:{qid}", []):                       # our generator, formula-filtered
                if formula(smi) == tf: add(smi, "gen")
    open(f"{OUT}/candidates.jsonl", "w").write("\n".join(json.dumps(r) for r in rows) + "\n")

    # reuse existing anon ids/predictions; only NEW smiles need forward-prediction
    old_map = json.load(open("data/fverify/anon_map.json")) if os.path.exists("data/fverify/anon_map.json") else {}
    have = set()
    for f in glob.glob("data/fverify/raw/*.json"): have |= set(json.load(open(f)))
    uniq = sorted({r["smiles"] for r in rows})
    amap = dict(old_map); nxt = max([int(v[1:]) for v in old_map.values()], default=-1) + 1
    new = []
    for s in uniq:
        if s not in amap:
            amap[s] = f"P{nxt:03d}"; nxt += 1
        if amap[s] not in have:
            new.append(s)
    json.dump(amap, open(f"{OUT}/anon_map.json", "w"))
    random.seed(5); random.shuffle(new)
    json.dump({amap[s]: s for s in new}, open(f"{OUT}/to_predict.json", "w"), indent=0)
    print(f"{len(rows)} candidates over {len({(r['qid'],r['dir']) for r in rows})} compounds; "
          f"{len(uniq)} unique SMILES, {len(new)} NEW to forward-predict "
          f"({len(uniq)-len(new)} reused).\n")
    B = 17
    for bi in range((len(new)+B-1)//B):
        print(f"##### FWD-GEN BATCH {bi+1} #####")
        for s in new[bi*B:(bi+1)*B]:
            print(f"{amap[s]}  {s}")

def score():
    rows = [json.loads(l) for l in open(f"{OUT}/candidates.jsonl")]
    amap = json.load(open(f"{OUT}/anon_map.json"))
    pred = {}
    for f in glob.glob("data/fverify/raw/*.json") + glob.glob(f"{OUT}/raw/*.json"):
        pred.update(json.load(open(f)))
    comps = {}
    for r in rows: comps.setdefault((r["qid"], r["dir"]), []).append(r)
    n=ceil=ver1=cond_n=cond_ver=0; missing=0
    for key, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            pid = amap.get(c["smiles"]); c["pred"] = pred.get(pid)
            if c["pred"] is None: missing += 1
            c["dist"] = fv.chamfer(c["pred"], obs) if c["pred"] else 999.0
        n += 1; has = any(c["is_true"] for c in cands); ceil += has
        best = min(cands, key=lambda c: c["dist"]); ver1 += best["is_true"]
        if has: cond_n += 1; cond_ver += best["is_true"]
    P = lambda x, d: f"{x}/{d} ({100*x//max(d,1)}%)"
    print(f"compounds: {n}   (missing predictions: {missing} candidates — run prep+forward-predict first)")
    print(f"  recall (true in pool)          : {P(ceil,n)}")
    print(f"  top-1, FORWARD-VERIFIED (gen)  : {P(ver1,n)}   <- vs paper generate-wide 30%")
    print(f"  CONDITIONAL on recall          : {P(cond_ver,cond_n)}")

if __name__ == "__main__":
    (prep if sys.argv[1] == "prep" else score)()
