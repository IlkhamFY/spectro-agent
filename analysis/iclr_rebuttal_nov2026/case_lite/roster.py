"""Locked n=500 roster for the CASE-lite diagnostic.

The loader follows analysis/rebuttal_pack/cohort.py on
cursor/rebuttal-analysis-pack-783b (commit d0fa2e6): the validated main round,
all of benchmark_v3, all of benchmark_v2_ctrl, every compound in
data/benchmark_expand at EXPAND_SHA, and the committed 200-qid cut of
data/benchmark_expand_500. Ground truth for the expansion arms is the unique
(formula, IR, 13C) join to data/irexp_resolved. That join is the same one the
locked rescore used.

Gold SMILES are returned only inside the `gold` dict. `public` rows are the
enumerator/ranker inputs: formula, printed IR, printed 13C, and the locked
LLM candidate SMILES. Callers that enumerate must not read `gold`.
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
GOLD_PATH = ROOT / "data" / "irexp_resolved" / "irexp_resolved.jsonl.gz"

# Locked generation wall on this roster (self-rank, not the forward-verify wall).
# 227 top-1 + 22 proposed at k<=3 but not rank 1 + 251 never proposed = 500.
# The forward-verify wall on the same molecules is 204 / 45 / 251 and is not
# what "proposed at k<=3" means.
EXPECTED_WALL = {"top1": 227, "proposed_not_top1": 22, "never": 251}


def q_c13(s):
    """Shifts printed with an assignment parenthesis. Same parser as the lock join."""
    return [round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", s or "")]


def g_c13(s):
    if "(" in (s or ""):
        return q_c13(s)
    return [round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", s or "")]


def ir_key(bands):
    return tuple(round(float(x), 1) for x in (bands or []))


def _git_show(sha, path):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT)


def _read_jsonl_bytes(blob):
    rows = []
    for line in blob.decode().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _index_gold(formulas):
    by = defaultdict(list)
    with gzip.open(GOLD_PATH, "rt") as fh:
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
            by[(form, ir_key(r.get("ir_bands_cm-1")), tuple(g_c13(r.get("c_nmr"))))].append({
                "smiles": Chem.MolToSmiles(m),
                "ik": (r.get("inchikey") or Chem.MolToInchiKey(m))[:14],
            })
    return by


def _match(q, gold):
    key = (q["formula"], ir_key(q.get("ir_bands_cm-1")), tuple(q_c13(q.get("c_nmr"))))
    hits = gold.get(key, [])
    if len(hits) != 1:
        raise SystemExit(f"{q.get('qid')}: expected 1 gold hit, got {len(hits)}")
    return hits[0]


def _llm_class(gold_ik, cands):
    flags = []
    for smi in (cands or [])[:3]:
        m = Chem.MolFromSmiles(smi) if smi else None
        ik = Chem.MolToInchiKey(m)[:14] if m else None
        flags.append(ik == gold_ik and gold_ik is not None)
    if not flags or gold_ik is None:
        return "never"
    if flags[0]:
        return "top1"
    if any(flags):
        return "proposed_not_top1"
    return "never"


def _row(q, hit, cohort, arm, cands):
    cands = list(cands or [])[:3]
    observed = q_c13(q.get("c_nmr"))
    # Printed lists with no assignment parentheses still carry numeric shifts.
    if not observed:
        observed = g_c13(q.get("c_nmr"))
    return {
        "public": {
            "uid": f"{cohort}:{q['qid']}",
            "cohort": cohort,
            "qid": q["qid"],
            "arm": arm,
            "formula": q["formula"],
            "difficulty": q.get("difficulty") or "?",
            "ir_bands_cm-1": [float(x) for x in (q.get("ir_bands_cm-1") or [])],
            "c_nmr_shifts": observed,
            "llm_candidates": cands,
        },
        "gold": {
            "uid": f"{cohort}:{q['qid']}",
            "smiles": hit["smiles"],
            "ik": hit["ik"],
            "llm_class": _llm_class(hit["ik"], cands),
        },
    }


def load():
    if not GOLD_PATH.exists():
        raise SystemExit(f"missing gold corpus: {GOLD_PATH}")
    formulas = set()
    for directory in ("benchmark_main", "benchmark_v3", "benchmark_v2_ctrl"):
        for line in open(ROOT / "data" / directory / "questions2.jsonl"):
            formulas.add(json.loads(line)["formula"])
    for round_dir in ("data/benchmark_expand", "data/benchmark_expand_500"):
        for row in _read_jsonl_bytes(_git_show(EXPAND_SHA, f"{round_dir}/questions2.jsonl")):
            formulas.add(row["formula"])
    gold = _index_gold(formulas)

    rows = []
    answers = {json.loads(l)["qid"]: json.loads(l) for l in open(ROOT / "data/benchmark_main/answers2.jsonl")}
    questions = {json.loads(l)["qid"]: json.loads(l) for l in open(ROOT / "data/benchmark_main/questions2.jsonl")}
    clean = set(json.load(open(ROOT / "data/benchmark_main/clean_qids.json")))
    pred = {}
    for f in sorted((ROOT / "data/benchmark_main/raw").glob("*.json")):
        pred.update(json.load(open(f)))
    for qid, ans in answers.items():
        if qid not in clean:
            continue
        cands = pred.get(f"M-{qid}")
        if cands is None:
            continue
        q = dict(questions[qid])
        q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
        hit = _match(q, gold)
        if hit["ik"] != ans["inchikey"][:14]:
            raise SystemExit(f"main {qid}: join InChIKey != committed answer key")
        rows.append(_row(q, hit, "locked-main", "locked194", cands))

    for cohort, directory, arm in (
        ("locked-v3", "benchmark_v3", "locked194"),
        ("locked-v2ctrl", "benchmark_v2_ctrl", "locked194"),
    ):
        base = ROOT / "data" / directory
        aa = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "answers2.jsonl")}
        qq = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "questions2.jsonl")}
        pp = {json.loads(l)["qid"]: json.loads(l) for l in open(base / "predictions2.jsonl")}
        for qid, ans in aa.items():
            q = dict(qq[qid])
            q["difficulty"] = ans.get("difficulty") or q.get("difficulty")
            hit = _match(q, gold)
            if hit["ik"] != ans["inchikey"][:14]:
                raise SystemExit(f"{directory} {qid}: join InChIKey != committed answer key")
            rows.append(_row(q, hit, cohort, arm, pp[qid].get("candidates", [])))

    if len(rows) != 194:
        raise SystemExit(f"locked slice is {len(rows)}, expected 194")

    def load_expansion(round_dir, cohort, arm, keep=None):
        qs = _read_jsonl_bytes(_git_show(EXPAND_SHA, f"{round_dir}/questions2.jsonl"))
        preds = {
            r["qid"]: r.get("candidates", [])
            for r in _read_jsonl_bytes(_git_show(EXPAND_SHA, f"{round_dir}/predictions2.jsonl"))
        }
        out = []
        for q in qs:
            if keep is not None and q["qid"] not in keep:
                continue
            hit = _match(q, gold)
            out.append(_row(q, hit, cohort, arm, preds.get(q["qid"], [])))
        return out

    rows += load_expansion("data/benchmark_expand", "expand", "plus106")
    cut = set(json.loads(_git_show(EXPAND_SHA, "data/benchmark_expand_500/headline500_expand200_qids.json")))
    e200 = load_expansion("data/benchmark_expand_500", "expand500", "expand200", keep=cut)
    rows += e200
    if len(rows) != 500:
        raise SystemExit(f"headline length {len(rows)}")

    counts = {"top1": 0, "proposed_not_top1": 0, "never": 0}
    for r in rows:
        counts[r["gold"]["llm_class"]] += 1
    if counts != EXPECTED_WALL:
        raise SystemExit(f"LLM wall {counts} != locked {EXPECTED_WALL}")
    return rows
