#!/usr/bin/env python3
"""IRSpectra-Bench-Electrolyte: filter IRexp for real experimental spectra of
organic chemical classes central to battery electrolytes and their decomposition
products, then build a blind elucidation subset (J-rich where recoverable)."""
import json, gzip, random, sys
from pathlib import Path
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import rdMolDescriptors
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.benchmark_v2 import difficulty, raw_1h_for  # noqa
import re

CLASSES = {
 "carbonate":   "[OX2][CX3](=[OX1])[OX2]",        # cyclic/linear carbonates (EC, DMC, VC, FEC, SEI alkyl carbonates)
 "sulfonyl":    "[SX4](=[OX1])(=[OX1])",           # sulfones / sulfonates / sultones / TFSI-FSI motifs
 "nitrile":     "[NX1]#[CX2]",                     # adiponitrile / succinonitrile additives
 "fluorinated": "[CX4][F]",                        # sp3 C-F: fluorinated solvents / additives (FEC, HFE)
 "phosphoryl":  "[PX4]=[OX1]",                     # phosphate / phosphonate flame-retardant additives, PF6 organics
 "glyme":       "[#6][OX2][CH2][CH2][OX2][#6]",    # glymes / polyethers (DME, diglyme, SEI oligomers)
}
PATS={k:Chem.MolFromSmarts(v) for k,v in CLASSES.items()}

def obs_c13(s): return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', s or "")]

def main(n_per_class=8, seed=202):
    random.seed(seed)
    seen=set()
    for af in Path(".").glob("data/benchmark*/answers*.jsonl"):
        for l in open(af): seen.add(json.loads(l)["inchikey"][:14])
    pools={k:[] for k in CLASSES}
    for l in gzip.open("data/irexp_resolved/irexp_resolved.jsonl.gz","rt"):
        r=json.loads(l); smi=r.get("smiles")
        if not (smi and r.get("h_nmr") and r.get("c_nmr") and r.get("ir_bands_cm-1")): continue
        m=Chem.MolFromSmiles(smi)
        if m is None or not (8<=m.GetNumHeavyAtoms()<=60): continue
        ik=(r.get("inchikey") or Chem.MolToInchiKey(m))[:14]
        if ik in seen: continue
        nobs=len(obs_c13(r["c_nmr"])); nC=sum(1 for a in m.GetAtoms() if a.GetSymbol()=="C")
        if nobs>nC or nobs<3: continue
        if rdMolDescriptors.CalcMolFormula(m)!=rdMolDescriptors.CalcMolFormula(m): continue
        for k,p in PATS.items():
            if m.HasSubstructMatch(p): pools[k].append((r,m,ik)); break
    for k in pools: random.shuffle(pools[k])
    print("electrolyte-class pool sizes:", {k:len(v) for k,v in pools.items()})
    out=Path("data/benchmark_electrolyte"); (out/"raw").mkdir(parents=True,exist_ok=True)
    chosen=[]; used=set()
    for k in CLASSES:
        got=0
        for r,m,ik in pools[k]:
            if got>=n_per_class: break
            if ik in used: continue
            raw=raw_1h_for(r)                          # J-rich if paper refetchable
            h = raw if (raw and "J" in raw) else r["h_nmr"]
            chosen.append((r,m,ik,h,k)); used.add(ik); got+=1
    random.shuffle(chosen)
    qf=open(out/"questions2.jsonl","w"); af=open(out/"answers2.jsonl","w"); clean=[]
    for i,(r,m,ik,h,k) in enumerate(chosen,1):
        qid=f"E{i:02d}"
        qf.write(json.dumps({"qid":qid,"difficulty":difficulty(m),"eclass":k,
            "formula":rdMolDescriptors.CalcMolFormula(m),"ir_bands_cm-1":r["ir_bands_cm-1"],
            "h_nmr":h,"c_nmr":r["c_nmr"]})+"\n")
        af.write(json.dumps({"qid":qid,"smiles":Chem.MolToSmiles(m),"inchikey":ik,
            "difficulty":difficulty(m),"eclass":k})+"\n")
        clean.append(qid)
    json.dump(clean,open(out/"clean_qids.json","w"))
    # batch files (6/agent)
    qs=[json.loads(l) for l in open(out/"questions2.jsonl")]
    B=6
    for bi in range((len(qs)+B-1)//B):
        with open(out/f"batch_{bi+1}.txt","w") as f:
            for q in qs[bi*B:(bi+1)*B]:
                f.write(f"E-{q['qid']} | formula {q['formula']}\n  IR cm-1: {q['ir_bands_cm-1']}\n  1H NMR: {q['h_nmr']}\n  13C NMR: {q['c_nmr']}\n\n")
    from collections import Counter
    print(f"built {len(chosen)} electrolyte-relevant compounds; classes:",
          dict(Counter(c[4] for c in chosen)), "; batches:", (len(qs)+B-1)//B)

if __name__=="__main__":
    main()
