#!/usr/bin/env python3
"""Leakage audit tied to the EXACT incremental-40 rescues that produce 54.1%/35.1%
(closing_the_gap_gen.py pipeline, formula-filtered). Self-contained: uses the committed
de-leaked split (contrib/generator_probe/artifacts/split_ik14.json) — train IK-14 set and
the benchmark∩sim-pretrain overlap — so no external 768K sim set / 28MB manifest is needed.
Run from repo root. (The full recompute from the raw sim set lives in spectro_v2.)"""
import json, importlib.util
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

def _imp(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
ctg = _imp("ctg", "scripts/closing_the_gap.py")

ART = "contrib/generator_probe/artifacts"
GEN = json.load(open(f"{ART}/gen_candidates.jsonl"))
SPLIT = json.load(open(f"{ART}/split_ik14.json"))
EXP = set(SPLIT["train_ik14"])                       # 29,157 exp-finetune compounds
BENCH_IN_SIM = set(SPLIT["benchmark_inter_simpretrain"])   # benchmark ∩ generic sim-pretrain
def formula(s):
    m = Chem.MolFromSmiles(s) if s else None
    return rdMolDescriptors.CalcMolFormula(m) if m else None
def canon(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToSmiles(m) if m else s

rows = ctg.load()
bench = {ctg.ik(t) for _, t, _, _ in rows}
print(f"exp-finetune IK-14: {len(EXP):,}   benchmark(194): {len(bench)}")
print(f"benchmark ∩ exp-finetune : {len(bench & EXP)}/{len(bench)}")
print(f"benchmark ∩ sim-pretrain : {len(bench & BENCH_IN_SIM)}/{len(bench)}  (sim is generic, not de-leaked)")

# the EXACT incremental-40: gen recalls truth, Claude does not (formula-filtered pool)
rescues = []
for qid, true, cands, obs in rows:
    t = ctg.ik(true); tf = formula(true)
    cl = {ctg.ik(canon(c)) for c in cands if c}
    g = [x for x in GEN.get(qid, []) if formula(x) == tf]
    if (t in (cl | {ctg.ik(x) for x in g})) and (t not in cl):
        rescues.append((qid, t))
R = {t for _, t in rescues}
print(f"\nincremental rescues (gen-only, formula-filtered): {len(rescues)}")
print(f"  rescues ∩ exp-finetune : {len(R & EXP)}/{len(rescues)}")
print(f"  rescues ∩ sim-pretrain : {len(R & BENCH_IN_SIM)}/{len(rescues)}")
print("  => the generator's recall contribution is absent from BOTH training stages." if not (R & EXP) and not (R & BENCH_IN_SIM)
      else "  => LEAK DETECTED")
