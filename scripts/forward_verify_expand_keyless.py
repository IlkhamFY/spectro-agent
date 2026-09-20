#!/usr/bin/env python3
"""
Keyless forward-verify prep for the Opus +106 expansion.

Official `scripts/forward_verify_main.py prep --round data/benchmark_expand
--out data/fverify_expand` needs answers2.jsonl only to set is_true. The
answer key is withheld. This script builds the same artifact shapes from
questions2.jsonl + raw/*.json (or predictions2.jsonl) so blind ¹³C agents can
fill raw/f*.json. It never opens answers2.jsonl and never scores.

  python scripts/forward_verify_expand_keyless.py
"""
import glob
import json
import os
import random
import re
import sys

from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

SRC = "data/benchmark_expand"
OUT = "data/fverify_expand"
PREFIX = "expand"
BATCH = 17
SEED = 11
# 13C-overread flags from the pre-solver spectral audit (STATUS.md / clean_qids.json).
# Not derived from the answer key.
FLAGGED = ("R12", "R22", "R25", "R82", "R91")


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def obs_c13(c_nmr):
    return [float(x) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", c_nmr or "")]


def _predictions():
    """Use predictions2.jsonl only. +106 raw/ is a partial batch dump;
    singles were banked into predictions2 and are not all under raw/.
    The user instruction is predictions-only; do not reconstruct from raw."""
    pred = {}
    path = f"{SRC}/predictions2.jsonl"
    if not os.path.exists(path):
        sys.stderr.write(f"missing {path}\n")
        sys.exit(1)
    for line in open(path):
        r = json.loads(line)
        pred[r["qid"]] = r.get("candidates", [])
    return pred


def _place_batches(uniq, smiles_qids):
    """Seed-11 order, then pack ~BATCH per file, splitting qid siblings when possible."""
    n = len(uniq)
    n_batches = (n + BATCH - 1) // BATCH
    base, extra = divmod(n, n_batches)
    sizes = [base + (1 if i < extra else 0) for i in range(n_batches)]
    batches = [[] for _ in range(n_batches)]
    batch_qids = [set() for _ in range(n_batches)]
    qid_order, qid_smiles, seen_q = [], {}, set()
    for smi in uniq:
        for q in sorted(smiles_qids.get(smi, ())):
            if q not in seen_q:
                qid_order.append(q)
                seen_q.add(q)
            qid_smiles.setdefault(q, []).append(smi)
    max_k = max((len(v) for v in qid_smiles.values()), default=0)
    placed = set()
    for k in range(max_k):
        for qid in qid_order:
            if k >= len(qid_smiles[qid]):
                continue
            smi = qid_smiles[qid][k]
            if smi in placed:
                continue
            qids = smiles_qids[smi]
            open_bi = [bi for bi in range(n_batches) if len(batches[bi]) < sizes[bi]]
            if not open_bi:
                raise RuntimeError(f"could not place {smi}")
            bi = min(open_bi, key=lambda i: (len(qids & batch_qids[i]), i))
            batches[bi].append(smi)
            batch_qids[bi] |= qids
            placed.add(smi)
    if len(placed) != len(uniq):
        raise RuntimeError(f"placed {len(placed)} of {len(uniq)}")
    return batches


def prep():
    if os.path.exists(f"{SRC}/answers2.jsonl"):
        sys.stderr.write("refusing to run: answers2.jsonl is present; keyless prep "
                         "must not sit next to a restored key\n")
        sys.exit(2)

    os.makedirs(f"{OUT}/raw", exist_ok=True)
    open(f"{OUT}/raw/.gitkeep", "w").close()

    questions = {json.loads(l)["qid"]: json.loads(l)
                 for l in open(f"{SRC}/questions2.jsonl")}
    pred = _predictions()
    qids = sorted(questions, key=lambda q: (len(q), q))
    if set(pred) != set(questions):
        missing = sorted(set(questions) - set(pred))
        extra = sorted(set(pred) - set(questions))
        sys.stderr.write(f"prediction/question mismatch missing={missing} extra={extra}\n")
        sys.exit(1)

    rows = []
    smiles_qids = {}
    dropped = 0
    for qid in qids:
        q = questions[qid]
        obs = obs_c13(q.get("c_nmr"))
        seen = set()
        for rank, smi in enumerate(pred.get(qid, [])[:3]):
            cs = canon(smi)
            if not cs or cs in seen:
                dropped += 1
                continue
            seen.add(cs)
            smiles_qids.setdefault(cs, set()).add(qid)
            row = {
                "cid": f"{PREFIX}:{qid}:{rank}",
                "dir": SRC,
                "qid": qid,
                "smiles": cs,
                "anon_id": None,
                "self_rank": rank,
                "obs_c13": obs,
                "difficulty": q.get("difficulty"),
            }
            rows.append(row)

    uniq = sorted(smiles_qids)
    random.seed(SEED)
    random.shuffle(uniq)
    batches = _place_batches(uniq, smiles_qids)
    ordered = [s for chunk in batches for s in chunk]
    amap = {s: f"Q{i:03d}" for i, s in enumerate(ordered)}
    json.dump(amap, open(f"{OUT}/anon_map.json", "w"), indent=None)

    for r in rows:
        r["anon_id"] = amap[r["smiles"]]
    with open(f"{OUT}/candidates.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    for old in glob.glob(f"{OUT}/fbatch_*.txt"):
        os.remove(old)
    for bi, chunk in enumerate(batches):
        body = "\n".join(f"{amap[s]}  {s}" for s in chunk)
        open(f"{OUT}/fbatch_{bi + 1}.txt", "w").write(body + "\n")

    n_q = len({r["qid"] for r in rows})
    sibling_same = 0
    for chunk in batches:
        seen_q = set()
        for s in chunk:
            hit = smiles_qids[s] & seen_q
            if hit:
                sibling_same += 1
            seen_q |= smiles_qids[s]

    sizes = [len(c) for c in batches]
    note = f"""# Keyless forward-verify prep — +106 expansion

This directory is a **keyless** prep so Opus agents can fill `raw/f*.json`
without anyone restoring `answers2.jsonl`.

Official score path:

```
python scripts/forward_verify_main.py prep --round data/benchmark_expand --out data/fverify_expand
```

needs the withheld key **only** to set `is_true`. Do not restore the key for
this campaign. Do not run official `prep` against this bundle (it would
rewrite `anon_map.json` / `fbatch_*.txt`). Score later with the key only
under `/tmp`, filling `is_true` on a `/tmp` candidates copy.

## What this prep is

| | |
|---|---|
| source | `{SRC}/predictions2.jsonl` + `questions2.jsonl` (raw/ not used; singles live only in predictions2) |
| answer key | **not read** (`is_true` absent from every candidates row) |
| compounds | **{n_q}** deposits (all of them; not the clean-101 subset) |
| candidate rows | **{len(rows)}** (top-3 SMILES / qid, RDKit-canonical, per-qid dups dropped) |
| unparseable / per-qid dup dropped | {dropped} |
| unique SMILES | **{len(uniq)}** (anon ids Q000…Q{len(uniq) - 1:03d}) |
| batches | **{len(batches)}** (`fbatch_1.txt`…`fbatch_{len(batches)}.txt`, seed {SEED}; sizes {sizes}) |
| sibling split | qid-mates packed into different batches when a free slot exists; {sibling_same} leftover co-batch sibling(s) |
| `raw/` | empty on purpose — Opus writes `f1.json`… here |

`anon_map.json` is smiles → anon_id only, matching `data/fverify_main/anon_map.json`.
There is no reverse map.

`candidates.jsonl` rows carry `qid`, `smiles`, `anon_id`, `self_rank`, plus the
official-shape fields that do **not** need the key (`cid`, `dir`, `obs_c13`
from the question ¹³C string, `difficulty` from `questions2.jsonl`). `is_true`
is omitted. Never invent it.

## Clean-101 (no key required)

`{SRC}/clean_qids.json` already lists the **101** spectrally-clean qids from
the pre-solver ¹³C-overread audit (STATUS.md). Flagged, still solved, excluded
only from a later validate-clean pool: {", ".join(FLAGGED)}.

This bundle includes **all 106** deposits so the blind ¹³C campaign covers
every Opus candidate. Headline n=500 keeps all 106 (same convention as
locked n=300). Official `forward_verify_main.py prep` would later restrict
to `clean_qids.json` when the key is restored for a clean-only score.

## Wave plan (budget)

Max 2 parallel Opus waves of ~5 fbatch files. First two waves: **f1–f5**
and **f6–f10**. Remaining after those deposit: f11–f{len(batches)}.

## Do not

- restore `answers2.jsonl` onto this branch
- run official `prep` against this directory (would rewrite the keyless
  `anon_map` / `fbatch_*.txt`)
- run `forward_verify_all.py` (would rewrite the n=194 `diagnosis.json`)
- write `is_true` into committed `candidates.jsonl`
- cite an n=500 fverify wall until `data/fverify_n500/WALL_n500.md` exists
"""
    open(f"{OUT}/PREP_NOTE.md", "w").write(note)
    print(f"{len(rows)} candidate rows over {n_q} qids; "
          f"{len(uniq)} unique SMILES; {len(batches)} batches {sizes}; "
          f"dropped {dropped}; sibling co-batch leftovers {sibling_same}")


if __name__ == "__main__":
    prep()
