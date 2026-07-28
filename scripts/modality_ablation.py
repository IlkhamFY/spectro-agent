#!/usr/bin/env python3
"""Modality-ablation harness (corrected, within-compound design).

The first pilot was confounded: using one solver agent per condition let between-run
solver-quality variance swamp the modality effect (the full-modality run even came out
worst). The fix implemented here:

  * LEAVE-ONE-OUT conditions: full (formula+IR+1H+13C), -IR, -1H, -13C.
  * Every (compound, condition) is solved in an INDEPENDENT, fresh context by the
    SAME solver/model, so the only thing that varies across conditions is the input
    modality. Pairing is WITHIN compound, which also controls for compound difficulty.
  * Scoring is paired: per-condition top-1/recovery plus McNemar's exact test of
    full vs each leave-one-out condition on the same compounds.

Usage:
  python scripts/modality_ablation.py prepare            # write anonymized prompts + key
  # ... run your solver on each data/modality/prompt_<cond>.txt, in fresh per-compound
  #     contexts, same model; save outputs as data/modality/out_<cond>.json = {mid:[smiles,...]}
  python scripts/modality_ablation.py score              # paired analysis

Run it on your tuned Opus pipeline for a publishable result; sub-agents are too weak
and variable to give a trustworthy absolute number (see docs/MODALITY_ABLATION.md)."""
import json, os, sys, random, math, glob
from itertools import combinations

OUT = "data/modality"
# "formulaonly" is not a modality ablation but the CONTAMINATION CONTROL: the solver is
# given the molecular formula and nothing else. A formula does not determine constitution,
# so accuracy materially above the near-zero floor indicates recall from pretraining rather
# than spectral reasoning. It shares this harness because it is the same blind protocol
# with every spectral channel masked.
CONDS = ["full", "noIR", "noH", "noC", "formulaonly"]
COND_KW = {"full": (1, 1, 1), "noIR": (0, 1, 1), "noH": (1, 0, 1), "noC": (1, 1, 0),
           "formulaonly": (0, 0, 0)}
SETS = ["data/benchmark_v3", "data/benchmark_v2_ctrl"]   # the 60-compound forward-verify set

def _block(r, ir, h, c):
    L = [f"### {r['mid']}", f"Molecular formula: {r['formula']}"]
    if ir: L.append(f"IR bands (cm-1): {r['ir']}")
    if h:  L.append(f"1H NMR: {r['h']}")
    if c:  L.append(f"13C NMR: {r['c']}")
    return "\n".join(L)

def prepare(seed=0, n_per_stratum=None):
    """n_per_stratum=None -> use the full set (recommended for the real run)."""
    rows = []
    for d in SETS:
        qq = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        qa = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        for qid, q in qq.items():
            a = qa.get(qid)
            if not a: continue
            rows.append(dict(src=f"{d}:{qid}", difficulty=a["difficulty"], formula=q["formula"],
                             ir=q.get("ir_bands_cm-1"), h=q["h_nmr"], c=q["c_nmr"],
                             true_smiles=a["smiles"], true_ik=a["inchikey"]))
    rng = random.Random(seed)
    if n_per_stratum:
        sel = []
        for strat in ("simple", "complex"):
            pool = sorted([r for r in rows if r["difficulty"] == strat], key=lambda r: r["src"])
            sel += rng.sample(pool, min(n_per_stratum, len(pool)))
        rows = sel
    rows.sort(key=lambda r: (r["difficulty"], r["src"]))
    for i, r in enumerate(rows, 1): r["mid"] = f"M{i:03d}"
    os.makedirs(OUT, exist_ok=True)
    key = {r["mid"]: {k: r[k] for k in ("src", "difficulty", "true_smiles", "true_ik")} for r in rows}
    json.dump(key, open(f"{OUT}/key.json", "w"), indent=0)
    for cond in CONDS:
        ir, h, c = COND_KW[cond]
        txt = "\n\n".join(_block(r, ir, h, c) for r in rows)
        open(f"{OUT}/prompt_{cond}.txt", "w").write(txt)
    print(f"prepared {len(rows)} compounds x {len(CONDS)} conditions -> {OUT}/prompt_*.txt")
    print(f"answer key (held out from solver): {OUT}/key.json")
    print("Solve EACH compound in EACH prompt file in an independent fresh context, SAME model,")
    print(f"and save outputs as {OUT}/out_<cond>.json mapping id -> [smiles,...]. Then: score.")

def _ik(s):
    from rdkit import Chem
    from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def _mcnemar(b, c):
    """exact two-sided McNemar p on discordant counts b, c."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * p)

def score():
    key = json.load(open(f"{OUT}/key.json"))
    truth = {m: _ik(v["true_smiles"]) for m, v in key.items()}
    outs = {}
    for cond in CONDS:
        p = f"{OUT}/out_{cond}.json"
        outs[cond] = json.load(open(p)) if os.path.exists(p) else None
    have = [c for c in CONDS if outs[c] is not None]
    if "full" not in have:
        print("need at least out_full.json; have:", have); return
    # paired top-1 vectors over compounds present in ALL available conditions
    ids = [m for m in truth if all(m in outs[c] for c in have)]
    if not ids:
        print("no compounds present in all available conditions — check that out_*.json "
              "are keyed by the M### ids from key.json."); return
    def top1(cond, m):
        cs = [_ik(s) for s in (outs[cond].get(m) or [])[:1]]
        return int(bool(cs) and cs[0] == truth[m])
    def rec(cond, m):
        cs = [_ik(s) for s in (outs[cond].get(m) or [])[:3]]
        return int(truth[m] in cs)
    n = len(ids)
    print(f"n = {n} compounds (paired, present in all available conditions: {have})\n")
    print(f"{'condition':<10}{'top-1':>8}{'recovered':>11}{'  vs full (McNemar)':>22}")
    base_t = {m: top1("full", m) for m in ids}
    for cond in have:
        t = sum(top1(cond, m) for m in ids) / n
        r = sum(rec(cond, m) for m in ids) / n
        note = ""
        if cond != "full":
            cur = {m: top1(cond, m) for m in ids}
            b = sum(base_t[m] == 1 and cur[m] == 0 for m in ids)   # full right, cond wrong
            c = sum(base_t[m] == 0 and cur[m] == 1 for m in ids)   # cond right, full wrong
            note = f"b={b} c={c} p={_mcnemar(b, c):.3f}"
        print(f"{cond:<10}{t:>7.1%}{r:>11.1%}{note:>22}")
    print("\nmarginal value of a modality = full - (its leave-one-out condition), paired.")
    print("A positive, significant drop on removal = that modality carries unique signal.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if cmd == "prepare":
        npe = int(sys.argv[2]) if len(sys.argv) > 2 else None
        prepare(n_per_stratum=npe)
    elif cmd == "score":
        score()
    else:
        print("usage: modality_ablation.py [prepare [n_per_stratum] | score]")
