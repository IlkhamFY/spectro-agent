#!/usr/bin/env python3
"""
Deterministic HOSE-code-style 13C predictor, trained on nmrshiftdb2, used as a
drop-in replacement for the LLM forward-verifier (paper §5/§7: "a deterministic
HOSE-code/DFT 13C verifier is the identified fix"). No LLM, fully reproducible.

A HOSE code is a radial (sphere-by-sphere) description of an atom's environment.
We realise the same idea natively in RDKit: the Morgan/ECFP per-atom identifier at
radius r is a canonical hash of the atom's environment out to r bonds, so a
(radius, identifier) bin groups carbons with identical local environments. We learn
the mean assigned 13C shift per bin from nmrshiftdb2 and predict by looking up the
deepest sufficiently-populated sphere (r=4 -> 3 -> 2 -> 1 -> hybridisation prior).

  build : parse nmrshiftdb2.sd -> data/nmrshiftdb/hose_c13.json.gz  (+ held-out MAE)
  score : re-rank data/fverify/candidates.jsonl by predicted-vs-observed 13C and
          report conditional-on-recall precision vs the LLM verifier.
"""
import json, gzip, sys, random, re, math
from collections import defaultdict
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SDF = "data/nmrshiftdb/nmrshiftdb2.sd"
DB  = "data/nmrshiftdb/hose_c13.json.gz"
RADII = [4, 3, 2, 1]
MINN = 3                      # min samples to trust a sphere bin

def atom_rad_bits(mol, rmax=4):
    """-> {atomIdx: {rad: bit}} for every atom, spheres 0..rmax."""
    info = {}
    rdMolDescriptors.GetMorganFingerprint(mol, rmax, bitInfo=info)
    out = defaultdict(dict)
    for bit, occ in info.items():
        for a, r in occ:
            out[a][r] = bit
    return out

def parse_spectrum(val):
    """nmrshiftdb 'shift;mult;atomidx|...' -> {atomidx: shift} (avg dups)."""
    acc = defaultdict(list)
    for ent in val.split("|"):
        p = ent.split(";")
        if len(p) < 3:
            continue
        try:
            sh = float(p[0]); ai = int(p[-1])
        except ValueError:
            continue
        acc[ai].append(sh)
    return {a: sum(v) / len(v) for a, v in acc.items()}

def build():
    supp = Chem.SDMolSupplier(SDF, removeHs=True, sanitize=True)
    bins = defaultdict(lambda: [0.0, 0])      # (rad,bit) -> [sum, n]
    prior = defaultdict(lambda: [0.0, 0])     # coarse hybridisation prior
    nmol = npts = 0
    heldout = []                               # 5% of mols held out for honest MAE
    for mol in supp:
        if mol is None:
            continue
        c13 = [p for p in mol.GetPropNames() if p.startswith("Spectrum 13C")]
        if not c13:
            continue
        assign = parse_spectrum(mol.GetProp(c13[0]))
        if not assign:
            continue
        nA = mol.GetNumAtoms()
        if any(not (0 <= a < nA) or mol.GetAtomWithIdx(a).GetSymbol() != "C"
               for a in assign):
            continue                            # H-explicit / mis-indexed record
        if random.random() < 0.05:
            heldout.append((mol, dict(assign)))   # keep mol: indices stay aligned
            continue                              # excluded from the table
        arb = atom_rad_bits(mol)
        for a, sh in assign.items():
            at = mol.GetAtomWithIdx(a)
            pk = ("ar" if at.GetIsAromatic() else str(at.GetHybridization()))
            prior[pk][0] += sh; prior[pk][1] += 1
            for r in RADII:
                b = arb[a].get(r)
                if b is not None:
                    bins[f"{r}:{b}"][0] += sh; bins[f"{r}:{b}"][1] += 1
            npts += 1
        nmol += 1
        if nmol % 5000 == 0:
            print(f"  ...{nmol} mols, {npts} carbons", flush=True)
    global _DB
    _DB = {"bins": {k: [round(s / n, 3), n] for k, (s, n) in bins.items()},
           "prior": {k: [round(s / n, 3), n] for k, (s, n) in prior.items()},
           "minn": MINN, "radii": RADII}
    json.dump(_DB, gzip.open(DB, "wt"))
    print(f"built HOSE DB: {nmol} mols, {npts} carbons, "
          f"{len(_DB['bins'])} env bins -> {DB}")
    # honest accuracy: per-atom MAE on held-out molecules (positional match)
    errs = []
    for m, assign in heldout:
        arb = atom_rad_bits(m)
        for a, true_sh in assign.items():
            if a >= m.GetNumAtoms() or m.GetAtomWithIdx(a).GetSymbol() != "C":
                continue
            sh = None
            for r in RADII:
                b = arb[a].get(r)
                rec = _DB["bins"].get(f"{r}:{b}") if b is not None else None
                if rec and rec[1] >= MINN:
                    sh = rec[0]; break
            if sh is not None:
                errs.append(abs(sh - true_sh))
    if errs:
        errs.sort()
        mae = sum(errs) / len(errs)
        med = errs[len(errs) // 2]
        print(f"held-out 13C accuracy: MAE {mae:.2f} ppm, median {med:.2f} ppm "
              f"(n={len(errs)} carbons, {len(heldout)} held-out mols)")

# ---- prediction --------------------------------------------------------------
_DB = None
def _load():
    global _DB
    if _DB is None:
        _DB = json.load(gzip.open(DB, "rt"))
    return _DB

def predict_c13(smiles):
    db = _load(); bins = db["bins"]; pri = db["prior"]
    m = Chem.MolFromSmiles(smiles) if smiles else None
    if m is None:
        return None
    arb = atom_rad_bits(m)
    out = []
    for a in range(m.GetNumAtoms()):
        at = m.GetAtomWithIdx(a)
        if at.GetSymbol() != "C":
            continue
        sh = None
        for r in RADII:
            b = arb[a].get(r)
            if b is None:
                continue
            rec = bins.get(f"{r}:{b}")
            if rec and rec[1] >= MINN:
                sh = rec[0]; break
        if sh is None:                     # coarse fallback
            pk = ("ar" if at.GetIsAromatic() else str(at.GetHybridization()))
            rec = pri.get(pk)
            sh = rec[0] if rec else 100.0
        out.append(sh)
    return out

def chamfer(pred, obs):
    if not pred or not obs:
        return 999.0
    a = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    b = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (a + b) / 2

def ik14(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToInchiKey(m)[:14] if m else None

def score():
    rows = [json.loads(l) for l in open("data/fverify/candidates.jsonl")]
    comps = defaultdict(list)
    for r in rows:
        comps[r["qid"] + r["dir"]].append(r)
    self1 = hose1 = ceil = n = 0
    cself = chose = cn = 0
    cal = []
    for key, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            c["pred"] = predict_c13(c["smiles"])
            c["dist"] = chamfer(c["pred"], obs)
        n += 1
        has = any(c["is_true"] for c in cands); ceil += has
        s = sorted(cands, key=lambda c: c["self_rank"])[0]["is_true"]; self1 += s
        best = min(cands, key=lambda c: c["dist"]); hose1 += best["is_true"]
        if has:
            cn += 1; cself += s; chose += best["is_true"]
            cal.append((best["dist"], best["is_true"]))
    print(f"compounds: {n}")
    print(f"  ceiling (recall):              {ceil}/{n} ({100*ceil//n}%)")
    print(f"  top-1 solver self-rank:        {self1}/{n} ({100*self1//n}%)")
    print(f"  top-1 HOSE-verified re-rank:   {hose1}/{n} ({100*hose1//n}%)")
    print(f"\n  CONDITIONAL on recall (n={cn}):")
    print(f"    solver self-rank:  {cself}/{cn} ({100*cself//cn}%)")
    print(f"    HOSE-verify:       {chose}/{cn} ({100*chose//cn}%)   "
          f"(LLM verifier was 84% on this set)")

if __name__ == "__main__":
    random.seed(7)
    (build() if sys.argv[1] == "build" else score())
