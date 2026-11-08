#!/usr/bin/env python3
"""Candidate-budget reanalysis of the generation-wall claim.

Uses only deposited candidate lists, forward-prediction logs, and answer keys.
Does not call a model API.

From the repo root, after the commits named below are in the local object
database (they are not ancestors of main):

  git fetch origin cursor/fverify-n500-unify-629c
  python3 analysis/iclr_rebuttal_nov2026/k_sweep/k_sweep.py

The n=60 / n=194 / generate-wide blocks read the working tree. The n=500
expansion block reads git objects from FVERIFY_SHA and is skipped, with a
message, when those objects are absent. Nothing under data/ is modified.
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import math
import os
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

from specmetrics import chamfer, ik14  # noqa: E402
import figstyle  # noqa: E402

# Expansion predictions and the n=500 forward-verify logs live on this commit,
# which is origin/cursor/fverify-n500-unify-629c at the time of this analysis.
# 48fcd30153df5e331fab43cfa514763db8ee3891 is an ancestor and holds the
# questions/predictions the rebuttal pack also reads.
FVERIFY_SHA = "473030fb9d046548ff1ad06d04d20915fc2943d2"
KS = (1, 2, 3, 5, 6, 10, 20, 50)
OUT = Path("analysis/iclr_rebuttal_nov2026/k_sweep")


def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def wilson(k, n, z=1.959963984540054):
    if n <= 0:
        return None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre, max(0.0, centre - half), min(1.0, centre + half)


def obs_c13(text):
    return [float(x) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or "")]


def q_c13(text):
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or ""))


def g_c13(text):
    if "(" in (text or ""):
        return q_c13(text)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", text or ""))


def ir_key(bands):
    return tuple(round(float(x), 1) for x in (bands or []))


def dedupe(smiles_list):
    """First-occurrence unique canonical SMILES. Unparseable entries are dropped."""
    out, seen = [], set()
    for smi in smiles_list or []:
        c = canon(smi)
        if not c or c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def length_stats(lengths):
    vals = list(lengths)
    n = len(vals)
    total = int(sum(vals))
    hist = dict(sorted(Counter(vals).items()))
    if n == 0:
        return {"n": 0, "sum": 0, "mean": None, "median": None, "min": None,
                "max": None, "hist": {}}
    ordered = sorted(vals)
    if n % 2:
        med = ordered[n // 2]
    else:
        med = (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    return {
        "n": n,
        "sum": total,
        "mean": total / n,
        "median": med,
        "min": ordered[0],
        "max": ordered[-1],
        "hist": hist,
    }


def git_show(sha, path):
    try:
        return subprocess.check_output(
            ["git", "show", f"{sha}:{path}"],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def git_json(sha, path):
    blob = git_show(sha, path)
    if blob is None:
        return None
    return json.loads(blob.decode())


def git_jsonl(sha, path):
    blob = git_show(sha, path)
    if blob is None:
        return None
    rows = []
    for line in blob.decode().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_pred_canon(rawglob, mapfile):
    """Canonical SMILES -> predicted 13C, re-canonicalising both sides."""
    if not os.path.exists(mapfile):
        return {}
    amap = json.load(open(mapfile))
    pred = {}
    for f in glob.glob(rawglob):
        pred.update(json.load(open(f)))
    out = {}
    for smi, aid in amap.items():
        c = canon(smi)
        if c and aid in pred:
            out[c] = pred[aid]
    return out


def score_ordered(ordered, truth, pred, obs, k):
    """Prefix-k of an ordered canonical list.

    Self-rank reads position 0. Forward-verify re-ranks the prefix by chamfer.
    An unpredicted candidate gets distance 999 and loses a tie to any predicted
    candidate. Equal distances keep the earlier list position.
    """
    pool = ordered[:k] if k is not None else list(ordered)
    iks = [ik14(s) for s in pool]
    has = truth is not None and truth in iks
    self_hit = bool(iks) and iks[0] == truth
    if pred is None or obs is None:
        return {
            "recall": has, "self": self_hit, "verify": False,
            "verify_defined": False, "selected_unpredicted": False,
            "n_in_prefix": len(pool),
        }
    if not pool:
        return {
            "recall": has, "self": self_hit, "verify": False,
            "verify_defined": True, "selected_unpredicted": False,
            "n_in_prefix": 0,
        }
    dists = []
    for smi in pool:
        p = pred.get(smi)
        dists.append(chamfer(p, obs) if p else 999.0)
    bi = min(range(len(pool)), key=lambda i: (dists[i], i))
    return {
        "recall": has,
        "self": self_hit,
        "verify": iks[bi] == truth,
        "verify_defined": True,
        "selected_unpredicted": dists[bi] >= 999.0,
        "n_in_prefix": len(pool),
    }


def aggregate(records, k):
    """records: list of dicts with ordered, truth, pred, obs, n_unique."""
    n = len(records)
    rec = self_h = ver = ver_def = unpred = 0
    n_ge = 0
    singletons = 0
    for r in records:
        n_ge += int(r["n_unique"] >= k)
        s = score_ordered(r["ordered"], r["truth"], r["pred"], r["obs"], k)
        rec += int(s["recall"])
        self_h += int(s["self"])
        if s["verify_defined"]:
            ver_def += 1
            ver += int(s["verify"])
            unpred += int(s["selected_unpredicted"])
        if s["recall"] and s["n_in_prefix"] == 1:
            singletons += 1
    verify_on = ver_def == n and n > 0
    return {
        "k": k,
        "n": n,
        "n_lists_ge_k": n_ge,
        "recall": rec,
        "self_top1": self_h,
        "self_prec_num": self_h,  # rank-1 correct implies truth is in every prefix
        "verify_top1": ver if verify_on else "",
        "verify_defined": ver_def,
        "verify_prec_num": ver if verify_on else "",
        "recall_singletons": singletons,
        "selected_unpredicted": unpred if verify_on else "",
        "gen_miss": n - rec,
        "rank_miss_self": rec - self_h,
        "rank_miss_verify": (rec - ver) if verify_on else "",
    }


def fmt_rate(num, den):
    if den == 0:
        return "— (0)"
    w = wilson(num, den)
    return f"{num}/{den} ({100 * num / den:.1f}%; {100 * w[1]:.1f}–{100 * w[2]:.1f})"


def write_csv(path, rows):
    if not rows:
        return
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def load_jsonl(path):
    return [json.loads(line) for line in open(path) if line.strip()]


def load_controlled_60():
    rows = []
    for d, tag in (("data/benchmark_v3", "V3"), ("data/benchmark_v2_ctrl", "CT")):
        questions = {r["qid"]: r for r in load_jsonl(f"{d}/questions2.jsonl")}
        answers = {r["qid"]: r for r in load_jsonl(f"{d}/answers2.jsonl")}
        preds = {r["qid"]: r for r in load_jsonl(f"{d}/predictions2.jsonl")}
        for qid, ans in answers.items():
            raw = list((preds.get(qid) or {}).get("candidates") or [])
            rows.append({
                "arm": "claude-opus-original",
                "subset": "n60",
                "dir": d,
                "qid": qid,
                "key": f"{tag}-{qid}",
                "truth": ans["inchikey"][:14],
                "obs": obs_c13(questions[qid]["c_nmr"]),
                "raw": raw,
                "ordered": dedupe(raw),
            })
    rows.sort(key=lambda r: (r["dir"], r["qid"]))
    return rows


def load_wide_lists():
    """Opus generate-wide lists. File order, g1..g10. Sonnet is separate."""
    wide = {}
    collisions = []
    for f in sorted(glob.glob("data/gw/raw/g*.json")):
        if "sonnet" in os.path.basename(f):
            continue
        blob = json.load(open(f))
        for key, smis in blob.items():
            if key in wide:
                collisions.append(key)
                wide[key].extend(smis)
            else:
                wide[key] = list(smis)
    return wide, collisions


def load_sonnet_wide():
    out = {}
    for f in sorted(glob.glob("data/gw/raw/sonnet_*.json")):
        blob = json.load(open(f))
        for key, smis in blob.items():
            out.setdefault(key, []).extend(smis)
    return out


def attach_pools(base, wide, pred):
    """Three ordered pools per compound: original, wide-only, original-then-wide."""
    arms = {"original": [], "wide-only": [], "pooled": []}
    missing_wide = []
    for r in base:
        wraw = wide.get(r["key"])
        if wraw is None:
            missing_wide.append(r["key"])
            wraw = []
        original = r["ordered"]
        wide_only = dedupe(wraw)
        pooled = list(original)
        have = set(pooled)
        for smi in wide_only:
            if smi not in have:
                pooled.append(smi)
                have.add(smi)
        for name, ordered in (
            ("original", original),
            ("wide-only", wide_only),
            ("pooled", pooled),
        ):
            arms[name].append({
                "id": r["key"],
                "ordered": ordered,
                "truth": r["truth"],
                "pred": pred,
                "obs": r["obs"],
                "n_raw": len(r["raw"]) if name == "original" else len(wraw),
                "n_unique": len(ordered),
            })
    return arms, missing_wide


def published_union_check(base, wide, pred):
    """Raw-string union used by scripts/score_generate_wide.py, for the endpoint check."""
    rec = self1 = ver = 0
    n = 0
    for r in base:
        seen = []
        have = set()
        for smi in r["raw"]:
            if smi not in have:
                seen.append(smi)
                have.add(smi)
        for smi in wide.get(r["key"], []):
            if smi not in have:
                seen.append(smi)
                have.add(smi)
        iks = [ik14(s) for s in seen]
        has = r["truth"] in iks
        # self-rank is the first original candidate, matching the original arm only
        orig_iks = [ik14(s) for s in dedupe(r["raw"])]
        s_hit = bool(orig_iks) and orig_iks[0] == r["truth"]
        dists = []
        canons = []
        for smi in seen:
            c = canon(smi)
            canons.append(c)
            p = pred.get(c) if c else None
            dists.append(chamfer(p, r["obs"]) if p else 999.0)
        bi = min(range(len(seen)), key=lambda i: (dists[i], i)) if seen else None
        v_hit = bi is not None and iks[bi] == r["truth"]
        n += 1
        rec += int(has)
        self1 += int(s_hit)
        ver += int(v_hit)
    return {"n": n, "recall": rec, "self_top1": self1, "verify_top1": ver}


def load_fverify_arm(cand_path, amap_path, raw_glob, roster_spec, pred_extra=None):
    """Deposited forward-verify candidate rows, ordered by self_rank.

    roster_spec: list of (dir, clean_qid_json or None). Denominator is the
    answer-key roster, including compounds with no parseable candidate.
    """
    rows = [json.loads(line) for line in open(cand_path) if line.strip()]
    amap = json.load(open(amap_path))
    raw_pred = {}
    for f in sorted(glob.glob(raw_glob)):
        raw_pred.update(json.load(open(f)))
    if pred_extra:
        raw_pred.update(pred_extra)
    by = defaultdict(list)
    for r in rows:
        by[(r["dir"], r["qid"])].append(r)
    out = []
    for d, cleanf in roster_spec:
        keep = set(json.load(open(cleanf))) if cleanf else None
        answers = {a["qid"]: a for a in load_jsonl(f"{d}/answers2.jsonl")}
        questions = {q["qid"]: q for q in load_jsonl(f"{d}/questions2.jsonl")}
        for qid, ans in answers.items():
            if keep is not None and qid not in keep:
                continue
            cands = sorted(by.get((d, qid), []), key=lambda c: c["self_rank"])
            ordered = []
            seen = set()
            for c in cands:
                smi = c["smiles"]
                if smi in seen:
                    continue
                seen.add(smi)
                ordered.append(smi)
            # Exact map lookup, as in scripts/forward_verify_all.py. Fall back to
            # the current RDKit canonical form only if the stored key moved.
            pred = {}
            for smi in ordered:
                aid = amap.get(smi)
                if aid is None:
                    aid = amap.get(canon(smi) or "")
                if aid is None:
                    # map keys themselves may be an older canonical spelling
                    for key, val in amap.items():
                        if canon(key) == canon(smi):
                            aid = val
                            break
                if aid is not None and aid in raw_pred:
                    pred[smi] = raw_pred[aid]
            out.append({
                "id": f"{d}:{qid}",
                "ordered": ordered,
                "truth": ans["inchikey"][:14],
                "pred": pred,
                "obs": cands[0]["obs_c13"] if cands else obs_c13(questions[qid]["c_nmr"]),
                "n_raw": len(cands),
                "n_unique": len(ordered),
                "deposited_is_true": [bool(c["is_true"]) for c in cands],
            })
    return out


def parse_prompt_blocks(text):
    rows = []
    for block in text.split("### ")[1:]:
        lines = block.splitlines()
        mid = lines[0].strip()
        formula = ""
        ir = []
        c_nmr = ""
        for ln in lines[1:]:
            if ln.startswith("Molecular formula:"):
                formula = ln.split(":", 1)[1].strip()
            elif ln.startswith("IR bands"):
                raw = ln.split(":", 1)[1].strip()
                try:
                    ir = json.loads(raw.replace("'", '"'))
                except Exception:
                    ir = []
            elif ln.startswith("13C NMR:"):
                c_nmr = ln.split(":", 1)[1].strip()
        rows.append({"mid": mid, "formula": formula, "ir": ir, "c_nmr": c_nmr})
    return rows


def map_mids():
    # The sweep replies are keyed by the ids in sweep_prompts/solve_*.md.
    # data/modality/prompt_full.txt is the same 60 compounds in a different id
    # order, so it must not be used to label these replies.
    blocks = []
    for path in sorted(Path("sweep_prompts").glob("solve_*.md")):
        blocks.extend(parse_prompt_blocks(path.read_text()))
    # v3 and v2_ctrl both number qids from R01, so the directory is part of the id.
    lookup = {}
    store = {}
    for d in ("data/benchmark_v3", "data/benchmark_v2_ctrl"):
        questions = {q["qid"]: q for q in load_jsonl(f"{d}/questions2.jsonl")}
        answers = {a["qid"]: a for a in load_jsonl(f"{d}/answers2.jsonl")}
        for qid, q in questions.items():
            key = (q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr")))
            lookup[key] = (d, qid)
            store[(d, qid)] = (q, answers[qid])
    mid_to = {}
    for b in blocks:
        key = (b["formula"], ir_key(b["ir"]), q_c13(b["c_nmr"]))
        found = lookup.get(key)
        if found is None:
            raise SystemExit(f"prompt {b['mid']} did not match a v3/v2_ctrl question")
        q, a = store[found]
        mid_to[b["mid"]] = {
            "qid": f"{found[0]}:{found[1]}",
            "truth": a["inchikey"][:14],
            "obs": obs_c13(q["c_nmr"]),
            "true_smiles": a.get("smiles"),
        }
    if len(mid_to) != 60:
        raise SystemExit(f"expected 60 prompt ids, got {len(mid_to)}")
    return mid_to


def load_sweep_model(directory):
    merged = {}
    collisions = 0
    files = sorted(glob.glob(f"sweep_out/{directory}/reply_*.json"))
    for f in files:
        blob = json.load(open(f))
        if not isinstance(blob, dict):
            continue
        for mid, cands in blob.items():
            if mid in merged:
                collisions += 1
            merged[mid] = cands
    return merged, len(files), collisions


def rebuild_anon(solve, k=3):
    uniq = sorted({
        c for cands in solve.values()
        for c in (canon(s) for s in (cands or [])[:k]) if c
    })
    rng = random.Random(5)
    rng.shuffle(uniq)
    return {s: f"P{i:03d}" for i, s in enumerate(uniq)}


def load_sweep_verify(directory):
    pred = {}
    files = sorted(glob.glob(f"sweep_out/{directory}/verify_*.json"))
    for f in files:
        blob = json.load(open(f))
        if isinstance(blob, dict):
            pred.update(blob)
    return pred, len(files)


def sweep_records(model_dir, mid_to, use_verify):
    solve, nfiles, collisions = load_sweep_model(model_dir)
    pred_anon, nv = load_sweep_verify(model_dir) if use_verify else ({}, 0)
    amap = rebuild_anon(solve) if pred_anon else {}
    # invert: anon id -> shifts, keyed back onto canonical smiles
    pred = {}
    if amap and pred_anon:
        for smi, aid in amap.items():
            if aid in pred_anon:
                pred[smi] = pred_anon[aid]
    rows = []
    for mid, info in mid_to.items():
        raw = list(solve.get(mid) or [])
        ordered = dedupe(raw)
        rows.append({
            "id": mid,
            "ordered": ordered,
            "truth": info["truth"],
            "pred": pred if pred else None,
            "obs": info["obs"],
            "n_raw": len(raw),
            "n_unique": len(ordered),
        })
    meta = {
        "reply_files": nfiles,
        "verify_files": nv,
        "key_collisions": collisions,
        "answered": sum(1 for r in rows if r["n_raw"] > 0),
        "verify_joined": sum(1 for r in rows if r["pred"] and any(s in r["pred"] for s in r["ordered"])),
    }
    return rows, meta


def index_gold(formulas):
    by = defaultdict(list)
    with gzip.open("data/irexp_resolved/irexp_resolved.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            smi = r.get("smiles")
            if not smi:
                continue
            m = Chem.MolFromSmiles(smi)
            if m is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(m)
            if form not in formulas:
                continue
            by[(form, ir_key(r.get("ir_bands_cm-1")), g_c13(r.get("c_nmr")))].append({
                "ik": (r.get("inchikey") or Chem.MolToInchiKey(m))[:14],
            })
    return by


def match_gold(q, gold):
    hits = gold.get((q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr"))), [])
    if len(hits) != 1:
        return None, len(hits)
    return hits[0]["ik"], 1


def load_expansion_generation(sha):
    """Self-rank pools for +106 and the expand-500 200-cut, from git objects."""
    questions = {
        "plus106": git_jsonl(sha, "data/benchmark_expand/questions2.jsonl"),
        "expand500": git_jsonl(sha, "data/benchmark_expand_500/questions2.jsonl"),
    }
    preds = {
        "plus106": git_jsonl(sha, "data/benchmark_expand/predictions2.jsonl"),
        "expand500": git_jsonl(sha, "data/benchmark_expand_500/predictions2.jsonl"),
    }
    cut = git_json(sha, "data/benchmark_expand_500/headline500_expand200_qids.json")
    if any(v is None for v in (*questions.values(), *preds.values(), (cut,))):
        return None, "git object missing (fetch origin cursor/fverify-n500-unify-629c)"
    formulas = set()
    for rows in questions.values():
        for q in rows:
            formulas.add(q["formula"])
    gold = index_gold(formulas)
    out = {}
    problems = []
    pred_maps = {}
    for name in ("plus106", "expand500"):
        pred_maps[name] = {r["qid"]: r.get("candidates") or [] for r in preds[name]}
    # +106: every question
    plus = []
    for q in questions["plus106"]:
        truth, n_hits = match_gold(q, gold)
        raw = pred_maps["plus106"].get(q["qid"], [])
        plus.append(_exp_row("plus106", q, truth, n_hits, raw))
        if truth is None:
            problems.append(f"plus106 {q['qid']}: gold hits={n_hits}")
    # expand-500: 200-cut and the rest, separately
    cut_set = set(cut)
    exp200, exprest = [], []
    for q in questions["expand500"]:
        truth, n_hits = match_gold(q, gold)
        raw = pred_maps["expand500"].get(q["qid"], [])
        row = _exp_row("expand500", q, truth, n_hits, raw)
        if truth is None:
            problems.append(f"expand500 {q['qid']}: gold hits={n_hits}")
        if q["qid"] in cut_set:
            row["subset"] = "expand200"
            exp200.append(row)
        else:
            row["subset"] = "expand500_rest"
            exprest.append(row)
    out["plus106"] = plus
    out["expand200"] = exp200
    out["expand500_rest"] = exprest
    out["problems"] = problems
    return out, None


def _exp_row(arm, q, truth, n_hits, raw):
    return {
        "id": f"{arm}:{q['qid']}",
        "qid": q["qid"],
        "ordered": dedupe(raw),
        "raw": list(raw),
        "truth": truth,
        "pred": None,
        "obs": obs_c13(q.get("c_nmr")),
        "n_raw": len(raw),
        "n_unique": len(dedupe(raw)),
        "gold_hits": n_hits,
        "subset": arm,
    }


def load_expansion_fverify(sha):
    """Forward-verify rows for +106 and expand-500, is_true recomputed by gold join."""
    bundles = {
        "plus106": "data/fverify_expand",
        "expand500": "data/fverify_expand_500",
    }
    # questions for the join already loaded by the caller via the same sha; this
    # function returns candidate rows keyed by qid, with shifts joined.
    loaded = {}
    for name, directory in bundles.items():
        cand_blob = git_show(sha, f"{directory}/candidates.jsonl")
        amap = git_json(sha, f"{directory}/anon_map.json")
        if cand_blob is None or amap is None:
            return None
        listing = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", sha, f"{directory}/raw"],
            stderr=subprocess.DEVNULL,
        ).decode().splitlines()
        pred = {}
        for path in listing:
            if not path.endswith(".json"):
                continue
            blob = git_json(sha, path)
            if isinstance(blob, dict):
                pred.update(blob)
        by = defaultdict(list)
        for line in cand_blob.decode().splitlines():
            if line.strip():
                r = json.loads(line)
                by[r["qid"]].append(r)
        loaded[name] = {"by": by, "amap": amap, "pred": pred}
    return loaded


def expansion_fv_records(rows, bundle):
    """Attach chamfer predictions. `rows` carry truth from the gold join."""
    out = []
    truth = {r["qid"]: r["truth"] for r in rows}
    for qid, cands in bundle["by"].items():
        if qid not in truth:
            continue
        cands = sorted(cands, key=lambda c: c.get("self_rank", 0))
        ordered = []
        pred = {}
        seen = set()
        for c in cands:
            smi = c["smiles"]
            if smi in seen:
                continue
            seen.add(smi)
            ordered.append(smi)
            aid = bundle["amap"].get(smi)
            if aid is not None and aid in bundle["pred"]:
                pred[smi] = bundle["pred"][aid]
        out.append({
            "id": qid,
            "ordered": ordered,
            "truth": truth[qid],
            "pred": pred,
            "obs": cands[0]["obs_c13"] if cands else None,
            "n_raw": len(cands),
            "n_unique": len(ordered),
        })
    # questions with no candidate row
    have = {r["id"] for r in out}
    for r in rows:
        if r["qid"] not in have:
            out.append({
                "id": r["qid"],
                "ordered": [],
                "truth": r["truth"],
                "pred": {},
                "obs": r["obs"],
                "n_raw": 0,
                "n_unique": 0,
            })
    return out


def locked194_generation():
    """Same cohort as scripts/score_main.py: clean main + all of v3 + v2_ctrl."""
    rows = []
    answers = {a["qid"]: a for a in load_jsonl("data/benchmark_main/answers2.jsonl")}
    questions = {q["qid"]: q for q in load_jsonl("data/benchmark_main/questions2.jsonl")}
    clean = set(json.load(open("data/benchmark_main/clean_qids.json")))
    pred = {}
    for f in glob.glob("data/benchmark_main/raw/*.json"):
        try:
            pred.update(json.load(open(f)))
        except Exception:
            pass
    for qid, ans in answers.items():
        if qid not in clean:
            continue
        raw = pred.get(f"M-{qid}")
        if raw is None:
            continue
        rows.append({
            "id": f"main:{qid}",
            "ordered": dedupe(raw),
            "raw": list(raw),
            "truth": ans["inchikey"][:14],
            "pred": None,
            "obs": obs_c13(questions[qid]["c_nmr"]),
            "n_raw": len(raw),
            "n_unique": len(dedupe(raw)),
            "subset": "locked194_main",
        })
    for d, subset in (("data/benchmark_v3", "locked194_v3"),
                      ("data/benchmark_v2_ctrl", "locked194_v2ctrl")):
        answers = {a["qid"]: a for a in load_jsonl(f"{d}/answers2.jsonl")}
        questions = {q["qid"]: q for q in load_jsonl(f"{d}/questions2.jsonl")}
        preds = {p["qid"]: p for p in load_jsonl(f"{d}/predictions2.jsonl")}
        for qid, ans in answers.items():
            raw = list((preds.get(qid) or {}).get("candidates") or [])
            rows.append({
                "id": f"{d}:{qid}",
                "ordered": dedupe(raw),
                "raw": raw,
                "truth": ans["inchikey"][:14],
                "pred": None,
                "obs": obs_c13(questions[qid]["c_nmr"]),
                "n_raw": len(raw),
                "n_unique": len(dedupe(raw)),
                "subset": subset,
            })
    return rows


def raw_top3(raw, truth):
    """Paper scorer: first three raw strings, no canonical dedupe."""
    flags = [ik14(s) == truth and truth is not None for s in (raw or [])[:3]]
    top1 = bool(flags) and flags[0]
    rec = any(flags)
    return top1, rec


def generator_lengths():
    path = "contrib/generator_probe/artifacts/gen_candidates.jsonl"
    if not os.path.exists(path):
        return None
    blob = json.load(open(path))
    lengths = [len(v) for v in blob.values() if isinstance(v, list)]
    return {
        "n_qids": len(blob),
        "lengths": length_stats(lengths),
        "note": (
            "gen_candidates.jsonl stores sorted canonical SMILES, not beam order. "
            "A prefix of that file is not a generation ranking, so no k curve is reported."
        ),
    }


def curve_rows(arm, subset, records, ks, ranker_note):
    rows = []
    max_len = max((r["n_unique"] for r in records), default=0)
    present = sorted(set(ks) | set(range(1, max_len + 1)))
    for k in present:
        agg = aggregate(records, k)
        agg.update({
            "arm": arm,
            "subset": subset,
            "max_unique_in_arm": max_len,
            "ranker_note": ranker_note,
            "identified": agg["n_lists_ge_k"] > 0,
        })
        rows.append(agg)
    return rows


def counts_row(arm, subset, records, length_key="n_unique"):
    stats = length_stats(r[length_key] for r in records)
    row = {
        "arm": arm,
        "subset": subset,
        "length": length_key,
        **{k: stats[k] for k in ("n", "sum", "mean", "median", "min", "max")},
        "hist": json.dumps(stats["hist"]),
    }
    return row


def series_for_plot(curve, arm, subset):
    pts = [r for r in curve if r["arm"] == arm and r["subset"] == subset and r["identified"]]
    pts = [r for r in pts if r["k"] <= r["max_unique_in_arm"]]
    return pts


def draw(curve):
    figstyle.apply()
    fig, ax_a, ax_b = figstyle.twin_panel(figsize=(figstyle.COL2, 3.35))
    specs = [
        ("original", "n60", "Original ≤3", figstyle.BLUE, "o"),
        ("wide-only", "n60", "Wide list only", figstyle.ORANGE, "s"),
        ("pooled", "n60", "Original + wide", figstyle.GREEN, "D"),
    ]
    ax = ax_a
    for arm, subset, label, color, marker in specs:
        pts = series_for_plot(curve, arm, subset)
        if not pts:
            continue
        xs = [p["k"] for p in pts]
        ys = [100 * p["recall"] / p["n"] for p in pts]
        ax.plot(xs, ys, color=color, marker=marker, ms=4.5, lw=1.3, label=label)
    ax.set_xlabel("prefix length k")
    ax.set_ylabel("generation recall (%)")
    xmax = max((p["k"] for arm, subset, *_ in specs for p in series_for_plot(curve, arm, subset)), default=6)
    ax.set_xticks([k for k in range(1, xmax + 1)])
    ax.set_ylim(0, 100)
    ax.set_xlim(0.7, xmax + 0.3)
    ax.legend(frameon=False, loc="upper left")
    figstyle.panel(ax, "a")

    ax = ax_b
    for arm, subset, label, color, marker in specs:
        pts = series_for_plot(curve, arm, subset)
        pts = [p for p in pts if p["recall"]]
        if not pts:
            continue
        xs = [p["k"] for p in pts]
        y_self = [100 * p["self_prec_num"] / p["recall"] for p in pts]
        y_ver = [100 * p["verify_prec_num"] / p["recall"] for p in pts]
        ax.plot(xs, y_ver, color=color, marker=marker, ms=4.5, lw=1.3, label=label)
        ax.plot(xs, y_self, color=color, lw=0.8, ls=(0, (2.2, 1.6)), alpha=0.9)
    ax.set_xlabel("prefix length k")
    ax.set_ylabel("precision | recall (%)")
    ax.set_xticks([k for k in range(1, xmax + 1)])
    ax.set_ylim(0, 105)
    ax.set_xlim(0.7, xmax + 0.3)
    ax.legend(frameon=False, loc="lower left")
    ax.text(0.98, 0.98, "solid: forward-verify\ndashed: self-rank",
            transform=ax.transAxes, ha="right", va="top", color=figstyle.NOTE, fontsize=8)
    figstyle.panel(ax, "b")
    figstyle.save(str(OUT / "fig_k_sweep.png"), fig)


def draw_hist(count_rows):
    import matplotlib.pyplot as plt
    figstyle.apply()
    fig, ax = plt.subplots(figsize=(figstyle.COL2, figstyle.H1))
    wanted = [
        ("claude-opus", "n60", "raw", "Original raw", figstyle.BLUE),
        ("original", "n60", "n_unique", "Original unique", figstyle.SKY),
        ("wide-only", "n60", "n_unique", "Wide unique", figstyle.ORANGE),
        ("pooled", "n60", "n_unique", "Pooled unique", figstyle.GREEN),
    ]
    # grouped bars over length 0..max
    bins = range(0, 10)
    width = 0.18
    for i, (arm, subset, length, label, color) in enumerate(wanted):
        match = [r for r in count_rows if r["arm"] == arm and r["subset"] == subset
                 and r["length"] == length]
        if not match:
            continue
        hist = json.loads(match[0]["hist"])
        xs = [b + (i - 1.5) * width for b in bins]
        ys = [int(hist.get(str(b), hist.get(b, 0))) for b in bins]
        ax.bar(xs, ys, width=width, color=color, label=label)
    ax.set_xlabel("candidates per compound")
    ax.set_ylabel("compounds (n = 60)")
    ax.set_xticks(list(bins))
    ax.legend(frameon=False, ncol=2)
    figstyle.panel(ax, "a", x=-0.14)
    figstyle.save(str(OUT / "fig_pool_sizes.png"), fig)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    notes = []
    checks = []

    pred = {}
    pred.update(load_pred_canon("data/fverify/raw/*.json", "data/fverify/anon_map.json"))
    pred.update(load_pred_canon("data/fverify2/raw/*.json", "data/fverify2/anon_map2.json"))
    if os.path.exists("data/fverify_gw/anon_map.json"):
        pred.update(load_pred_canon("data/fverify_gw/raw/*.json", "data/fverify_gw/anon_map.json"))

    base = load_controlled_60()
    wide, collisions = load_wide_lists()
    if collisions:
        notes.append(f"generate-wide keys present in more than one g*.json: {collisions}")
    arms, missing_wide = attach_pools(base, wide, pred)
    if missing_wide:
        notes.append(f"n=60 compounds with no generate-wide list: {missing_wide}")

    pub = published_union_check(base, wide, pred)
    checks.append({
        "name": "published_generate_wide_endpoint",
        "got": f"{pub['recall']}/60 recall, {pub['verify_top1']}/60 verify, {pub['self_top1']}/60 self",
        "expect": "25/60 recall, 18/60 verify, 14/60 self",
        "ok": pub["recall"] == 25 and pub["verify_top1"] == 18 and pub["self_top1"] == 14,
    })

    curve = []
    counts = []
    # n=60 three pools. Also keep raw lengths on the original arm.
    for name, records in arms.items():
        curve.extend(curve_rows(name, "n60", records, KS, "chamfer re-rank of the prefix; self-rank is list position 0"))
        counts.append(counts_row(name, "n60", records, "n_unique"))
    counts.append(counts_row("claude-opus", "n60", arms["original"], "n_raw"))
    counts.append({
        "arm": "claude-opus",
        "subset": "n60",
        "length": "raw",
        **{k: length_stats(r["n_raw"] for r in arms["original"])[k]
           for k in ("n", "sum", "mean", "median", "min", "max")},
        "hist": json.dumps(length_stats(r["n_raw"] for r in arms["original"])["hist"]),
    })
    # The counts_row above used n_raw stored on original records. The explicit
    # claude-opus raw row is the one the 2.20 claim is checked against.
    raw_stats = length_stats(r["n_raw"] for r in arms["original"])
    uniq_stats = length_stats(r["n_unique"] for r in arms["original"])
    checks.append({
        "name": "claude_n60_mean_raw",
        "got": f"{raw_stats['sum']}/{raw_stats['n']} = {raw_stats['mean']:.4f}",
        "expect": "132/60 = 2.20 if the published two-decimal figure is exact",
        "ok": raw_stats["n"] == 60 and raw_stats["sum"] == 132,
    })

    # Deposited fverify pools (the scorer behind Table 6 / the n=194 wall).
    fv60 = load_fverify_arm(
        "data/fverify/candidates.jsonl",
        "data/fverify/anon_map.json",
        "data/fverify/raw/*.json",
        [("data/benchmark_v3", None), ("data/benchmark_v2_ctrl", None)],
    )
    fv134 = load_fverify_arm(
        "data/fverify_main/candidates.jsonl",
        "data/fverify_main/anon_map.json",
        "data/fverify_main/raw/*.json",
        [("data/benchmark_main", "data/benchmark_main/clean_qids.json")],
    )
    curve.extend(curve_rows("fverify-deposited", "n60", fv60, KS, "deposited candidates.jsonl order by self_rank"))
    curve.extend(curve_rows("fverify-deposited", "n134", fv134, KS, "deposited candidates.jsonl order by self_rank"))
    fv194 = fv60 + fv134
    curve.extend(curve_rows("fverify-deposited", "n194", fv194, KS, "n60 and n134 deposited pools pooled"))
    for subset, recs in (("n60", fv60), ("n134", fv134), ("n194", fv194)):
        counts.append(counts_row("fverify-deposited", subset, recs, "n_unique"))
    full60 = aggregate(fv60, 10_000)
    full194 = aggregate(fv194, 10_000)
    checks.append({
        "name": "fverify_n60_full_pool",
        "got": f"recall {full60['recall']}/60 self {full60['self_top1']}/60 verify {full60['verify_top1']}/60",
        "expect": "19/60, 14/60, 16/60",
        "ok": (full60["recall"], full60["self_top1"], full60["verify_top1"]) == (19, 14, 16),
    })
    checks.append({
        "name": "fverify_n194_full_pool",
        "got": (f"recall {full194['recall']}/{full194['n']} self {full194['self_top1']} "
                f"verify {full194['verify_top1']}"),
        "expect": "65/194, 55, 58",
        "ok": full194["n"] == 194 and (full194["recall"], full194["self_top1"], full194["verify_top1"]) == (65, 55, 58),
    })

    # Cross-vendor sweep replies. Verify join is rebuilt; accepted only if the
    # published recall integers come back.
    mid_to = map_mids()
    # Exact fractions in docs/ESI.md. Composer and Luna are published as
    # rounded percents; those are checked after the integer is measured.
    expected_recall = {
        "grok-4.6": 32,
        "gemini-3.7-flash": 30,
        "gpt-5.6-sol": 25,
        "grok-4.6-clean": 28,
    }
    expected_top1 = {
        "grok-4.6": 23,
        "gemini-3.7-flash": 23,
        "gpt-5.6-sol": 21,
    }
    # Forward-verify precision | recall, same table.
    expected_fv = {
        "grok-4.6": (20, 32),
        "gemini-3.7-flash": (22, 30),
        "gpt-5.6-sol": (17, 25),
    }
    sweep_meta = {}
    for model in ("grok-4.6", "grok-4.6-clean", "gemini-3.7-flash", "gpt-5.6-sol",
                  "composer-2.5", "gpt-5.6-luna"):
        if not glob.glob(f"sweep_out/{model}/reply_*.json"):
            notes.append(f"no sweep_out/{model}/reply_*.json")
            continue
        use_verify = bool(glob.glob(f"sweep_out/{model}/verify_*.json"))
        records, meta = sweep_records(model, mid_to, use_verify)
        sweep_meta[model] = meta
        at3 = aggregate(records, 3)
        if model in expected_recall:
            checks.append({
                "name": f"sweep_recall_{model}",
                "got": f"{at3['recall']}/60",
                "expect": f"{expected_recall[model]}/60",
                "ok": at3["recall"] == expected_recall[model],
            })
        if model in expected_top1:
            checks.append({
                "name": f"sweep_top1_{model}",
                "got": f"{at3['self_top1']}/60",
                "expect": f"{expected_top1[model]}/60",
                "ok": at3["self_top1"] == expected_top1[model],
            })
        fv_ok = False
        if model in expected_fv and at3["verify_defined"] == at3["n"]:
            want_v, want_r = expected_fv[model]
            fv_ok = at3["verify_top1"] == want_v and at3["recall"] == want_r
            checks.append({
                "name": f"sweep_fv_{model}",
                "got": f"verify {at3['verify_top1']}/{at3['recall']}",
                "expect": f"{want_v}/{want_r}",
                "ok": fv_ok,
            })
        if not fv_ok:
            for r in records:
                r["pred"] = None
            if use_verify:
                notes.append(
                    f"{model}: rebuilt anon map did not reproduce the published "
                    f"forward-verify count (joined compounds={meta['verify_joined']}). "
                    "Chamfer curve withheld; self-rank curve kept."
                )
        curve.extend(curve_rows(model, "n60", records, KS, "sweep reply order; chamfer only if anon rebuild joined"))
        counts.append(counts_row(model, "n60", records, "n_unique"))
        counts.append(counts_row(model, "n60", records, "n_raw"))

    # 24-compound ladder. Candidate counts and self-rank only (no forward-verify logs).
    import score_models
    answers = {a["qid"]: a for a in load_jsonl("data/benchmark_main/answers2.jsonl")}
    for model, glb in score_models.SRC.items():
        loaded = score_models.load(glb)
        records = []
        for qid in score_models.SUBSET:
            raw = list(loaded.get(qid) or [])
            records.append({
                "id": qid,
                "ordered": dedupe(raw),
                "truth": answers[qid]["inchikey"][:14],
                "pred": None,
                "obs": None,
                "n_raw": len(raw),
                "n_unique": len(dedupe(raw)),
            })
        curve.extend(curve_rows(model, "n24", records, KS, "self-rank only; no forward-verify log on this subset"))
        counts.append(counts_row(model, "n24", records, "n_raw"))
        counts.append(counts_row(model, "n24", records, "n_unique"))

    # Sonnet generate-wide, the 12 compounds that were actually run.
    sonnet = load_sonnet_wide()
    sonnet_records = []
    by_key = {r["key"]: r for r in base}
    for key, raw in sorted(sonnet.items()):
        src = by_key.get(key)
        if src is None:
            notes.append(f"sonnet wide key {key} is not in the n=60 arm")
            continue
        ordered = dedupe(raw)
        sonnet_records.append({
            "id": key,
            "ordered": ordered,
            "truth": src["truth"],
            "pred": None,
            "obs": src["obs"],
            "n_raw": len(raw),
            "n_unique": len(ordered),
        })
    if sonnet_records:
        curve.extend(curve_rows("sonnet-wide", "n12", sonnet_records, KS, "file order; no separate forward-verify map"))
        counts.append(counts_row("sonnet-wide", "n12", sonnet_records, "n_unique"))

    # Locked 194 generation (self-rank), to sit next to the n=500 headline.
    locked = locked194_generation()
    t1 = rec = 0
    for r in locked:
        a, b = raw_top3(r["raw"], r["truth"])
        t1 += int(a)
        rec += int(b)
    checks.append({
        "name": "locked194_raw_top3",
        "got": f"top1 {t1}/{len(locked)} recall {rec}/{len(locked)}",
        "expect": "55/194 and 65/194",
        "ok": len(locked) == 194 and t1 == 55 and rec == 65,
    })
    curve.extend(curve_rows("claude-opus-raw-top3-scorer", "locked194", locked, KS,
                            "first k raw strings, the score_main / rebuttal scorer; no chamfer"))
    counts.append(counts_row("claude-opus-raw", "locked194", locked, "n_raw"))
    counts.append(counts_row("claude-opus-unique", "locked194", locked, "n_unique"))

    # n=500 expansion, if the git objects are present.
    expansion, err = load_expansion_generation(FVERIFY_SHA)
    fv_bundle = load_expansion_fverify(FVERIFY_SHA) if expansion else None
    if expansion is None:
        notes.append(f"n=500 expansion not scored: {err}")
    else:
        if expansion["problems"]:
            notes.append("gold join failed for: " + "; ".join(expansion["problems"][:8]))
        else:
            for subset in ("plus106", "expand200", "expand500_rest"):
                rows = expansion[subset]
                t1 = rec = 0
                for r in rows:
                    a, b = raw_top3(r["raw"], r["truth"])
                    t1 += int(a)
                    rec += int(b)
                curve.extend(curve_rows(
                    "claude-opus-raw-top3-scorer", subset, rows, KS,
                    "first k raw strings; gold join on formula+IR+13C; no chamfer on this row",
                ))
                counts.append(counts_row("claude-opus-raw", subset, rows, "n_raw"))
                counts.append(counts_row("claude-opus-unique", subset, rows, "n_unique"))
                if subset == "plus106":
                    checks.append({
                        "name": "plus106_raw_top3",
                        "got": f"{t1}/{len(rows)} and {rec}/{len(rows)}",
                        "expect": "63/106 and 68/106",
                        "ok": len(rows) == 106 and t1 == 63 and rec == 68,
                    })
                if subset == "expand200":
                    checks.append({
                        "name": "expand200_raw_top3",
                        "got": f"{t1}/{len(rows)} and {rec}/{len(rows)}",
                        "expect": "109/200 and 116/200",
                        "ok": len(rows) == 200 and t1 == 109 and rec == 116,
                    })
            # Headline 500 = locked 194 + plus106 + expand200, raw top-3 scorer.
            headline = locked + expansion["plus106"] + expansion["expand200"]
            t1 = rec = 0
            for r in headline:
                a, b = raw_top3(r["raw"], r["truth"])
                t1 += int(a)
                rec += int(b)
            checks.append({
                "name": "n500_raw_top3",
                "got": f"top1 {t1}/{len(headline)} recall {rec}/{len(headline)}",
                "expect": "227/500 and 249/500",
                "ok": len(headline) == 500 and t1 == 227 and rec == 249,
            })
            curve.extend(curve_rows(
                "claude-opus-raw-top3-scorer", "n500", headline, KS,
                "locked 194 + plus106 + expand200; first k raw strings",
            ))
            counts.append(counts_row("claude-opus-raw", "n500", headline, "n_raw"))
            counts.append(counts_row("claude-opus-unique", "n500", headline, "n_unique"))

        if fv_bundle and not expansion["problems"]:
            for subset, bundle_name in (("plus106", "plus106"), ("expand200", "expand500")):
                rows = expansion[subset]
                # expand200 is a cut of the expand500 candidate file
                if subset == "expand200":
                    keep = {r["qid"] for r in rows}
                    bundle = {
                        "by": {q: v for q, v in fv_bundle["expand500"]["by"].items() if q in keep},
                        "amap": fv_bundle["expand500"]["amap"],
                        "pred": fv_bundle["expand500"]["pred"],
                    }
                else:
                    bundle = fv_bundle[bundle_name]
                fv_rows = expansion_fv_records(rows, bundle)
                curve.extend(curve_rows(
                    "fverify-expansion", subset, fv_rows, KS,
                    "deposited fverify candidates, self_rank order, chamfer on the prefix",
                ))
                counts.append(counts_row("fverify-expansion", subset, fv_rows, "n_unique"))
                full = aggregate(fv_rows, 10_000)
                if subset == "plus106":
                    checks.append({
                        "name": "plus106_fverify_full",
                        "got": (f"recall {full['recall']}/{full['n']} self {full['self_top1']} "
                                f"verify {full['verify_top1']}"),
                        "expect": "68/106, 63, 56",
                        "ok": full["n"] == 106 and (full["recall"], full["self_top1"], full["verify_top1"]) == (68, 63, 56),
                    })
                if subset == "expand200":
                    checks.append({
                        "name": "expand200_fverify_full",
                        "got": (f"recall {full['recall']}/{full['n']} self {full['self_top1']} "
                                f"verify {full['verify_top1']}"),
                        "expect": "116/200, 109, 90",
                        "ok": full["n"] == 200 and (full["recall"], full["self_top1"], full["verify_top1"]) == (116, 109, 90),
                    })
            # n=500 forward-verify = deposited n=194 + plus106 + expand200
            fv_plus = [r for r in curve if r["arm"] == "fverify-expansion" and r["subset"] == "plus106" and r["k"] >= 1000]
            # rebuild from records rather than from the aggregated curve
            fv_n500 = fv194 + expansion_fv_records(expansion["plus106"], fv_bundle["plus106"])
            exp_keep = {r["qid"] for r in expansion["expand200"]}
            fv_n500 += expansion_fv_records(expansion["expand200"], {
                "by": {q: v for q, v in fv_bundle["expand500"]["by"].items() if q in exp_keep},
                "amap": fv_bundle["expand500"]["amap"],
                "pred": fv_bundle["expand500"]["pred"],
            })
            curve.extend(curve_rows(
                "fverify-expansion", "n500", fv_n500, KS,
                "n194 deposited + expansion fverify logs; chamfer on the prefix",
            ))
            counts.append(counts_row("fverify-expansion", "n500", fv_n500, "n_unique"))
            full = aggregate(fv_n500, 10_000)
            checks.append({
                "name": "n500_fverify_full",
                "got": (f"n {full['n']} recall {full['recall']} verify {full['verify_top1']} "
                        f"rank_miss {full['rank_miss_verify']} gen_miss {full['gen_miss']}"),
                "expect": "500, recall 249, verify 204, rank_miss 45, gen_miss 251",
                "ok": (full["n"], full["recall"], full["verify_top1"],
                       full["rank_miss_verify"], full["gen_miss"]) == (500, 249, 204, 45, 251),
            })

    gen = generator_lengths()
    if gen:
        notes.append(
            f"generator probe: {gen['n_qids']} qids, unique SMILES "
            f"sum {gen['lengths']['sum']}, mean {gen['lengths']['mean']:.2f}, "
            f"median {gen['lengths']['median']}, max {gen['lengths']['max']}. {gen['note']}"
        )

    # DeepSeek / Nemotron are cited in the paper and are not in sweep_out.
    if not glob.glob("sweep_out/**/*deepseek*") and not os.path.isdir("data/cross_vendor"):
        notes.append(
            "DeepSeek V4 Pro and Nemotron replies are not in the tree. "
            "docs/MODELS.md points at data/cross_vendor/, which is gitignored and absent here."
        )

    # Drop the duplicate n_raw count row that counts_row wrote under the original arm
    # with length n_raw, keeping the explicitly named claude-opus raw row.
    write_csv(OUT / "k_curve.csv", curve)
    write_csv(OUT / "candidate_counts.csv", counts)
    with open(OUT / "checks.json", "w") as fh:
        json.dump({"checks": checks, "notes": notes, "sweep_meta": sweep_meta,
                   "fverify_sha": FVERIFY_SHA,
                   "raw_n60": raw_stats, "unique_n60": uniq_stats,
                   "published_union": pub}, fh, indent=2)

    import matplotlib.pyplot as plt
    draw(curve)
    plt.close("all")
    draw_hist(counts)

    failed = [c for c in checks if not c["ok"]]
    print(f"compounds in original n60: {len(base)}")
    print(f"raw candidates {raw_stats['sum']}/{raw_stats['n']} mean {raw_stats['mean']:.4f} "
          f"median {raw_stats['median']} hist {raw_stats['hist']}")
    print(f"unique candidates {uniq_stats['sum']}/{uniq_stats['n']} mean {uniq_stats['mean']:.4f} "
          f"median {uniq_stats['median']} hist {uniq_stats['hist']}")
    print(f"checks: {len(checks) - len(failed)}/{len(checks)} passed")
    for c in checks:
        mark = "OK " if c["ok"] else "FAIL"
        print(f"  {mark} {c['name']}: {c['got']} (expect {c['expect']})")
    for n in notes:
        print(f"NOTE {n}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
