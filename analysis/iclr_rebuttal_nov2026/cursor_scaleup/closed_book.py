#!/usr/bin/env python3
"""Closed-book runner for a new Cursor-scale arm.

The solver prompt is built from frozen question records only: molecular formula,
IR band list, printed 1H, printed 13C. Gold SMILES and InChIKey never enter the
prompt, and this module's `export` command does not open an answer file.

Score afterwards, offline:

    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py export \
        --arm n60 --outdir /tmp/cb_n60 --k 10 --batch-size 6
    # a fresh solver context writes reply_NN.json next to each prompt
    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py collect \
        --arm n60 --outdir /tmp/cb_n60 \
        --predictions analysis/iclr_rebuttal_nov2026/cursor_scaleup/predictions/cursor_n60_k10.jsonl
    python3 analysis/iclr_rebuttal_nov2026/cursor_scaleup/closed_book.py score \
        --predictions analysis/iclr_rebuttal_nov2026/cursor_scaleup/predictions/cursor_n60_k10.jsonl \
        --out analysis/iclr_rebuttal_nov2026/cursor_scaleup/scores.csv

`score` prints fractions only. It does not print a gold structure.
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
HERE = Path(__file__).resolve().parent
GOLD_GZ = ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz"

PROMPT_KEYS = ("qid", "formula", "ir_bands_cm-1", "h_nmr", "c_nmr")
FORBIDDEN_KEYS = {
    "smiles", "inchikey", "true_smiles", "true_ik", "is_true", "candidates",
    "self_rank", "source_doi",
}
INCHIKEY_RE = re.compile(r"\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b")

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

Return ONLY a JSON object mapping each id to a list of SMILES strings, e.g.:
  {{"{example}": ["CCO", "COC"]}}

Compounds:

"""


def git_bytes(sha: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL)


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
            + load_git_questions(EXPAND_SHA, "data/benchmark_expand/questions2.jsonl", "benchmark_expand", None)
            + load_git_questions(
                EXPAND_SHA, "data/benchmark_expand_500/questions2.jsonl", "benchmark_expand_500", keep200
            )
        )
    else:
        raise SystemExit(f"unknown arm {arm!r}")
    # Stable, gold-free order. Difficulty is stored on the question at draw time.
    rows.sort(key=lambda r: (r["difficulty"], r["qid"]))
    seen = set()
    for row in rows:
        if row["qid"] in seen:
            raise SystemExit(f"duplicate qid {row['qid']}")
        seen.add(row["qid"])
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
    for banned in ("true_smiles", "inchikey", "is_true", "answers2"):
        if banned in text.lower():
            raise SystemExit(f"refusing to write a prompt that contains {banned}")
    return text


def export_prompts(arm: str, outdir: Path, k: int, batch_size: int) -> None:
    rows = roster(arm)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    nb = (len(rows) + batch_size - 1) // batch_size
    for i in range(nb):
        chunk = rows[i * batch_size:(i + 1) * batch_size]
        text = render_prompt(chunk, k)
        name = f"solve_{i + 1:02d}.md"
        (outdir / name).write_text(text)
        manifest.append({
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
        "expand_sha": EXPAND_SHA if arm == "n500" else None,
        "prompt_fields": ["qid", "formula", "ir_bands_cm-1", "h_nmr", "c_nmr"],
        "gold_fields_excluded": sorted(FORBIDDEN_KEYS),
        "batches": manifest,
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


def formula_of(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return None
    return rdMolDescriptors.CalcMolFormula(mol)


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
            raw_text = reply.read_text()
            obj = extract_json(raw_text)
            if obj is None:
                raise SystemExit(f"{reply} is not a JSON object")
            wanted = set(batch["qids"])
            extra = sorted(set(obj) - wanted)
            if extra:
                raise SystemExit(f"{reply} has ids that were not in the prompt: {extra[:5]}")
            for qid, formula in zip(batch["qids"], batch["formulas"]):
                cands = obj.get(qid)
                if cands is None:
                    cands = []
                if isinstance(cands, str):
                    cands = [cands]
                if not isinstance(cands, list):
                    raise SystemExit(f"{qid}: candidates are not a list")
                cleaned = []
                for smi in cands:
                    if isinstance(smi, str) and smi.strip():
                        cleaned.append(smi.strip())
                record = {
                    "qid": qid,
                    "candidates": cleaned,
                    "model": model,
                    "arm": arm,
                    "k_requested": manifest["k_requested"],
                    "batch": batch["batch"],
                    "prompt_sha256": batch["sha256"],
                    "formula": formula,
                    "n_returned": len(cleaned),
                    "n_parseable": sum(formula_of(s) is not None for s in cleaned),
                    "n_formula_match": sum(formula_of(s) == formula for s in cleaned),
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
            if form not in formulas:
                continue
            by[(form, ir_key(row.get("ir_bands_cm-1")), g_c13(row.get("c_nmr")))].append(
                (row.get("inchikey") or Chem.MolToInchiKey(mol))[:14]
            )
    return by


def truth_for(records: list[dict]) -> dict[str, str]:
    """InChIKey-14 by qid. Local answer keys when they exist; otherwise the unique
    (formula, IR, 13C) join used for the withheld expansion keys. Prints nothing."""
    truth = {}
    need_join = []
    local = {}
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
            local[f"{cohort}:{row['qid']}"] = row["inchikey"][:14]
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
    for rec in records:
        qid = rec["qid"]
        if qid in local:
            truth[qid] = local[qid]
        else:
            need_join.append(qid)
    if need_join:
        formulas = {questions[q]["formula"] for q in need_join}
        gold = index_gold(formulas)
        ambiguous = 0
        for qid in need_join:
            q = questions[qid]
            hits = gold.get((q["formula"], ir_key(q.get("ir_bands_cm-1")), q_c13(q.get("c_nmr"))), [])
            uniq = sorted(set(hits))
            if len(uniq) != 1:
                ambiguous += 1
                continue
            truth[qid] = uniq[0]
        if ambiguous:
            raise SystemExit(f"{ambiguous} expansion questions did not have a unique gold join")
    return truth


def unique_constitutions(candidates: list) -> list[str]:
    """First-occurrence InChIKey-14. Unparseable strings are dropped and not promoted."""
    out, seen = [], set()
    for smiles in candidates or []:
        mol = Chem.MolFromSmiles(smiles) if smiles else None
        if mol is None:
            continue
        key = Chem.MolToInchiKey(mol)[:14]
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def score_file(predictions: Path, out: Path) -> None:
    records = read_jsonl(predictions)
    if not records:
        raise SystemExit(f"no predictions in {predictions}")
    truth = truth_for(records)
    max_k = 0
    parsed_rows = []
    for rec in records:
        qid = rec["qid"]
        if qid not in truth:
            raise SystemExit(f"no truth for {qid}")
        cands = list(rec.get("candidates") or [])
        raw_iks = [ik14(s) for s in cands]
        uniq = unique_constitutions(cands)
        max_k = max(max_k, len(cands), len(uniq))
        parsed_rows.append((rec, truth[qid], raw_iks, uniq))
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "arm", "model", "list_kind", "k_requested", "k", "n", "n_lists_ge_k",
        "top1", "recall", "precision_given_recall",
        "n_formula_match_rank1", "n_parseable_rank1", "n_empty", "identified",
    ]
    arms = sorted({r["arm"] for r, _, _, _ in parsed_rows})
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for arm in arms:
            group = [row for row in parsed_rows if row[0]["arm"] == arm]
            model = group[0][0]["model"]
            k_req = group[0][0]["k_requested"]
            n = len(group)
            n_empty = sum(1 for rec, _, _, _ in group if not rec.get("candidates"))
            for kind, index in (("raw_slots", 2), ("unique_constitutions", 3)):
                limit = max(len(row[index]) for row in group)
                if limit == 0:
                    writer.writerow({
                        "arm": arm, "model": model, "list_kind": kind,
                        "k_requested": k_req, "k": 0, "n": n, "n_lists_ge_k": 0,
                        "top1": f"0/{n}", "recall": f"0/{n}",
                        "precision_given_recall": "0/0",
                        "n_formula_match_rank1": "", "n_parseable_rank1": "",
                        "n_empty": n_empty, "identified": "true",
                    })
                    continue
                for k in range(1, limit + 1):
                    top1 = recall = ge = rank1_formula = rank1_parse = 0
                    for rec, tik, raw_iks, uniq in group:
                        iks = raw_iks if kind == "raw_slots" else uniq
                        prefix = iks[:k]
                        ge += int(len(iks) >= k)
                        recall += int(tik in prefix)
                        top1 += int(bool(prefix) and prefix[0] == tik)
                        if k == 1 and kind == "raw_slots":
                            raw0 = (rec.get("candidates") or [None])[0]
                            rank1_parse += int(ik14(raw0) is not None) if raw0 else 0
                            rank1_formula += int(formula_of(raw0) == rec.get("formula")) if raw0 else 0
                    writer.writerow({
                        "arm": arm,
                        "model": model,
                        "list_kind": kind,
                        "k_requested": k_req,
                        "k": k,
                        "n": n,
                        "n_lists_ge_k": ge,
                        "top1": f"{top1}/{n}",
                        "recall": f"{recall}/{n}",
                        "precision_given_recall": f"{top1}/{recall}" if recall else "0/0",
                        "n_formula_match_rank1": f"{rank1_formula}/{n}" if k == 1 and kind == "raw_slots" else "",
                        "n_parseable_rank1": f"{rank1_parse}/{n}" if k == 1 and kind == "raw_slots" else "",
                        "n_empty": n_empty if k == 1 else "",
                        "identified": "true",
                    })
    print(f"scored {len(records)} predictions, max stored list {max_k}. fractions -> {out}")
    print("No structure was printed.")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    exp = sub.add_parser("export")
    exp.add_argument("--arm", required=True, choices=("n60", "n500"))
    exp.add_argument("--outdir", type=Path, required=True)
    exp.add_argument("--k", type=int, default=10)
    exp.add_argument("--batch-size", type=int, default=6)
    col = sub.add_parser("collect")
    col.add_argument("--arm", required=True)
    col.add_argument("--outdir", type=Path, required=True)
    col.add_argument("--predictions", type=Path, required=True)
    col.add_argument("--model", default="grok-4.7-high-fast")
    sc = sub.add_parser("score")
    sc.add_argument("--predictions", type=Path, required=True)
    sc.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "export":
        export_prompts(args.arm, args.outdir, args.k, args.batch_size)
    elif args.cmd == "collect":
        collect(args.arm, args.outdir, args.predictions, args.model)
    else:
        score_file(args.predictions, args.out)


if __name__ == "__main__":
    main()
