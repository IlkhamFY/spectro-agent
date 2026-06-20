#!/usr/bin/env python3
"""Recall-headroom analysis for the 'enumerate + verify' fix.

The paper's bottleneck is candidate RECALL (true structure never proposed). The model
is, however, scaffold-accurate (56% Tanimoto>=0.45). So the question is: of the
compounds we currently MISS, how many have a true structure that is merely a
constitutional/regio-isomer of something the model DID propose? Those are recoverable
by enumerating isomers around the model's candidates and re-ranking by forward
verification -- no new generation skill required.

Pure offline analysis over the frozen benchmark predictions (no LLM calls)."""
import importlib.util
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

sm = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("sm", "scripts/score_main.py"))
importlib.util.spec_from_file_location("sm", "scripts/score_main.py").loader.exec_module(sm)

def mol(s): return Chem.MolFromSmiles(s) if s else None
def ik(s):
    m = mol(s); return Chem.MolToInchiKey(m)[:14] if m else None
def formula(s):
    m = mol(s); return rdMolDescriptors.CalcMolFormula(m) if m else None
def scaffold(s, generic=False):
    m = mol(s)
    if not m: return None
    sc = MurckoScaffold.GetScaffoldForMol(m)
    if generic: sc = MurckoScaffold.MakeScaffoldGeneric(sc)
    return Chem.MolToSmiles(sc) if sc and sc.GetNumAtoms() else None
def tani(a, b):
    ma, mb = mol(a), mol(b)
    if not ma or not mb: return 0.0
    fa = AllChem.GetMorganFingerprintAsBitVect(ma, 2, 2048)
    fb = AllChem.GetMorganFingerprintAsBitVect(mb, 2, 2048)
    return DataStructs.TanimotoSimilarity(fa, fb)

rows = sm.load()
misses = []          # recall-negative compounds
recalled = 0
for ans, cands in rows:
    cs = cands[:3]
    t = ik(ans["smiles"])
    if any(ik(c) == t for c in cs):
        recalled += 1; continue
    true = ans["smiles"]
    tf, tsc, tscg = formula(true), scaffold(true), scaffold(true, True)
    same_formula = any(formula(c) == tf for c in cs if c)
    same_scaff   = tsc is not None and any(scaffold(c) == tsc for c in cs if c)
    same_scaff_g = tscg is not None and any(scaffold(c, True) == tscg for c in cs if c)
    # ENUMERABLE proxy: same formula AND same (non-None) generic scaffold. NOTE this is
    # an UPPER BOUND — generic-scaffold equality is looser than what the ring-pendant /
    # heteroatom-walk enumerator can actually reach (e.g. it cannot break an ethyl into
    # two methyls). The realised reach is measured directly by closing_the_gap.py
    # (recall 33.5% -> 41.8%); treat the ceiling below as optimistic, not achieved.
    iso_of_cand  = tscg is not None and any(
        formula(c) == tf and scaffold(c, True) == tscg for c in cs if c)
    best_t = max([tani(true, c) for c in cs if c] or [0.0])
    misses.append(dict(diff=ans["difficulty"], same_formula=same_formula,
                       same_scaff=same_scaff, same_scaff_g=same_scaff_g,
                       iso_of_cand=iso_of_cand, best_t=best_t))

N = len(rows); M = len(misses)
def pct(n, d): return f"{100*n/d:4.1f}%" if d else "  n/a"
print(f"N={N} compounds   currently recalled (top-3): {recalled} ({pct(recalled,N)})   "
      f"misses: {M}\n")
print("Of the current recall-MISSES, the true structure shares with a model candidate:")
print(f"  same molecular formula              : {sum(m['same_formula'] for m in misses)}/{M}  ({pct(sum(m['same_formula'] for m in misses),M)})")
print(f"  same Bemis-Murcko scaffold          : {sum(m['same_scaff'] for m in misses)}/{M}  ({pct(sum(m['same_scaff'] for m in misses),M)})")
print(f"  same GENERIC scaffold               : {sum(m['same_scaff_g'] for m in misses)}/{M}  ({pct(sum(m['same_scaff_g'] for m in misses),M)})")
print(f"  isomer of a candidate (formula+gen scaffold) -> ENUMERABLE : "
      f"{sum(m['iso_of_cand'] for m in misses)}/{M}  ({pct(sum(m['iso_of_cand'] for m in misses),M)})")
for thr in (0.6, 0.7, 0.8):
    print(f"  best Tanimoto to a candidate >= {thr}    : "
          f"{sum(m['best_t']>=thr for m in misses)}/{M}  ({pct(sum(m['best_t']>=thr for m in misses),M)})")

enum = sum(m['iso_of_cand'] for m in misses)
ceil = recalled + enum
print(f"\nOPTIMISTIC recall upper bound of 'enumerate isomers around candidates + verify':")
print(f"  {recalled} (current) + {enum} (formula+scaffold-matched misses) = {ceil}/{N}  ({pct(ceil,N)})")
print("  WARNING: this is a LOOSE upper bound — generic-scaffold equality overcounts what the")
print("  enumerator can actually build. The REALISED reach is measured by closing_the_gap.py")
print("  (recall 33.5% -> 41.8%); use that, not this ceiling, as the achievable figure.")
