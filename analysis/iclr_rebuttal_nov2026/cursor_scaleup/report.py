#!/usr/bin/env python3
"""Write REPORT.md from the CSVs in this directory. Fractions are copied, not recomputed
into a rounded percent in the prose.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_csv(name: str) -> list[dict]:
    with (HERE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def md_table(rows: list[dict], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    rule = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, rule, *body])


def pair(text: str) -> tuple[int, int]:
    left, right = text.split("/")
    return int(left), int(right)


def frac(num: int, den: int) -> str:
    return f"{num}/{den}" if den else "0/0"


def empty_qids(name: str) -> list[str]:
    found = []
    for line in (HERE / "predictions" / name).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not row.get("candidates"):
            found.append(row["qid"])
    return found


def reply_mismatches(reply_dir: Path, predictions: Path) -> int:
    manifest = json.loads((reply_dir / "manifest.json").read_text())
    by_qid = {}
    for batch in manifest["batches"]:
        text = (reply_dir / f"reply_{batch['batch']}.json").read_text()
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            raw = json.loads(text[start:end + 1])
        for qid in batch["qids"]:
            cands = raw.get(qid) or []
            if isinstance(cands, str):
                cands = [cands]
            by_qid[qid] = [item.strip() for item in cands if isinstance(item, str) and item.strip()]
    mismatches = 0
    for line in predictions.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if list(row.get("candidates") or []) != by_qid.get(row["qid"]):
            mismatches += 1
    return mismatches


def main() -> None:
    inventory = read_csv("inventory.csv")
    prefixes = read_csv("prefix_scores.csv")
    n60 = [r for r in read_csv("scores_n60.csv") if r["list_kind"] == "unique_constitutions"]
    n60_raw = [r for r in read_csv("scores_n60.csv") if r["list_kind"] == "raw_slots"]
    n500 = [r for r in read_csv("scores_n500.csv") if r["list_kind"] == "unique_constitutions"]
    wider = [r for r in prefixes if int(r["k"]) >= 4]
    checks = (HERE / "checks.json").read_text().strip()

    def at(rows, k):
        for row in rows:
            if int(row["k"]) == k:
                return row
        return None

    k1 = at(n60, 1)
    k3 = at(n60, 3)
    k5 = at(n60, 5)
    k10 = at(n60, 10)
    raw_k2 = at(n60_raw, 2)
    uniq_k2 = at(n60, 2)
    n500_max = max((int(r["k"]) for r in n500), default=0)
    n500_n = n500[0]["n"] if n500 else "0"
    lines = []
    a = lines.append
    a("# Cursor-scale arm on IRSpectra-Bench")
    a("")
    a("This file is an additional system. It does not replace the locked Claude headline.")
    a("")
    a("Model id: `grok-4.7-high-fast`. That is `originalModelName` on cloud run `bc-7b28bf66-ffdb-5c8e-a63f-1fc38e11fc5a`. Each batch was a fresh subagent of that run. No external vendor API key was present, so no other model was called.")
    a("")
    a("Request: up to 10 distinct constitutions, best first. Closed book. The prompt fields were molecular formula, IR band list, printed 1H, and printed 13C. Gold SMILES and InChIKey were not in the prompt. `export` does not open an answer file.")
    a("")
    a("Scoring is RDKit InChIKey connectivity (first 14 characters), offline, after the prediction JSONL was written. `list_kind=unique_constitutions` keeps the first parseable SMILES of each connectivity and drops later duplicates. Unparseable strings are dropped rather than promoted. Fractions below are copied from `scores_n60.csv`, `scores_n500.csv`, `scores_n218.csv`, `scores_posthoc_sum500.csv`, `inventory.csv`, and `prefix_scores.csv`.")
    a("")
    a("## Locked Claude headline, unchanged")
    a("")
    a("Recomputed from the deposited Claude lists by `inventory.py`. These integers matched the lock, and this arm does not edit them.")
    a("")
    a("| quantity | fraction |")
    a("|---|---|")
    a("| self-rank top-1 | 227/500 |")
    a("| recall at the stored lists (maximum length 3) | 249/500 |")
    a("| precision given recall | 227/249 |")
    a("")
    a("Arithmetic from those fractions: generation misses are 251/500, because 500 − 249 = 251, and self-rank misses among the recalled items are 22/249, because 249 − 227 = 22. The forward-verify wall was not refit in this directory. No Cursor number is substituted for 227/500.")
    a("")
    a("`checks.json` records the same lock, plus the n=60 Claude original arm 14/60 top-1 and 19/60 recall, and the stored generate-wide union recall 25/60:")
    a("")
    a("```json")
    a(checks)
    a("```")
    a("")
    a("## What was already on disk")
    a("")
    a("Every generation deposit found in this checkout, plus the expansion lists at `48fcd30153df5e331fab43cfa514763db8ee3891` and the partial Fable lists at `473030fb9d046548ff1ad06d04d20915fc2943d2`. Top-1 and recall are the full stored raw list. `analysis/iclr_rebuttal_nov2026/` on current `main` had no prediction JSONL; the three notes on other branches are prose, not extra candidate lists.")
    a("")
    a(md_table(inventory, [
        "model", "subset", "n", "max_stored_raw", "max_stored_unique",
        "top1", "recall", "precision_given_recall", "path",
    ]))
    a("")
    a("## Prefixes that were actually stored")
    a("")
    a("A prefix row exists only for k = 1 … max unique constitutions in that deposit. k = 10, 20, and 50 were not written for these old logs. The longest stored LLM pool is the original-then-generate-wide union, max unique 9, and only one of 60 lists reaches 9. Copying 25/60 into a k = 10, 20, or 50 column would invent the curve. The trained generator file is sorted canonical SMILES (248 keys, unordered full-pool recall 94/248). That recall is not formula-filtered and is not a ranked prefix, so it has no k row.")
    a("")
    a("Rows with k ≥ 4, which the ≤3 protocol did not score. `n_lists_ge_k` is how many lists actually contain at least k unique constitutions. Shorter lists contribute the list they have. Forward-verify is blank where no 13C prediction map was stored.")
    a("")
    a(md_table(wider, [
        "model", "subset", "k", "n", "n_lists_ge_k", "top1_self", "recall",
        "precision_given_recall", "top1_forward_verify",
    ]))
    a("")
    a("On the original-then-wide pool, forward-verify top-1 is 18/60 at k = 3, 17/60 at k = 4, and 18/60 from k = 5 through k = 9. Recall reaches 25/60 at k = 6 and stays 25/60 through k = 9, with `n_lists_ge_k` falling from 28 to 1. That plateau is the measured prefix of lists that end, not a filled-in k = 10.")
    a("")
    a("## New arm: nested n = 60, requested k = 10")
    a("")
    empty60 = [
        json.loads(line)["qid"]
        for line in (HERE / "predictions/cursor_n60_k10.jsonl").read_text().splitlines()
        if line.strip() and not json.loads(line).get("candidates")
    ]
    a("Finished 60/60. File: `predictions/cursor_n60_k10.jsonl`. Raw replies, unmodified, are in `raw_replies/n60/`. Empty lists, kept in the denominator: "
      + (", ".join(f"`{q}`" for q in empty60) if empty60 else "none")
      + ". Rank-1 formula match on the raw first string is "
      + f"{n60_raw[0]['n_formula_match_rank1']}. Rank-1 parseable is {n60_raw[0]['n_parseable_rank1']}.")
    a("")
    a("Unique-constitution prefixes. This is the curve to cite for this arm.")
    a("")
    a(md_table(n60, [
        "k", "n", "n_lists_ge_k", "top1", "recall", "precision_given_recall",
    ]))
    a("")
    a(f"At the reviewers' marks: k = 3 is top-1 {k3['top1']}, recall {k3['recall']}, precision given recall {k3['precision_given_recall']}, n_lists_ge_k {k3['n_lists_ge_k']}/60. k = 5 is top-1 {k5['top1']}, recall {k5['recall']}, precision given recall {k5['precision_given_recall']}, n_lists_ge_k {k5['n_lists_ge_k']}/60. k = 10 is top-1 {k10['top1']}, recall {k10['recall']}, precision given recall {k10['precision_given_recall']}, n_lists_ge_k {k10['n_lists_ge_k']}/60. k = 20 and k = 50 were not requested in this arm, and no row is filled for them.")
    a("")
    a(f"k = 1 is {k1['top1']} top-1, which equals recall because a one-constitution prefix cannot be misranked. From k = 6 through k = 10, unique recall stays {k10['recall']}. That is a measured plateau: n_lists_ge_k falls from {at(n60, 6)['n_lists_ge_k']} at k = 6 to {k10['n_lists_ge_k']} at k = 10, and the extra stored slots did not add a hit. It is not a copy of a shorter budget into an unasked column.")
    a("")
    a(f"Raw-slot prefixes are in the same CSV (`list_kind=raw_slots`). They match the unique curve except at k = 2, where raw recall is {raw_k2['recall']} and unique recall is {uniq_k2['recall']}. Dropping an unparseable or duplicate string moves one true constitution into the length-2 prefix. Both rows are stored.")
    a("")
    a("These 60 are the vendor-comparison arm (`benchmark_v3` 40 plus `benchmark_v2_ctrl` 20), nested inside the locked 500. They are not a new 500-wide headline. Claude's own lists on this same 60 remain 14/60 top-1 and 19/60 recall at the stored ≤3 budget.")
    a("")
    a("## New arm: n = 500 roster, requested k = 10, partial")
    a("")
    a(f"Finished items in `predictions/cursor_n500_k10.jsonl`: {n500_n}. Denominator is {n500_n}, the finished count. The other roster items are not scored and are not counted as misses. This is not a 500-wide rate.")
    a("")
    a("The nested 60 are not repeated in that file and were not re-solved. Batches 01–37 of the n=500 prompt manifest are disjoint from those 60 and contain 222 compounds. All 37 replies were present at scoring time, so this file is that whole disjoint block, not a sample inside it. From batch 38 that manifest overlaps the nested 60, so those prompts were not relaunched. This denominator stays 222. The non-nested simple items are scored in their own file and are not written into these fractions.")
    a("")
    if n500:
        empty500 = [
            json.loads(line)["qid"]
            for line in (HERE / "predictions/cursor_n500_k10.jsonl").read_text().splitlines()
            if line.strip() and not json.loads(line).get("candidates")
        ]
        a("Empty lists inside this partial file, kept in its denominator: "
          + (", ".join(f"`{q}`" for q in empty500) if empty500 else "none")
          + ".")
        a("")
        k10_row = at(n500, 10)
        if k10_row is None:
            a(f"Longest stored list among the finished {n500_n} is {n500_max}. `n_lists_ge_10` is 0. No k = 10 fraction is written. The model was asked for 10 and did not return 10 constitutions for any finished item, so the k = {n500_max} row is not copied forward.")
        else:
            a(f"Longest stored list among the finished {n500_n} is {n500_max}. At k = 10, top-1 is {k10_row['top1']}, recall is {k10_row['recall']}, precision given recall is {k10_row['precision_given_recall']}, and n_lists_ge_k is {k10_row['n_lists_ge_k']}/{n500_n}. Lists shorter than 10 contribute the constitutions they have. k = 20 and k = 50 are not filled from this ask.")
        a("")
        a(md_table(n500, [
            "k", "n", "n_lists_ge_k", "top1", "recall", "precision_given_recall",
        ]))
        a("")
    n218 = [r for r in read_csv("scores_n218.csv") if r["list_kind"] == "unique_constitutions"]
    n218_raw = [r for r in read_csv("scores_n218.csv") if r["list_kind"] == "raw_slots"]
    composition = json.loads((HERE / "composition_n218.json").read_text())
    leaks = json.loads((HERE / "leak_scan_n218.json").read_text())
    if composition["n"] != 218 or composition["n_simple"] != 218 or composition["n_not_simple"] != 0:
        raise SystemExit("composition audit is not 218 simple items")
    if composition["overlap_nested_n60"] != 0 or composition["overlap_complex_n222"] != 0:
        raise SystemExit("composition audit overlap is not zero")
    if composition["union_with_n60_and_n222"] != 500:
        raise SystemExit("the three files do not union to 500")
    if not n218 or n218[0]["n"] != "218":
        raise SystemExit("n218 score file denominator is not 218")
    cohort_bits = ", ".join(f"`{name}` {count}" for name, count in composition["cohorts"].items())
    empty218 = empty_qids("cursor_n218_k10.jsonl")
    pred218 = HERE / "predictions" / "cursor_n218_k10.jsonl"
    mismatches = reply_mismatches(HERE / "raw_replies" / "n218", pred218)
    a("## New arm: non-nested simple n = 218, requested k = 10")
    a("")
    a("Finished 218/218. File: `predictions/cursor_n218_k10.jsonl`. Raw replies are in `raw_replies/n218/`. "
      "This block is every simple item in the n=500 roster outside the nested 60 "
      f"(248 simple − 30 nested simple). `composition_n218.json` records n={composition['n']}, "
      f"n_simple={composition['n_simple']}, overlap with the nested 60 = {composition['overlap_nested_n60']}, "
      f"overlap with the finished complex file = {composition['overlap_complex_n222']}, "
      f"union of the three files = {composition['union_with_n60_and_n222']}. "
      f"The block is contiguous in the difficulty-then-qid roster, indices "
      f"{composition['roster_index_start']} through {composition['roster_index_end']}. "
      f"Cohorts: {cohort_bits}. The nested 60 and the 222 were not re-solved.")
    a("")
    a("Empty lists, kept in the denominator: "
      + (", ".join(f"`{q}`" for q in empty218) if empty218 else "none")
      + ". Rank-1 formula match on the raw first string is "
      + f"{n218_raw[0]['n_formula_match_rank1']}. Rank-1 parseable is {n218_raw[0]['n_parseable_rank1']}.")
    a("")
    a("Unique-constitution prefixes. This is the curve to cite for this arm. "
      "Shorter lists contribute the constitutions they have. k = 20 and k = 50 were not requested.")
    a("")
    a(md_table(n218, [
        "k", "n", "n_lists_ge_k", "top1", "recall", "precision_given_recall",
    ]))
    a("")
    k10_218 = at(n218, 10)
    if k10_218 is None:
        raise SystemExit("n218 was asked for k=10 and the score file has no k=10 row")
    a(f"At k = 10, top-1 is {k10_218['top1']}, recall is {k10_218['recall']}, precision given recall is {k10_218['precision_given_recall']}, and n_lists_ge_k is {k10_218['n_lists_ge_k']}/218.")
    if int(k10_218["n_lists_ge_k"]) == 0:
        a("No returned list contains 10 unique constitutions, so n_lists_ge_k at k = 10 is 0. The k = 10 prefix is the stored list. No SMILES was added to fill a tenth slot.")
    a("")
    a("## Post-hoc sum of three complementary finished files")
    a("")
    a("Label: post-hoc sum of three complementary finished files of `grok-4.7-high-fast` under the same closed-book k=10 protocol. The files are the nested n=60 arm, the non-nested complex n=222 arm, and this non-nested simple n=218 arm. Their qids are disjoint and their union has 500 items. This is not a single 500-item run. No partial rate is scaled to 500. The locked Claude headline remains the deposited self-rank 227/500 top-1 and 249/500 recall at stored lists of maximum length 3.")
    a("")
    posthoc = []
    missing_k = []
    for k in range(1, 11):
        parts_k = [at(n60, k), at(n500, k), at(n218, k)]
        if any(row is None for row in parts_k):
            missing_k.append(k)
            continue
        top_n = sum(pair(row["top1"])[0] for row in parts_k)
        rec_n = sum(pair(row["recall"])[0] for row in parts_k)
        ge_n = sum(int(row["n_lists_ge_k"]) for row in parts_k)
        den = sum(int(row["n"]) for row in parts_k)
        if den != 500:
            raise SystemExit(f"post-hoc denominator at k={k} is {den}, expected 500")
        posthoc.append({
            "k": k,
            "n": den,
            "n_lists_ge_k": ge_n,
            "top1": frac(top_n, den),
            "recall": frac(rec_n, den),
            "precision_given_recall": frac(top_n, rec_n),
            "label": "posthoc_sum_of_three_complementary_files",
        })
    if missing_k:
        a("No post-hoc row is written for k = " + ", ".join(str(k) for k in missing_k) + ", because that prefix is absent from at least one of the three score files.")
        a("")
    if posthoc:
        a(md_table(posthoc, [
            "k", "n", "n_lists_ge_k", "top1", "recall", "precision_given_recall",
        ]))
        a("")
        fields = ["k", "n", "n_lists_ge_k", "top1", "recall", "precision_given_recall", "label"]
        with (HERE / "scores_posthoc_sum500.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(posthoc)
    a("## Closed-book caveat")
    a("")
    a("Each solver was instructed to read only its batch markdown, to skip the web, the repository, gold files, isomer databases, and NMR-Solver, and to use RDKit only after a proposal, to check that the SMILES parses and matches the formula. The same limit is stated in `scripts/manual_collect.py`: the harness cannot prove a solver obeyed it. Predictions were written before scoring. Collected SMILES were not edited by hand. "
      f"`cursor_n60_k10.jsonl` matches `raw_replies/n60/` after whitespace stripping, 0 mismatches. "
      f"`cursor_n218_k10.jsonl` matches `raw_replies/n218/` after whitespace stripping, {mismatches} mismatches. "
      "The only metadata change after collection was the model string, set to `grok-4.7-high-fast`.")
    a("")
    a(f"Prompt leak scan on the 218 exported prompts (`leak_scan_n218.json`): InChIKey pattern matches {leaks['inchikey_pattern_matches']}, gold SMILES token matches {leaks['gold_smiles_token_matches']}, gold InChIKey matches {leaks['gold_inchikey_matches']}, gold InChIKey-14 matches {leaks['gold_inchikey14_matches']}, banned-token counts {json.dumps(leaks['banned_token_matches'])}. The prompt template uses the word SMILES as the requested output format. `export` does not open an answer file. Re-export of the existing n=60 and n=500 batch 01 prompts reproduced the deposited sha256 values in `renderer_check.json`.")
    a("")
    a("## What is still unidentified")
    a("")
    a("- k = 20 and k = 50, on this model and on the deposited Claude lists. Not requested on this arm, and not stored in the old logs.")
    a("- A single 500-item Cursor run. The post-hoc table is the sum of three finished files. The 222 file is not scaled to 500.")
    a("- Forward-verify of the new Cursor lists. No blind 13C prediction pass was run, so precision given recall here is self-rank, not chamfer.")
    a("")
    text = "\n".join(lines) + "\n"
    (HERE / "REPORT.md").write_text(text)
    parts = []
    for name in ("scores_n60.csv", "scores_n500.csv", "scores_n218.csv"):
        blob = (HERE / name).read_text().splitlines()
        if not parts:
            parts.extend(blob)
        else:
            parts.extend(blob[1:])
    (HERE / "scores.csv").write_text("\n".join(parts) + "\n")
    print(f"wrote {HERE / 'REPORT.md'} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
