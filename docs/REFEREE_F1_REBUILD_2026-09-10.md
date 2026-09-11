# Referee F1 IR rebuild — 2026-09-10

Code-focused remediations for IRexp thousands-separator truncation (F1), plus
optional F2/F3 quality flags. **No Zenodo mint. Production HF not overwritten.**

## A) Parser fix merged

| Item | Value |
|------|-------|
| Branch | `fix/ir-thousands` |
| Fix commit | `35808ead98bea04f1cd5a27a9f4cb60c631d44f6` |
| PR | https://github.com/IlkhamFY/spectro-agent/pull/38 |
| Merge commit on `main` | `432932a` |
| Tests | `12 passed` (`tests/test_extract.py`) |

### Commands

```powershell
cd C:\Users\zolot\.openclaw\workspace\projects\spectro-agent
gh pr create --base main --head fix/ir-thousands `
  --title "Fix IR thousands-separator parsing in band extraction" `
  --body "..."
gh pr merge 38 --merge
git checkout main ; git pull origin main
C:\Users\zolot\miniforge3\python.exe -m pytest tests/test_extract.py -q
```

Fix: `spectro_scraper/extract.py` `_parse_ir_bands` strips US thousands commas
(`2,976` → `2976`) before matching; leaves spaced list separators alone.

## B) Source inventory (local)

| Artifact | Path | Notes |
|----------|------|-------|
| Harvest snapshot | `data/irexp/ir_harvest_snapshot.jsonl.gz` | **N=134893**, every row has `ir_raw` + `ir_bands_cm-1` |
| Seen papers | `data/irexp/seen_papers.txt.gz` | present |
| Curated IRexp | `data/irexp/irexp.jsonl.gz` | N=121233; **no `ir_raw`** (bands only + structure/license) |
| Resolved | `data/irexp_resolved/irexp_resolved.jsonl.gz` | N=43060 |
| Release train/test/pretrain | `data/irexp_release/*.jsonl.gz` | present |
| PMC OA txt cache | — | **not found locally** |
| Chemotion ingest | `data/chemotion/` | gitignored; not used tonight |

**Fast path chosen:** re-parse harvest `ir_raw` with fixed `_parse_ir_bands`, then
propagate new bands into curated/release rows via
`(source_doi, old_bands)` (fallback `(source_doi, h_nmr, c_nmr)`).
No PMC re-fetch required for the bulk of F1; unmatched curated rows keep old bands.

## C) Rebuild commands

```powershell
cd C:\Users\zolot\.openclaw\workspace\projects\spectro-agent
C:\Users\zolot\miniforge3\python.exe scripts\rebuild_ir_bands_from_raw.py `
  --outdir data\irexp_rebuild_20260910

C:\Users\zolot\miniforge3\python.exe scripts\flag_ir_quality.py `
  --input data\irexp_rebuild_20260910\irexp_reparsed.jsonl.gz `
  --out data\irexp_rebuild_20260910\irexp_ir_quality_flags.jsonl.gz

C:\Users\zolot\miniforge3\python.exe scripts\flag_ir_quality.py `
  --input data\irexp_rebuild_20260910\irexp_resolved_reparsed.jsonl.gz `
  --out data\irexp_rebuild_20260910\irexp_resolved_ir_quality_flags.jsonl.gz

C:\Users\zolot\miniforge3\python.exe scripts\flag_ir_quality.py `
  --input data\irexp_rebuild_20260910\release_train_reparsed.jsonl.gz `
  --out data\irexp_rebuild_20260910\release_train_ir_quality_flags.jsonl.gz
```

Staging root (do **not** push to HF until Ilkham OK):

`data/irexp_rebuild_20260910/`

## D) Before / after — `max(band) < 1000` proxy

| Dataset | N | max&lt;1000 before | max&lt;1000 after | rows changed | unmatched |
|---------|---|-------------------:|------------------:|-------------:|----------:|
| Harvest snapshot | 134893 | 3733 | 771 | 15747 | 0 (all have `ir_raw`) |
| `irexp.jsonl.gz` | 121233 | 1757 | 78 | 9532 | 3045 |
| `irexp_resolved` | 43060 | 510 | 2 | 2548 | 2333 |
| release `train` | 25280 | 341 | **0** | 1599 | 404 |
| release `test` | 2808 | 33 | 1 | 184 | 41 |
| release `pretrain_ir` | 119345 | 1756 | 77 | 9532 | 1157 |
| release `train_no_bench` | 42808 | 508 | 2 | 2535 | 2332 |

Harvest rows with thousands-comma pattern in `ir_raw`: **3507**.

Full machine stats: `data/irexp_rebuild_20260910/rebuild_stats.json`.

## E) PMC6268696 check

Referee example compound (raw: `ν (cm-1): 3,060, 2,976, 2,874 (CH stretching), 1,730, 1,678 (CO)`):

| | bands |
|--|-------|
| Before | `[976, 874, 730, 678]` |
| After | `[3060, 2976, 2874, 1730, 1678]` |
| Expected | `[3060, 2976, 2874, 1730, 1678]` |

**PASS** — expected set present among the 12 PMC6268696 curated compounds after rebuild
(other compounds in that paper correctly keep their own distinct band sets).

## F) F2 / F3 flag sidecars (no rows dropped)

Script: `scripts/flag_ir_quality.py`

| Flag | Meaning |
|------|---------|
| `ir_shared_in_paper` (F2) | Same `pmcid`, identical `ir_bands` tuple across ≥2 distinct ids/InChIKeys |
| `ir_table_flatten_suspect` (F3) | After a band &lt;1500, a later band ≥2800 (X-H after fingerprint) |

| Input | N | F2 true | F3 true | F2 shared groups |
|-------|---:|--------:|--------:|-----------------:|
| `irexp_reparsed` | 121233 | 20666 | 6086 | 9539 |
| `irexp_resolved_reparsed` | 43060 | 1977 | 2921 | 910 |
| `release_train_reparsed` | 25280 | 1415 | 768 | 661 |

Sidecars live next to rebuild outputs (`*_ir_quality_flags.jsonl.gz` + `*_stats.json`).

## G) Outputs checklist

- `ir_harvest_snapshot_reparsed.jsonl.gz`
- `irexp_reparsed.jsonl.gz`
- `irexp_resolved_reparsed.jsonl.gz`
- `release_{train,test,pretrain_ir,train_no_bench}_reparsed.jsonl.gz`
- `*_ir_quality_flags.jsonl.gz` (+ stats)
- `rebuild_stats.json`

## H) Blockers / follow-ups

1. **Unmatched curated rows** (no harvest join key): keep old bands — 3045 on full irexp,
   2333 on resolved. Residual `max&lt;1000` after rebuild is largely these + true
   fingerprint-only spectra. Optional next step: targeted PMC OA re-fetch for residual
   `max&lt;1000` rows (no local PMC txt cache tonight).
2. **Do not overwrite HF / Zenodo** until Ilkham reviews staged rebuild + F2/F3 drop policy.
3. F2/F3 are **flags only** — user decides which rows to drop for the next curated release.
4. No AI coauthor; git author unchanged (`Ilkham Yabbarov <ilkhamfy@gmail.com>`).
