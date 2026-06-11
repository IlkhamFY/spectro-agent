#!/usr/bin/env python3
"""Score the electrolyte subset overall and by electrolyte chemical class."""
import json, glob
from collections import defaultdict
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
def ik(s):
    m=Chem.MolFromSmiles(s) if s else None; return Chem.MolToInchiKey(m)[:14] if m else None
a={json.loads(l)["qid"]:json.loads(l) for l in open("data/benchmark_electrolyte/answers2.jsonl")}
pred={}
for f in glob.glob("data/benchmark_electrolyte/raw/*.json"):
    try:
        for k,v in json.load(open(f)).items(): pred[k.replace("E-","")]=v
    except Exception: pass
by=defaultdict(lambda:[0,0,0])   # class -> [n, top1, recovered]
N=t1=rec=0
for qid,ans in a.items():
    cands=pred.get(qid)
    if cands is None: continue
    t=ans["inchikey"][:14]; cs=cands[:3]; cl=ans["eclass"]
    a1=bool(cs) and ik(cs[0])==t; ar=any(ik(s)==t for s in cs)
    N+=1; t1+=a1; rec+=ar
    by[cl][0]+=1; by[cl][1]+=a1; by[cl][2]+=ar
print(f"IRSpectra-Bench-Electrolyte: n={N} scored")
print(f"  overall: top-1 {t1}/{N} ({100*t1//max(N,1)}%)  recovered {rec}/{N} ({100*rec//max(N,1)}%)")
print("  by electrolyte class:")
for cl,(n,a1,ar) in sorted(by.items()):
    print(f"    {cl:12} n={n}  top-1 {a1}/{n} ({100*a1//n if n else 0}%)  recovered {ar}/{n}")
