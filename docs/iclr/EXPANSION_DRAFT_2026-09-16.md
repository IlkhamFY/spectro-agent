# Expansion draft — 2026-09-16 (v0.11 candidate)

Overnight follow-up after Opus expansion completed on spectro-agent
`claude/funny-maxwell-u5S31` (PR #18). **Do not merge that PR.**

This file travels with the ICLR TeX so morning review has one place to check
locks. The intended postcard repo is `IlkhamFY/IRSpectra-Bench` (new branch from
its `main`). This environment can **read** that repo but **cannot push** to it
(GitHub 403 for `cursor[bot]`), so the same blinded manuscript lives here under
`docs/iclr/` for review and for a one-file port onto IRSpectra-Bench.

## What is true this morning

Numbers copied from committed spectro-agent `data/benchmark_expand/STATUS.md` —
**not invented:**

| set | n | top-1 | recall (top-3) |
|---|---:|---|---|
| Opus, all deposited | 106 | 63/106 (59%) | 68/106 (64%) |
| simple / complex | 53 / 53 | 41/53 (77%) / 22/53 (42%) | 43/53 (81%) / 25/53 (47%) |
| validate-clean | 101 | 61/101 (60%) | 65/101 (64%) |

- 5 flagged 13C-overread: R12, R22, R25, R82, R91.
- Fable 68/106, **not scored**. Expansion **forward-verify not run**.
- Headline n=194 tables / CIs / `fig_wall` **untouched**.
- Pre-reg licenses pooling to ~300 after the round is complete; report as
  **independent replication first**. Pooling + figure rebuilds await
  forward-verify **and Ilkham OK**.

## Manuscript edits in this PR

- `iclr_paper.tex`: new § Pre-registered expansion (independent replication)
  with Table `tab:expansion`. Contributions / conclusion / limitations (vi)–(vii)
  / appendix point at it. **No new CIs. No vendor numbers for the 106.**
- Double-blind locks **unchanged**: `\iclrfinalcopy` OFF; companion bib
  `yabbarov2026irexp` remains **Anonymous**; dataset URL in the PDF is only
  `https://anonymous.4open.science/r/peaklist-corpus-review-10C4/`; no
  `ilkhamfy/*` in the TeX that ships to the PDF.
- `docs/LEADERBOARD.md`: n=194 lock kept; expansion table added as replication.
- `docs/ICLR_PAPER.md`: marked stale; leftover `ilkhamfy/IRexp` pointers in that
  snapshot replaced with the anonymous.4open URL so a copy-paste cannot leak.

## What this PR does **not** do

- Does not merge spectro-agent PR #18.
- Does not restore `answers2.jsonl`.
- Does not rewrite headline 28.4% / 15.2% / 34% / 89% (58/65).
- Does not rebuild `fig_wall`.
- Does not invent expansion CIs or Fable / Grok / Gemini / GPT numbers on the 106.

## Morning checklist

1. Review `iclr_paper.tex` §expansion against STATUS tables.
2. Rebuild PDF (Overleaf pdfLaTeX+BibTeX, or `python3 scripts/build_pdf.py`).
   Confirm **Anonymous authors**, **Anonymous (2026)** for IRexp, no
   `Yabbarov` / `ilkhamfy` / `huggingface` / `McMaster` in PDF text.
3. **Do not pool to ~300** until expansion forward-verify + Ilkham OK.
4. spectro-agent PR #18 stays open; Fable finish is optional; key stays withheld.
5. Camera-ready only: uncomment `\iclrfinalcopy`, delete the under-review
   `\lhead` override (see `docs/ANONYMITY_ICLR.md`).

## Locked facts (do not drift)

| Item | Value |
|---|---|
| Headline n | 194 |
| Expansion (independent) | 63/106 (59%) top-1; 68/106 (64%) recall |
| Dataset URL in PDF | anonymous.4open `…/peaklist-corpus-review-10C4/` |
| `\iclrfinalcopy` | OFF |
| Companion bib | Anonymous |
