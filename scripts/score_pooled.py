#!/usr/bin/env python3
"""Honest pooled IRSpectra-Bench generation metrics (n=194 + expansion).

The pre-registration licenses pooling the expansion round with the locked n=194
cohort *after* the round is complete. This script is that pool: it re-derives
every count from the existing scorers (`scripts/score_main.py` for n=194;
InChIKey-14 against the expansion key + `predictions2.jsonl` for the 106).

The expansion answer key is withheld from the tree (Fable arm still incomplete).
This script reconstructs it only under /tmp by unique (formula, IR bands, ¹³C)
match against irexp_resolved — the same lost-vault recovery recorded as
deviation 4 — and never writes answers2.jsonl into the working tree.

Forward-verification has not been run on the expansion. This script therefore
reports **generation** top-1 / recall only for the pool. It does not invent
verification-precision or fig_wall segments.

  python scripts/score_pooled.py
  python scripts/score_pooled.py --stereo
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_main import STEREO, boot, fp, ik, load, metrics  # noqa: E402

GOLD = Path("data/irexp_resolved/irexp_resolved.jsonl.gz")
EXPAND = Path("data/benchmark_expand")
QUESTIONS = EXPAND / "questions2.jsonl"
PREDS = EXPAND / "predictions2.jsonl"
CLEAN = EXPAND / "clean_qids.json"
FLAGGED = ("R12", "R22", "R25", "R82", "R91")
VAULT = Path("/tmp/blind/_key/benchmark_expand.answers2.jsonl.withheld")
SIDECAR = Path("data/pooled_headline.json")

# Eligible-corpus stratum weight from scripts/corpus_reweight.py (28,988 records).
# Recomputed here only if --recompute-corpus is passed; otherwise frozen.
CORPUS_SIMPLE_W = 0.175  # 17.5% simple / 82.5% complex


def _norm_bands(bands):
    return tuple(round(float(x), 4) for x in (bands or []))


def reconstruct_expand_key(dest: Path) -> list[dict]:
    """Unique match of each committed question against irexp_resolved.

    Match key: (RDKit formula, IR band list, ¹³C string). Returns answer rows
    in qid order and writes them only to *dest* (outside the working tree).
    """
    qs = [json.loads(l) for l in QUESTIONS.open()]
    preds = {json.loads(l)["qid"] for l in PREDS.open()}
    if {q["qid"] for q in qs} != preds:
        raise SystemExit("questions2.jsonl qids do not match predictions2.jsonl")

    seen_prior = set()
    for af in Path("data").glob("benchmark*/answers*.jsonl"):
        if af.resolve() == dest.resolve():
            continue
        for line in af.open():
            seen_prior.add(json.loads(line)["inchikey"][:14])

    index = {}
    collisions = 0
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not (smi and r.get("c_nmr") and r.get("ir_bands_cm-1")):
            continue
        m = Chem.MolFromSmiles(smi)
        if m is None:
            continue
        formula = rdMolDescriptors.CalcMolFormula(m)
        key = (formula, _norm_bands(r["ir_bands_cm-1"]), r["c_nmr"])
        rec = {
            "smiles": Chem.MolToSmiles(m),
            "inchikey": r.get("inchikey") or Chem.MolToInchiKey(m),
            "heavy_atoms": m.GetNumHeavyAtoms(),
            "source_doi": r.get("source_doi"),
        }
        if key in index and index[key]["inchikey"][:14] != rec["inchikey"][:14]:
            collisions += 1
            index[key] = None  # mark non-unique
        elif key not in index:
            index[key] = rec

    rows = []
    unmatched = []
    ambiguous = []
    for q in qs:
        key = (q["formula"], _norm_bands(q["ir_bands_cm-1"]), q["c_nmr"])
        rec = index.get(key)
        if rec is None:
            if key in index:
                ambiguous.append(q["qid"])
            else:
                unmatched.append(q["qid"])
            continue
        ik14 = rec["inchikey"][:14]
        if ik14 in seen_prior:
            raise SystemExit(f"{q['qid']}: reconstructed InChIKey-14 collides with a prior round")
        rows.append({
            "qid": q["qid"],
            "smiles": rec["smiles"],
            "inchikey": rec["inchikey"],
            "difficulty": q["difficulty"],
            "heavy_atoms": rec["heavy_atoms"],
            "source_doi": rec.get("source_doi"),
        })

    if unmatched or ambiguous:
        raise SystemExit(f"key reconstruction failed: unmatched={unmatched} ambiguous={ambiguous}")
    if len(rows) != 106:
        raise SystemExit(f"expected 106 reconstructed answers, got {len(rows)}")
    n_simple = sum(1 for r in rows if r["difficulty"] == "simple")
    if n_simple != 53:
        raise SystemExit(f"strata drifted: simple={n_simple} (want 53)")

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"reconstructed {len(rows)} answers -> {dest}  "
          f"(gold-index collisions skipped: {collisions})")
    return rows


def expand_rows(answers: list[dict], clean_only: bool) -> list[tuple]:
    keep = set(json.load(open(CLEAN))) if clean_only else None
    preds = {json.loads(l)["qid"]: json.loads(l) for l in PREDS.open()}
    out = []
    for ans in answers:
        if keep is not None and ans["qid"] not in keep:
            continue
        out.append((ans, preds[ans["qid"]].get("candidates", [])))
    return out


def summarise(label: str, rows: list[dict], n_boot: int = 2000) -> dict:
    def rate(rs, key):
        return 100 * sum(r[key] for r in rs) / len(rs) if rs else 0

    out = {"label": label, "n": len(rows), "slices": {}}
    for slabel, sub in [("ALL", rows),
                        ("simple", [r for r in rows if r["diff"] == "simple"]),
                        ("complex", [r for r in rows if r["diff"] == "complex"])]:
        p, lo, hi = boot(sub, lambda s: rate(s, "top1"), n=n_boot)
        pr, rlo, rhi = boot(sub, lambda s: rate(s, "rec"), n=n_boot)
        n1 = sum(r["top1"] for r in sub)
        nr = sum(r["rec"] for r in sub)
        mt = sum(r["tani"] for r in sub) / len(sub) if sub else 0
        scaf = 100 * sum(r["tani"] >= 0.45 for r in sub) / len(sub) if sub else 0
        block = {
            "n": len(sub),
            "top1_n": n1,
            "top1_pct": p,
            "top1_ci": [lo, hi],
            "recall_n": nr,
            "recall_pct": pr,
            "recall_ci": [rlo, rhi],
            "scaffold_ge_0.45_pct": scaf,
            "mean_tanimoto": mt,
        }
        out["slices"][slabel] = block
        print(f"{label:18} {slabel:8} n={len(sub):3}  "
              f"top1 {n1}/{len(sub)} ({p:.1f}%) [{lo:.0f}-{hi:.0f}]   "
              f"recall {nr}/{len(sub)} ({pr:.1f}%) [{rlo:.0f}-{rhi:.0f}]   "
              f"scaffold(>=0.45) {scaf:.0f}%   meanTani {mt:.2f}")
    out["by_size"] = {}
    for b in ("<=15", "16-25", ">25"):
        sub = [r for r in rows if r["hac"] == b]
        if not sub:
            continue
        n1 = sum(r["top1"] for r in sub)
        nr = sum(r["rec"] for r in sub)
        out["by_size"][b] = {
            "n": len(sub), "top1_n": n1, "top1_pct": rate(sub, "top1"),
            "recall_n": nr, "recall_pct": rate(sub, "rec"),
        }
        print(f"{'':18} size {b:6} n={len(sub):3}  "
              f"top1 {n1}/{len(sub)} ({rate(sub, 'top1'):.1f}%)  "
              f"recall {nr}/{len(sub)} ({rate(sub, 'rec'):.1f}%)")
    return out


def reweight(pooled: dict, w_simple: float) -> dict:
    """Corpus-reweighted rates from pooled per-stratum accuracies. No invented CIs:
    bootstrap the stratum rates, then apply frozen corpus weights."""
    s = pooled["slices"]["simple"]
    c = pooled["slices"]["complex"]
    rng = random.Random(0)
    ns, nc = s["n"], c["n"]
    vs = [1] * s["top1_n"] + [0] * (ns - s["top1_n"])
    vc = [1] * c["top1_n"] + [0] * (nc - c["top1_n"])
    rs = [1] * s["recall_n"] + [0] * (ns - s["recall_n"])
    rc = [1] * c["recall_n"] + [0] * (nc - c["recall_n"])
    w = w_simple

    def corpus_rate(a, b, na, nb, n=20000):
        pt = w * sum(a) / na + (1 - w) * sum(b) / nb
        bs = sorted(w * sum(a[rng.randrange(na)] for _ in range(na)) / na
                    + (1 - w) * sum(b[rng.randrange(nb)] for _ in range(nb)) / nb
                    for _ in range(n))
        return 100 * pt, 100 * bs[int(0.025 * n)], 100 * bs[int(0.975 * n)]

    t1, tlo, thi = corpus_rate(vs, vc, ns, nc)
    rec, rlo, rhi = corpus_rate(rs, rc, ns, nc)
    out = {
        "corpus_simple_weight": w,
        "top1_pct": t1, "top1_ci": [tlo, thi],
        "recall_pct": rec, "recall_ci": [rlo, rhi],
    }
    print(f"corpus-reweighted   top1 {t1:.1f}% [{tlo:.0f}-{thi:.0f}]   "
          f"recall {rec:.1f}% [{rlo:.0f}-{rhi:.0f}]   "
          f"(w_simple={w:.3f})")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=str(VAULT),
                    help="where to write/read the reconstructed expansion key (outside the tree)")
    ap.add_argument("--sidecar", default=str(SIDECAR))
    ap.add_argument("--stereo", action="store_true",
                    help="full InChIKey (score_main also reads this flag from argv)")
    args, _unknown = ap.parse_known_args()
    random.seed(0)

    layer = ("FULL InChIKey (stereochemistry-sensitive)" if STEREO
             else "InChIKey connectivity (constitution)")
    print(f"scoring layer: {layer}\n")

    key_path = Path(args.key)
    if key_path.exists():
        answers = [json.loads(l) for l in key_path.open()]
        print(f"using existing key at {key_path} ({len(answers)} rows)")
    else:
        answers = reconstruct_expand_key(key_path)

    # Never copy the key into the round directory from this script.
    if (EXPAND / "answers2.jsonl").exists():
        raise SystemExit("data/benchmark_expand/answers2.jsonl is in the working tree; "
                         "withhold it before committing. This scorer reads the vault only.")

    n194 = metrics(load())
    exp106 = metrics(expand_rows(answers, clean_only=False))
    exp101 = metrics(expand_rows(answers, clean_only=True))
    if len(exp106) != 106 or len(exp101) != 101:
        raise SystemExit(f"expansion sizes drifted: all={len(exp106)} clean={len(exp101)}")
    clean = set(json.load(open(CLEAN)))
    flagged_got = sorted(q["qid"] for q in answers if q["qid"] not in clean)
    if flagged_got != sorted(FLAGGED):
        raise SystemExit(f"flagged qids drifted: {flagged_got} vs {list(FLAGGED)}")

    pooled300 = n194 + exp106
    pooled295 = n194 + exp101

    blocks = [
        summarise("n=194 (locked)", n194),
        summarise("expansion all", exp106),
        summarise("expansion clean", exp101),
        summarise("pooled n=300", pooled300),
        summarise("pooled n=295 HEADLINE", pooled295),
    ]

    print()
    rew = reweight(blocks[-1], CORPUS_SIMPLE_W)

    sidecar = {
        "date": "2026-09-16",
        "scoring_layer": "InChIKey-14 constitution" if not STEREO else "full InChIKey",
        "headline": "pooled n=295 (194 + 101 validate-clean expansion)",
        "headline_excludes_flagged": True,
        "flagged_qids": list(FLAGGED),
        "flagged_reason": "13C-overread; validate_benchmark.py before scoring",
        "forward_verify_expansion": "not run",
        "fable_expansion": "68/106 deposited; not scored; not pooled",
        "blocks": blocks,
        "corpus_reweighted_headline_n295": rew,
        "fig_wall": {
            "status": "NOT rebuilt",
            "reason": "scripts/make_fig_wall.py reads data/diagnosis.json from "
                      "scripts/forward_verify_all.py. That sidecar is n=194 "
                      "(58/7/129). Expansion joins only when data/fverify_expand*/ "
                      "exists; it does not. Do not invent pooled verified/misranked/wall.",
            "current_diagnosis_json": {
                "n": 194, "verified": 58, "misranked": 7, "wall": 129, "recalled": 65,
                "self_ranked": 55,
            },
            "to_regenerate": [
                "Run scripts/forward_verify_main.py on data/benchmark_expand (blind 13C campaign)",
                "Deposit data/fverify_expand/ {candidates.jsonl, anon_map.json, raw/}",
                "Re-run scripts/forward_verify_all.py → data/diagnosis.json",
                "Re-run scripts/make_fig_wall.py → docs/figures/fig_wall.png",
            ],
        },
        "fig1_difficulty": {
            "status": "NOT rebuilt",
            "reason": "scripts/make_figures.py calls score_main.load() which is still "
                      "the n=194 union. It has no pooled-cohort switch. Rebuild after "
                      "score_main.load() includes the expansion (key must be present).",
        },
    }
    sidecar_path = Path(args.sidecar)
    if STEREO and sidecar_path == SIDECAR:
        sidecar_path = Path("data/pooled_headline_stereo.json")
    sidecar["scoring_layer"] = ("full InChIKey (stereochemistry-sensitive)" if STEREO
                                else "InChIKey-14 constitution")
    sidecar_path.write_text(json.dumps(sidecar, indent=1) + "\n")
    print(f"\nwrote {sidecar_path}")
    print("expansion key remains outside the working tree at", key_path)
    if Path("data/benchmark_expand/answers2.jsonl").exists():
        raise SystemExit("answers2.jsonl leaked into the tree")


if __name__ == "__main__":
    main()
