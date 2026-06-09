#!/usr/bin/env python3
"""
Pilot benchmark: LLM structure elucidation on IRexp gold records.

Replicates the inverse task from Anthropic's "Making Claude a Chemist" (spectra +
formula -> structure) but (a) on real scraped experimental data at a larger scale,
(b) adding the IR modality they did not test, and (c) deliberately spanning
molecule sizes to probe where it breaks (their stated natural-product gap).

Protocol (blind, mechanically scored):
  sample : draw N gold records (real IR + 1H + 13C + a known structure), derive
           the molecular formula from the *true* SMILES, and write
             data/benchmark/questions.jsonl  (qid, formula, ir, 1H, 13C -- NO structure)
             data/benchmark/answers.jsonl    (qid, true smiles/inchikey)  [not printed]
           The solver sees only questions.jsonl; answers never enter its context.
  score  : compare data/benchmark/predictions.jsonl (qid, smiles) to answers via
           RDKit -- exact constitution (InChIKey 1st block), full InChIKey (w/ stereo),
           and Morgan Tanimoto -- broken down by molecule-size bucket.

    python scripts/benchmark_elucidation.py sample --n 20 --seed 7
    # (solver fills data/benchmark/predictions.jsonl)
    python scripts/benchmark_elucidation.py score
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors, AllChem, DataStructs
RDLogger.DisableLog("rdApp.*")

GOLD = Path("data/irexp_resolved/irexp_resolved.jsonl.gz")
BDIR = Path("data/benchmark")
Q = BDIR / "questions.jsonl"
A = BDIR / "answers.jsonl"
P = BDIR / "predictions.jsonl"


def _bucket(hac: int) -> str:
    return "small (<18)" if hac < 18 else "medium (18-28)" if hac <= 28 else "large (>28)"


def sample(n: int, seed: int):
    random.seed(seed)
    pool = []
    seen = set()
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not (smi and r.get("h_nmr") and r.get("c_nmr") and r.get("ir_bands_cm-1")):
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        hac = mol.GetNumHeavyAtoms()
        if hac < 8 or hac > 60:
            continue
        ik = r.get("inchikey") or Chem.MolToInchiKey(mol)
        key = ik[:14]
        if key in seen:
            continue
        seen.add(key)
        # need a few real peaks (not a near-empty list)
        if r["h_nmr"].count("(") < 3 or r["c_nmr"].count("(") < 3:
            continue
        pool.append((r, mol, hac, ik))
    # stratify across size buckets so hard (large/natural-product-like) cases are present
    buckets = {"small (<18)": [], "medium (18-28)": [], "large (>28)": []}
    for item in pool:
        buckets[_bucket(item[2])].append(item)
    per = max(1, n // 3)
    chosen = []
    for b, items in buckets.items():
        random.shuffle(items)
        chosen += items[:per]
    random.shuffle(chosen)
    chosen = chosen[:n]

    BDIR.mkdir(parents=True, exist_ok=True)
    with Q.open("w") as q, A.open("w") as a:
        for i, (r, mol, hac, ik) in enumerate(chosen, 1):
            qid = f"Q{i:02d}"
            formula = rdMolDescriptors.CalcMolFormula(mol)
            q.write(json.dumps({"qid": qid, "formula": formula,
                                "ir_bands_cm-1": r["ir_bands_cm-1"],
                                "h_nmr": r["h_nmr"], "c_nmr": r["c_nmr"]},
                               ensure_ascii=False) + "\n")
            a.write(json.dumps({"qid": qid, "smiles": Chem.MolToSmiles(mol),
                                "inchikey": ik, "heavy_atoms": hac,
                                "bucket": _bucket(hac)}, ensure_ascii=False) + "\n")
    print(f"wrote {len(chosen)} questions -> {Q}")
    print(f"size mix: " + ", ".join(
        f"{b}={sum(1 for _,_,h,_ in chosen if _bucket(h)==b)}" for b in buckets))
    print("\n================  QUESTIONS (solve blind)  ================")
    for line in Q.open():
        d = json.loads(line)
        print(f"\n[{d['qid']}]  formula {d['formula']}")
        print(f"  IR  cm-1 : {d['ir_bands_cm-1']}")
        print(f"  1H NMR   : {d['h_nmr']}")
        print(f"  13C NMR  : {d['c_nmr']}")


def _fp(mol):
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)


def score():
    ans = {json.loads(l)["qid"]: json.loads(l) for l in A.open()}
    preds = {json.loads(l)["qid"]: json.loads(l) for l in P.open()}
    rows, by_bucket = [], {}
    for qid, a in sorted(ans.items()):
        pred = preds.get(qid, {})
        psmi = pred.get("smiles", "")
        tmol = Chem.MolFromSmiles(a["smiles"])
        pmol = Chem.MolFromSmiles(psmi) if psmi else None
        exact = full = False
        tani = 0.0
        if pmol is not None:
            pik = Chem.MolToInchiKey(pmol)
            exact = pik[:14] == a["inchikey"][:14]        # constitution
            full = pik == a["inchikey"]                    # incl. stereo
            tani = DataStructs.TanimotoSimilarity(_fp(tmol), _fp(pmol))
        rows.append((qid, a["bucket"], exact, full, round(tani, 3), psmi))
        b = by_bucket.setdefault(a["bucket"], [0, 0, 0.0])
        b[0] += 1; b[1] += int(exact); b[2] += tani

    n = len(rows)
    ex = sum(r[2] for r in rows); fu = sum(r[3] for r in rows)
    mt = sum(r[4] for r in rows) / n if n else 0
    print(f"\n=== ELUCIDATION BENCHMARK ({n} compounds, IR+1H+13C+formula, blind) ===\n")
    print(f"{'qid':4} {'bucket':14} {'exact':6} {'stereo':6} {'Tanimoto':8}  predicted")
    for qid, bk, exact, full, tani, psmi in rows:
        print(f"{qid:4} {bk:14} {'YES' if exact else '·':6} "
              f"{'YES' if full else '·':6} {tani:<8} {psmi[:46]}")
    print(f"\nexact constitution match : {ex}/{n}  ({100*ex//n}%)")
    print(f"exact incl. stereochem    : {fu}/{n}  ({100*fu//n}%)")
    print(f"mean Tanimoto (Morgan)    : {mt:.3f}")
    print("\nby molecule size:")
    for b in ("small (<18)", "medium (18-28)", "large (>28)"):
        if b in by_bucket:
            c, e, t = by_bucket[b]
            print(f"  {b:14} exact {e}/{c} ({100*e//c}%)   meanTani {t/c:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample"); s.add_argument("--n", type=int, default=20); s.add_argument("--seed", type=int, default=7)
    sub.add_parser("score")
    a = ap.parse_args()
    if a.cmd == "sample":
        sample(a.n, a.seed)
    else:
        score()
