# Branch cleanup (spectro-agent)

Goal: reduce `cursor/*` / Overleaf sync branch chaos. Safe deletes only
(merged PR heads, ancestors of `main`, obsolete Overleaf sync refs).

## Deleted (this pass)

### Merged PR heads
- `cursor/irspectra-bench-expand-9a67`
- `cursor/scidata-figures-nmrexp-9a67`
- `cursor/scidata-figures-nature-9a67`
- `cursor/scidata-figures-premium-9a67`
- `cursor/scidata-figures-9a67` (already gone)
- `cursor/scidata-accept-ready-9a67`
- `cursor/fix-combined-figures-9a67`
- `cursor/combined-figures-9a67`
- `cursor/bolder-structure-figures-9a67`
- `cursor/editorial-clean-9a67`
- `cursor/chemrxiv-twocolumn-9a67`
- `cursor/figure-readability-9a67`
- `cursor/fig1-wall-redesign-9a67`
- `cursor/submission-format-figures-9a67`
- `cursor/scientific-editor-pass-9a67`
- `audit/worksheet-and-scorer`

### Ancestors of `main` (fully merged tip)
- `cursor/audit-strengthen-limitations-9a67`
- `cursor/author-block-scidata-9a67`
- `cursor/author-contrib-fix-9a67`
- `cursor/crossref-drop-ai-heading-9a67`
- `cursor/editorial-cuts-5-8-9a67`
- `cursor/editorial-cuts-9a67`
- `cursor/fix-generator-probe-label-9a67`
- `cursor/fix-titleblock-fontspec-9a67`
- `cursor/iclr-manuscript-9a67`
- `cursor/irexp-licence-remediation-9a67`
- `cursor/irexp-scidata-audit-9a67`
- `cursor/irexp-scidata-merge-7f6d`
- `cursor/jcim-strengthen-9a67`
- `cursor/merge-overleaf-1908-9a67`
- `cursor/old-paper-frontmatter-9a67`
- `cursor/opus-tikz-nature-figures-8e10`
- `cursor/overleaf-remove-symlinks-9a67`
- `cursor/overleaf-tex-manuscripts-9a67`
- `cursor/pdf-layout-orphans-9a67`
- `cursor/premium-typography-audit-9a67`
- `cursor/scidata-affil-wrap-9a67`
- `cursor/scidata-audit-closeout-9a67`
- `cursor/scidata-sn-article-9a67`
- `cursor/scidata-sync-licence-counts-9a67`
- `cursor/scidata-title-irexp-9a67`
- `cursor/scientific-data-manuscript-9a67`
- `cursor/shorten-acks-data-9a67`
- `cursor/split-completion-audit-2f41`
- `cursor/split-orchestration-9a67`
- `cursor/table-caption-booktabs-9a67`
- `cursor/toc-graphic-hierarchy-9a67`
- `cursor/typographic-perfection-9a67`
- `cursor/verifier-mae-label-9a67`
- `cursor/vertical-breathing-9a67`
- `copilot/make-repo-private`
- `copilot/review-session-history`

### Obsolete Overleaf sync branches
- `overleaf-2026-08-24-0427`
- `overleaf-2026-08-24-0454`
- `overleaf-2026-08-24-0505`
- `overleaf-2026-08-24-1908`
- `overleaf-2026-08-24-1911`
- `overleaf-2026-08-26-1921`
- `overleaf-2026-08-26-2230`
- `overleaf-2026-08-26-2231`
- `overleaf-2026-08-26-2232`
- `overleaf-2026-08-26-2240`
- `overleaf-2026-08-27-0121`
- `overleaf-2026-08-28-0150`

## Kept (human decision needed)

| Branch | Why kept |
|---|---|
| `cursor/remove-section-rules-9a67` | Open PR #26 |
| `cursor/tex-nature-figures-62e9` | Open draft PR #36 |
| `claude/funny-maxwell-u5S31` | Open draft PR #18 |
| `cursor/setup-dev-environment-7eec` | Open draft PR #8 |
| `cursor/sweep-all-models-7eec` | Not merged into `main` |
| `cursor/sweep-gpt56sol-7eec` | Not merged into `main` |
| `generator-probe-sec5.6` | Not merged into `main` |
| `verifier-probe-sec5.7` | Not merged into `main` |

**Suggested human follow-up:** close stale draft PRs (#8, #18, #36) if obsolete, then delete those heads; merge or drop the two sweep branches and the two probe branches after review.

## Policy going forward

Prefer work on `main` or short-lived human branches. Avoid long-lived `cursor/*` forests.
New manuscript work should live in `IRexp` / `IRSpectra-Bench` clean repos (single `main`).
