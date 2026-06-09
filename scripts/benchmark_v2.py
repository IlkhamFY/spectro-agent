#!/usr/bin/env python3
"""
Benchmark v2 -- methodology-aligned to Anthropic's "Making Claude a Chemist"
inverse task, on real IRexp data.

Differences vs the v1 pilot, each chosen to match their protocol so the
comparison is fair:
  * stratified  : "simple" (single-ring / two separate fragments) vs "complex"
                  (fused rings / spiro / bridgehead / large) -- their 8-vs-7 split.
  * J-enriched  : re-fetch each compound's source paper and use the RAW 1H NMR
                  string (multiplicities + J couplings + assignments) instead of
                  the J-stripped spectro format -- closer to what a chemist (and
                  their paste-from-paper setup) actually sees.
  * top-3 score : the solver returns up to 3 ranked candidate SMILES per compound;
                  "recovered" = the true constitution appears among the 3
                  (their "up to three ranked candidate structures"). We also keep
                  the strict top-1 exact metric for continuity with v1.

We do NOT give the complex set a starting-material hint (their complex 7 did get
one) -- we cannot reconstruct real reaction precursors from the data, so the
complex numbers here test the harder, hint-free regime and are not directly
comparable to their complex results. This is stated in the report.

    python scripts/benchmark_v2.py sample2 --n 20 --seed 23
    #   solver writes data/benchmark_v2/predictions2.jsonl as
    #   {"qid": "...", "candidates": ["smiles1","smiles2","smiles3"]}
    python scripts/benchmark_v2.py score2
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import urllib.request
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors, AllChem, DataStructs
RDLogger.DisableLog("rdApp.*")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from spectro_scraper.extract import extract_records                    # noqa: E402
from spectro_scraper.normalize import to_spectro_h, to_spectro_c        # noqa: E402

import glob
GOLD = Path("data/irexp_resolved/irexp_resolved.jsonl.gz")
BDIR = Path("data/benchmark_v2")        # overridden by --outdir
Q = A = P = None                        # set in _paths()


def _paths(outdir: str):
    global BDIR, Q, A, P
    BDIR = Path(outdir)
    Q, A, P = BDIR / "questions2.jsonl", BDIR / "answers2.jsonl", BDIR / "predictions2.jsonl"
S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
CACHE = Path("data/cache/pmc_text")


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


def s3_txt(num: str) -> str:
    p = CACHE / f"{num}.txt"
    if p.exists() and p.stat().st_size > 0:
        return p.read_text(errors="replace")
    for v in (1, 2):
        try:
            req = urllib.request.Request(f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt",
                                         headers={"User-Agent": "spectro-agent"})
            t = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            CACHE.mkdir(parents=True, exist_ok=True); p.write_text(t)
            return t
        except Exception:
            continue
    return ""


def raw_1h_for(gold: dict) -> str | None:
    """Re-extract the source paper and return the RAW 1H NMR (with J) for the
    record whose spectro-format + IR match this gold record."""
    sd = str(gold.get("source_doi") or "")
    if not sd.startswith("PMC:"):
        return None
    txt = s3_txt(sd.split(":", 1)[1])
    if not txt:
        return None
    key = (gold.get("h_nmr") or "", gold.get("c_nmr") or "",
           tuple(gold.get("ir_bands_cm-1") or []))
    for rec in extract_records(txt):
        if not rec.ir_bands:
            continue
        if (to_spectro_h(rec) or "", to_spectro_c(rec) or "",
                tuple(rec.ir_bands)) == key:
            return rec.h_nmr            # raw payload with multiplicities + J
    return None


def sample2(n: int, seed: int):
    random.seed(seed)
    pool = {"simple": [], "complex": []}
    # exclude every compound already revealed in ANY prior benchmark run
    seen = set()
    for af in glob.glob("data/benchmark*/answers*.jsonl"):
        if Path(af) == A:
            continue
        for l in open(af):
            seen.add(json.loads(l)["inchikey"][:14])
    print(f"excluding {len(seen)} previously-seen compounds from the pool", flush=True)
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not (smi and r.get("h_nmr") and r.get("c_nmr") and r.get("ir_bands_cm-1")):
            continue
        m = Chem.MolFromSmiles(smi)
        if m is None or not (8 <= m.GetNumHeavyAtoms() <= 60):
            continue
        ik = r.get("inchikey") or Chem.MolToInchiKey(m)
        if ik[:14] in seen:
            continue
        if r["h_nmr"].count("(") < 3 or r["c_nmr"].count("(") < 3:
            continue
        seen.add(ik[:14])
        pool[difficulty(m)].append((r, m, ik))
    BDIR.mkdir(parents=True, exist_ok=True)
    chosen = []
    for diff in ("simple", "complex"):
        random.shuffle(pool[diff])
        picked, i = [], 0
        # take records whose raw 1H (with J) we can recover, up to n//2 each
        while len(picked) < n // 2 and i < len(pool[diff]):
            r, m, ik = pool[diff][i]; i += 1
            raw = raw_1h_for(r)
            if raw and "J" in raw:                  # require genuine J info
                picked.append((r, m, ik, raw))
        chosen += [(*x, diff) for x in picked]
    random.shuffle(chosen)

    with Q.open("w") as q, A.open("w") as a:
        for i, (r, m, ik, raw, diff) in enumerate(chosen, 1):
            qid = f"R{i:02d}"
            q.write(json.dumps({"qid": qid, "difficulty": diff,
                                "formula": rdMolDescriptors.CalcMolFormula(m),
                                "ir_bands_cm-1": r["ir_bands_cm-1"],
                                "h_nmr": raw, "c_nmr": r["c_nmr"]},
                               ensure_ascii=False) + "\n")
            a.write(json.dumps({"qid": qid, "smiles": Chem.MolToSmiles(m),
                                "inchikey": ik, "difficulty": diff,
                                "heavy_atoms": m.GetNumHeavyAtoms()},
                               ensure_ascii=False) + "\n")
    ns = sum(1 for c in chosen if c[-1] == "simple")
    print(f"wrote {len(chosen)} questions ({ns} simple, {len(chosen)-ns} complex) -> {Q}")
    print("\n================  QUESTIONS v2 (top-3 candidates, blind)  ================")
    for line in Q.open():
        d = json.loads(line)
        print(f"\n[{d['qid']}]  ({d['difficulty']})  formula {d['formula']}")
        print(f"  IR cm-1 : {d['ir_bands_cm-1']}")
        print(f"  1H NMR  : {d['h_nmr']}")
        print(f"  13C NMR : {d['c_nmr']}")


def _fp(m):
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)


def score2():
    ans = {json.loads(l)["qid"]: json.loads(l) for l in A.open()}
    preds = {json.loads(l)["qid"]: json.loads(l) for l in P.open()}
    by = {"simple": [0, 0, 0, 0.0], "complex": [0, 0, 0, 0.0]}   # n, recovered, top1, sumBestTani
    rows = []
    for qid, a in sorted(ans.items()):
        tmol = Chem.MolFromSmiles(a["smiles"]); tik = a["inchikey"][:14]
        cands = (preds.get(qid) or {}).get("candidates", [])[:3]
        hit = top1 = False; best = 0.0; bestsmi = ""
        for rank, smi in enumerate(cands):
            pm = Chem.MolFromSmiles(smi) if smi else None
            if pm is None:
                continue
            match = Chem.MolToInchiKey(pm)[:14] == tik
            t = DataStructs.TanimotoSimilarity(_fp(tmol), _fp(pm))
            if t > best:
                best, bestsmi = t, smi
            if match:
                hit = True
                if rank == 0:
                    top1 = True
        d = a["difficulty"]; b = by[d]
        b[0] += 1; b[1] += int(hit); b[2] += int(top1); b[3] += best
        rows.append((qid, d, hit, top1, round(best, 3), bestsmi[:42]))

    print(f"\n=== BENCHMARK v2  (formula + IR + J-rich 1H + 13C, top-3 candidates) ===\n")
    print(f"{'qid':4} {'diff':8} {'recov':6} {'top1':5} {'bestTani':8} best-candidate")
    for qid, d, hit, top1, t, smi in rows:
        print(f"{qid:4} {d:8} {'YES' if hit else '·':6} {'YES' if top1 else '·':5} {t:<8} {smi}")
    N = sum(b[0] for b in by.values())
    R = sum(b[1] for b in by.values()); T1 = sum(b[2] for b in by.values())
    print(f"\noverall recovered (top-3): {R}/{N} ({100*R//N}%)   top-1 exact: {T1}/{N} ({100*T1//N}%)")
    for d in ("simple", "complex"):
        n_, r_, t1_, st = by[d]
        if n_:
            print(f"  {d:8}: recovered {r_}/{n_} ({100*r_//n_}%)  "
                  f"top1 {t1_}/{n_} ({100*t1_//n_}%)  meanBestTani {st/n_:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample2"); s.add_argument("--n", type=int, default=20); s.add_argument("--seed", type=int, default=23)
    s.add_argument("--outdir", default="data/benchmark_v2")
    sc = sub.add_parser("score2"); sc.add_argument("--outdir", default="data/benchmark_v2")
    a = ap.parse_args()
    _paths(a.outdir)
    sample2(a.n, a.seed) if a.cmd == "sample2" else score2()
