#!/usr/bin/env python3
"""
Extends closing_the_gap.py with a NEURAL-GENERATOR candidate source (training-free
verifier held fixed). For each benchmark compound, compare candidate pools:
  (a) Claude original         (b) +scaffold enumeration   (c) +neural generator
  (d) +generator+enumeration
reranked by the same deterministic HOSE 13C verifier. Generator candidates are
formula-filtered to the target formula (the formula is given in the blind question).
Reports recall (truth in pool) and HOSE top-1, plus projected top-1 @ a strong (0.84)
verifier. Generator candidates from spectro_v2 (data/experimental/gen_candidates.jsonl).
"""
import json, glob, re, importlib.util
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def _imp(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
hose = _imp("hose", "scripts/hose_predict.py")
enum = _imp("enum", "scripts/enumerate_isomers.py")
ctg  = _imp("ctg",  "scripts/closing_the_gap.py")   # reuse load(), ik(), obs_c13()

GEN = json.load(open("contrib/generator_probe/artifacts/gen_candidates.jsonl"))

def formula(s):
    m = Chem.MolFromSmiles(s) if s else None
    return rdMolDescriptors.CalcMolFormula(m) if m else None
def canon(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToSmiles(m) if m else s

def verify_top1(pool, obs):
    best, bestd = None, 1e9
    for s in pool:
        pred = hose.predict_c13(s)
        d = hose.chamfer(pred, obs) if pred else 1e9
        if d < bestd: bestd, best = d, s
    return best

def main():
    import random
    rows = ctg.load(); N = len(rows)
    R = {k: 0 for k in ["claude","enum","gen","gen_enum"]}
    T = {k: 0 for k in ["claude","enum","gen","gen_enum"]}
    rec = {k: [] for k in ["claude","gen"]}      # per-compound recalled (obs present)
    top = {k: [] for k in ["claude","gen"]}      # per-compound top-1 correct (obs present)
    gen_sizes, gen_pool_sizes = [], []
    for qid, true, cands, obs in rows:
        t = ctg.ik(true); tf = formula(true)
        cands = [canon(c) for c in cands if c]
        gcand = [g for g in GEN.get(qid, []) if formula(g) == tf]
        gen_sizes.append(len(gcand))
        enum_pool = list(dict.fromkeys(cands))
        for c in cands:
            for iso in enum.enumerate_regioisomers(c, cap=200):
                ci = canon(iso)
                if ci not in enum_pool: enum_pool.append(ci)
        pools = {"claude": list(dict.fromkeys(cands)), "enum": enum_pool,
                 "gen": list(dict.fromkeys(cands + gcand)),
                 "gen_enum": list(dict.fromkeys(enum_pool + gcand))}
        for k, pool in pools.items():
            R[k] += any(ctg.ik(p) == t for p in pool)
            if obs:
                b = verify_top1(pool, obs)
                ok = (b is not None and ctg.ik(b) == t); T[k] += ok
                if k in ("claude","gen"):
                    rec[k].append(any(ctg.ik(p) == t for p in pool)); top[k].append(ok)
        gen_pool_sizes.append(len(pools["gen"]))
    pc = lambda n: f"{100*n/N:4.1f}%"
    print(f"N = {N}   HOSE verifier (deterministic, conservative); gen formula-filtered\n")
    print(f"{'pool':<22}{'recall':>10}{'HOSE top-1':>14}{'proj@0.84':>12}")
    for k, lab in [("claude","Claude only"),("enum","+ enumeration"),
                   ("gen","+ generator"),("gen_enum","+ generator + enum")]:
        print(f"{lab:<22}{pc(R[k]):>10}{pc(T[k]):>14}{pc(0.84*R[k]):>12}")

    # --- recall x conditional-precision decomposition + significance (Claude vs +generator) ---
    cl_t, cl_r = top["claude"], rec["claude"]; gn_t, gn_r = top["gen"], rec["gen"]
    n = len(cl_t)
    cprec = lambda tl, rl: sum(a and b for a,b in zip(tl,rl))/max(sum(rl),1)
    print(f"\n--- decomposition (n={n} with obs 13C) ---")
    print(f"Claude   : recall {sum(cl_r)}/{n}  cond.precision {sum(cl_t)}/{sum(cl_r)} = {100*cprec(cl_t,cl_r):.1f}%")
    print(f"+gen     : recall {sum(gn_r)}/{n}  cond.precision {sum(gn_t)}/{sum(gn_r)} = {100*cprec(gn_t,gn_r):.1f}%")
    inc_r = sum(g and not c for g,c in zip(gn_r,cl_r)); inc_t = sum(gt and not ct for gt,ct in zip(gn_t,cl_t))
    print(f"INCREMENTAL rescues: +{inc_r} recalled, +{inc_t} top-1 → cond.prec on rescues {inc_t}/{inc_r} = {100*inc_t/max(inc_r,1):.1f}%  (chance≈1/pool)")
    # McNemar (paired top-1: Claude vs +gen)
    b = sum(ct and not gt for ct,gt in zip(cl_t,gn_t))   # claude right, gen wrong
    c = sum(gt and not ct for ct,gt in zip(cl_t,gn_t))   # gen right, claude wrong
    from math import comb
    p_mcnemar = sum(comb(b+c,i) for i in range(min(b,c)+1))*2/ (2**(b+c)) if (b+c)>0 else 1.0
    print(f"McNemar (top-1): discordant b(claude-only)={b}, c(gen-only)={c}, exact 2-sided p={min(p_mcnemar,1.0):.4f}")
    # bootstrap CI on top-1 delta
    random.seed(0); deltas=[]
    for _ in range(2000):
        idx=[random.randrange(n) for _ in range(n)]
        deltas.append((sum(gn_t[i] for i in idx)-sum(cl_t[i] for i in idx))/n)
    deltas.sort(); lo,hi=deltas[50],deltas[1949]
    print(f"top-1 delta (+gen − Claude) = {100*(sum(gn_t)-sum(cl_t))/n:+.1f}pp  95% CI [{100*lo:+.1f}, {100*hi:+.1f}]")
    gen_sizes.sort(); gen_pool_sizes.sort()
    print(f"\ngen cand/compound (formula-filtered): median {gen_sizes[len(gen_sizes)//2]}, max {gen_sizes[-1]}; gen-pool median {gen_pool_sizes[len(gen_pool_sizes)//2]}")
    print(f"(Claude paper headline top-1 = 28.4%)")

if __name__ == "__main__":
    main()
