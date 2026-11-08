#!/usr/bin/env python3
"""Closed-book prompt export, collection, and prefix scoring.

Solver prompts are built from frozen question records only: compound id,
molecular formula, IR band list, printed 1H, printed 13C. Gold SMILES and
InChIKey never enter a prompt. `export` does not open an answer file.

    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py export \
        --arm n60 --outdir /tmp/cb_claude_n60 --k 10 --batch-size 6
    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py check \
        --arm n60 --outdir /tmp/cb_claude_n60 \
        --out analysis/iclr_rebuttal_nov2026/cursor_scaleup/checks_claude-opus-5-5-high_n60.json
    # one fresh solver context per solve_NN.md writes reply_NN.json
    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py collect \
        --arm n60 --outdir /tmp/cb_claude_n60 \
        --predictions analysis/iclr_rebuttal_nov2026/cursor_scaleup/predictions/cursor_claude-opus-5-5-high_n60_k10.jsonl \
        --model claude-opus-5-5-high
    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py score \
        --predictions analysis/iclr_rebuttal_nov2026/cursor_scaleup/predictions/cursor_claude-opus-5-5-high_n60_k10.jsonl \
        --out analysis/iclr_rebuttal_nov2026/cursor_scaleup/scores_claude-opus-5-5-high_n60.csv

`score` prints fractions only. It does not print a gold structure.
Rows are written only for k = 1 .. max stored unique-constitution length.
A shorter list is not copied forward to an unmeasured k.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
GOLD_GZ = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"

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
) -> None:
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
        "n": len(rows),
        "k_requested": k,
        "batch_size": batch_size,
        "n_batches": nb,
        "exclude_arm": exclude_arm,
        "skip": skip,
        "limit": limit,
        "expand_sha": EXPAND_SHA if arm == "n500" else None,
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
    print("selftest ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    exp = sub.add_parser("export")
    exp.add_argument("--arm", required=True, choices=("n60", "n500"))
    exp.add_argument("--outdir", type=Path, required=True)
    exp.add_argument("--k", type=int, default=10)
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
    sub.add_parser("selftest")
    args = parser.parse_args()
    if args.cmd == "export":
        export_prompts(args.arm, args.outdir, args.k, args.batch_size, args.exclude_arm, args.skip, args.limit)
    elif args.cmd == "check":
        check_prompts(args.arm, args.outdir, args.out)
    elif args.cmd == "collect":
        collect(args.arm, args.outdir, args.predictions, args.model)
    elif args.cmd == "score":
        score_file(args.predictions, args.out)
    elif args.cmd == "lengths":
        length_summary(args.predictions, args.out)
    else:
        selftest()


if __name__ == "__main__":
    main()
