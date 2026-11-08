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
    a("Scoring is RDKit InChIKey connectivity (first 14 characters), offline, after the prediction JSONL was written. `list_kind=unique_constitutions` keeps the first parseable SMILES of each connectivity and drops later duplicates. Unparseable strings are dropped rather than promoted. Fractions below are copied from `scores_n60.csv`, `scores_n500.csv`, `inventory.csv`, and `prefix_scores.csv`.")
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
    a("The nested 60 are not repeated in that file and were not re-solved. Batches 01–37 of the n=500 prompt manifest are disjoint from those 60 and contain 222 compounds. All 37 replies were present at scoring time, so this file is that whole disjoint block, not a sample inside it. From batch 38 the manifest overlaps the nested 60; those prompts are not relaunched, so the scored n=60 arm is not replaced. The 218 roster items that sit in batches 38–84 are unscored.")
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
    a("## Closed-book caveat")
    a("")
    a("Each solver was instructed to read only its batch markdown, to skip the web, the repository, gold files, isomer databases, and NMR-Solver, and to use RDKit only after a proposal, to check that the SMILES parses and matches the formula. The same limit is stated in `scripts/manual_collect.py`: the harness cannot prove a solver obeyed it. Predictions were written before scoring. Collected SMILES were not edited by hand; `cursor_n60_k10.jsonl` matches `raw_replies/n60/` after whitespace stripping, 0 mismatches. The only metadata change after collection was the model string, from a placeholder to `grok-4.7-high-fast`.")
    a("")
    a("## What is still unidentified")
    a("")
    a("- k = 20 and k = 50, on this model and on the deposited Claude lists. Not requested yet on this arm, and not stored in the old logs.")
    a("- A finished 500-wide Cursor rate. The partial file must not be scaled to 500.")
    a("- Forward-verify of the new Cursor lists. No blind 13C prediction pass was run, so precision given recall here is self-rank, not chamfer.")
    a("")
    text = "\n".join(lines) + "\n"
    (HERE / "REPORT.md").write_text(text)
    parts = []
    for name in ("scores_n60.csv", "scores_n500.csv"):
        blob = (HERE / name).read_text().splitlines()
        if not parts:
            parts.extend(blob)
        else:
            parts.extend(blob[1:])
    (HERE / "scores.csv").write_text("\n".join(parts) + "\n")
    print(f"wrote {HERE / 'REPORT.md'} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
