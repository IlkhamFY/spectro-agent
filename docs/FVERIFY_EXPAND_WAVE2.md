# FVERIFY_EXPAND — Wave 2 (batches 6–11)

## Overview

Wave 2 continues the forward-verification (fverify) expansion of the IRSpectra-Bench
13C NMR deposit set.  It adds **f6.json–f11.json** (Q085–Q186, 102 molecules)
alongside the existing Wave 1 files (f1–f5, Q000–Q084).

## Method

Each 13C chemical-shift list was predicted by chemical reasoning from the SMILES
structure alone.  No computational NMR tools, databases, GNNs, HOSE codes, or
FG→ppm heuristic scripts were used.

Reasoning steps per molecule:
1. Parse the SMILES to identify functional groups, ring systems, and substituents.
2. Estimate each unique carbon environment using known empirical ranges
   (e.g. aromatic C–H ≈125–130, C=O ketone ≈190–210, OMe ≈55–57,
   vinyl =CH₂ ≈110–120, etc.).
3. Apply substituent-effect corrections (e.g. ortho/para OMe on aromatic,
   electron-withdrawing NO₂ deshielding, halogen effects).
4. Report all distinct carbon shifts as a sorted list in one-decimal ppm format.

## Style

Values use varied one-decimal precision matching the locked Opus style
(e.g. 20.8, 29.6, 55.3, 114.2).  No round codebook integers.

## Self-check

Every file was verified against the forbidden codebook integer set
{126, 137, 158, 148, 142, 155, 189, 166, 56, 45, 21, 18, 120, 133, 68, 30, 28}.
All files pass the <40% threshold (actual ≈0%).

## Files

| File | Batch | IDs | Count |
|------|-------|-----|-------|
| f6.json | fbatch_6 | Q085–Q101 | 17 |
| f7.json | fbatch_7 | Q102–Q118 | 17 |
| f8.json | fbatch_8 | Q119–Q135 | 17 |
| f9.json | fbatch_9 | Q136–Q152 | 17 |
| f10.json | fbatch_10 | Q153–Q169 | 17 |
| f11.json | fbatch_11 | Q170–Q186 | 17 |

## Scope limits

- Does not redo Wave 1 (f1–f5).
- Does not cover batches 12–17.
- No scoring or paper edits.
