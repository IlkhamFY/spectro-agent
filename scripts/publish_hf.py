#!/usr/bin/env python3
"""Create and upload ilkhamfy/IRexp to the Hugging Face Hub.

Requires a write-capable Hugging Face token in the environment:

  export HF_TOKEN=hf_...   # https://huggingface.co/settings/tokens  (Write)
  python scripts/publish_hf.py

Or:  HF_TOKEN=hf_... python scripts/publish_hf.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ID = "ilkhamfy/IRexp"
ROOT = Path(__file__).resolve().parents[1]

# (local path, path_in_repo)
FILES = [
    (ROOT / "data/irexp_release/README_HF.md", "README.md"),
    (ROOT / "data/NOTICE", "NOTICE"),
    (ROOT / "data/irexp/irexp.jsonl.gz", "data/irexp.jsonl.gz"),
    (ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz", "data/irexp_resolved.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench.jsonl.gz", "data/train_no_bench.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench_nmr.jsonl.gz", "data/train_no_bench_nmr.jsonl.gz"),
    (ROOT / "data/irexp_release/pretrain_ir.jsonl.gz", "data/pretrain_ir.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench_stats.json", "data/train_no_bench_stats.json"),
    (ROOT / "data/irexp_release/train_no_bench_stats_nmr.json", "data/train_no_bench_stats_nmr.json"),
    # Licence-remediated pools (commercial = primary redistributable)
    (ROOT / "data/irexp/licence_pools/irexp_commercial.jsonl.gz", "data/irexp_commercial.jsonl.gz"),
    (ROOT / "data/irexp/licence_pools/irexp_non_commercial.jsonl.gz", "data/irexp_non_commercial.jsonl.gz"),
    (ROOT / "data/irexp/licence_pools/irexp_sharealike.jsonl.gz", "data/irexp_sharealike.jsonl.gz"),
    (ROOT / "data/irexp/licence_pools/irexp_empty_unknown.jsonl.gz", "data/irexp_empty_unknown.jsonl.gz"),
    (ROOT / "data/irexp/pmc_licence_summary.json", "data/pmc_licence_summary.json"),
    (ROOT / "docs/scientific_data/LICENCE_REMEDIATION.md", "LICENCE_REMEDIATION.md"),
    (ROOT / "docs/LEADERBOARD.md", "LEADERBOARD.md"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repo-id", default=REPO_ID)
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args()

    missing = [str(src) for src, _ in FILES if not src.exists()]
    if missing:
        print("missing files:\n  " + "\n  ".join(missing))
        sys.exit(1)

    for src, dest in FILES:
        print(f"  {src.relative_to(ROOT)}  ({src.stat().st_size / 1e6:.1f} MB) -> {dest}")

    if args.dry_run:
        print("dry-run: no upload")
        return

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not token:
        print(
            "ERROR: set HF_TOKEN to a Write token from https://huggingface.co/settings/tokens\n"
            "  The Cursor Hugging Face MCP is authenticated for read/search only;\n"
            "  uploads need a Write user access token in this environment.",
            file=sys.stderr,
        )
        sys.exit(2)

    from huggingface_hub import HfApi, login

    login(token=token, add_to_git_credential=False)
    api = HfApi()
    who = api.whoami()
    print(f"authenticated as {who['name']}")

    api.create_repo(
        repo_id=args.repo_id,
        repo_type="dataset",
        private=args.private,
        exist_ok=True,
    )
    print(f"repo ready: https://huggingface.co/datasets/{args.repo_id}")

    for src, dest in FILES:
        print(f"uploading {dest} ...")
        api.upload_file(
            path_or_fileobj=str(src),
            path_in_repo=dest,
            repo_id=args.repo_id,
            repo_type="dataset",
            commit_message=f"Add {dest}",
        )
    print(f"done: https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()
