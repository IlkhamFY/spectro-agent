"""Frozen printed-list payloads for the extra-solver runs.

Model-facing records contain the formula and the printed IR / 1H / 13C fields only.
The answer key is a separate object and is not an argument of any runner.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"


def _git_show(path: str) -> str:
    import subprocess
    return subprocess.check_output(["git", "show", f"{EXPAND_SHA}:{path}"], cwd=ROOT).decode()


def _q_c13(text: str) -> tuple:
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or ""))


def _g_c13(text: str) -> tuple:
    if "(" in (text or ""):
        return _q_c13(text)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", text or ""))


def _ir_key(bands) -> tuple:
    return tuple(round(float(x), 1) for x in (bands or []))


def _public_from_question(cohort: str, q: dict) -> dict:
    return {
        "uid": f"{cohort}:{q['qid']}",
        "cohort": cohort,
        "qid": q["qid"],
        "formula": q.get("formula") or "",
        "ir_bands_cm-1": list(q.get("ir_bands_cm-1") or []),
        "h_nmr": q.get("h_nmr") or "",
        "c_nmr": q.get("c_nmr") or "",
        "difficulty": q.get("difficulty") or "",
    }


def _gold_by_join(questions: list[dict]) -> dict[str, str]:
    """Unique (formula, IR, 13C) join against the resolved corpus. Scoring key only."""
    import gzip
    from collections import defaultdict

    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    from rdkit import RDLogger

    RDLogger.DisableLog("rdApp.*")
    formulas = {q["formula"] for q in questions}
    by = defaultdict(list)
    gold_path = ROOT / "data" / "irexp_resolved" / "irexp_resolved.jsonl.gz"
    with gzip.open(gold_path, "rt") as fh:
        for line in fh:
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
            key = (form, _ir_key(row.get("ir_bands_cm-1")), _g_c13(row.get("c_nmr")))
            ik = (row.get("inchikey") or Chem.MolToInchiKey(mol))[:14]
            by[key].append(ik)
    gold = {}
    for q in questions:
        key = (q["formula"], _ir_key(q.get("ir_bands_cm-1")), _q_c13(q.get("c_nmr")))
        hits = list(dict.fromkeys(by.get(key, [])))
        if len(hits) != 1:
            raise SystemExit(f"{q['uid']}: expected 1 gold hit, got {len(hits)}")
        gold[q["uid"]] = hits[0]
    return gold


def load_expand_headline() -> tuple[list[dict], dict[str, str]]:
    """The 306 expansion questions inside the locked n=500 headline, not the 194."""
    expand_rows = [json.loads(l) for l in _git_show("data/benchmark_expand/questions2.jsonl").splitlines() if l.strip()]
    rest_rows = [json.loads(l) for l in _git_show("data/benchmark_expand_500/questions2.jsonl").splitlines() if l.strip()]
    cut = set(json.loads(_git_show("data/benchmark_expand_500/headline500_expand200_qids.json")))
    public = [_public_from_question("expand", q) for q in expand_rows]
    public += [_public_from_question("expand500", q) for q in rest_rows if q["qid"] in cut]
    if len(public) != 306:
        raise SystemExit(f"headline expansion is {len(public)}, expected 306")
    # difficulty may live only on the question for these rounds
    gold = _gold_by_join(public)
    return public, gold


def load_arm(name: str = "60") -> tuple[list[dict], dict[str, str]]:
    """Return (public records, uid -> InChIKey-14).

    arm "60" is benchmark_v3 (40) plus benchmark_v2_ctrl (20), the forward-verify arm.
    arm "194" adds the clean locked main round.
    """
    specs = [("v3", "benchmark_v3"), ("v2ctrl", "benchmark_v2_ctrl")]
    if name == "306":
        return load_expand_headline()
    if name == "194":
        specs = [("main", "benchmark_main")] + specs
    elif name != "60":
        raise SystemExit(f"unknown arm {name}")

    public: list[dict] = []
    gold: dict[str, str] = {}
    for cohort, directory in specs:
        base = ROOT / "data" / directory
        questions = {r["qid"]: r for r in _read_jsonl(base / "questions2.jsonl")}
        answers = {r["qid"]: r for r in _read_jsonl(base / "answers2.jsonl")}
        if cohort == "main":
            keep = set(json.loads((base / "clean_qids.json").read_text()))
        else:
            keep = set(questions)
        for qid, q in questions.items():
            if qid not in keep or qid not in answers:
                continue
            uid = f"{cohort}:{qid}"
            public.append({
                "uid": uid,
                "cohort": cohort,
                "qid": qid,
                "formula": q.get("formula") or "",
                "ir_bands_cm-1": list(q.get("ir_bands_cm-1") or []),
                "h_nmr": q.get("h_nmr") or "",
                "c_nmr": q.get("c_nmr") or "",
                "difficulty": (answers[qid].get("difficulty") or q.get("difficulty") or ""),
            })
            gold[uid] = (answers[qid].get("inchikey") or "")[:14]
    if name == "60" and len(public) != 60:
        raise SystemExit(f"arm 60 has {len(public)} records")
    if name == "194" and len(public) != 194:
        raise SystemExit(f"arm 194 has {len(public)} records")
    missing = [r["uid"] for r in public if len(gold[r["uid"]]) != 14]
    if missing:
        raise SystemExit(f"answer key missing InChIKey-14 for {missing[:5]}")
    return public, gold


def fverify_pool() -> dict[str, list[str]]:
    """Frozen candidate SMILES on the 60-compound arm, in self-rank order.

    `is_true` is ignored. The gold structure is not inserted.
    """
    from collections import defaultdict

    groups: dict[str, list[tuple[int, str]]] = defaultdict(list)
    path = ROOT / "data" / "fverify" / "candidates.jsonl"
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cohort = "v3" if row["dir"].endswith("benchmark_v3") else "v2ctrl"
        uid = f"{cohort}:{row['qid']}"
        groups[uid].append((int(row["self_rank"]), row["smiles"]))
    return {uid: [s for _, s in sorted(pairs)] for uid, pairs in groups.items()}
