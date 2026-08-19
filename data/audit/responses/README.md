# Reviewer responses

One JSON file per reviewer, exported from [`../worksheet.html`](../worksheet.html).
Name it after the reviewer (`r-sondhi.json`). Commit them; they are the audit's
primary record, and `scripts/score_audit.py` reads every `*.json` in this directory.

```
python3 scripts/score_audit.py                  # Table A + Table B
python3 scripts/score_audit.py --json out.json  # ...and machine-readable read-outs
```

Scoring also needs `../key.jsonl`, which is git-ignored on purpose. Whoever scores
regenerates it with `python3 scripts/make_audit_sample.py` (seed = 0, deterministic).
**A reviewer should not run that while they still have compounds to judge** — it
writes the answer key into the working tree.

## Format — `spectro-audit-response/1`

```json
{
  "schema": "spectro-audit-response/1",
  "reviewer": "r-sondhi",
  "submitted_utc": "2026-08-18T14:02:11.000Z",
  "sample_sha256": "6f1ca6947cef3b4f…",
  "responses": {
    "A01": {
      "task1": {
        "consistency": 4,
        "verdict": "wrong-regiochemistry",
        "diagnostic_peak": "203.8 ppm ketone C=O with no matching IR band above 1700"
      }
    },
    "A23": {
      "task1": { "consistency": 5, "verdict": "correct", "diagnostic_peak": "…" },
      "task2": { "ranking": ["B", "A", "C"], "confidence": 4 }
    }
  }
}
```

- `verdict` is one of `correct`, `wrong-regiochemistry`, `wrong-scaffold`, `uninterpretable`.
- `consistency` and `confidence` are integers 1–5.
- `ranking` is best → worst and must list each candidate label exactly once.
- `sample_sha256` is the digest of the `sample.jsonl` that was scored. The scorer
  warns if a response was filled against a different draw, so a re-generated sample
  cannot be silently mixed with an old one.
- A compound missing any Task-1 field is omitted from the export rather than
  half-recorded; the worksheet warns before exporting an incomplete sheet.
