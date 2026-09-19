# Blind forward-13C pack (expand)

ONLY files here are `fbatch_*.txt` (ID + SMILES).

Do NOT open, search, or read:
- `data/fverify_expand/candidates.jsonl`
- `data/fverify_expand/anon_map.json`
- any `answers*.jsonl`
- any file containing `obs_c13`

Write predictions to `data/fverify_expand_blind/raw/fN.json` as `{ID:[ppm,...]}`.
Predictions must NOT equal observed spectra (you do not have them).
