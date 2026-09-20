#!/usr/bin/env python3
"""
Inventory the +106 Opus expansion's forward-verify gap.

Counts unique RDKit-canonical SMILES from predictions2.jsonl only (no
answer key) and how many already have a non-empty numeric ¹³C list under
any data/fverify* path. Writes data/fverify_expand/INVENTORY_*.md and
refreshes the coverage table in data/fverify_expand/STATUS.md.

  python scripts/inventory_fverify_expand.py
"""
import glob
import json
import os
from collections import defaultdict
from datetime import date

from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

SRC = "data/benchmark_expand"
OUT = "data/fverify_expand"
PRED = f"{SRC}/predictions2.jsonl"
QUEST = f"{SRC}/questions2.jsonl"


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def is_num_list(v):
    return (isinstance(v, list) and len(v) > 0
            and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    for x in v))


def _amap_smiles_to_id(raw):
    """Official maps are smiles -> Qxxx. Accept a reversed map too."""
    if not raw:
        return {}
    sample = list(raw)[:5]
    if all(isinstance(k, str) and k[:1] in "QPG" and len(k) <= 5
           for k in sample):
        return {v: k for k, v in raw.items()}
    return raw


def load_plus106():
    questions = [json.loads(l)["qid"] for l in open(QUEST)]
    pred_rows = [json.loads(l) for l in open(PRED)]
    if set(questions) != {r["qid"] for r in pred_rows}:
        raise SystemExit("predictions2.jsonl / questions2.jsonl qid mismatch")
    dropped = []
    per_qid = defaultdict(set)
    smiles_qids = defaultdict(set)
    raw_slots = 0
    for r in pred_rows:
        qid = r["qid"]
        for rank, smi in enumerate(r.get("candidates", [])[:3]):
            raw_slots += 1
            cs = canon(smi)
            if not cs:
                dropped.append((qid, rank, "unparseable"))
                continue
            if cs in per_qid[qid]:
                dropped.append((qid, rank, "per-qid-dup"))
                continue
            per_qid[qid].add(cs)
            smiles_qids[cs].add(qid)
    return {
        "qids": questions,
        "raw_slots": raw_slots,
        "kept_rows": sum(len(v) for v in per_qid.values()),
        "dropped": dropped,
        "per_qid": per_qid,
        "smiles_qids": smiles_qids,
        "uniq": sorted(smiles_qids),
    }


def load_arm(d):
    amap = {}
    for name in ("anon_map.json", "anon_map2.json"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            amap = _amap_smiles_to_id(json.load(open(p)))
            break
    preds = {}
    for f in glob.glob(os.path.join(d, "raw", "*.json")):
        payload = json.load(open(f))
        if isinstance(payload, dict):
            preds.update(payload)
    cand = set()
    cp = os.path.join(d, "candidates.jsonl")
    if os.path.exists(cp):
        for l in open(cp):
            r = json.loads(l)
            if r.get("smiles"):
                cand.add(r["smiles"])
    id_to_smi = {aid: smi for smi, aid in amap.items()}
    predicted_smiles = set()
    pred_ids = empty = unmatched = 0
    for aid, shifts in preds.items():
        if is_num_list(shifts):
            pred_ids += 1
            smi = id_to_smi.get(aid)
            if smi:
                predicted_smiles.add(smi)
            else:
                unmatched += 1
        else:
            empty += 1
    return {
        "dir": d,
        "amap_n": len(amap),
        "cand_n": len(cand),
        "pred_ids": pred_ids,
        "empty": empty,
        "unmatched": unmatched,
        "amap_smiles": set(amap),
        "cand_smiles": cand,
        "predicted_smiles": predicted_smiles,
        "raw_files": sorted(glob.glob(os.path.join(d, "raw", "*.json"))),
    }


def inventory():
    os.makedirs(OUT, exist_ok=True)
    src = load_plus106()
    dirs = sorted(d for d in glob.glob("data/fverify*") if os.path.isdir(d))
    arms = [load_arm(d) for d in dirs]
    uniq = set(src["uniq"])
    any_13c = set()
    expand_13c = set()
    any_amap = set()
    expand_amap = set()
    per_arm = []
    for a in arms:
        hit_amap = uniq & a["amap_smiles"]
        hit_13c = uniq & a["predicted_smiles"]
        any_amap |= hit_amap
        any_13c |= hit_13c
        if os.path.basename(a["dir"]).startswith("fverify_expand"):
            expand_amap |= hit_amap
            expand_13c |= hit_13c
        per_arm.append({
            "dir": a["dir"],
            "amap_n": a["amap_n"],
            "cand_n": a["cand_n"],
            "pred_ids": a["pred_ids"],
            "raw_files": len(a["raw_files"]),
            "in_amap": len(hit_amap),
            "has_13c": len(hit_13c),
        })

    def qid_cover(cover):
        full = part = zero = 0
        for qid in src["qids"]:
            smis = src["per_qid"][qid]
            n = len(smis & cover)
            if not smis or n == 0:
                zero += 1
            elif n == len(smis):
                full += 1
            else:
                part += 1
        return full, part, zero

    own_arm = next((a for a in arms if a["dir"] == OUT), None)
    own_13c = (uniq & own_arm["predicted_smiles"]) if own_arm else set()
    own_raw = len(own_arm["raw_files"]) if own_arm else 0
    n_batches = 0
    if os.path.isdir(OUT):
        n_batches = len(glob.glob(f"{OUT}/fbatch_*.txt"))

    hist = {k: sum(1 for q in src["qids"] if len(src["per_qid"][q]) == k)
            for k in range(4)}
    full_any, part_any, zero_any = qid_cover(any_13c)
    full_ex, part_ex, zero_ex = qid_cover(expand_13c)
    still = len(uniq - any_13c)
    still_expand = len(uniq - expand_13c)

    return {
        "date": date.today().isoformat(),
        "compounds": len(src["qids"]),
        "raw_slots": src["raw_slots"],
        "kept_rows": src["kept_rows"],
        "dropped": src["dropped"],
        "unique_smiles": len(uniq),
        "cands_per_qid": hist,
        "arms": per_arm,
        "already_13c_any": len(any_13c),
        "already_13c_expand_star": len(expand_13c),
        "already_amap_any": len(any_amap),
        "already_amap_expand_star": len(expand_amap),
        "still_need_any": still,
        "still_need_expand_star": still_expand,
        "qids_full_any": full_any,
        "qids_partial_any": part_any,
        "qids_zero_any": zero_any,
        "qids_full_expand_star": full_ex,
        "qids_partial_expand_star": part_ex,
        "qids_zero_expand_star": zero_ex,
        "own_raw_files": own_raw,
        "own_13c": len(own_13c),
        "n_batches": n_batches,
        "exists_fverify_expand": os.path.isdir(OUT),
        "exists_fverify_n500_wall": os.path.exists("data/fverify_n500/WALL_n500.md"),
    }


def write_md(inv):
    os.makedirs(OUT, exist_ok=True)
    drop_rows = "\n".join(
        f"| {q} | {r} | {why} |" for q, r, why in inv["dropped"]
    ) or "| — | — | none |"
    arm_rows = "\n".join(
        f"| `{a['dir']}` | {a['amap_n']} | {a['cand_n']} | {a['pred_ids']} | "
        f"{a['raw_files']} | {a['in_amap']} | {a['has_13c']} |"
        for a in inv["arms"]
    )
    body = f"""# fverify +106 inventory — {inv['date']}

Blind ¹³C gap on the Opus +106 expansion
(`data/benchmark_expand/predictions2.jsonl`). Counts come from
`scripts/inventory_fverify_expand.py`. No answer key was read.

A SMILES “already exists” only if it is in that path’s `anon_map` **and**
`raw/*.json` has a non-empty numeric ¹³C list for its anon id.

## +106 source (predictions only)

| | count |
|---|---:|
| compounds (`questions2.jsonl` ∩ `predictions2.jsonl`) | **{inv['compounds']}** |
| raw top-3 candidate slots | **{inv['raw_slots']}** |
| kept rows (RDKit-canonical, per-qid dups dropped) | **{inv['kept_rows']}** |
| unique canonical SMILES | **{inv['unique_smiles']}** |
| dropped | **{len(inv['dropped'])}** |

Candidates per qid: 1 → {inv['cands_per_qid'][1]}; 2 → {inv['cands_per_qid'][2]}; 3 → {inv['cands_per_qid'][3]}.

Dropped rows:

| qid | rank | reason |
|---|---:|---|
{drop_rows}

## Existing `data/fverify*` paths

| dir | anon_map | candidates | pred ids | raw files | +106 in map | +106 with ¹³C |
|---|---:|---:|---:|---:|---:|---:|
{arm_rows}

`data/fverify_expand/` (this campaign) exists: **{str(inv['exists_fverify_expand']).lower()}**.
Own raw files: **{inv['own_raw_files']}**. Own +106 SMILES with ¹³C: **{inv['own_13c']}**.
fbatch files present: **{inv['n_batches']}**.

## Remaining work

| | count |
|---|---:|
| unique SMILES that need a blind ¹³C list | **{inv['unique_smiles']}** |
| already have ¹³C under any `fverify*` | **{inv['already_13c_any']}** |
| already have ¹³C under any `fverify_expand*` | **{inv['already_13c_expand_star']}** |
| already in any `fverify*` anon_map | **{inv['already_amap_any']}** |
| **still need a new ¹³C prediction** | **{inv['still_need_any']}** |
| qids with every candidate already covered (any path) | **{inv['qids_full_any']}** |
| qids with partial coverage (any path) | **{inv['qids_partial_any']}** |
| qids with zero coverage (any path) | **{inv['qids_zero_any']}** |

`data/fverify_n500/WALL_n500.md` exists: **{str(inv['exists_fverify_n500_wall']).lower()}**.
The paper may cite an n=500 fverify wall only after that file exists and
is written by a script from scored arms.

## Do not

- invent coverage numbers
- restore `answers2.jsonl` into the tree
- treat this inventory as a verification-precision result
"""
    path = f"{OUT}/INVENTORY_{inv['date']}.md"
    open(path, "w").write(body)
    print(f"wrote {path}")
    return path


def write_status(inv):
    os.makedirs(OUT, exist_ok=True)
    n_bat = inv["n_batches"]
    body = f"""# fverify +106 — status

Blind ¹³C forward-verification of the Opus +106 expansion
(`data/benchmark_expand/`). Prep is keyless (`PREP_NOTE.md` once written).
The answer key is **not** in the tree.

**This is the remaining hole for a scored+fverify n=500 corpus.**
Locked n=194 wall is 58/7/129. expand-500 fverify is 681/681 and scored.
+106 fverify was never run for the paper.

Counts below are from `scripts/inventory_fverify_expand.py`
({inv['date']}). Companion: `INVENTORY_{inv['date']}.md`.

## Coverage (deposits)

| | count |
|---|---:|
| compounds | **{inv['compounds']}** |
| unique SMILES (target) | **{inv['unique_smiles']}** |
| kept candidate rows | **{inv['kept_rows']}** |
| already have ¹³C under any `fverify*` / any `fverify_expand*` | **{inv['already_13c_any']}** / **{inv['already_13c_expand_star']}** |
| **still need blind ¹³C** | **{inv['still_need_any']}** |
| `raw/f*.json` in this directory | **{inv['own_raw_files']}** |
| fbatch files | **{n_bat}** |
| qids with every candidate covered | **{inv['qids_full_any']}** / {inv['compounds']} |

## What is not done

| item | status |
|---|---|
| keyless prep (`anon_map` + `fbatch_*.txt`) | {"present" if n_bat else "not yet"} |
| Opus ¹³C deposits | **{inv['own_13c']}/{inv['unique_smiles']}** |
| official chamfer score (`is_true` from /tmp key only) | not run |
| `data/fverify_n500/WALL_n500.md` | {"exists" if inv["exists_fverify_n500_wall"] else "absent — paper must not cite n=500 fverify wall"} |

## Do not

- commit `answers2.jsonl` or write `is_true` into `candidates.jsonl`
- run official `forward_verify_main.py prep` against this directory (would
  need the key and would rewrite the keyless map)
- run `forward_verify_all.py` (would rewrite the n=194 `diagnosis.json`)
- invent wall integers
- merge PR #18
"""
    path = f"{OUT}/STATUS.md"
    open(path, "w").write(body)
    print(f"wrote {path}")
    return path


if __name__ == "__main__":
    inv = inventory()
    write_md(inv)
    write_status(inv)
    print(f"unique SMILES {inv['unique_smiles']}; "
          f"already 13C {inv['already_13c_any']}; "
          f"still need {inv['still_need_any']}")
