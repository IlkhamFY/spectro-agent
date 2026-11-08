#!/usr/bin/env python3
"""Score a prediction jsonl with the arm's InChIKey-14 key. Does not call a model."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from payloads import load_arm  # noqa: E402
from score import score_ranked, summarize, write_json  # noqa: E402


def _ranked(row: dict) -> list[str]:
    if "ranked" not in row:
        return []
    out = []
    for item in row["ranked"]:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict) and item.get("smiles"):
            out.append(item["smiles"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=("60", "194", "306"))
    ap.add_argument("--pred", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    public, gold = load_arm(args.arm)
    by = {}
    for path in args.pred:
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                by[row["uid"]] = row
    scored = []
    missing = []
    for rec in public:
        row = by.get(rec["uid"])
        if row is None:
            missing.append(rec["uid"])
            continue
        item = score_ranked(_ranked(row), gold[rec["uid"]])
        item["uid"] = rec["uid"]
        item["cohort"] = rec["cohort"]
        item["difficulty"] = rec["difficulty"]
        scored.append(item)
    if missing:
        raise SystemExit(f"{len(missing)} predictions missing, e.g. {missing[:5]}")
    summary = summarize(scored)
    summary["rows"] = scored
    write_json(args.out, summary)
    print(json.dumps({k: summary[k] for k in ("n", "top1", "recall")}))


if __name__ == "__main__":
    main()
