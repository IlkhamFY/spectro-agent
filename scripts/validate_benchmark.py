#!/usr/bin/env python3
"""Limitation fixes (extraction noise + ground-truth integrity): for every
benchmark compound check that the resolved ground-truth structure is
self-consistent with its reported spectrum, and recompute metrics on the
spectrally-clean subset. Pure RDKit, no LLM."""
import json, glob, re
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import rdMolDescriptors

def obs_c13(s): return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', s or "")]
def n_sym_carbons(m):                      # symmetry-unique carbons
    ranks = list(Chem.CanonicalRankAtoms(m, breakTies=False))
    cs = {ranks[a.GetIdx()] for a in m.GetAtoms() if a.GetSymbol()=="C"}
    return len(cs)

for d in ["data/benchmark_v3","data/benchmark_v2_ctrl"]:
    q={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/questions2.jsonl")}
    a={json.loads(l)["qid"]:json.loads(l) for l in open(f"{d}/answers2.jsonl")}
    clean=set(); flags={}
    for qid,ans in a.items():
        m=Chem.MolFromSmiles(ans["smiles"])
        nobs=len(obs_c13(q[qid]["c_nmr"])); nC=sum(1 for at in m.GetAtoms() if at.GetSymbol()=="C")
        nsym=n_sym_carbons(m)
        # formula + SELFIES sanity
        fmla_ok = rdMolDescriptors.CalcMolFormula(m)==q[qid]["formula"]
        rt_ok=True
        try:
            import selfies as sf; rt_ok = Chem.MolToSmiles(Chem.MolFromSmiles(sf.decoder(sf.encoder(ans["smiles"]))))==Chem.MolToSmiles(m)
        except Exception: rt_ok=False
        reason=[]
        if nobs>nC: reason.append(f"13C-overread({nobs}>{nC})")     # contamination / merged
        if nobs < max(2,nsym//2): reason.append(f"13C-sparse({nobs}<{nsym})")
        if not fmla_ok: reason.append("formula-mismatch")
        if not rt_ok: reason.append("selfies-rt-fail")
        if reason: flags[qid]=reason
        else: clean.add(qid)
    json.dump(sorted(clean), open(f"{d}/clean_qids.json","w"))
    print(f"{d}: {len(clean)}/{len(a)} spectrally-clean ground truths; {len(flags)} flagged")
    for qid,r in list(flags.items())[:6]: print(f"    {qid}: {r}")
