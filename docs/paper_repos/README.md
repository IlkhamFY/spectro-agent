# Clean paper repositories

Two single-purpose manuscript repos were prepared as pristine local trees
(agent token cannot `gh repo create` under `IlkhamFY`).

| Paper | Local path | Suggested GitHub name | Overleaf main file | Compiler |
|---|---|---|---|---|
| Scientific Data (IRexp) | `/workspace/exports/IRexp` | `IlkhamFY/IRexp` | `scientific_data.tex` | pdfLaTeX |
| ICLR (IRSpectra-Bench) | `/workspace/exports/IRSpectra-Bench` | `IlkhamFY/IRSpectra-Bench` | `iclr_paper.tex` | pdfLaTeX |

## Packs (this repo)

Under `artifacts/paper_repos/`:

- `IRexp-overleaf.zip` / `IRSpectra-Bench-overleaf.zip` — Overleaf zip upload
- `IRexp-git.tar.gz` / `IRSpectra-Bench-git.tar.gz` — git repos with single `release v0.1` commit
- See also `PUSH_INSTRUCTIONS.md`

## What each repo contains

### IRexp (Sci Data only)

- `scientific_data.tex` + `references.bib` + vendored `sn-jnl` / `.bst`
- `figures/` — positioning, pipeline, distribution
- `data/` — manifests + HF/Zenodo **pointers** (no large `jsonl.gz`)
- `HUMAN_SUBMISSION_CHECKLIST.md`, `LICENCE_REMEDIATION.md`, `ZENODO_DATA_ONLY_CHECKLIST.md`
- `OVERLEAF.md`, `COMMIT_POLICY.md`, `scripts/build_pdf.py`
- Omitted: peer-review simulation, figure-agent playbooks, ICLR content

### IRSpectra-Bench (ICLR only)

- `iclr_paper.tex` + ICLR 2026 style files + cited figures
- `docs/LEADERBOARD.md`, `BENCHMARK.md`, `SUBMISSION.md`
- `OVERLEAF.md`, `COMMIT_POLICY.md`, `scripts/build_pdf.py`
- Omitted: Sci Data sn-jnl manuscript / licence-pool dumps

## Commit author used in packs

**Ilkham Yabbarov \<ilkhamfy@gmail.com\>** (author + committer), message `release v0.1`.

Going forward: see `COMMIT_POLICY.md` (nondescript `release …` messages; human identity only; single `main`).

## Human remaining steps

1. Create `IlkhamFY/IRexp` and `IlkhamFY/IRSpectra-Bench` on GitHub; push packs (`PUSH_INSTRUCTIONS.md`).
2. Overleaf → Import from GitHub (or zip upload); set main `.tex` + pdfLaTeX.
3. Mint Zenodo data-only DOI when ready (do **not** invent); fill checklist in IRexp pack.
4. Optionally close leftover open draft PRs / delete remaining unmerged agent branches listed in `BRANCH_CLEANUP.md`.
