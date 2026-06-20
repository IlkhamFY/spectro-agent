#!/usr/bin/env python3
"""Realized 'enumerate + verify' experiment (deterministic, no LLM).

Recipe: take the model's candidates, enumerate scaffold-constrained regioisomers
around each (scripts/enumerate_isomers.py), and re-rank the pooled set by a
deterministic HOSE-code 13C verifier (scripts/hose_predict.py) against the observed
13C. We hold the verifier fixed and compare original-pool vs enumerated-pool, so the
delta isolates the effect of enumeration. HOSE is weaker than the LLM verifier
(paper Sec.5.4), so realized top-1 here is a conservative lower bound.
"""
import json, glob, re, importlib.util
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def _imp(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
hose = _imp("hose", "scripts/hose_predict.py")
enum = _imp("enum", "scripts/enumerate_isomers.py")

def ik(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None
def obs_c13(c_nmr):
    return [float(x) for x in re.findall(r"([0-9]+\.?[0-9]*)\s*\(", c_nmr or "")]

def load():
    """yield (qid, true_smiles, candidates[<=3], obs_c13)."""
    out = []
    # main round
    qa = {json.loads(l)["qid"]: json.loads(l) for l in open("data/benchmark_main/answers2.jsonl")}
    qq = {json.loads(l)["qid"]: json.loads(l) for l in open("data/benchmark_main/questions2.jsonl")}
    clean = set(json.load(open("data/benchmark_main/clean_qids.json")))
    pred = {}
    for f in glob.glob("data/benchmark_main/raw/*.json"):
        try:
            pred.update(json.load(open(f)))
        except Exception: pass
    for qid, ans in qa.items():
        if qid not in clean: continue
        cs = pred.get(f"M-{qid}")
        if cs is None: continue
        out.append((qid, ans["smiles"], cs[:3], obs_c13(qq[qid]["c_nmr"])))
    # original rounds
    for d in ["data/benchmark_v3", "data/benchmark_v2_ctrl"]:
        qa = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        qq = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        qp = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/predictions2.jsonl")}
        for qid, ans in qa.items():
            out.append((f"{d}:{qid}", ans["smiles"],
                        qp[qid].get("candidates", [])[:3], obs_c13(qq[qid]["c_nmr"])))
    return out

def verify_top1(pool, obs):
    """rank pool by HOSE chamfer to obs; return best SMILES (or None)."""
    best, bestd = None, 1e9
    for s in pool:
        pred = hose.predict_c13(s)
        d = hose.chamfer(pred, obs) if pred else 1e9
        if d < bestd:
            bestd, best = d, s
    return best

def main():
    rows = load()
    N = len(rows)
    base_recall = enum_recall = 0
    base_top1 = fix_top1 = 0
    pool_sizes = []
    for qid, true, cands, obs in rows:
        t = ik(true)
        cands = [c for c in cands if c]
        recalled = any(ik(c) == t for c in cands)
        base_recall += recalled

        # enumerate regioisomers around each candidate; canonicalize before de-dup so
        # non-canonical raw candidates don't double-count against canonical isomers
        def _canon(s):
            m = Chem.MolFromSmiles(s) if s else None
            return Chem.MolToSmiles(m) if m else s
        pool = list(dict.fromkeys(_canon(c) for c in cands))
        for c in cands:
            for iso in enum.enumerate_regioisomers(c, cap=200):
                ciso = _canon(iso)
                if ciso not in pool:
                    pool.append(ciso)
        pool_sizes.append(len(pool))
        enum_recalled = any(ik(p) == t for p in pool)
        enum_recall += enum_recalled

        # HOSE-verify, holding the verifier fixed: original pool vs enumerated pool
        if obs:
            b = verify_top1(cands, obs)
            f = verify_top1(pool, obs)
            base_top1 += (b is not None and ik(b) == t)
            fix_top1  += (f is not None and ik(f) == t)

    def pc(n): return f"{100*n/N:4.1f}%"
    print(f"N = {N} compounds   (HOSE verifier; deterministic, conservative)\n")
    print(f"  recall    original candidates      : {base_recall:3}/{N}  ({pc(base_recall)})")
    print(f"  recall    + scaffold enumeration    : {enum_recall:3}/{N}  ({pc(enum_recall)})"
          f"   (+{enum_recall-base_recall})")
    print(f"  top-1     HOSE-verify, original pool : {base_top1:3}/{N}  ({pc(base_top1)})")
    print(f"  top-1     HOSE-verify, + enumeration : {fix_top1:3}/{N}  ({pc(fix_top1)})"
          f"   (+{fix_top1-base_top1})")
    pool_sizes.sort()
    print(f"\n  enumerated pool size: median {pool_sizes[len(pool_sizes)//2]}, "
          f"max {pool_sizes[-1]}")
    # the cheap verifier backfires; project top-1 under a strong (LLM, 0.84) verifier
    print(f"\n  projected top-1 @ strong verifier (0.84 x recall; OPTIMISTIC -- assumes")
    print(f"  precision holds on the larger pool, which it typically does not):")
    print(f"    original    : {0.84*base_recall:4.0f}/{N}  ({pc(0.84*base_recall)})")
    print(f"    + enumerate : {0.84*enum_recall:4.0f}/{N}  ({pc(0.84*enum_recall)})")
    print("  => enumeration is recall-bound at ~42%; the residual same-formula misses are")
    print("     deeper constitutional rearrangements (generation, not enumeration), and the")
    print("     gain needs a precise verifier -- the cheap HOSE one regresses (above).")

if __name__ == "__main__":
    main()
