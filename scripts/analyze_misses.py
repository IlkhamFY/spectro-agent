#!/usr/bin/env python3
"""
What does a top-1 miss actually look like?

§4 originally asserted that the model fails "predominantly on regiochemistry — which
position a substituent occupies". That is a chemical claim about 139 specific failures,
and the expert-chemist audit (§7) was designed partly to test it. Most of it is
mechanically decidable, so it should be measured rather than asserted, leaving the panel
a narrower question.

Three nested descriptions of a miss, from weakest to strongest:
  * constitutional isomer  — exactly the right atoms, wrong connectivity
  * same Murcko scaffold   — the ring/linker skeleton is right, so the error is
                             genuinely positional: a substituent in the wrong place
  * high Tanimoto          — near-identical structures

  python scripts/analyze_misses.py
"""
import json, glob
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, DataStructs, rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

GEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
ROUNDS = [("data/benchmark_main", "data/benchmark_main/clean_qids.json", "M-"),
          ("data/benchmark_v3", None, None),
          ("data/benchmark_v2_ctrl", None, None)]


def ik14(m):
    return Chem.MolToInchiKey(m)[:14] if m else None


def scaffold(m):
    try:
        return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception:
        return None


def collect():
    misses, unparseable, hits = [], 0, 0
    for d, cleanf, prefix in ROUNDS:
        keep = set(json.load(open(cleanf))) if cleanf else None
        ans = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        pred = {}
        if prefix:
            for f in glob.glob(f"{d}/raw/*.json"):
                pred.update(json.load(open(f)))
            pred = {k[len(prefix):]: v for k, v in pred.items()}
        else:
            for l in open(f"{d}/predictions2.jsonl"):
                r = json.loads(l); pred[r["qid"]] = r.get("candidates", [])
        for q, a in ans.items():
            if keep is not None and q not in keep:
                continue
            top = pred.get(q, [])[:1]
            truth = Chem.MolFromSmiles(a.get("smiles") or "")
            if truth is None or not top:
                continue
            cand = Chem.MolFromSmiles(top[0] or "")
            if cand is None:
                unparseable += 1
                continue
            if ik14(cand) == ik14(truth):
                hits += 1
                continue
            misses.append({
                "same_formula": (rdMolDescriptors.CalcMolFormula(cand)
                                 == rdMolDescriptors.CalcMolFormula(truth)),
                "same_scaffold": scaffold(cand) is not None
                                 and scaffold(cand) == scaffold(truth),
                "tanimoto": DataStructs.TanimotoSimilarity(
                    GEN.GetFingerprint(cand), GEN.GetFingerprint(truth)),
            })
    return misses, unparseable, hits


def formula_adherence():
    """The formula is an INPUT, so obeying it is a constraint the solver can break.
    Reported per round because the rounds differ: §8 describes the RDKit formula check
    as uniform, but the headline round adheres materially less well than the controlled
    ones, and a reader applying one figure to the other would be misled."""
    import re
    norm = lambda f: re.sub(r'[+\-]\d*$', '', (f or "").replace(" ", ""))
    print("\nAdherence to the supplied molecular formula, top-1, by round:")
    for d, cleanf, prefix in ROUNDS:
        keep = set(json.load(open(cleanf))) if cleanf else None
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        ans = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        pred = {}
        if prefix:
            for f in glob.glob(f"{d}/raw/*.json"):
                pred.update(json.load(open(f)))
            pred = {k[len(prefix):]: v for k, v in pred.items()}
        else:
            for l in open(f"{d}/predictions2.jsonl"):
                r = json.loads(l); pred[r["qid"]] = r.get("candidates", [])
        tot = ok = 0
        for qid, a in ans.items():
            if keep is not None and qid not in keep:
                continue
            top = pred.get(qid, [])[:1]
            given = norm(q.get(qid, {}).get("formula"))
            if not top or not given:
                continue
            tot += 1
            c = Chem.MolFromSmiles(top[0] or "")
            if c and norm(rdMolDescriptors.CalcMolFormula(c)) == given:
                ok += 1
        if tot:
            print(f"  {d.split('/')[-1]:<24} {ok:>4}/{tot:<4} {100*ok/tot:5.1f}%")


def recall_drivers():
    """What distinguishes a compound whose true structure was never proposed?
    §5.3 explains the recall plateau by naming exotic chemistry; this tests that."""
    from rdkit import Chem
    ROUND_SPEC = ROUNDS
    R, N = [], []
    for d, cleanf, prefix in ROUND_SPEC:
        keep = set(json.load(open(cleanf))) if cleanf else None
        ans = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        pred = {}
        if prefix:
            for f in glob.glob(f"{d}/raw/*.json"):
                pred.update(json.load(open(f)))
            pred = {k[len(prefix):]: v for k, v in pred.items()}
        else:
            for l in open(f"{d}/predictions2.jsonl"):
                r = json.loads(l); pred[r["qid"]] = r.get("candidates", [])
        for q, a in ans.items():
            if keep is not None and q not in keep:
                continue
            t = Chem.MolFromSmiles(a.get("smiles") or "")
            if t is None:
                continue
            cands = [Chem.MolFromSmiles(s or "") for s in pred.get(q, [])[:3]]
            (R if any(c and ik14(c) == ik14(t) for c in cands) else N).append(t)
    nN = lambda m: sum(1 for a in m.GetAtoms() if a.GetSymbol() == "N")
    rings = lambda m: m.GetRingInfo().NumRings()
    med = lambda ms, f: sorted(f(m) for m in ms)[len(ms) // 2]
    pct = lambda ms, f: 100 * sum(1 for m in ms if f(m)) / len(ms)
    print(f"\nRecall drivers — {len(R)} recalled vs {len(N)} missed:")
    print(f"  {'feature':<28}{'recalled':>10}{'missed':>10}")
    print(f"  {'median heavy atoms':<28}{med(R, lambda m: m.GetNumHeavyAtoms()):>10}"
          f"{med(N, lambda m: m.GetNumHeavyAtoms()):>10}")
    print(f"  {'median ring count':<28}{med(R, rings):>10}{med(N, rings):>10}")
    print(f"  {'>=4 rings':<28}{pct(R, lambda m: rings(m) >= 4):>9.1f}%"
          f"{pct(N, lambda m: rings(m) >= 4):>9.1f}%")
    print(f"  {'>=4 nitrogens':<28}{pct(R, lambda m: nN(m) >= 4):>9.1f}%"
          f"{pct(N, lambda m: nN(m) >= 4):>9.1f}%")
    for sym in ("Se", "S", "F", "Cl", "P"):
        h = lambda m, s=sym: any(a.GetSymbol() == s for a in m.GetAtoms())
        print(f"  {'contains ' + sym:<28}{pct(R, h):>9.1f}%{pct(N, h):>9.1f}%")
    print("  → size and ring count separate; halogens and S do not.")


def main():
    misses, unparseable, hits = collect()
    n = len(misses)
    total = n + unparseable
    iso = [m for m in misses if m["same_formula"]]
    pos = [m for m in iso if m["same_scaffold"]]
    print(f"top-1 correct: {hits}    top-1 misses: {total} "
          f"({unparseable} unparseable, {n} analysable)\n")
    row = lambda k, lab: print(f"  {lab:<52}{k:>4}/{n}  {100*k/n:5.1f}%")
    row(len(iso), "constitutional isomer (right formula, wrong bonds)")
    row(len(pos), "…and the same Murcko scaffold → positional error")
    for t in (0.85, 0.70, 0.55):
        row(sum(1 for m in iso if m["tanimoto"] >= t), f"…and Tanimoto ≥ {t:.2f}")
    row(n - len(iso), "wrong molecular formula (a different compound)")
    if iso:
        ts = sorted(m["tanimoto"] for m in iso)
        print(f"\n  Tanimoto(miss, truth) over the isomer misses: "
              f"median {ts[len(ts)//2]:.2f}  min {ts[0]:.2f}  max {ts[-1]:.2f}")
    formula_adherence()
    recall_drivers()
    print("\nReading: the composition is usually right and the connectivity is not.\n"
          "'Which position a substituent occupies' describes the scaffold-preserving\n"
          "row only — a minority of misses, not the predominant failure mode.")


if __name__ == "__main__":
    main()
