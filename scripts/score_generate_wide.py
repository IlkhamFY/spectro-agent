#!/usr/bin/env python3
"""Reproduce Table 6: generate-wide vs the original candidate pool, on the same 60 compounds.

§5.3's headline (top-1 23% -> 26% -> 30%) previously had no released scorer: the artifacts
were in the repository but nothing regenerated the table from them, so a reader had to take
the numbers on trust. This closes that gap.

Inputs, all released:
  data/fverify/candidates.jsonl   original candidates (<=3/compound) + observed 13C
  data/fverify/raw/*.json         forward-predicted 13C for those, keyed by anon id
  data/fverify/anon_map.json      smiles -> anon id
  data/gw/raw/*.json              generate-wide proposals (<=6/compound), keyed "V3-R01"
  data/fverify2/raw/*.json        forward-predicted 13C for the new wide candidates
  data/fverify2/anon_map2.json    smiles -> anon id for those

Scoring is identical to scripts/forward_verify.py: candidates are re-ranked by the
symmetric chamfer distance in scripts/specmetrics.py between predicted and observed 13C.

  python3 scripts/score_generate_wide.py
"""
import glob, json, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specmetrics import chamfer, ik14
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")


def canon(smi):
    """Canonical SMILES, so predictions match candidates across files.

    The generate-wide proposals and the forward-prediction anon map were written by
    different runs and spell the same molecule differently (e.g. Cc1ccc(cc1)S(=O)... vs
    Cc1ccc(S(=O)...)cc1). Matching on the raw string silently loses ~94% of the
    predictions and understates the result; match on the canonical form.
    """
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None

CAND = "data/fverify/candidates.jsonl"


def _load_preds(rawglob, mapfile):
    """smiles -> predicted 13C shift list."""
    amap = json.load(open(mapfile))
    pred = {}
    for f in glob.glob(rawglob):
        pred.update(json.load(open(f)))
    return {canon(smi): pred[aid] for smi, aid in amap.items()
            if aid in pred and canon(smi)}


def _qid_key(dirname, qid):
    """data/gw/raw keys are CT-R01 (v2_ctrl) and V3-R01 (v3); candidates carry dir + qid."""
    tag = "V3" if dirname.endswith("v3") else "CT"
    return f"{tag}-{qid}"


def _gold():
    """qid -> reference InChIKey-14, read from the benchmark answer keys.

    Ground truth must come from the answer key, not from the original candidate list:
    for the 41 compounds the solver never proposed correctly, the original pool contains
    no true candidate, so deriving truth from it would make it impossible for a
    generate-wide candidate to ever count as recovered -- exactly the compounds this
    experiment is about.
    """
    g = {}
    for d in ("data/benchmark_v3", "data/benchmark_v2_ctrl"):
        for line in open(f"{d}/answers2.jsonl"):
            a = json.loads(line)
            g[(d, a["qid"])] = a["inchikey"][:14]
    return g


def main():
    rows = [json.loads(l) for l in open(CAND)]
    pred = _load_preds("data/fverify/raw/*.json", "data/fverify/anon_map.json")
    pred.update(_load_preds("data/fverify2/raw/*.json", "data/fverify2/anon_map2.json"))

    wide = {}
    for f in glob.glob("data/gw/raw/*.json"):
        for k, v in json.load(open(f)).items():
            wide.setdefault(k, []).extend(v)

    gold = _gold()
    comps = {}
    for r in rows:
        comps.setdefault((r["dir"], r["qid"]), []).append(r)

    def evaluate(pool_for):
        """pool_for(dir,qid,orig) -> list of (smiles, is_true); returns the four numbers."""
        n = recall = ver1 = cond_hit = cond_n = 0
        for (d, q), orig in comps.items():
            obs = orig[0]["obs_c13"]
            cands = pool_for(d, q, orig)
            n += 1
            has = any(t for _, t in cands)
            recall += has
            scored = [(chamfer(pred.get(canon(s)), obs) if pred.get(canon(s)) else 999.0,
                       s, t) for s, t in cands]
            best = min(scored, key=lambda x: x[0])
            ver1 += best[2]
            if has:
                cond_n += 1; cond_hit += best[2]
        return n, recall, ver1, cond_hit, cond_n

    def orig_pool(d, q, orig):
        return [(c["smiles"], c["is_true"]) for c in orig]

    def wide_pool(d, q, orig):
        """Original candidates pooled with the generate-wide proposals, truth from the key."""
        g = gold.get((d, q))
        seen = {c["smiles"]: c["is_true"] for c in orig}
        for smi in wide.get(_qid_key(d, q), []):
            if smi not in seen:
                seen[smi] = (ik14(smi) == g) if g else False
        return list(seen.items())

    n, r0, v0, c0, cn0 = evaluate(orig_pool)
    _, r1, v1, c1, cn1 = evaluate(wide_pool)
    self1 = sum(1 for cs in comps.values()
                if sorted(cs, key=lambda c: c["self_rank"])[0]["is_true"])

    pct = lambda a, b: f"{a}/{b} ({100*a//b}%)"   # floor, matching the paper's tables
    print(f"GENERATE-WIDE vs ORIGINAL — forward-verification on the same {n} compounds\n")
    print(f"{'':<44}{'original':>14}{'generate-wide':>16}")
    print(f"{'recall (true structure in candidate set)':<44}{pct(r0,n):>14}{pct(r1,n):>16}")
    print(f"{'forward-verified top-1':<44}{pct(v0,n):>14}{pct(v1,n):>16}")
    print(f"{'self-rank top-1 (baseline)':<44}{pct(self1,n):>14}{'-':>16}")
    print(f"{'verification precision (cond. on recall)':<44}"
          f"{pct(c0,cn0):>14}{pct(c1,cn1):>16}")
    print("\nRe-ranking uses the symmetric chamfer distance of scripts/specmetrics.py.")
    print("Compare against the recorded run in data/fverify2/results.txt.")


if __name__ == "__main__":
    main()
