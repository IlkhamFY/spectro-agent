#!/usr/bin/env python3
"""Diagnose which enumerable recall-misses the enumerator fails to recover, and why,
so we can target new transforms. Prints (best matching candidate, true) for misses
where true shares formula+generic-scaffold with a candidate but enumeration misses it."""
import importlib.util
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def _imp(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
cg = _imp("cg", "scripts/closing_the_gap.py")
en = _imp("en", "scripts/enumerate_isomers.py")

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None
def formula(s):
    m = Chem.MolFromSmiles(s) if s else None
    return rdMolDescriptors.CalcMolFormula(m) if m else None
def gscaf(s):
    m = Chem.MolFromSmiles(s) if s else None
    if not m: return None
    sc = MurckoScaffold.GetScaffoldForMol(m)
    try: sc = MurckoScaffold.MakeScaffoldGeneric(sc)
    except Exception: return None
    return Chem.MolToSmiles(sc) if sc and sc.GetNumAtoms() else None

rows = cg.load()
miss_enumerable = recovered = missed = 0
shown = 0
for qid, true, cands, obs in rows:
    t = ik(true); cands = [c for c in cands if c]
    if any(ik(c) == t for c in cands):
        continue                                  # already recalled
    tf, tg = formula(true), gscaf(true)
    match = [c for c in cands if formula(c) == tf and gscaf(c) == tg]
    if not match:
        continue                                  # not in the enumerable headroom
    miss_enumerable += 1
    pool = set()
    for c in cands:
        pool |= en.enumerate_regioisomers(c, cap=400)
    if t in {ik(p) for p in pool}:
        recovered += 1
    else:
        missed += 1
        if shown < 18:
            shown += 1
            print(f"[{qid}]  cand: {match[0]}")
            print(f"        true: {true}")
print(f"\nenumerable misses: {miss_enumerable}   recovered by enumerator: {recovered}   "
      f"still missed: {missed}")
