# HF publish — F1 commercial DoR (2026-09-10)

**Status:** published to Hugging Face (Zenodo **not** minted).
**Actor:** IlkhamFY via Chem Partner decision — commercial dataset-of-record with F2/F3 kept as flag fields (rows not excluded).

## Hub

| Field | Value |
|-------|-------|
| URL | https://huggingface.co/datasets/ilkhamfy/IRexp |
| Revision (tip after upload + omit superseded) | `2fb44992d33b389e2ba30d6d03a6ac76a261855a` |
| YAML license | `cc-by-4.0` (commercial DoR) |
| Zenodo DOI | **pending** (not invented) |

## Counts (stream-verified from Hub revision above)

| Config / file | n |
|---|---:|
| `commercial` (`data/irexp_commercial.jsonl.gz`) | **88545** |
| `resolved_commercial` | 28899 |
| `train_no_bench_commercial` | 29111 |
| F2 `ir_shared_in_paper` (commercial) | 18651 |
| F3 `ir_table_flatten_suspect` (commercial) | 3154 |

All streamed commercial rows have `license_pool=commercial`. Licence fields retained: `license`, `license_pool`, `license_raw`, `license_source`.

## Source bytes (staged, gitignored)

- Stage root: `data/irexp_rebuild_20260910/`
- Curated: `irexp_reparsed_refetch.jsonl.gz`
- Flags: `irexp_ir_quality_flags.jsonl.gz`, `irexp_resolved_ir_quality_flags.jsonl.gz`
- Materialised publish set: `data/irexp_rebuild_20260910/hf_publish/`
- Builder: `scripts/build_hf_commercial_f1.py`
- Uploader: `scripts/publish_hf.py` (default `--f1-commercial`)

## Spot-check PMC6268696

- Row `id=73c2e8a41a6601afa622` is commercial.
- `ir_bands_cm-1` = `[3060.0, 2976.0, 2874.0, 1730.0, 1678.0]` — **PASS** (streamed from Hub).

## Hub file list (this revision)

- `README.md`, `NOTICE`, `LICENCE_REMEDIATION.md`, `LEADERBOARD.md`
- `data/irexp_commercial.jsonl.gz`
- `data/irexp_resolved_commercial.jsonl.gz`
- `data/train_no_bench_commercial.jsonl.gz`
- `data/f1_commercial_build_stats.json`
- `.gitattributes`

**Omitted from Hub this round** (deleted if previously present): NC, empty_unknown, sharealike, multi-licence `irexp.jsonl.gz` / resolved / pretrain / train_no_bench dumps.

## Card notes

- F1 thousands-separator rebuild + refetch merge documented.
- F2/F3 flag-only policy; headline commercial **n remains 88545**.
- No unrecomputed manuscript totals beyond commercial 88545 claimed on the card.
- Zenodo DOI line left pending.

## Repo commit

| Field | Value |
|-------|-------|
| Git commit | 3af6f5af244cbec0c8f763973fedd5d93af3de20 |
| Author | Ilkham Yabbarov <ilkhamfy@gmail.com> |
| Message | Publish F1 commercial IRexp DoR to HF (flags kept). |
| GitHub | https://github.com/IlkhamFY/spectro-agent/commit/3af6f5af244cbec0c8f763973fedd5d93af3de20 |
