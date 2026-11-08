#!/usr/bin/env python3
"""Closed-book prompt export, collection, and prefix scoring for a requested
budget of 50 constitutions.

Solver prompts are built from frozen question records only: compound id,
molecular formula, IR band list, printed 1H, printed 13C. Gold SMILES and
InChIKey never enter a prompt. `export` does not open an answer file.

The roster is the locked 500, sorted by (difficulty, qid), the same order as
the ask-for-ten closed-book export. 1-based positions 223-252 and 471-500 are
the nested v3 + v2_ctrl control. 1-based positions 411-470 are the disjoint
simple 60 used by the ask-for-ten Opus continuation (that arm stored the same
compounds as 0-based indices 410-469). The remaining 380 positions are the
leftover slice. The three slices are pairwise disjoint and their union is the
locked 500.

    python3 analysis/iclr_rebuttal_nov2026/ask50/closed_book.py export \
        --slice nested60 --outdir ask50_nested60 --k 50 --batch-size 6

`summarize` scores unique-constitution prefixes at k = 1, 3, 5, 10, 20, 50.
A list shorter than k contributes the constitutions it has. Empty lists stay
in the denominator. Fractions are n/N. Gold structures are not printed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from specmetrics import ik14  # noqa: E402

EXPAND_SHA = "48fcd30153df5e331fab43cfa514763db8ee3891"
CASE_LITE_SHA = "0bd7c7f750a95974ba7f2c50f3273ab942639c05"
CASE_LITE_CSV = "analysis/iclr_rebuttal_nov2026/case_lite/outputs/per_molecule.csv"
GOLD_GZ = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"
REPORT_KS = (1, 3, 5, 10, 20, 50)
# 1-based inclusive positions on roster("n500").
SLICE_RANGES = {
    "nested60": ((223, 252), (471, 500)),
    "simple60": ((411, 470),),
    "rest380": (),
}
CASE_COHORT = {
    "benchmark_main": "locked-main",
    "benchmark_v3": "locked-v3",
    "benchmark_v2_ctrl": "locked-v2ctrl",
    "benchmark_expand": "expand",
    "benchmark_expand_500": "expand500",
}

PROMPT_KEYS = ("qid", "formula", "ir_bands_cm-1", "h_nmr", "c_nmr")
FORBIDDEN_KEYS = {
    "smiles", "inchikey", "true_smiles", "true_ik", "is_true", "candidates",
    "self_rank", "source_doi",
}
INCHIKEY_RE = re.compile(r"\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b")
INCHIKEY14_RE = re.compile(r"\b[A-Z]{14}\b")
FORMULA_RE = re.compile(r"([A-Z][a-z]?)(\d*)")

HEADER = """\
# Blind structure-elucidation task

You are given real experimental spectra for organic molecules. For EACH compound
you are given the molecular formula, the IR band list, and the printed 1H and 13C
NMR lists. No name, SMILES, InChI, or other hint is given.

For each compound, propose up to {K} distinct constitutions, best first, as SMILES.

Rules:
  - Use only the spectra in this file. Do not open any other file, do not search
    the web, and do not look up a name, a structure, or an identifier.
  - Do not enumerate isomers with a database or a structure generator. You may
    use RDKit only to check that a SMILES you already wrote parses and has this
    molecular formula.
  - Every candidate must match the given molecular formula exactly.
  - Order candidates by your own confidence, most likely first.
  - If you cannot honestly propose {K} different constitutions, return fewer.
    Do not pad with duplicates or with structures that break the formula.
  - If you know more distinct formula-matching constitutions than {K}, stop at {K}
    unless you would have written them anyway. Do not invent fillers.

Return ONLY a JSON object mapping each id to a list of SMILES strings, e.g.:
  {{"{example}": ["CCO", "COC"]}}

Compounds:

"""


def git_bytes(sha: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{sha}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL
    )


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_jsonl_bytes(blob: bytes) -> list[dict]:
    return [json.loads(line) for line in blob.decode().splitlines() if line.strip()]


def question_payload(row: dict, qid: str) -> dict:
    unknown = set(row) - set(PROMPT_KEYS) - {"difficulty"}
    leaked = unknown & FORBIDDEN_KEYS
    if leaked:
        raise SystemExit(f"{qid}: question record has gold-bearing keys {sorted(leaked)}")
    payload = {
        "qid": qid,
        "formula": row["formula"],
        "ir_bands_cm-1": row.get("ir_bands_cm-1") or [],
        "h_nmr": row.get("h_nmr") or "",
        "c_nmr": row.get("c_nmr") or "",
    }
    for key in ("smiles", "inchikey", "true_smiles", "true_ik", "is_true"):
        if key in payload:
            raise SystemExit(f"{qid}: refused to put {key} in the payload")
    return payload


def load_local_questions(directory: str, cohort: str) -> list[dict]:
    path = ROOT / directory / "questions2.jsonl"
    out = []
    for row in read_jsonl(path):
        qid = f"{cohort}:{row['qid']}"
        item = question_payload(row, qid)
        item["difficulty"] = row.get("difficulty") or "?"
        item["cohort"] = cohort
        out.append(item)
    return out


def load_git_questions(sha: str, path: str, cohort: str, keep: set[str] | None) -> list[dict]:
    out = []
    for row in read_jsonl_bytes(git_bytes(sha, path)):
        if keep is not None and row["qid"] not in keep:
            continue
        qid = f"{cohort}:{row['qid']}"
        item = question_payload(row, qid)
        item["difficulty"] = row.get("difficulty") or "?"
        item["cohort"] = cohort
        out.append(item)
    return out


def roster(arm: str) -> list[dict]:
    """Frozen questions only. This function must not open an answer key."""
    if arm == "n60":
        rows = load_local_questions("data/benchmark_v3", "benchmark_v3")
        rows += load_local_questions("data/benchmark_v2_ctrl", "benchmark_v2_ctrl")
    elif arm == "n500":
        clean = set(json.loads((ROOT / "data/benchmark_main/clean_qids.json").read_text()))
        main = []
        for row in read_jsonl(ROOT / "data/benchmark_main/questions2.jsonl"):
            if row["qid"] not in clean:
                continue
            item = question_payload(row, f"benchmark_main:{row['qid']}")
            item["difficulty"] = row.get("difficulty") or "?"
            item["cohort"] = "benchmark_main"
            main.append(item)
        keep200 = set(json.loads(git_bytes(
            EXPAND_SHA, "data/benchmark_expand_500/headline500_expand200_qids.json"
        ).decode()))
        rows = (
            main
            + load_local_questions("data/benchmark_v3", "benchmark_v3")
            + load_local_questions("data/benchmark_v2_ctrl", "benchmark_v2_ctrl")
            + load_git_questions(
                EXPAND_SHA, "data/benchmark_expand/questions2.jsonl", "benchmark_expand", None
            )
            + load_git_questions(
                EXPAND_SHA,
                "data/benchmark_expand_500/questions2.jsonl",
                "benchmark_expand_500",
                keep200,
            )
        )
    else:
        raise SystemExit(f"unknown arm {arm!r}")
    rows.sort(key=lambda r: (r["difficulty"], r["qid"]))
    seen = set()
    for row in rows:
        if row["qid"] in seen:
            raise SystemExit(f"duplicate qid {row['qid']}")
        seen.add(row["qid"])
    return rows


def select_rows(arm: str, exclude_arm: str | None, skip: int, limit: int | None) -> list[dict]:
    rows = roster(arm)
    if exclude_arm:
        banned = {row["qid"] for row in roster(exclude_arm)}
        rows = [row for row in rows if row["qid"] not in banned]
    if skip:
        rows = rows[skip:]
    if limit is not None:
        rows = rows[:limit]
    return rows


def indexed_roster() -> list[dict]:
    rows = roster("n500")
    if len(rows) != 500:
        raise SystemExit(f"locked roster has {len(rows)} rows, expected 500")
    out = []
    for position, row in enumerate(rows, start=1):
        item = dict(row)
        item["position"] = position
        out.append(item)
    return out


def _in_ranges(position: int, ranges: tuple) -> bool:
    return any(start <= position <= stop for start, stop in ranges)


def slice_rows(name: str) -> list[dict]:
    rows = indexed_roster()
    nested = [row for row in rows if _in_ranges(row["position"], SLICE_RANGES["nested60"])]
    simple = [row for row in rows if _in_ranges(row["position"], SLICE_RANGES["simple60"])]
    nested_ids = {row["qid"] for row in nested}
    simple_ids = {row["qid"] for row in simple}
    if len(nested_ids) != 60 or len(simple_ids) != 60:
        raise SystemExit("slice sizes drifted")
    if nested_ids & simple_ids:
        raise SystemExit("nested60 and simple60 overlap")
    v3_ctrl = {row["qid"] for row in roster("n60")}
    if nested_ids != v3_ctrl:
        raise SystemExit("nested60 is not the v3 + v2_ctrl set")
    if name == "nested60":
        chosen = nested
    elif name == "simple60":
        chosen = simple
    elif name == "rest380":
        chosen = [row for row in rows if row["qid"] not in nested_ids and row["qid"] not in simple_ids]
    elif name == "all500":
        chosen = rows
    else:
        raise SystemExit(f"unknown slice {name}")
    if name == "rest380" and len(chosen) != 380:
        raise SystemExit(f"rest380 has {len(chosen)} rows")
    if name == "all500" and len(chosen) != 500:
        raise SystemExit(f"all500 has {len(chosen)} rows")
    seen = set()
    for row in chosen:
        if row["qid"] in seen:
            raise SystemExit(f"duplicate qid in {name}: {row['qid']}")
        seen.add(row["qid"])
    return chosen


def fraction(numer: int, denom: int) -> str:
    return f"{numer}/{denom}"


def render_prompt(rows: list[dict], k: int) -> str:
    example = rows[0]["qid"] if rows else "benchmark_v3:R01"
    blocks = []
    for row in rows:
        blocks.append("\n".join([
            f"### {row['qid']}",
            f"Molecular formula: {row['formula']}",
            f"IR bands (cm-1): {row['ir_bands_cm-1']}",
            f"1H NMR: {row['h_nmr']}",
            f"13C NMR: {row['c_nmr']}",
        ]))
    text = HEADER.format(K=k, example=example) + "\n\n".join(blocks) + "\n"
    if INCHIKEY_RE.search(text):
        raise SystemExit("refusing to write a prompt that contains an InChIKey")
    for banned in ("true_smiles", "inchikey", "is_true", "answers2", "source_doi"):
        if banned in text.lower():
            raise SystemExit(f"refusing to write a prompt that contains {banned}")
    return text


def export_prompts(
    arm: str,
    outdir: Path,
    k: int,
    batch_size: int,
    exclude_arm: str | None = None,
    skip: int = 0,
    limit: int | None = None,
    rows: list[dict] | None = None,
    slice_name: str | None = None,
) -> None:
    if rows is None:
        rows = select_rows(arm, exclude_arm, skip, limit)
    if not rows:
        raise SystemExit("export selected zero questions")
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_batches = []
    nb = (len(rows) + batch_size - 1) // batch_size
    for i in range(nb):
        chunk = rows[i * batch_size:(i + 1) * batch_size]
        text = render_prompt(chunk, k)
        name = f"solve_{i + 1:02d}.md"
        (outdir / name).write_text(text)
        manifest_batches.append({
            "batch": f"{i + 1:02d}",
            "file": name,
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "k_requested": k,
            "qids": [r["qid"] for r in chunk],
            "formulas": [r["formula"] for r in chunk],
        })
    meta = {
        "arm": arm,
        "slice": slice_name,
        "n": len(rows),
        "k_requested": k,
        "batch_size": batch_size,
        "n_batches": nb,
        "exclude_arm": exclude_arm,
        "skip": skip,
        "limit": limit,
        "positions_1based": [row.get("position") for row in rows],
        "expand_sha": EXPAND_SHA,
        "prompt_fields": ["qid", "formula", "ir_bands_cm-1", "h_nmr", "c_nmr"],
        "gold_fields_excluded": sorted(FORBIDDEN_KEYS),
        "batches": manifest_batches,
    }
    (outdir / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"arm {arm}: {len(rows)} questions, {nb} prompts, k={k} -> {outdir}")
    print("prompts contain formula, IR, 1H, 13C, and the qid. No answer file was opened.")


def extract_json(text: str) -> dict | None:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    bodies = [fenced.group(1)] if fenced else []
    bodies.append(text)
    for body in bodies:
        try:
            obj = json.loads(body)
        except Exception:
            i, j = body.find("{"), body.rfind("}")
            if i < 0 or j <= i:
                continue
            try:
                obj = json.loads(body[i:j + 1])
            except Exception:
                continue
        if isinstance(obj, dict):
            return obj
    return None


def formula_counts(formula: str | None) -> tuple | None:
    if not formula:
        return None
    text = formula.strip().split()[0]
    text = re.sub(r"[+-]\d*$", "", text)
    counts: dict[str, int] = {}
    if not text or not FORMULA_RE.search(text):
        return None
    consumed = 0
    for match in FORMULA_RE.finditer(text):
        if match.start() != consumed:
            return None
        element, number = match.group(1), match.group(2)
        counts[element] = counts.get(element, 0) + (int(number) if number else 1)
        consumed = match.end()
    if consumed != len(text) or not counts:
        return None
    return tuple(sorted(counts.items()))


def formula_of(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return None
    return rdMolDescriptors.CalcMolFormula(mol)


def formula_matches(smiles: str, formula: str) -> bool:
    got = formula_of(smiles)
    if got is None:
        return False
    if got == formula:
        return True
    return formula_counts(got) == formula_counts(formula) and formula_counts(got) is not None


def kept_constitutions(candidates: list, formula: str) -> list[str]:
    """Parseable, formula-matching, first-occurrence canonical SMILES.

    Identity is InChIKey-14. Unparseable strings and formula mismatches are
    dropped and do not occupy a rank. RDKit is not asked to invent a structure.
    """
    out, seen = [], set()
    for smiles in candidates or []:
        if not isinstance(smiles, str) or not smiles.strip():
            continue
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            continue
        canonical = Chem.MolToSmiles(mol)
        if not formula_matches(canonical, formula):
            continue
        key = ik14(canonical)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(canonical)
    return out


def candidate_strings(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise SystemExit("candidates are not a list")
    cleaned = []
    for item in value:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip())
        elif isinstance(item, dict) and isinstance(item.get("smiles"), str):
            cleaned.append(item["smiles"].strip())
    return cleaned


def collect(arm: str, outdir: Path, predictions: Path, model: str) -> None:
    manifest = json.loads((outdir / "manifest.json").read_text())
    if manifest["arm"] != arm:
        raise SystemExit(f"manifest arm is {manifest['arm']}, expected {arm}")
    predictions.parent.mkdir(parents=True, exist_ok=True)
    n_out = 0
    missing_batches = []
    with predictions.open("w") as handle:
        for batch in manifest["batches"]:
            reply = outdir / f"reply_{batch['batch']}.json"
            if not reply.exists():
                missing_batches.append(batch["batch"])
                continue
            obj = extract_json(reply.read_text())
            if obj is None:
                raise SystemExit(f"{reply} is not a JSON object")
            wanted = set(batch["qids"])
            extra = sorted(set(obj) - wanted)
            if extra:
                raise SystemExit(f"{reply} has ids that were not in the prompt: {extra[:5]}")
            for qid, formula in zip(batch["qids"], batch["formulas"]):
                raw = candidate_strings(obj.get(qid))
                kept = kept_constitutions(raw, formula)
                record = {
                    "qid": qid,
                    "raw_candidates": raw,
                    "candidates": kept,
                    "model": model,
                    "arm": arm,
                    "k_requested": manifest["k_requested"],
                    "batch": batch["batch"],
                    "prompt_sha256": batch["sha256"],
                    "formula": formula,
                    "n_returned": len(raw),
                    "n_parseable": sum(formula_of(s) is not None for s in raw),
                    "n_formula_match": sum(formula_matches(s, formula) for s in raw),
                    "n_unique": len(kept),
                }
                handle.write(json.dumps(record) + "\n")
                n_out += 1
    print(f"wrote {n_out} prediction rows -> {predictions}")
    if missing_batches:
        print(f"missing reply batches (not imputed): {', '.join(missing_batches)}")
    print("score has not been run. Gold was not read.")


def q_c13(text: str) -> tuple:
    return tuple(round(float(x), 2) for x in re.findall(r"(-?\d+\.?\d*)\s*\(", text or ""))


def g_c13(text: str) -> tuple:
    if "(" in (text or ""):
        return q_c13(text)
    return tuple(round(float(x), 2) for x in re.findall(r"-?\d+\.?\d*", text or ""))


def ir_key(bands) -> tuple:
    return tuple(round(float(x), 1) for x in (bands or []))


def local_answers() -> dict[str, dict]:
    found = {}
    for cohort, directory in (
        ("benchmark_main", "data/benchmark_main"),
        ("benchmark_v3", "data/benchmark_v3"),
        ("benchmark_v2_ctrl", "data/benchmark_v2_ctrl"),
        ("benchmark_v2", "data/benchmark_v2"),
        ("benchmark_electrolyte", "data/benchmark_electrolyte"),
    ):
        path = ROOT / directory / "answers2.jsonl"
        if not path.exists():
            alt = ROOT / directory / "answers.jsonl"
            path = alt if alt.exists() else None
        if path is None:
            continue
        for row in read_jsonl(path):
            found[f"{cohort}:{row['qid']}"] = row
    return found


def question_index() -> dict[str, dict]:
    questions = {}
    for cohort, directory in (
        ("benchmark_main", "data/benchmark_main"),
        ("benchmark_v3", "data/benchmark_v3"),
        ("benchmark_v2_ctrl", "data/benchmark_v2_ctrl"),
    ):
        for row in read_jsonl(ROOT / directory / "questions2.jsonl"):
            questions[f"{cohort}:{row['qid']}"] = row
    for path, cohort in (
        ("data/benchmark_expand/questions2.jsonl", "benchmark_expand"),
        ("data/benchmark_expand_500/questions2.jsonl", "benchmark_expand_500"),
    ):
        for row in read_jsonl_bytes(git_bytes(EXPAND_SHA, path)):
            questions[f"{cohort}:{row['qid']}"] = row
    return questions


def index_gold(formulas: set[str]) -> dict:
    import gzip
    by = defaultdict(list)
    with gzip.open(GOLD_GZ, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            smiles = row.get("smiles")
            if not smiles:
                continue
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
            form = rdMolDescriptors.CalcMolFormula(mol)
            if form not in formulas and row.get("formula") not in formulas:
                continue
            key = (form, ir_key(row.get("ir_bands_cm-1")), g_c13(row.get("c_nmr")))
            ik = (row.get("inchikey") or Chem.MolToInchiKey(mol))[:14]
            by[key].append({"inchikey14": ik, "smiles": smiles})
    return by


def truth_maps(qids: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    """Return qid -> InChIKey-14 and qid -> gold SMILES. Prints nothing."""
    local = local_answers()
    questions = question_index()
    truth, smiles = {}, {}
    need_join = []
    for qid in qids:
        row = local.get(qid)
        if row and row.get("inchikey"):
            truth[qid] = row["inchikey"][:14]
            if row.get("smiles"):
                smiles[qid] = row["smiles"]
        else:
            need_join.append(qid)
    if need_join:
        formulas = set()
        for qid in need_join:
            q = questions[qid]
            formulas.add(q["formula"])
            mol_formula = q["formula"]
            formulas.add(mol_formula)
        gold = index_gold(formulas)
        ambiguous = 0
        for qid in need_join:
            q = questions[qid]
            hits = gold.get((q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr"))), [])
            keys = sorted({hit["inchikey14"] for hit in hits})
            if len(keys) != 1:
                ambiguous += 1
                continue
            truth[qid] = keys[0]
            smile_set = sorted({hit["smiles"] for hit in hits if hit["inchikey14"] == keys[0]})
            if len(smile_set) == 1:
                smiles[qid] = smile_set[0]
        if ambiguous:
            raise SystemExit(f"{ambiguous} questions did not have a unique gold join")
    return truth, smiles


def truth_for(records: list[dict]) -> dict[str, str]:
    truth, _smiles = truth_maps([rec["qid"] for rec in records])
    missing = [rec["qid"] for rec in records if rec["qid"] not in truth]
    if missing:
        raise SystemExit(f"no truth for {len(missing)} qids, first {missing[:3]}")
    return truth


def check_prompts(arm: str, outdir: Path, out: Path) -> None:
    """Fail if any gold InChIKey or gold SMILES was written into a solver prompt."""
    manifest = json.loads((outdir / "manifest.json").read_text())
    if manifest["arm"] != arm:
        raise SystemExit(f"manifest arm is {manifest['arm']}, expected {arm}")
    qids = [qid for batch in manifest["batches"] for qid in batch["qids"]]
    texts = []
    regex_hits = 0
    for batch in manifest["batches"]:
        text = (outdir / batch["file"]).read_text()
        texts.append(text)
        regex_hits += len(INCHIKEY_RE.findall(text))
    blob = "\n".join(texts)
    truth, smiles = truth_maps(qids)
    key_leaks = []
    smiles_leaks = []
    for qid, key in truth.items():
        if key and key in blob:
            key_leaks.append(qid)
        full = None
        local = local_answers().get(qid)
        if local and local.get("inchikey") and local["inchikey"] in blob:
            full = qid
        if full and qid not in key_leaks:
            key_leaks.append(qid)
    for qid, smile in smiles.items():
        if smile and smile in blob:
            smiles_leaks.append(qid)
    passed = regex_hits == 0 and not key_leaks and not smiles_leaks and len(truth) == len(qids)
    report = {
        "arm": arm,
        "n_prompts": len(manifest["batches"]),
        "n_qids": len(qids),
        "n_gold_keys_scanned": len(truth),
        "n_gold_smiles_scanned": len(smiles),
        "inchikey_regex_hits": regex_hits,
        "gold_key_leaks": len(key_leaks),
        "gold_smiles_leaks": len(smiles_leaks),
        "leaking_qids": sorted(set(key_leaks + smiles_leaks)),
        "passed": passed,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"gold-key check {'PASS' if passed else 'FAIL'}: "
        f"{len(truth)} keys, {len(smiles)} smiles, "
        f"regex_hits={regex_hits}, key_leaks={len(key_leaks)}, smiles_leaks={len(smiles_leaks)}"
    )
    if not passed:
        raise SystemExit("solver prompts failed the gold-key unit check")


def prefix_counts(groups: list[tuple[str, list[str]]], k: int) -> dict:
    """groups are (truth_ik14, ordered constitution keys)."""
    n = len(groups)
    top1 = recall = ge = empty = 0
    for truth, keys in groups:
        if not keys:
            empty += 1
        ge += int(len(keys) >= k)
        prefix = keys[:k]
        recall += int(bool(truth) and truth in prefix)
        top1 += int(bool(prefix) and prefix[0] == truth)
    return {
        "n": n,
        "n_lists_ge_k": ge,
        "top1": top1,
        "recall": recall,
        "n_empty": empty,
    }


def score_file(predictions: Path, out: Path) -> None:
    records = read_jsonl(predictions)
    if not records:
        raise SystemExit(f"no predictions in {predictions}")
    truth = truth_for(records)
    parsed = []
    max_unique = 0
    for rec in records:
        raw = list(rec.get("raw_candidates") or rec.get("candidates") or [])
        if "candidates" in rec and "raw_candidates" in rec:
            kept = list(rec["candidates"])
        else:
            kept = kept_constitutions(raw, rec.get("formula") or "")
        uniq_keys = [ik14(s) for s in kept]
        uniq_keys = [key for key in uniq_keys if key]
        raw_keys = []
        seen = set()
        for smiles in raw:
            key = ik14(smiles) if isinstance(smiles, str) else None
            if not key or key in seen:
                continue
            seen.add(key)
            raw_keys.append(key)
        max_unique = max(max_unique, len(uniq_keys))
        parsed.append((rec, truth[rec["qid"]], uniq_keys, raw_keys))
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "arm", "model", "list_kind", "k_requested", "k", "n", "n_lists_ge_k",
        "top1", "recall", "precision_given_recall", "n_empty", "identified",
    ]
    arms = sorted({rec["arm"] for rec, *_rest in parsed})
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for arm in arms:
            group = [row for row in parsed if row[0]["arm"] == arm]
            model = group[0][0]["model"]
            k_req = group[0][0]["k_requested"]
            for kind, index in (("unique_constitutions", 2), ("raw_unique_including_wrong_formula", 3)):
                limit = max(len(row[index]) for row in group)
                pairs = [(row[1], row[index]) for row in group]
                if limit == 0:
                    counts = prefix_counts(pairs, 1)
                    writer.writerow({
                        "arm": arm,
                        "model": model,
                        "list_kind": kind,
                        "k_requested": k_req,
                        "k": 0,
                        "n": counts["n"],
                        "n_lists_ge_k": 0,
                        "top1": f"0/{counts['n']}",
                        "recall": f"0/{counts['n']}",
                        "precision_given_recall": "0/0",
                        "n_empty": counts["n_empty"],
                        "identified": "true",
                    })
                    continue
                for k in range(1, limit + 1):
                    counts = prefix_counts(pairs, k)
                    recall = counts["recall"]
                    top1 = counts["top1"]
                    writer.writerow({
                        "arm": arm,
                        "model": model,
                        "list_kind": kind,
                        "k_requested": k_req,
                        "k": k,
                        "n": counts["n"],
                        "n_lists_ge_k": counts["n_lists_ge_k"],
                        "top1": f"{top1}/{counts['n']}",
                        "recall": f"{recall}/{counts['n']}",
                        "precision_given_recall": f"{top1}/{recall}" if recall else "0/0",
                        "n_empty": counts["n_empty"] if k == 1 else "",
                        "identified": "true",
                    })
                # Reviewer checkpoints past the longest stored list are not
                # measurements. Leave the rates blank rather than repeat the plateau.
                for k in (10, 20, 50):
                    if k <= limit:
                        continue
                    writer.writerow({
                        "arm": arm,
                        "model": model,
                        "list_kind": kind,
                        "k_requested": k_req,
                        "k": k,
                        "n": len(group),
                        "n_lists_ge_k": 0,
                        "top1": "",
                        "recall": "",
                        "precision_given_recall": "",
                        "n_empty": "",
                        "identified": "false",
                    })
    print(f"scored {len(records)} finished predictions. max unique constitution length {max_unique}.")
    print(f"fractions -> {out}")
    print("k above that maximum was not written. No structure was printed.")


def length_summary(predictions: Path, out: Path) -> None:
    records = read_jsonl(predictions)
    hist = defaultdict(int)
    empty = []
    over = []
    for rec in records:
        n = len(rec.get("candidates") or [])
        hist[n] += 1
        if n == 0:
            empty.append(rec["qid"])
        if n > int(rec.get("k_requested") or 0):
            over.append({"qid": rec["qid"], "n_unique": n})
    payload = {
        "n_finished": len(records),
        "model": records[0]["model"] if records else None,
        "arm": records[0]["arm"] if records else None,
        "k_requested": records[0]["k_requested"] if records else None,
        "unique_length_histogram": {str(k): hist[k] for k in sorted(hist)},
        "n_empty": len(empty),
        "empty_qids": empty,
        "n_longer_than_requested": len(over),
        "longer_than_requested": over,
        "max_unique": max(hist) if hist else 0,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"finished {payload['n_finished']}, empty {payload['n_empty']}, "
        f"max unique {payload['max_unique']}, longer than requested {payload['n_longer_than_requested']}"
    )


def ordered_keys(record: dict) -> list[str]:
    """Recompute unique formula-matching constitutions from the raw strings.

    The stored `candidates` field is not trusted.
    """
    raw = candidate_strings(record.get("raw_candidates"))
    if not raw and record.get("candidates"):
        raw = candidate_strings(record.get("candidates"))
    formula = record.get("formula") or ""
    return [ik14(smiles) for smiles in kept_constitutions(raw, formula)]


def case_lite_keys() -> dict[str, str]:
    blob = git_bytes(CASE_LITE_SHA, CASE_LITE_CSV).decode().splitlines()
    out = {}
    for row in csv.DictReader(blob):
        cohort, qid = row["uid"].split(":", 1)
        reverse = {value: key for key, value in CASE_COHORT.items()}
        bench = reverse.get(cohort)
        if bench is None:
            raise SystemExit(f"unknown CASE-lite cohort {cohort}")
        out[f"{bench}:{qid}"] = row["gold_ik"]
    if len(out) != 500:
        raise SystemExit(f"CASE-lite gold table has {len(out)} rows, expected 500")
    return out


def prefix_block(groups: list[tuple[str, list[str]]], ks: tuple[int, ...]) -> dict:
    n = len(groups)
    lengths = [len(keys) for _truth, keys in groups]
    blocks = {}
    for k in ks:
        counts = prefix_counts(groups, k)
        misses = n - counts["recall"]
        blocks[str(k)] = {
            "k": k,
            "n": fraction(n, n) if n else "0/0",
            "recall": fraction(counts["recall"], n),
            "top1": fraction(counts["top1"], n),
            "generation_misses": fraction(misses, n),
            "n_lists_ge_k": fraction(counts["n_lists_ge_k"], n),
            "recall_count": counts["recall"],
            "top1_count": counts["top1"],
            "generation_miss_count": misses,
            "n_lists_ge_k_count": counts["n_lists_ge_k"],
        }
    return {
        "n": n,
        "lengths": lengths,
        "prefixes": blocks,
    }


def movement(prefixes: dict) -> dict:
    def hits(k: int) -> int:
        return prefixes[str(k)]["recall_count"]

    denom = int(prefixes["1"]["recall"].split("/")[1])

    def pair(left: int, right: int) -> dict:
        delta = hits(right) - hits(left)
        return {
            "recall_left": prefixes[str(left)]["recall"],
            "recall_right": prefixes[str(right)]["recall"],
            "delta": fraction(delta, denom),
            "still_moves": delta != 0,
        }

    return {
        "after_k10": pair(10, 20),
        "after_k20": pair(20, 50),
        "after_k50": {
            "still_moves": False,
            "reason": "The request stops at 50 distinct constitutions. There is no scored prefix past k=50.",
        },
    }


def build_summary(records: list[dict], slice_name: str) -> dict:
    if not records:
        raise SystemExit("no predictions to summarize")
    truth = truth_for(records)
    case_keys = case_lite_keys()
    groups = []
    case_groups = []
    mismatches = []
    for record in records:
        qid = record["qid"]
        keys = ordered_keys(record)
        groups.append((truth[qid], keys))
        case_key = case_keys.get(qid)
        if case_key is None:
            raise SystemExit(f"{qid} missing from CASE-lite gold table")
        if case_key != truth[qid]:
            mismatches.append(qid)
        case_groups.append((case_key, keys))
    block = prefix_block(groups, REPORT_KS)
    case_block = prefix_block(case_groups, REPORT_KS)
    lengths = block["lengths"]
    n = block["n"]
    ordered = sorted(lengths)
    mid = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    reach20 = sum(length >= 20 for length in lengths)
    reach50 = sum(length >= 50 for length in lengths)
    longer = sum(length > 50 for length in lengths)
    uncapped_hits = sum(truth in keys for truth, keys in groups)
    capped_hits = block["prefixes"]["50"]["recall_count"]
    if uncapped_hits != capped_hits:
        block_move_override = {
            "still_moves": True,
            "reason": "At least one returned list is longer than 50 and a gold key sits past position 50.",
            "recall_capped_at_50": block["prefixes"]["50"]["recall"],
            "recall_full_returned_list": fraction(uncapped_hits, n),
        }
    else:
        block_move_override = None
    summary = {
        "model": records[0].get("model"),
        "thinking": "high",
        "k_requested": records[0].get("k_requested"),
        "slice": slice_name,
        "n_finished": n,
        "denominator": n,
        "empty_lists_stay_in_denominator": True,
        "n_empty": fraction(sum(length == 0 for length in lengths), n),
        "list_length": {
            "mean": round(statistics.fmean(lengths), 4) if lengths else None,
            "median": mid,
            "max": max(lengths) if lengths else 0,
            "n_reach_20": fraction(reach20, n),
            "n_reach_50": fraction(reach50, n),
            "n_longer_than_requested": fraction(longer, n),
        },
        "prefixes": block["prefixes"],
        "recall_movement": movement(block["prefixes"]),
        "case_lite": {
            "sha": CASE_LITE_SHA,
            "n_gold_ik_mismatch_vs_answer_key": len(mismatches),
            "mismatch_qids": mismatches,
            "prefixes_if_scored_on_case_lite_gold_ik": case_block["prefixes"],
        },
        "scoring": "InChIKey connectivity, first 14 characters, unique constitutions in model order. Shorter lists contribute the constitutions they contain. This file is one slice, not a 500-wide rate.",
    }
    if block_move_override is not None:
        summary["recall_movement"]["after_k50"] = block_move_override
    return summary


def public_summary(summary: dict) -> dict:
    """Drop integer count twins so the deposited summary is fractions only."""
    out = json.loads(json.dumps(summary))
    for block in out["prefixes"].values():
        for key in ("recall_count", "top1_count", "generation_miss_count", "n_lists_ge_k_count"):
            block.pop(key, None)
    for block in out["case_lite"]["prefixes_if_scored_on_case_lite_gold_ik"].values():
        for key in ("recall_count", "top1_count", "generation_miss_count", "n_lists_ge_k_count"):
            block.pop(key, None)
    return out


def write_summary_csv(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "slice", "model", "k_requested", "k", "n", "recall", "top1",
        "generation_misses", "n_lists_ge_k", "source",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for source, blocks in (
            ("answer_key", summary["prefixes"]),
            ("case_lite_gold_ik", summary["case_lite"]["prefixes_if_scored_on_case_lite_gold_ik"]),
        ):
            for key in ("1", "3", "5", "10", "20", "50"):
                block = blocks[key]
                writer.writerow({
                    "slice": summary["slice"],
                    "model": summary["model"],
                    "k_requested": summary["k_requested"],
                    "k": block["k"],
                    "n": summary["denominator"],
                    "recall": block["recall"],
                    "top1": block["top1"],
                    "generation_misses": block["generation_misses"],
                    "n_lists_ge_k": block["n_lists_ge_k"],
                    "source": source,
                })


def summarize_file(predictions: Path, slice_name: str, json_out: Path, csv_out: Path) -> dict:
    records = read_jsonl(predictions)
    summary = build_summary(records, slice_name)
    deposited = public_summary(summary)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(deposited, indent=2) + "\n")
    write_summary_csv(summary, csv_out)
    print(f"summarized {summary['n_finished']} lists -> {json_out.name}")
    for key in ("1", "3", "5", "10", "20", "50"):
        block = summary["prefixes"][key]
        print(
            f"k={key} recall {block['recall']} top1 {block['top1']} "
            f"misses {block['generation_misses']} ge {block['n_lists_ge_k']}"
        )
    move = summary["recall_movement"]
    print(
        f"recall moves after k=10: {move['after_k10']['still_moves']}; "
        f"after k=20: {move['after_k20']['still_moves']}; "
        f"after k=50: {move['after_k50']['still_moves']}"
    )
    print(
        f"length mean {summary['list_length']['mean']} "
        f"median {summary['list_length']['median']} "
        f"max {summary['list_length']['max']} "
        f"reach20 {summary['list_length']['n_reach_20']} "
        f"reach50 {summary['list_length']['n_reach_50']}"
    )
    if summary["case_lite"]["n_gold_ik_mismatch_vs_answer_key"]:
        print(
            "CASE-lite gold_ik mismatches answer keys: "
            f"{summary['case_lite']['n_gold_ik_mismatch_vs_answer_key']}"
        )
    else:
        print("CASE-lite gold_ik matches the answer-key InChIKey-14 on every finished row")
    return summary


def rescore_check(predictions: Path, summary_path: Path, slice_name: str) -> None:
    """Recompute from raw strings and answer keys. Ignore nothing in the summary except as a comparison target."""
    fresh = build_summary(read_jsonl(predictions), slice_name)
    stored = json.loads(summary_path.read_text())
    bad = []
    for key in ("1", "3", "5", "10", "20", "50"):
        for field in ("recall", "top1", "generation_misses", "n_lists_ge_k"):
            got = fresh["prefixes"][key][field]
            have = stored["prefixes"][key][field]
            if got != have:
                bad.append(f"k={key} {field}: recomputed {got} summary {have}")
        case_got = fresh["case_lite"]["prefixes_if_scored_on_case_lite_gold_ik"][key]["recall"]
        case_have = stored["case_lite"]["prefixes_if_scored_on_case_lite_gold_ik"][key]["recall"]
        if case_got != case_have:
            bad.append(f"k={key} case-lite recall: recomputed {case_got} summary {case_have}")
    for field in ("mean", "median", "max", "n_reach_20", "n_reach_50"):
        if fresh["list_length"][field] != stored["list_length"][field]:
            bad.append(f"length {field}: recomputed {fresh['list_length'][field]} summary {stored['list_length'][field]}")
    if bad:
        raise SystemExit("independent rescore mismatch:\n" + "\n".join(bad))
    print(f"independent rescore matches {summary_path.name} on {fresh['n_finished']} lists")


def union_check(paths: list[Path]) -> None:
    """Refuse a 500-wide label unless the files are complementary and cover the roster."""
    rows = indexed_roster()
    wanted = {row["qid"]: row["position"] for row in rows}
    seen = {}
    for path in paths:
        for record in read_jsonl(path):
            qid = record["qid"]
            if qid in seen:
                raise SystemExit(f"{qid} appears in more than one file")
            if qid not in wanted:
                raise SystemExit(f"{qid} is not on the locked roster")
            seen[qid] = path.name
    missing = [qid for qid in wanted if qid not in seen]
    print(f"union covers {len(seen)}/500 locked qids; missing {len(missing)}")
    if missing:
        print("not a 500-wide result")
    else:
        print("files are pairwise disjoint and their union is the locked 500")


def selftest() -> None:
    ethanol = kept_constitutions(["CCO", "CCO", "OCC", "not-a-smiles", "c1ccccc1"], "C2H6O")
    if ethanol != ["CCO"]:
        raise SystemExit(f"selftest dedupe failed: {ethanol}")
    groups = [
        ("AAA", ["AAA", "BBB"]),
        ("CCC", ["DDD"]),
        ("EEE", []),
        ("FFF", ["FFF"]),
    ]
    k1 = prefix_counts(groups, 1)
    k2 = prefix_counts(groups, 2)
    if k1["top1"] != 2 or k1["recall"] != 2 or k1["n_lists_ge_k"] != 3 or k1["n_empty"] != 1:
        raise SystemExit(f"selftest k1 failed: {k1}")
    if k2["recall"] != 2 or k2["top1"] != 2 or k2["n_lists_ge_k"] != 1:
        raise SystemExit(f"selftest k2 failed: {k2}")
    text = render_prompt([{
        "qid": "benchmark_v3:R01",
        "formula": "C2H6O",
        "ir_bands_cm-1": [3000.0],
        "h_nmr": "1.0 (t)",
        "c_nmr": "18.0 (1C, s)",
    }], 10)
    if "C2H6O" not in text or INCHIKEY_RE.search(text):
        raise SystemExit("selftest prompt render failed")
    try:
        render_prompt([{
            "qid": "benchmark_v3:R01",
            "formula": "C2H6O",
            "ir_bands_cm-1": [],
            "h_nmr": "LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            "c_nmr": "",
        }], 3)
    except SystemExit:
        pass
    else:
        raise SystemExit("selftest did not reject an InChIKey in a prompt")
    groups = [
        ("AAA", ["AAA", "BBB"]),
        ("CCC", ["DDD"]),
        ("EEE", []),
        ("FFF", ["FFF"]),
    ]
    block = prefix_block(groups, REPORT_KS)
    if block["prefixes"]["1"]["recall"] != "2/4":
        raise SystemExit("selftest prefix recall failed")
    if block["prefixes"]["1"]["generation_misses"] != "2/4":
        raise SystemExit("selftest misses failed")
    if block["prefixes"]["1"]["n_lists_ge_k"] != "3/4":
        raise SystemExit("selftest ge_k failed")
    if block["prefixes"]["50"]["recall"] != "2/4":
        raise SystemExit("selftest short-list prefix failed")
    if block["prefixes"]["50"]["n_lists_ge_k"] != "0/4":
        raise SystemExit("selftest k=50 support failed")
    nested = slice_rows("nested60")
    simple = slice_rows("simple60")
    rest = slice_rows("rest380")
    ids = [row["qid"] for row in nested + simple + rest]
    if len(ids) != 500 or len(set(ids)) != 500:
        raise SystemExit("selftest slices are not a partition of 500")
    if [row["position"] for row in nested[:1]] != [223]:
        raise SystemExit("selftest nested origin failed")
    if simple[0]["qid"] != "benchmark_main:R11" or simple[-1]["qid"] != "benchmark_main:R99":
        raise SystemExit("selftest simple60 bounds failed")
    print("selftest ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    exp = sub.add_parser("export")
    exp.add_argument("--arm", choices=("n60", "n500"))
    exp.add_argument("--slice", choices=("nested60", "simple60", "rest380", "all500"))
    exp.add_argument("--outdir", type=Path, required=True)
    exp.add_argument("--k", type=int, default=50)
    exp.add_argument("--batch-size", type=int, default=6)
    exp.add_argument("--exclude-arm", choices=("n60", "n500"))
    exp.add_argument("--skip", type=int, default=0)
    exp.add_argument("--limit", type=int)
    chk = sub.add_parser("check")
    chk.add_argument("--arm", required=True)
    chk.add_argument("--outdir", type=Path, required=True)
    chk.add_argument("--out", type=Path, required=True)
    col = sub.add_parser("collect")
    col.add_argument("--arm", required=True)
    col.add_argument("--outdir", type=Path, required=True)
    col.add_argument("--predictions", type=Path, required=True)
    col.add_argument("--model", required=True)
    sc = sub.add_parser("score")
    sc.add_argument("--predictions", type=Path, required=True)
    sc.add_argument("--out", type=Path, required=True)
    leng = sub.add_parser("lengths")
    leng.add_argument("--predictions", type=Path, required=True)
    leng.add_argument("--out", type=Path, required=True)
    summ = sub.add_parser("summarize")
    summ.add_argument("--predictions", type=Path, required=True)
    summ.add_argument("--slice", required=True)
    summ.add_argument("--json-out", type=Path, required=True)
    summ.add_argument("--csv-out", type=Path, required=True)
    resc = sub.add_parser("rescore")
    resc.add_argument("--predictions", type=Path, required=True)
    resc.add_argument("--summary", type=Path, required=True)
    resc.add_argument("--slice", required=True)
    uni = sub.add_parser("union")
    uni.add_argument("--predictions", type=Path, nargs="+", required=True)
    sub.add_parser("selftest")
    args = parser.parse_args()
    if args.cmd == "export":
        if args.slice:
            export_prompts(
                args.slice, args.outdir, args.k, args.batch_size,
                rows=slice_rows(args.slice), slice_name=args.slice,
            )
        elif args.arm:
            export_prompts(args.arm, args.outdir, args.k, args.batch_size, args.exclude_arm, args.skip, args.limit)
        else:
            raise SystemExit("export needs --slice or --arm")
    elif args.cmd == "check":
        check_prompts(args.arm, args.outdir, args.out)
    elif args.cmd == "collect":
        collect(args.arm, args.outdir, args.predictions, args.model)
    elif args.cmd == "score":
        score_file(args.predictions, args.out)
    elif args.cmd == "lengths":
        length_summary(args.predictions, args.out)
    elif args.cmd == "summarize":
        summarize_file(args.predictions, args.slice, args.json_out, args.csv_out)
    elif args.cmd == "rescore":
        rescore_check(args.predictions, args.summary, args.slice)
    elif args.cmd == "union":
        union_check(args.predictions)
    else:
        selftest()


if __name__ == "__main__":
    main()
