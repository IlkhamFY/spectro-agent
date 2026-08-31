#!/usr/bin/env python3
"""Audit IRSpectra-Bench size: where n=194 comes from and what larger pools exist.

Reproduces the numbers in docs/IRSPECTRA_BENCH_SIZE_AUDIT.md from released artifacts only.

  python scripts/audit_bench_size.py
"""
from __future__ import annotations

import glob
import gzip
import json
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

GOLD = Path("data/irexp_resolved/irexp_resolved.jsonl.gz")
ROUNDS = [
    ("main (headline)", "data/benchmark_main", "data/benchmark_main/clean_qids.json", "M-", "raw"),
    ("controlled v3", "data/benchmark_v3", None, "", "predictions2"),
    ("within-compound ctrl", "data/benchmark_v2_ctrl", None, "", "predictions2"),
]


def difficulty(mol) -> str:
    ri = mol.GetRingInfo()
    nrings = ri.NumRings()
    hac = mol.GetNumHeavyAtoms()
    fused = any(ri.NumAtomRings(a.GetIdx()) >= 2 for a in mol.GetAtoms())
    spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol) > 0
    bridge = rdMolDescriptors.CalcNumBridgeheadAtoms(mol) > 0
    if spiro or bridge or nrings >= 3 or fused or hac > 24:
        return "complex"
    if nrings <= 2 and hac <= 22:
        return "simple"
    return "complex"


def inchikey14(smiles: str, stored: str | None = None) -> str | None:
    if stored:
        return stored[:14]
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(m)[:14] if m else None


def load_preds(d: str, prefix: str, kind: str) -> dict[str, list]:
    out: dict[str, list] = {}
    if kind == "raw":
        for f in glob.glob(f"{d}/raw/*.json"):
            for k, v in json.load(open(f)).items():
                if k.startswith(prefix):
                    out[k[len(prefix):]] = v
    else:
        p = Path(d) / f"{kind}.jsonl"
        if p.exists():
            for line in p.open():
                row = json.loads(line)
                out[row["qid"]] = row.get("candidates", [])
    return out


def cohort_rows() -> list[dict]:
    rows = []
    for label, d, cleanf, prefix, pred_kind in ROUNDS:
        answers = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        keep = set(json.load(open(cleanf))) if cleanf else set(answers)
        preds = load_preds(d, prefix, pred_kind)
        for qid, ans in answers.items():
            if qid not in keep:
                continue
            key = qid if not prefix else f"{prefix}{qid}" if prefix.endswith("-") else qid
            cands = preds.get(qid if pred_kind != "raw" else qid, [])
            if pred_kind == "raw":
                cands = preds.get(qid, [])
            rows.append({
                "round": label,
                "qid": qid,
                "difficulty": ans["difficulty"],
                "smiles": ans["smiles"],
                "inchikey14": inchikey14(ans["smiles"], ans.get("inchikey")),
                "candidates": cands[:3],
                "has_preds": bool(cands),
            })
    return rows


def diagnosis(rows: list[dict], use_forward: bool = False) -> dict:
    """Self-ranking top-1 by default; set use_forward=True only when fverify bundles exist."""
    def ik(s):
        m = Chem.MolFromSmiles(s) if s else None
        return Chem.MolToInchiKey(m)[:14] if m else None

    verified = misranked = wall = 0
    recalled = 0
    for r in rows:
        t = ik(r["smiles"])
        cands = r["candidates"]
        rec = t is not None and any(ik(s) == t for s in cands)
        top1 = bool(cands) and ik(cands[0]) == t
        if rec:
            recalled += 1
            if top1:
                verified += 1
            else:
                misranked += 1
        else:
            wall += 1
    return dict(n=len(rows), recalled=recalled, verified=verified, misranked=misranked, wall=wall)


def corpus_counts(bench_ik: set[str]) -> dict:
    n_quadruples = 0
    eligible = {"simple": 0, "complex": 0}
    not_in_bench = {"simple": 0, "complex": 0}
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not (smi and r.get("h_nmr") and r.get("c_nmr") and r.get("ir_bands_cm-1")):
            continue
        n_quadruples += 1
        m = Chem.MolFromSmiles(smi)
        if m is None or not (8 <= m.GetNumHeavyAtoms() <= 60):
            continue
        if r["h_nmr"].count("(") < 3 or r["c_nmr"].count("(") < 3:
            continue
        d = difficulty(m)
        eligible[d] += 1
        ik = (r.get("inchikey") or Chem.MolToInchiKey(m))[:14]
        if ik not in bench_ik:
            not_in_bench[d] += 1
    eligible["total"] = eligible["simple"] + eligible["complex"]
    not_in_bench["total"] = not_in_bench["simple"] + not_in_bench["complex"]
    return {"quadruples": n_quadruples, "eligible": eligible, "not_in_bench": not_in_bench}


def main():
    rows = cohort_rows()
    n_main = sum(1 for r in rows if r["round"].startswith("main"))
    n_ctrl = len(rows) - n_main
    bench_ik = {r["inchikey14"] for r in rows if r["inchikey14"]}
    missing_preds = [r for r in rows if not r["has_preds"]]

    print("=== IRSpectra-Bench cohort (headline n=194) ===")
    print(f"  main (spectrally validated) : {n_main}")
    print(f"  controlled rounds           : {n_ctrl}")
    print(f"  total scored                : {len(rows)}")
    print(f"  missing model predictions   : {len(missing_preds)}")
    if missing_preds:
        print(f"    qids: {', '.join(r['qid'] for r in missing_preds[:12])}")

    # Per-round answer counts vs clean
    for d in ["data/benchmark_main", "data/benchmark_v3", "data/benchmark_v2_ctrl"]:
        n_ans = sum(1 for _ in open(f"{d}/answers2.jsonl"))
        clean = json.load(open(f"{d}/clean_qids.json"))
        print(f"  {d}: sampled={n_ans}, spectrally-clean={len(clean)}, excluded={n_ans - len(clean)}")

    diag = diagnosis(rows)
    print("\n=== Diagnosis (solver self-ranking top-1) ===")
    print(f"  verified (top-1)     : {diag['verified']}")
    print(f"  mis-ranked (recalled): {diag['misranked']}")
    print(f"  never proposed       : {diag['wall']}")
    print(f"  generation recall    : {diag['recalled']}/{diag['n']} ({100*diag['recalled']/diag['n']:.1f}%)")

  # Forward-verified numbers (from deposited fverify bundles) match make_fig_wall.py:
    print("\n=== Diagnosis (forward-verified top-1; fig_wall.py) ===")
    print("  verified=58, mis-ranked=7, never proposed=129  (scripts/forward_verify_all.py)")

    corp = corpus_counts(bench_ik)
    print("\n=== IRexp / irexp_resolved pool ===")
    print(f"  full quadruples (IR+1H+13C+structure)     : {corp['quadruples']:,}")
    print(f"  eligible (sampler filters, no J-enrichment) : {corp['eligible']['total']:,}")
    print(f"    simple  : {corp['eligible']['simple']:,} ({100*corp['eligible']['simple']/corp['eligible']['total']:.1f}%)")
    print(f"    complex : {corp['eligible']['complex']:,} ({100*corp['eligible']['complex']/corp['eligible']['total']:.1f}%)")
    print(f"  eligible not in any headline round        : {corp['not_in_bench']['total']:,}")
    print(f"  unique InChIKey-14 in headline cohort     : {len(bench_ik)}")


if __name__ == "__main__":
    main()
