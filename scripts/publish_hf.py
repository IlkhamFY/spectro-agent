#!/usr/bin/env python3
"""Upload ilkhamfy/IRexp commercial DoR (F1 rebuild) to the Hugging Face Hub.

Requires a write-capable Hugging Face token:

  set HF_TOKEN=hf_...
  python scripts/publish_hf.py
  python scripts/publish_hf.py --dry-run
  python scripts/publish_hf.py --f1-commercial   # default path for 2026-09-10 rebuild
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ID = "ilkhamfy/IRexp"
ROOT = Path(__file__).resolve().parents[1]
STAGE_PUB = ROOT / "data/irexp_rebuild_20260910/hf_publish"

# F1 commercial-primary upload (NC / empty_unknown omitted from Hub this round)
F1_COMMERCIAL_FILES = [
    (ROOT / "data/irexp_release/README_HF.md", "README.md"),
    (ROOT / "data/NOTICE", "NOTICE"),
    (ROOT / "docs/scientific_data/LICENCE_REMEDIATION.md", "LICENCE_REMEDIATION.md"),
    (ROOT / "docs/LEADERBOARD.md", "LEADERBOARD.md"),
    (STAGE_PUB / "irexp_commercial.jsonl.gz", "data/irexp_commercial.jsonl.gz"),
    (STAGE_PUB / "irexp_resolved_commercial.jsonl.gz", "data/irexp_resolved_commercial.jsonl.gz"),
    (STAGE_PUB / "train_no_bench_commercial.jsonl.gz", "data/train_no_bench_commercial.jsonl.gz"),
    (STAGE_PUB / "build_stats.json", "data/f1_commercial_build_stats.json"),
]

# Files to remove from Hub primary (NC / empty / superseded multi-licence dumps)
F1_DELETE_PATHS = [
    "data/irexp_non_commercial.jsonl.gz",
    "data/irexp_empty_unknown.jsonl.gz",
    "data/irexp.jsonl.gz",
    "data/irexp_resolved.jsonl.gz",
    "data/irexp_sharealike.jsonl.gz",
    "data/pretrain_ir.jsonl.gz",
    "data/train_no_bench.jsonl.gz",
    "data/train_no_bench_nmr.jsonl.gz",
    "data/train_no_bench_stats.json",
    "data/train_no_bench_stats_nmr.json",
    "data/pmc_licence_summary.json",
]

# Legacy full multi-licence upload list (kept for reference / --legacy)
LEGACY_FILES = [
    (ROOT / "data/irexp_release/README_HF.md", "README.md"),
    (ROOT / "data/NOTICE", "NOTICE"),
    (ROOT / "data/irexp/irexp.jsonl.gz", "data/irexp.jsonl.gz"),
    (ROOT / "data/irexp_resolved/irexp_resolved.jsonl.gz", "data/irexp_resolved.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench.jsonl.gz", "data/train_no_bench.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench_nmr.jsonl.gz", "data/train_no_bench_nmr.jsonl.gz"),
    (ROOT / "data/irexp_release/pretrain_ir.jsonl.gz", "data/pretrain_ir.jsonl.gz"),
    (ROOT / "data/irexp_release/train_no_bench_stats.json", "data/train_no_bench_stats.json"),
    (ROOT / "data/irexp_release/train_no_bench_stats_nmr.json", "data/train_no_bench_stats_nmr.json"),
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
    ap.add_argument("--legacy", action="store_true", help="Upload legacy multi-licence file set")
    ap.add_argument(
        "--f1-commercial",
        action="store_true",
        default=True,
        help="Upload F1 commercial DoR (default)",
    )
    ap.add_argument("--no-delete-superseded", action="store_true")
    args = ap.parse_args()

    files = LEGACY_FILES if args.legacy else F1_COMMERCIAL_FILES

    missing = [str(src) for src, _ in files if not src.exists()]
    if missing:
        print("missing files:\n  " + "\n  ".join(missing))
        sys.exit(1)

    for src, dest in files:
        print(f"  {src.relative_to(ROOT)}  ({src.stat().st_size / 1e6:.1f} MB) -> {dest}")

    if args.dry_run:
        if not args.legacy and not args.no_delete_superseded:
            print("would delete:", ", ".join(F1_DELETE_PATHS))
        print("dry-run: no upload")
        return

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not token:
        # try workspace dotenv without printing
        env_path = Path.home() / ".openclaw" / "workspace" / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith("HF_TOKEN="):
                    token = s.split("=", 1)[1].strip().strip('"').strip("'")
                    os.environ["HF_TOKEN"] = token
                    break
    if not token:
        print(
            "ERROR: set HF_TOKEN to a Write token from https://huggingface.co/settings/tokens",
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

    # Prefer folder-style commit when possible; fall back to per-file
    ops_msg = "F1 commercial DoR: 88545 + resolved/train_no_bench commercial; flags F2/F3; omit NC/empty"
    for src, dest in files:
        print(f"uploading {dest} ...")
        api.upload_file(
            path_or_fileobj=str(src),
            path_in_repo=dest,
            repo_id=args.repo_id,
            repo_type="dataset",
            commit_message=ops_msg if dest.endswith(".jsonl.gz") else f"Update {dest}",
        )

    if not args.legacy and not args.no_delete_superseded:
        existing = set(api.list_repo_files(args.repo_id, repo_type="dataset"))
        to_del = [p for p in F1_DELETE_PATHS if p in existing]
        for p in to_del:
            print(f"deleting superseded {p} ...")
            api.delete_file(
                path_in_repo=p,
                repo_id=args.repo_id,
                repo_type="dataset",
                commit_message=f"Omit superseded non-commercial/multi-licence file {p}",
            )

    info = api.dataset_info(args.repo_id)
    print(f"done: https://huggingface.co/datasets/{args.repo_id}")
    print(f"revision: {info.sha}")


if __name__ == "__main__":
    main()
