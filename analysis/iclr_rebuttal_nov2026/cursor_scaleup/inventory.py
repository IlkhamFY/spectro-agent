#!/usr/bin/env python3
"""Inventory every structure-prediction deposit in this checkout and score the
prefixes that were actually stored.

No model is called. Gold SMILES are not printed. A row is written for each
k from 1 through the longest stored list in that deposit. k beyond that
maximum is omitted rather than filled with the plateau.

    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/inventory.py
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
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
sys.path.insert(0, str(ROOT / "scripts"))
from specmetrics import chamfer, ik14  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
FVERIFY_SHA = "473030fb9d046548ff1ad06d04d20915fc2943d2"
GOLD = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"


def git_bytes(sha: str, path: str) -> bytes | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{sha}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None


def git_json(sha: str, path: str):
    blob = git_bytes(sha, path)
    return None if blob is None else json.loads(blob.decode())


def git_jsonl(sha: str, path: str) -> list[dict] | None:
    blob = git_bytes(sha, path)
    if blob is None:
        return None
    return [json.loads(line) for line in blob.decode().splitlines() if line.strip()]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def canon(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    return Chem.MolToSmiles(mol) if mol else None


def obs_c13(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or "")]


def q_c13(text: str) -> tuple:
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or ""))


def g_c13(text: str) -> tuple:
    if "(" in (text or ""):
        return q_c13(text)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", text or ""))


def ir_key(bands) -> tuple:
    return tuple(round(float(x), 1) for x in (bands or []))


def dedupe(smiles_list) -> list[str]:
    out, seen = [], set()
    for smiles in smiles_list or []:
        c = canon(smiles)
        if not c or c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def merge_raw(pattern: str) -> dict:
    """Later path in sorted order overwrites the same key. Documented in REPORT."""
    merged = {}
    for path in sorted(glob.glob(pattern)):
        merged.update(json.load(open(path)))
    return merged


def answers_by_qid(path: Path) -> dict[str, dict]:
    return {row["qid"]: row for row in load_jsonl(path)}


def questions_by_qid(path: Path) -> dict[str, dict]:
    return {row["qid"]: row for row in load_jsonl(path)}


def index_gold(formulas: set[str]) -> dict:
    by = defaultdict(list)
    with gzip.open(GOLD, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            smiles = row.get("smiles")
            if not smiles:
                continue
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(mol)
            if form not in formulas:
                continue
            by[(form, ir_key(row.get("ir_bands_cm-1")), g_c13(row.get("c_nmr")))].append(
                (row.get("inchikey") or Chem.MolToInchiKey(mol))[:14]
            )
    return by


def match_ik(question: dict, gold: dict) -> str:
    hits = gold.get(
        (question["formula"], ir_key(question.get("ir_bands_cm-1")), q_c13(question.get("c_nmr"))),
        [],
    )
    uniq = sorted(set(hits))
    if len(uniq) != 1:
        raise SystemExit(f"{question.get('qid')}: expected 1 gold hit, got {len(uniq)}")
    return uniq[0]


def load_pred_canon(rawglob: str, mapfile: str) -> dict[str, list]:
    if not os.path.exists(mapfile):
        return {}
    amap = json.load(open(mapfile))
    pred = {}
    for path in glob.glob(rawglob):
        pred.update(json.load(open(path)))
    out = {}
    for smiles, aid in amap.items():
        c = canon(smiles)
        if c and aid in pred:
            out[c] = pred[aid]
    return out


def raw_prefix_hit(raw: list, truth: str, k: int) -> tuple[bool, bool]:
    """Headline scorer: first k raw strings, unparseable does not match and is not skipped."""
    prefix = list(raw)[:k]
    iks = [ik14(s) for s in prefix]
    top1 = bool(iks) and iks[0] == truth
    recall = truth in iks
    return top1, recall


def unique_prefix_hit(ordered: list[str], truth: str, k: int) -> tuple[bool, bool]:
    prefix = ordered[:k]
    iks = [ik14(s) for s in prefix]
    top1 = bool(iks) and iks[0] == truth
    recall = truth in iks
    return top1, recall


def fv_hit(ordered: list[str], truth: str, pred: dict, obs: list, k: int) -> bool | None:
    """Empty prefix is a defined miss when a forward-verify map exists.

    V3-R27 has no generate-wide list. Dropping it from the denominator would
    turn 18/60 into 18/59.
    """
    if pred is None or obs is None:
        return None
    pool = ordered[:k]
    if not pool:
        return False
    dists = []
    for smiles in pool:
        p = pred.get(smiles)
        dists.append(chamfer(p, obs) if p else 999.0)
    best = min(range(len(pool)), key=lambda i: (dists[i], i))
    return ik14(pool[best]) == truth


def fraction(num: int, den: int) -> str:
    return f"{num}/{den}" if den else "0/0"


def add_deposit(rows: list, prefixes: list, *, model: str, subset: str, path: str,
                order: str, items: list[dict], note: str, score_unique_curve: bool,
                score_fv: bool) -> None:
    """items: raw (list[str]), truth (str), ordered (list[str] canonical), obs, pred."""
    n = len(items)
    if n == 0:
        rows.append({
            "model": model, "subset": subset, "n": 0, "max_stored_raw": 0,
            "max_stored_unique": 0, "top1": "0/0", "recall": "0/0",
            "precision_given_recall": "0/0", "order": order, "path": path, "note": note,
        })
        return
    max_raw = max(len(it["raw"]) for it in items)
    max_unique = max(len(it["ordered"]) for it in items)
    # Full stored list, raw order, which is the deposited protocol for k<=3 arms
    # and the whole returned list for longer arms.
    top1 = recall = 0
    for it in items:
        k_full = len(it["raw"])
        t, r = raw_prefix_hit(it["raw"], it["truth"], k_full if k_full else 0)
        # empty list: miss
        if k_full == 0:
            t, r = False, False
        top1 += int(t)
        recall += int(r)
    rows.append({
        "model": model,
        "subset": subset,
        "n": n,
        "max_stored_raw": max_raw,
        "max_stored_unique": max_unique,
        "top1": fraction(top1, n),
        "recall": fraction(recall, n),
        "precision_given_recall": fraction(top1, recall),
        "order": order,
        "path": path,
        "note": note,
    })
    if not score_unique_curve or max_unique == 0:
        return
    for k in range(1, max_unique + 1):
        t_n = r_n = ge = fv_n = fv_def = 0
        for it in items:
            ge += int(len(it["ordered"]) >= k)
            t, r = unique_prefix_hit(it["ordered"], it["truth"], k)
            t_n += int(t)
            r_n += int(r)
            if score_fv and it.get("pred") is not None and it.get("obs") is not None:
                hit = fv_hit(it["ordered"], it["truth"], it["pred"], it["obs"], k)
                if hit is not None:
                    fv_def += 1
                    fv_n += int(hit)
        prefixes.append({
            "model": model,
            "subset": subset,
            "order": order,
            "k": k,
            "n": n,
            "n_lists_ge_k": ge,
            "top1_self": fraction(t_n, n),
            "recall": fraction(r_n, n),
            "precision_given_recall": fraction(t_n, r_n),
            "top1_forward_verify": fraction(fv_n, fv_def) if fv_def else "",
            "identified": "true",
            "path": path,
            "note": note,
        })


def controlled_60() -> list[dict]:
    items = []
    for directory, tag in (("data/benchmark_v3", "V3"), ("data/benchmark_v2_ctrl", "CT")):
        questions = questions_by_qid(ROOT / directory / "questions2.jsonl")
        answers = answers_by_qid(ROOT / directory / "answers2.jsonl")
        preds = {row["qid"]: row for row in load_jsonl(ROOT / directory / "predictions2.jsonl")}
        for qid, ans in answers.items():
            raw = list((preds.get(qid) or {}).get("candidates") or [])
            items.append({
                "key": f"{tag}-{qid}",
                "qid": qid,
                "dir": directory,
                "truth": ans["inchikey"][:14],
                "obs": obs_c13(questions[qid]["c_nmr"]),
                "raw": raw,
                "ordered": dedupe(raw),
            })
    return items


def wide_lists() -> dict[str, list]:
    wide = {}
    for path in sorted(glob.glob(str(ROOT / "data/gw/raw/g*.json"))):
        if "sonnet" in os.path.basename(path):
            continue
        for key, smiles in json.load(open(path)).items():
            wide.setdefault(key, []).extend(smiles)
    return wide


def sonnet_wide() -> dict[str, list]:
    out = {}
    for path in sorted(glob.glob(str(ROOT / "data/gw/raw/sonnet_*.json"))):
        for key, smiles in json.load(open(path)).items():
            out.setdefault(key, []).extend(smiles)
    return out


def mid_map() -> dict[str, dict]:
    """Same id order as scripts/cross_vendor_sweep.py load_rows('fverify60')."""
    rows = []
    for directory in ("data/benchmark_v3", "data/benchmark_v2_ctrl"):
        questions = questions_by_qid(ROOT / directory / "questions2.jsonl")
        answers = answers_by_qid(ROOT / directory / "answers2.jsonl")
        for qid, ans in answers.items():
            q = questions[qid]
            rows.append({
                "src": f"{directory.split('/')[-1]}:{qid}",
                "difficulty": ans.get("difficulty") or q.get("difficulty"),
                "truth": ans["inchikey"][:14],
                "obs": obs_c13(q.get("c_nmr")),
                "key": ("V3" if directory.endswith("v3") else "CT") + f"-{qid}",
            })
    rows.sort(key=lambda r: (r["difficulty"], r["src"]))
    return {f"M{i:03d}": row for i, row in enumerate(rows, 1)}


def load_reply_dir(directory: str, mapping: dict[str, dict]) -> list[dict]:
    merged = merge_raw(str(ROOT / directory / "reply_*.json"))
    items = []
    for mid, meta in mapping.items():
        raw = list(merged.get(mid) or [])
        items.append({
            "raw": raw,
            "ordered": dedupe(raw),
            "truth": meta["truth"],
            "obs": meta["obs"],
            "pred": None,
        })
    return items


def jsonl_candidates(path: Path, answers: dict[str, dict], keyfn) -> list[dict]:
    preds = {row["qid"]: row for row in load_jsonl(path)}
    items = []
    for qid, ans in answers.items():
        raw = list((preds.get(qid) or {}).get("candidates") or [])
        items.append({
            "raw": raw, "ordered": dedupe(raw), "truth": ans["inchikey"][:14],
            "obs": None, "pred": None, "local": keyfn(qid),
        })
    return items


def expansion_items(sha: str, qpath: str, ppath: str, keep: set[str] | None) -> list[dict]:
    questions = git_jsonl(sha, qpath) or []
    preds = {row["qid"]: row.get("candidates") or [] for row in (git_jsonl(sha, ppath) or [])}
    formulas = {q["formula"] for q in questions if keep is None or q["qid"] in keep}
    gold = index_gold(formulas)
    items = []
    for q in questions:
        if keep is not None and q["qid"] not in keep:
            continue
        raw = list(preds.get(q["qid"]) or [])
        truth = match_ik(q, gold)
        items.append({
            "raw": raw, "ordered": dedupe(raw), "truth": truth,
            "obs": obs_c13(q.get("c_nmr")), "pred": None, "qid": q["qid"],
        })
    return items


def fable_expand_items(sha: str) -> list[dict]:
    listing = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", sha], cwd=ROOT, text=True
    )
    paths = sorted(
        p for p in listing.splitlines()
        if p.startswith("data/benchmark_expand/raw_fable/") and p.endswith(".json")
    )
    by_qid = {}
    for path in paths:
        blob = json.loads(git_bytes(sha, path).decode())
        rows = blob if isinstance(blob, list) else [{"qid": k, "candidates": v} for k, v in blob.items()]
        for row in rows:
            qid = row["qid"]
            if qid.startswith("M-"):
                qid = qid[2:]
            by_qid[qid] = list(row.get("candidates") or [])
    questions = {q["qid"]: q for q in git_jsonl(sha, "data/benchmark_expand/questions2.jsonl")}
    gold = index_gold({questions[q]["formula"] for q in by_qid if q in questions})
    items = []
    for qid, raw in sorted(by_qid.items()):
        q = questions.get(qid)
        if q is None:
            continue
        items.append({
            "raw": raw, "ordered": dedupe(raw), "truth": match_ik(q, gold),
            "obs": None, "pred": None,
        })
    return items


def generator_set() -> tuple[int, int, int, int]:
    """Unordered full-pool recall. The file is sorted canonical SMILES, so no prefix curve."""
    blob = json.load(open(ROOT / "contrib/generator_probe/artifacts/gen_candidates.jsonl"))
    # Map keys onto answer keys. Main-round bare qids use benchmark_main answers.
    main_ans = answers_by_qid(ROOT / "data/benchmark_main/answers2.jsonl")
    other = {}
    for directory in (
        "data/benchmark_v3", "data/benchmark_v2_ctrl", "data/benchmark_v2",
        "data/benchmark_electrolyte",
    ):
        cohort = directory.split("/")[-1]
        for row in load_jsonl(ROOT / directory / "answers2.jsonl"):
            other[f"data/{cohort}:{row['qid']}"] = row["inchikey"][:14]
            other[f"{cohort}:{row['qid']}"] = row["inchikey"][:14]
    n = hit = mapped = max_len = 0
    for key, smiles in blob.items():
        n += 1
        max_len = max(max_len, len(smiles))
        if key in main_ans:
            truth = main_ans[key]["inchikey"][:14]
        elif key in other:
            truth = other[key]
        else:
            continue
        mapped += 1
        iks = {ik14(s) for s in smiles}
        hit += int(truth in iks)
    return n, mapped, hit, max_len


def main() -> None:
    os.chdir(ROOT)
    deposits = []
    prefixes = []

    # Pilot, one SMILES.
    pilot_q = questions_by_qid(ROOT / "data/benchmark/questions.jsonl")
    pilot_a = answers_by_qid(ROOT / "data/benchmark/answers.jsonl")
    pilot_p = {row["qid"]: [row["smiles"]] for row in load_jsonl(ROOT / "data/benchmark/predictions.jsonl")}
    pilot_items = []
    for qid, ans in pilot_a.items():
        raw = pilot_p.get(qid, [])
        pilot_items.append({"raw": raw, "ordered": dedupe(raw), "truth": ans["inchikey"][:14]})
    add_deposit(
        deposits, prefixes, model="Claude Opus 4.8 (pilot, one context)", subset="n21",
        path="data/benchmark/predictions.jsonl", order="single SMILES",
        items=pilot_items, score_unique_curve=True, score_fv=False,
        note="docs/MODELS.md pilot. k=1 only. Not part of 227/500.",
    )

    # Long-context v2 arm. Separate from the controlled 20.
    v2_items = jsonl_candidates(
        ROOT / "data/benchmark_v2/predictions2.jsonl",
        answers_by_qid(ROOT / "data/benchmark_v2/answers2.jsonl"),
        lambda q: q,
    )
    add_deposit(
        deposits, prefixes, model="Claude Opus (one long context)", subset="n20-long-context",
        path="data/benchmark_v2/predictions2.jsonl", order="model rank",
        items=v2_items, score_unique_curve=True, score_fv=False,
        note="§4.3 arm (a). Not the controlled 20 and not inside 227/500.",
    )

    base60 = controlled_60()
    pred = {}
    pred.update(load_pred_canon("data/fverify/raw/*.json", "data/fverify/anon_map.json"))
    pred.update(load_pred_canon("data/fverify2/raw/*.json", "data/fverify2/anon_map2.json"))
    pred.update(load_pred_canon("data/fverify_gw/raw/*.json", "data/fverify_gw/anon_map.json"))
    for it in base60:
        it["pred"] = pred
    add_deposit(
        deposits, prefixes, model="Claude Opus (original ≤3)", subset="n60",
        path="data/benchmark_v3/predictions2.jsonl + data/benchmark_v2_ctrl/predictions2.jsonl",
        order="model rank", items=base60, score_unique_curve=True, score_fv=True,
        note="Vendor-comparison denominator. Nested inside the locked 194.",
    )

    wide = wide_lists()
    wide_only, pooled = [], []
    missing = []
    for it in base60:
        wraw = wide.get(it["key"])
        if wraw is None:
            missing.append(it["key"])
            wraw = []
        w_ordered = dedupe(wraw)
        pool = list(it["ordered"])
        have = set(pool)
        for smiles in w_ordered:
            if smiles not in have:
                pool.append(smiles)
                have.add(smiles)
        wide_only.append({
            "raw": wraw, "ordered": w_ordered, "truth": it["truth"],
            "obs": it["obs"], "pred": pred,
        })
        pooled.append({
            "raw": list(it["raw"]) + list(wraw), "ordered": pool, "truth": it["truth"],
            "obs": it["obs"], "pred": pred,
        })
    add_deposit(
        deposits, prefixes, model="Claude Opus generate-wide", subset="n60",
        path="data/gw/raw/g1.json–g10.json", order="file order (g1..g10); confidence order was not stored",
        items=wide_only, score_unique_curve=True, score_fv=True,
        note=("Asked for up to 6. " + (f"Missing wide list: {', '.join(missing)}. " if missing else "")
              + "Empty list stays in the denominator. Prefixes past 3 are stored."),
    )
    add_deposit(
        deposits, prefixes, model="Claude Opus original then generate-wide", subset="n60",
        path="data/benchmark_v3 + data/benchmark_v2_ctrl predictions, then data/gw/raw/g*.json",
        order="original model rank, then wide file order",
        items=pooled, score_unique_curve=True, score_fv=True,
        note="Longest stored LLM pool on this 60. Not an ask for 10.",
    )

    sw = sonnet_wide()
    sonnet_items = []
    for it in base60:
        raw = list(sw.get(it["key"]) or [])
        if it["key"] not in sw:
            continue
        sonnet_items.append({
            "raw": raw, "ordered": dedupe(raw), "truth": it["truth"],
            "obs": it["obs"], "pred": None,
        })
    add_deposit(
        deposits, prefixes, model="Claude Sonnet generate-wide", subset=f"n{len(sonnet_items)}",
        path="data/gw/raw/sonnet_b1.json + sonnet_b2.json",
        order="file order", items=sonnet_items, score_unique_curve=True, score_fv=False,
        note="Covers 12 of the 60. No forward-verify map. Prefixes past 3 are stored.",
    )

    mapping = mid_map()
    for model, directory, note in (
        ("grok-4.6", "sweep_out/grok-4.6", "Asked for 3. No list longer than 3."),
        ("grok-4.6-clean", "sweep_out/grok-4.6-clean", "Clone. No verify log. No list longer than 3."),
        ("gemini-3.7-flash", "sweep_out/gemini-3.7-flash", "Asked for 3. No list longer than 3."),
        ("gpt-5.6-sol", "sweep_out/gpt-5.6-sol", "Asked for 3. No list longer than 3."),
        ("gpt-5.6-luna", "sweep_out/gpt-5.6-luna", "Asked for 3. No list longer than 3."),
        ("composer-2.5", "sweep_out/composer-2.5", "Asked for 3. Some lists are empty. No list longer than 3."),
    ):
        add_deposit(
            deposits, prefixes, model=model, subset="n60", path=directory,
            order="model rank (M001.. order of cross_vendor_sweep.load_rows)",
            items=load_reply_dir(directory, mapping), score_unique_curve=True, score_fv=False,
            note=note,
        )

    for name, path in (
        ("Claude Opus modality full", "data/modality/out_full.json"),
        ("Claude Opus formula-only", "data/modality/out_formulaonly.json"),
    ):
        blob = json.load(open(ROOT / path))
        items = []
        for mid, meta in mapping.items():
            raw = list(blob.get(mid) or [])
            items.append({"raw": raw, "ordered": dedupe(raw), "truth": meta["truth"]})
        add_deposit(
            deposits, prefixes, model=name, subset="n60", path=path, order="model rank",
            items=items, score_unique_curve=True, score_fv=False,
            note="Same 60, M-id order as the vendor sweep. No list longer than 3.",
        )

    # Locked 194 pieces and the 500.
    main_ans = answers_by_qid(ROOT / "data/benchmark_main/answers2.jsonl")
    main_q = questions_by_qid(ROOT / "data/benchmark_main/questions2.jsonl")
    clean = set(json.load(open(ROOT / "data/benchmark_main/clean_qids.json")))
    opus_raw = merge_raw("data/benchmark_main/raw/*.json")
    main_items = []
    for qid in sorted(clean):
        raw = list(opus_raw.get(f"M-{qid}") or opus_raw.get(qid) or [])
        if f"M-{qid}" not in opus_raw and qid not in opus_raw:
            continue
        main_items.append({
            "raw": raw, "ordered": dedupe(raw), "truth": main_ans[qid]["inchikey"][:14],
        })
    add_deposit(
        deposits, prefixes, model="Claude Opus", subset="main-clean",
        path="data/benchmark_main/raw/*.json", order="model rank",
        items=main_items, score_unique_curve=True, score_fv=False,
        note="Spectrally validated main round. Keys M-<qid>. Sorted paths, later file wins.",
    )
    for label, pattern in (
        ("Claude Sonnet", "data/benchmark_main/sonnet/*.json"),
        ("Claude Haiku", "data/benchmark_main/haiku/*.json"),
        ("Claude Fable 5", "data/benchmark_main/fable/*.json"),
    ):
        blob = merge_raw(pattern)
        items = []
        for key, raw in blob.items():
            qid = key[2:] if key.startswith("M-") else key
            if qid not in main_ans:
                continue
            items.append({"raw": list(raw), "ordered": dedupe(raw), "truth": main_ans[qid]["inchikey"][:14]})
        add_deposit(
            deposits, prefixes, model=label, subset="main24", path=pattern,
            order="model rank", items=items, score_unique_curve=True, score_fv=False,
            note="Fixed 24-compound ladder. No list longer than 3.",
        )
    ladder = ['R01','R02','R04','R05','R06','R07','R08','R09','R10','R11','R12','R13',
              'R15','R16','R17','R18','R19','R20','R21','R22','R23','R24','R25','R26']
    opus24 = []
    for qid in ladder:
        raw = list(opus_raw.get(f"M-{qid}") or [])
        opus24.append({"raw": raw, "ordered": dedupe(raw), "truth": main_ans[qid]["inchikey"][:14]})
    add_deposit(
        deposits, prefixes, model="Claude Opus (rescored main-round lists)", subset="main24",
        path="data/benchmark_main/raw/*.json", order="model rank",
        items=opus24, score_unique_curve=True, score_fv=False,
        note="Not a fresh 24-compound run. The §4.4 Opus column re-reads these lists. No list longer than 3.",
    )

    elec_ans = answers_by_qid(ROOT / "data/benchmark_electrolyte/answers2.jsonl")
    elec_raw = merge_raw("data/benchmark_electrolyte/raw/*.json")
    elec_items = []
    for key, raw in elec_raw.items():
        qid = key[2:] if key.startswith("E-") else key
        if qid not in elec_ans:
            continue
        elec_items.append({
            "raw": list(raw), "ordered": dedupe(raw), "truth": elec_ans[qid]["inchikey"][:14],
        })
    add_deposit(
        deposits, prefixes, model="Claude Opus", subset="electrolyte",
        path="data/benchmark_electrolyte/raw/*.json", order="model rank",
        items=elec_items, score_unique_curve=True, score_fv=False,
        note="Held out of 227/500. 48 curated questions; scored rows are those with a deposit.",
    )

    exp106 = expansion_items(
        EXPAND_SHA, "data/benchmark_expand/questions2.jsonl",
        "data/benchmark_expand/predictions2.jsonl", None,
    )
    add_deposit(
        deposits, prefixes, model="Claude Opus (expand +106)", subset="n106",
        path=f"{EXPAND_SHA}:data/benchmark_expand/predictions2.jsonl",
        order="model rank", items=exp106, score_unique_curve=True, score_fv=False,
        note="All 106 deposited, including five 13C-overread flags. Answer key withheld; unique (formula, IR, 13C) join.",
    )
    keep200 = set(git_json(EXPAND_SHA, "data/benchmark_expand_500/headline500_expand200_qids.json"))
    exp200 = expansion_items(
        EXPAND_SHA, "data/benchmark_expand_500/questions2.jsonl",
        "data/benchmark_expand_500/predictions2.jsonl", keep200,
    )
    exp230 = expansion_items(
        EXPAND_SHA, "data/benchmark_expand_500/questions2.jsonl",
        "data/benchmark_expand_500/predictions2.jsonl", None,
    )
    add_deposit(
        deposits, prefixes, model="Claude Opus 5 thinking-high (expand-500, 200-cut)",
        subset="n200", path=f"{EXPAND_SHA}:data/benchmark_expand_500/predictions2.jsonl",
        order="model rank", items=exp200, score_unique_curve=True, score_fv=False,
        note="String-sorted clean-qid prefix of 200. Inside the locked 500. Not an ask for 10.",
    )
    add_deposit(
        deposits, prefixes, model="Claude Opus 5 thinking-high (expand-500, all 230)",
        subset="n230", path=f"{EXPAND_SHA}:data/benchmark_expand_500/predictions2.jsonl",
        order="model rank", items=exp230, score_unique_curve=True, score_fv=False,
        note="Full draw. The locked headline keeps 200 of these, not 230.",
    )

    locked = main_items + [it for it in base60] + exp106 + exp200
    add_deposit(
        deposits, prefixes, model="Claude Opus family (locked headline, self-rank)",
        subset="n500", path="main raw + v3 + v2_ctrl + expand 106 + expand-500 200-cut",
        order="model rank", items=locked, score_unique_curve=True, score_fv=False,
        note="Must reproduce 227/500 top-1 and 249/500 recall. Not a new arm.",
    )

    fable_items = fable_expand_items(FVERIFY_SHA)
    add_deposit(
        deposits, prefixes, model="Claude Fable (partial +106)", subset=f"n{len(fable_items)}",
        path=f"{FVERIFY_SHA}:data/benchmark_expand/raw_fable/",
        order="model rank", items=fable_items, score_unique_curve=True, score_fv=False,
        note="Incomplete round. Not in the locked 500. Later sorted path overwrites a repeated qid.",
    )

    gen_n, gen_mapped, gen_hit, gen_max = generator_set()
    deposits.append({
        "model": "trained SELFIES generator (4-config ensemble)",
        "subset": f"n{gen_n}",
        "n": gen_mapped,
        "max_stored_raw": gen_max,
        "max_stored_unique": gen_max,
        "top1": "",
        "recall": fraction(gen_hit, gen_mapped),
        "precision_given_recall": "",
        "order": "sorted canonical SMILES (rank destroyed)",
        "path": "contrib/generator_probe/artifacts/gen_candidates.jsonl",
        "note": (f"File has {gen_n} keys, {gen_mapped} joined to an answer key. "
                 "Recall is the unordered full pool, not formula-filtered and not the published 60-compound generator figure. "
                 "No k-curve: a prefix of a sorted list is not a budget."),
    })

    # Checks that this scorer still hits the locked integers.
    def parse(frac: str) -> tuple[int, int]:
        a, b = frac.split("/")
        return int(a), int(b)

    locked_row = next(r for r in deposits if r["subset"] == "n500" and "locked" in r["model"])
    if locked_row["top1"] != "227/500" or locked_row["recall"] != "249/500":
        raise SystemExit(f"locked headline was not reproduced: {locked_row['top1']} {locked_row['recall']}")
    n60 = next(r for r in deposits if r["model"].startswith("Claude Opus (original"))
    if n60["top1"] != "14/60" or n60["recall"] != "19/60":
        raise SystemExit(f"n60 original was not reproduced: {n60['top1']} {n60['recall']}")
    pooled_row = next(r for r in deposits if r["model"].startswith("Claude Opus original then"))
    if pooled_row["recall"] != "25/60":
        raise SystemExit(f"generate-wide union recall was not 25/60: {pooled_row['recall']}")

    # Wider-than-3 prefixes must not exist for the locked 500.
    locked_prefix = [r for r in prefixes if r["subset"] == "n500"]
    if any(int(r["k"]) > 3 for r in locked_prefix):
        raise SystemExit("locked 500 has a stored prefix past 3; refusing to treat that as the headline budget")
    if any(r["identified"] != "true" for r in prefixes):
        raise SystemExit("a prefix row was not identified")

    inv_path = HERE / "inventory.csv"
    pre_path = HERE / "prefix_scores.csv"
    with inv_path.open("w", newline="") as handle:
        fields = ["model", "subset", "n", "max_stored_raw", "max_stored_unique",
                  "top1", "recall", "precision_given_recall", "order", "path", "note"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(deposits)
    with pre_path.open("w", newline="") as handle:
        fields = ["model", "subset", "order", "k", "n", "n_lists_ge_k", "top1_self",
                  "recall", "precision_given_recall", "top1_forward_verify",
                  "identified", "path", "note"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(prefixes)

    wider = [r for r in prefixes if int(r["k"]) >= 4]
    checks = {
        "locked_top1": locked_row["top1"],
        "locked_recall": locked_row["recall"],
        "locked_precision_given_recall": locked_row["precision_given_recall"],
        "n60_original_top1": n60["top1"],
        "n60_original_recall": n60["recall"],
        "wide_union_recall": pooled_row["recall"],
        "n_deposits": len(deposits),
        "n_prefix_rows": len(prefixes),
        "n_prefix_rows_k_ge_4": len(wider),
        "max_k_scored": max(int(r["k"]) for r in prefixes),
        "generator_unordered_recall": fraction(gen_hit, gen_mapped),
        "generator_file_keys": gen_n,
        "generator_max_stored": gen_max,
        "missing_wide_keys": missing,
        "expand_sha": EXPAND_SHA,
    }
    (HERE / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    print(f"deposits -> {inv_path}")
    print(f"prefixes -> {pre_path}")
    print("k past the stored maximum was not written.")


if __name__ == "__main__":
    main()
