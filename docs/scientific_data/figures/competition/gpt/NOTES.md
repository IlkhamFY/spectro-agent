# IRexp Nature figure set — GPT entry

## Design rationale

- **Positioning:** A true log10 comparison keeps every database legible without an axis break or pseudo-3D distortion. IRexp’s overlapping measures are adjacent bars rather than a mathematically invalid stack. Access tags, exact values, and the restrained callout card establish a clear editorial hierarchy.
- **Pipeline:** A single left-to-right reading path uses numbered badges, short stage labels, and one controlled merge branch. Cleaning is visually subordinate but connected to the licence stage. Rejection cards use symbolic examples so they do not fabricate record-level observations.
- **Distribution:** The 2 × 3 grid shares strict baselines and spacing. Source and linkage bars are linear; the five-order licence range is explicitly log10. Panel F is a nested 2 × 2 with the frozen histogram bins, medians, aggregate elbows, and an “automated checks only” watermark.

## Data and honesty

All displayed counts and metrics come from `frozen_plot_data.json`. The brief’s `188,016 PMCIDs scanned` and the legacy SVG’s numeric QC examples are not in the frozen file, so they are intentionally not displayed. “Band lists” is used consistently; no human audit is implied.

## Production checks

- Exact canvas width: **183 mm** for all figures.
- One-page vector PDFs with embedded Helvetica-compatible Nimbus Sans fonts.
- PNG companions rendered at **600 dpi**.
- Clean `pdflatex -halt-on-error` build: no overfull/underfull boxes or warnings.
- No raster assets embedded in the TeX sources.

## Self-score

| Figure | Score | Assessment |
|---|---:|---|
| Positioning | **9.4/10** | Honest scale, strong hierarchy, clean direct annotation |
| Pipeline | **9.5/10** | Most editorially resolved; excellent flow and restrained QC treatment |
| Distribution | **9.3/10** | Dense six-panel job remains aligned and readable; panel F is necessarily compact |
| **Overall** | **9.4/10** | Submission-ready programmatic artwork; final journal compositor review remains appropriate |
