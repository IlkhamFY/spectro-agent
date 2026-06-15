#!/usr/bin/env python3
"""Statistically-powered scoring across all benchmark rounds: top-1 / recall /
Tanimoto by difficulty and molecule size, with bootstrap 95% CIs. Unifies the
benchmark_main (134) + benchmark_v3 (40) + benchmark_v2_ctrl (20) rounds."""
import json, glob, random
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import AllChem, DataStructs

def ik(s):
    m=Chem.MolFromSmiles(s) if s else None; return Chem.MolToInchiKey(m)[:14] if m else None
def fp(s):
    m=Chem.MolFromSmiles(s) if s else None
    return AllChem.GetMorganFingerprintAsBitVect(m,2,2048) if m else None

def load():
    rows=[]
    # main round: answers + per-batch raw predictions (keyed "M-<qid>")
    a={json.loads(l)["qid"]:json.loads(l) for l in open("data/benchmark_main/answers2.jsonl")}
    clean=set(json.load(open("data/benchmark_main/clean_qids.json")))
    pred={}
    for f in glob.glob("data/benchmark_main/raw/*.json"):
        try:
            for k,v in json.load(open(f)).items(): pred[k]=v
        except Exception: pass
    for qid,ans in a.items():
        if qid not in clean: continue
        cands=pred.get(f"M-{qid}")
        if cands is None: continue            # not yet solved
        rows.append((ans,cands))
    # original rounds
    for d in ["data/benchmark_v3","data/benchmark_v2_ctrl"]:
        a={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        p={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/predictions2.jsonl")}
        for qid,ans in a.items():
            rows.append((ans,p[qid].get("candidates",[])))
    return rows

def hac_bucket(smi):
    m=Chem.MolFromSmiles(smi); h=m.GetNumHeavyAtoms() if m else 0
    return "<=15" if h<=15 else "16-25" if h<=25 else ">25"

def metrics(rows):
    res=[]
    for ans,cands in rows:
        t=ik(ans["smiles"]); cs=cands[:3]
        top1=bool(cs) and ik(cs[0])==t
        rec=any(ik(s)==t for s in cs)
        af=fp(ans["smiles"]); best=0.0
        for s in cs:
            pf=fp(s)
            if af and pf: best=max(best,DataStructs.TanimotoSimilarity(af,pf))
        res.append({"top1":top1,"rec":rec,"tani":best,"diff":ans["difficulty"],"hac":hac_bucket(ans["smiles"])})
    return res

def boot(vals, f, n=2000):
    if not vals: return (0,0,0)
    pt=f(vals); bs=[]
    for _ in range(n):
        s=[vals[random.randrange(len(vals))] for _ in vals]; bs.append(f(s))
    bs.sort(); return (pt, bs[int(0.025*n)], bs[int(0.975*n)])

if __name__=="__main__":
    random.seed(0)
    R=metrics(load())
    print(f"N = {len(R)} compounds (combined rounds)\n")
    def rate(rs,key): return 100*sum(r[key] for r in rs)/len(rs) if rs else 0
    for label,sub in [("ALL",R),("simple",[r for r in R if r['diff']=='simple']),
                      ("complex",[r for r in R if r['diff']=='complex'])]:
        p,lo,hi=boot(sub, lambda s: rate(s,'top1'))
        pr,rlo,rhi=boot(sub, lambda s: rate(s,'rec'))
        mt=sum(r['tani'] for r in sub)/len(sub) if sub else 0
        scaf=100*sum(r['tani']>=0.45 for r in sub)/len(sub) if sub else 0
        print(f"{label:8} n={len(sub):3}  top1 {p:4.1f}% [{lo:.0f}-{hi:.0f}]   recall {pr:4.1f}% [{rlo:.0f}-{rhi:.0f}]   scaffold(>=0.45) {scaf:4.0f}%   meanTani {mt:.2f}")
    print("\nby size:")
    for b in ["<=15","16-25",">25"]:
        sub=[r for r in R if r['hac']==b]
        if sub: print(f"  {b:6} n={len(sub):3}  top1 {rate(sub,'top1'):.1f}%  recall {rate(sub,'rec'):.1f}%")
