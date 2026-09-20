#!/usr/bin/env python3
"""
Score +106 fverify (key only under /tmp) and write the unified n=500 wall.

n=500 = locked 194 (diagnosis.json) + all Opus +106 + expand-500 200-qid cut.
Integers come from this script. Does not write answers2.jsonl into the tree,
does not write is_true into committed candidates.jsonl, and does not run
forward_verify_all.py (n=194 sidecar stays locked).

  python scripts/fverify_n500_wall.py
"""
import glob
import gzip
import json
import os
import re
import sys
from collections import defaultdict

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

GOLD = "data/irexp_resolved/irexp_resolved.jsonl.gz"
VAULT = "/tmp/blind/_key"
WALL = "data/fverify_n500/WALL_n500.md"
DIAG = "data/diagnosis.json"
HEAD200 = "data/benchmark_expand_500/headline500_expand200_qids.json"

# Committed generation sanity (HEADLINE_n500 / STATUS). Abort if reconstruction misses.
SANITY = {
    ("expand", "gen_top1"): 63,
    ("expand", "gen_recall"): 68,
    ("expand", "n"): 106,
    ("expand500", "gen_top1"): 129,
    ("expand500", "gen_recall"): 138,
    ("expand500", "n"): 230,
    ("expand500_200", "gen_top1"): 109,
    ("expand500_200", "gen_recall"): 116,
    ("expand500_200", "n"): 200,
    ("expand500", "fv_verify"): 103,
    ("expand500", "fv_recall"): 138,
    ("n194", "verified"): 58,
    ("n194", "misranked"): 7,
    ("n194", "wall"): 129,
}


def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToInchiKey(m)[:14] if m else None


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def formula(smi):
    m = Chem.MolFromSmiles(smi)
    return rdMolDescriptors.CalcMolFormula(m) if m else None


def q_c13(s):
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", s or ""))


def g_c13(s):
    if "(" in (s or ""):
        return q_c13(s)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", s or ""))


def ir_key(bands):
    return tuple(round(float(x), 1) for x in (bands or []))


def chamfer(pred, obs):
    if not pred or not obs:
        return 999.0
    a = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    b = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (a + b) / 2


def prior_ik14():
    seen = set()
    for af in glob.glob("data/benchmark*/answers*.jsonl"):
        if os.path.basename(os.path.dirname(af)) in ("benchmark_expand", "benchmark_expand_500"):
            raise SystemExit(f"refusing: {af} is in the tree")
        for l in open(af):
            seen.add(json.loads(l)["inchikey"][:14])
    return seen


def index_gold():
    by = defaultdict(list)
    for line in gzip.open(GOLD, "rt"):
        r = json.loads(line)
        smi = r.get("smiles")
        if not smi:
            continue
        m = Chem.MolFromSmiles(smi)
        if m is None:
            continue
        f = rdMolDescriptors.CalcMolFormula(m)
        rec = {
            "smiles": Chem.MolToSmiles(m),
            "inchikey": r.get("inchikey") or Chem.MolToInchiKey(m),
            "heavy_atoms": m.GetNumHeavyAtoms(),
            "source_doi": r.get("source_doi"),
        }
        by[(f, ir_key(r.get("ir_bands_cm-1")), g_c13(r.get("c_nmr")))].append(rec)
    return by


def reconstruct(qpath, gold, prior, dest):
    qs = [json.loads(l) for l in open(qpath)]
    rows = []
    collide = 0
    for q in qs:
        key = (q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr")))
        hits = gold.get(key, [])
        if len(hits) != 1:
            raise SystemExit(f"{qpath} {q['qid']}: expected 1 gold hit, got {len(hits)}")
        h = hits[0]
        if h["inchikey"][:14] in prior:
            collide += 1
        rows.append({
            "qid": q["qid"],
            "smiles": h["smiles"],
            "inchikey": h["inchikey"],
            "difficulty": q.get("difficulty"),
            "heavy_atoms": h["heavy_atoms"],
            "source_doi": h.get("source_doi"),
        })
    if collide:
        raise SystemExit(f"{qpath}: {collide} prior-round InChIKey-14 collisions")
    os.makedirs(os.path.dirname(dest), mode=0o700, exist_ok=True)
    with open(dest, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return {r["qid"]: r for r in rows}


def gen_score(pred_path, ans):
    preds = {json.loads(l)["qid"]: json.loads(l) for l in open(pred_path)}
    top1 = recall = n = 0
    per = {}
    for qid, a in ans.items():
        n += 1
        tik = a["inchikey"][:14]
        cands = (preds.get(qid) or {}).get("candidates", [])[:3]
        hits = []
        for smi in cands:
            if ik14(smi) == tik:
                hits.append(True)
            else:
                hits.append(False)
        rec = any(hits)
        s1 = bool(hits) and hits[0]
        recall += rec
        top1 += s1
        per[qid] = {"gen_recall": rec, "gen_top1": s1}
    return {"n": n, "top1": top1, "recall": recall, "per": per}


def fv_score(bundle, ans, keep=None):
    rows = [json.loads(l) for l in open(f"{bundle}/candidates.jsonl")]
    amap = json.load(open(f"{bundle}/anon_map.json"))
    pred = {}
    for f in sorted(glob.glob(f"{bundle}/raw/*.json")):
        pred.update(json.load(open(f)))
    if keep is not None:
        rows = [r for r in rows if r["qid"] in keep]
    missing = [s for s in {r["smiles"] for r in rows} if not pred.get(amap.get(s))]
    comps = {}
    for r in rows:
        r = dict(r)
        r["is_true"] = ik14(r["smiles"]) == ans[r["qid"]]["inchikey"][:14]
        comps.setdefault(r["qid"], []).append(r)
    recs = []
    for qid, cands in comps.items():
        obs = cands[0]["obs_c13"]
        for c in cands:
            c["pred"] = pred.get(amap.get(c["smiles"]))
            c["dist"] = chamfer(c["pred"], obs) if c["pred"] else 999.0
        has = any(c["is_true"] for c in cands)
        s = sorted(cands, key=lambda c: c["self_rank"])[0]["is_true"]
        v = min(cands, key=lambda c: c["dist"])["is_true"]
        recs.append({
            "qid": qid,
            "n_cand": len(cands),
            "recall": has,
            "self": s,
            "verify": v,
            "predicted": any(c["pred"] for c in cands),
            "class": ("never-proposed" if not has
                      else ("verified" if v else "misranked")),
        })
    n = len(recs)
    ceil = sum(r["recall"] for r in recs)
    self1 = sum(r["self"] for r in recs)
    ver1 = sum(r["verify"] for r in recs)
    cond = [r for r in recs if r["recall"]]
    multi = [r for r in cond if r["n_cand"] > 1]
    footer = (
        f"forward predictions loaded: {len(pred)}/{len(amap)} unique SMILES\n"
        f"compounds: {n}\n"
        f"  recall (true in candidate set): {ceil}/{n} ({100*ceil/n:.0f}%)\n"
        f"  top-1, solver self-rank:        {self1}/{n} ({100*self1/n:.0f}%)\n"
        f"  top-1, forward-verified rerank: {ver1}/{n} ({100*ver1/n:.0f}%)\n"
        f"  conditional on recall (n={len(cond)}): self {sum(r['self'] for r in cond)}/{len(cond)} "
        f"({100*sum(r['self'] for r in cond)/len(cond):.0f}%) | verify "
        f"{sum(r['verify'] for r in cond)}/{len(cond)} "
        f"({100*sum(r['verify'] for r in cond)/len(cond):.0f}%)\n"
        f"  multi-candidate only  (n={len(multi)}): self {sum(r['self'] for r in multi)}/{len(multi)} "
        f"| verify {sum(r['verify'] for r in multi)}"
    )
    wall = {
        "n": n,
        "verified": sum(r["class"] == "verified" for r in recs),
        "misranked": sum(r["class"] == "misranked" for r in recs),
        "wall": sum(r["class"] == "never-proposed" for r in recs),
        "recalled": ceil,
        "self_ranked": self1,
        "verify_top1": ver1,
        "missing_preds": len(missing),
    }
    assert wall["verified"] + wall["misranked"] + wall["wall"] == n
    return wall, recs, footer, missing


def demand(label, got, want):
    if got != want:
        raise SystemExit(f"sanity fail {label}: got {got} want {want}")


def main():
    for p in ("data/benchmark_expand/answers2.jsonl",
              "data/benchmark_expand_500/answers2.jsonl"):
        if os.path.exists(p):
            raise SystemExit(f"refusing: {p} is present")

    inv_need = 0
    amap = json.load(open("data/fverify_expand/anon_map.json"))
    pred = {}
    for f in glob.glob("data/fverify_expand/raw/*.json"):
        pred.update(json.load(open(f)))
    for smi, aid in amap.items():
        v = pred.get(aid)
        if not (isinstance(v, list) and v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)):
            inv_need += 1
    if inv_need:
        raise SystemExit(f"+106 fverify incomplete: {inv_need} SMILES lack 13C")

    gold = index_gold()
    prior = prior_ik14()
    os.makedirs(VAULT, mode=0o700, exist_ok=True)
    a106 = reconstruct("data/benchmark_expand/questions2.jsonl", gold, prior,
                       f"{VAULT}/benchmark_expand.answers2.jsonl.withheld")
    a500 = reconstruct("data/benchmark_expand_500/questions2.jsonl", gold, prior,
                       f"{VAULT}/benchmark_expand_500.answers2.jsonl.withheld")
    overlap = {a["inchikey"][:14] for a in a106.values()} & {a["inchikey"][:14] for a in a500.values()}
    if overlap:
        raise SystemExit(f"+106 vs expand-500 InChIKey-14 overlap: {len(overlap)}")

    g106 = gen_score("data/benchmark_expand/predictions2.jsonl", a106)
    g500 = gen_score("data/benchmark_expand_500/predictions2.jsonl", a500)
    cut = set(json.load(open(HEAD200)))
    g200 = gen_score("data/benchmark_expand_500/predictions2.jsonl",
                     {q: a500[q] for q in cut})
    demand("+106 gen n", g106["n"], SANITY[("expand", "n")])
    demand("+106 gen top1", g106["top1"], SANITY[("expand", "gen_top1")])
    demand("+106 gen recall", g106["recall"], SANITY[("expand", "gen_recall")])
    demand("e500 gen n", g500["n"], SANITY[("expand500", "n")])
    demand("e500 gen top1", g500["top1"], SANITY[("expand500", "gen_top1")])
    demand("e500 gen recall", g500["recall"], SANITY[("expand500", "gen_recall")])
    demand("e500-200 gen n", g200["n"], SANITY[("expand500_200", "n")])
    demand("e500-200 gen top1", g200["top1"], SANITY[("expand500_200", "gen_top1")])
    demand("e500-200 gen recall", g200["recall"], SANITY[("expand500_200", "gen_recall")])

    w106, rec106, foot106, miss106 = fv_score("data/fverify_expand", a106)
    w230, rec230, foot230, miss230 = fv_score("data/fverify_expand_500", a500)
    w200, rec200, foot200, miss200 = fv_score("data/fverify_expand_500", a500, keep=cut)
    if miss106 or miss230 or miss200:
        raise SystemExit(f"missing 13C: +106 {len(miss106)} e500 {len(miss230)} cut200 {len(miss200)}")
    demand("e500 fv verify", w230["verify_top1"], SANITY[("expand500", "fv_verify")])
    demand("e500 fv recall", w230["recalled"], SANITY[("expand500", "fv_recall")])

    d194 = json.load(open(DIAG))
    demand("n194 verified", d194["verified"], SANITY[("n194", "verified")])
    demand("n194 misranked", d194["misranked"], SANITY[("n194", "misranked")])
    demand("n194 wall", d194["wall"], SANITY[("n194", "wall")])
    if d194["n"] != 194:
        raise SystemExit(f"diagnosis.json n={d194['n']}, want 194")

    arms = {
        "locked_194": {"n": 194, "verified": d194["verified"],
                       "misranked": d194["misranked"], "wall": d194["wall"],
                       "recalled": d194["recalled"], "self_ranked": d194["self_ranked"],
                       "verify_top1": d194["verified"]},
        "plus_106": w106,
        "expand500_200": w200,
    }
    n500 = {
        "n": 500,
        "verified": arms["locked_194"]["verified"] + w106["verified"] + w200["verified"],
        "misranked": arms["locked_194"]["misranked"] + w106["misranked"] + w200["misranked"],
        "wall": arms["locked_194"]["wall"] + w106["wall"] + w200["wall"],
    }
    n500["recalled"] = n500["verified"] + n500["misranked"]
    assert n500["verified"] + n500["misranked"] + n500["wall"] == 500

    os.makedirs("data/fverify_expand", exist_ok=True)
    open("data/fverify_expand/results.txt", "w").write(
        "# official chamfer arithmetic (forward_verify_main.py score()) — +106\n"
        "# is_true filled under /tmp only; committed candidates.jsonl unchanged.\n"
        "# prep was not run (would rewrite the keyless anon_map / fbatches).\n\n"
        + foot106 + "\n"
    )

    body = f"""# WALL n=500

Script: `scripts/fverify_n500_wall.py`. Integers below are from that run.
Keys reconstructed by unique (formula, IR, ¹³C) match vs
`irexp_resolved.jsonl.gz` into `{VAULT}` only (106/106 and 230/230 unique;
0 prior-round InChIKey-14 collisions; 0 +106↔expand-500 collisions).
Committed `candidates.jsonl` files still omit `is_true`.
`answers2.jsonl` is **not** in the tree.

The paper may cite an n=500 fverify wall **only after this file exists**.

Classification (same as `scripts/forward_verify_all.py` sidecar):

- **verified** — true structure recalled and ranked first by chamfer
- **misranked** — recalled, but a distractor ranked first
- **never-proposed** — true structure not in the candidate set (generation wall)

## n=500 wall

| arm | n | verified | misranked | never-proposed |
|---|---:|---:|---:|---:|
| locked 194 (`data/diagnosis.json`) | 194 | **{arms['locked_194']['verified']}** | **{arms['locked_194']['misranked']}** | **{arms['locked_194']['wall']}** |
| Opus +106 | 106 | **{w106['verified']}** | **{w106['misranked']}** | **{w106['wall']}** |
| expand-500 200-qid cut | 200 | **{w200['verified']}** | **{w200['misranked']}** | **{w200['wall']}** |
| **n=500** | **500** | **{n500['verified']}** | **{n500['misranked']}** | **{n500['wall']}** |

Addition check: {arms['locked_194']['verified']}+{w106['verified']}+{w200['verified']} = {n500['verified']};
{arms['locked_194']['misranked']}+{w106['misranked']}+{w200['misranked']} = {n500['misranked']};
{arms['locked_194']['wall']}+{w106['wall']}+{w200['wall']} = {n500['wall']}.
{n500['verified']}+{n500['misranked']}+{n500['wall']} = 500.

Recalled (verified + misranked) = **{n500['recalled']}/500**.

## +106 fverify (verbatim score footer)

```
{foot106}
```

## expand-500 200-cut fverify (verbatim score footer)

```
{foot200}
```

## Sanity (must match committed generation / expand-500 fverify)

| check | script | committed |
|---|---|---|
| +106 generation top-1 / recall | {g106['top1']}/{g106['n']} / {g106['recall']}/{g106['n']} | 63/106 / 68/106 |
| expand-500 generation top-1 / recall | {g500['top1']}/{g500['n']} / {g500['recall']}/{g500['n']} | 129/230 / 138/230 |
| expand-500 200-cut generation | {g200['top1']}/{g200['n']} / {g200['recall']}/{g200['n']} | 109/200 / 116/200 |
| expand-500 fverify verify / recall (all 230) | {w230['verify_top1']}/{w230['n']} / {w230['recalled']}/{w230['n']} | 103/230 / 138/230 |
| locked 194 wall | {d194['verified']}/{d194['misranked']}/{d194['wall']} | 58/7/129 |

## Do not

- invent these integers
- restore `answers2.jsonl` into the tree
- rewrite `data/diagnosis.json` via `forward_verify_all.py`
- merge PR #18
"""
    os.makedirs("data/fverify_n500", exist_ok=True)
    open(WALL, "w").write(body)
    json.dump({
        "n": 500,
        "verified": n500["verified"],
        "misranked": n500["misranked"],
        "wall": n500["wall"],
        "recalled": n500["recalled"],
        "arms": {
            "locked_194": {k: arms["locked_194"][k] for k in
                           ("n", "verified", "misranked", "wall", "recalled")},
            "plus_106": {k: w106[k] for k in
                         ("n", "verified", "misranked", "wall", "recalled",
                          "self_ranked", "verify_top1")},
            "expand500_200": {k: w200[k] for k in
                              ("n", "verified", "misranked", "wall", "recalled",
                               "self_ranked", "verify_top1")},
        },
        "source": "scripts/fverify_n500_wall.py",
    }, open("data/fverify_n500/wall.json", "w"), indent=1)

    # never leave answers in the tree
    for p in ("data/benchmark_expand/answers2.jsonl",
              "data/benchmark_expand_500/answers2.jsonl"):
        if os.path.exists(p):
            raise SystemExit(f"answers leaked into {p}")

    print(foot106)
    print("---")
    print(f"n=500 wall {n500['verified']}/{n500['misranked']}/{n500['wall']}")
    print(f"wrote {WALL}")


if __name__ == "__main__":
    main()
