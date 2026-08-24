# IRSpectra-Bench leaderboard

Blind structure elucidation from **molecular formula + IR + ¹H + ¹³C** peak lists exactly as reported in open-access papers. Constitution scoring uses RDKit InChIKey connectivity (first 14 characters) unless noted.

**Paper:** [IRSpectra-Bench and IRexp](https://github.com/IlkhamFY/spectro-agent) (manuscript in preparation, 2026).

---

## Main benchmark (n = 194)

| Rank | Model / method | Top-1 ↑ | Recall (top-3) ↑ | Gen. recall | Verif. prec. \| recall | Notes |
|---:|---|--:|--:|--:|--:|---|
| 1 | Claude Fable 5 | **46%** | 54% | — | — | 24-compound subset only |
| 2 | Claude Opus + generate-wide + forward-verify | **30%** | — | 42% | 72% | 60-compound arm |
| 3 | Claude Opus + forward-verify | 30% | 33.5% | 34% | **89%** | Full benchmark (headline) |
| 4 | Claude Opus (solver self-rank) | 28.4% | 33.5% | 34% | 85% | Full benchmark |
| 5 | Grok 4.6 | — | — | 53% | 62% | 60-compound arm |
| 6 | Gemini 3.7 Flash | — | — | 50% | 73% | 60-compound arm |
| 7 | GPT-5.6 Sol | — | — | 42% | 68% | 60-compound arm |
| 8 | Claude Sonnet | 21% | 25% | — | — | 24-compound subset |
| 9 | Claude Haiku | 0% | 4% | — | — | 24-compound subset |

Bootstrap 95% CIs for the headline row: top-1 **28.4% [22–35]**, recall **33.5% [27–40]**. Corpus-reweighted top-1 (17.5% simple / 82.5% complex): **15.2% [11–20]**.

**Key finding:** verification precision exceeds generation recall for every vendor tested — the binding constraint is *candidate proposal*, not spectral ranking.

### By difficulty (Claude Opus, n = 194)

| Stratum | n | Top-1 | Recall |
|---|---:|--:|--:|
| All | 194 | 28.4% | 33.5% |
| Simple | 98 | 48.0% | 54.1% |
| Complex | 96 | 8.3% | 12.5% |

---

## Evaluate your model

### 1. Download the benchmark (questions only — no answers in the solver prompt)

```bash
git clone https://github.com/IlkhamFY/spectro-agent.git
cd spectro-agent
pip install -r requirements.txt
```

Questions (blind inputs):

- `data/benchmark_main/questions2.jsonl` (140; use `clean_qids.json` for validated subset)
- `data/benchmark_v3/questions2.jsonl` (40)
- `data/benchmark_v2_ctrl/questions2.jsonl` (20)

Each row: `qid`, `formula`, `ir_bands_cm-1`, `h_nmr`, `c_nmr`. **No structure hints.**

### 2. Run your elucidator

Return up to **three ranked SMILES** per `qid`. Protocol:

- Inputs: formula + IR + ¹H + ¹³C only (as printed in the source paper).
- No web search, no structure hints, no answer-key access.
- Document model version, prompt, and tool access in your submission.

### 3. Score locally

Write predictions as JSONL:

```json
{"qid": "R01", "candidates": ["SMILES_rank1", "SMILES_rank2", "SMILES_rank3"]}
```

```bash
python scripts/score_submission.py --predictions my_run.jsonl --name "YourModel-1.0"
# optional strict stereochemistry scoring:
python scripts/score_submission.py --predictions my_run.jsonl --stereo
```

Reproduce the official headline numbers:

```bash
python scripts/score_main.py
python scripts/forward_verify_all.py
```

### 4. Submit to the leaderboard

Open a GitHub issue or PR on [IlkhamFY/spectro-agent](https://github.com/IlkhamFY/spectro-agent) with:

1. `--name` label for the table
2. `score_submission.py` output (copy-paste)
3. Predictions file (`my_run.jsonl`) or link to reproducible run
4. Model ID, date, and brief protocol note (tools, candidate budget, reasoning tier)
5. Confirmation: blind protocol, no answer-key access

We will verify scoring with `scripts/score_submission.py` before adding a row.

---

## Subsets & extensions

| Benchmark | n | Purpose |
|---|---:|---|
| **IRSpectra-Bench** (main + v3 + v2_ctrl) | 194 | Headline leaderboard |
| IRSpectra-Bench (main clean only) | 134 | Spectrally validated main round |
| IRSpectra-Bench-Electrolyte | 46 | Battery-electrolyte functional classes |
| Cross-vendor arm | 60 | Same compounds, multiple vendors (`docs/CROSS_VENDOR.md`) |
| Model comparison subset | 24 | Claude Haiku → Fable ladder |

---

## Related resources

- **IRexp dataset (training):** https://huggingface.co/datasets/ilkhamfy/IRexp — use `data/train_no_bench.jsonl.gz` to avoid benchmark leakage (`data/irexp_release/README_HF.md`)
- **Cross-vendor protocol:** `docs/CROSS_VENDOR.md`
- **Forward-verification:** `docs/FORWARD_VERIFY.md`
- **Full reproduction:** `README.md` in repository root

---

## Citation

If you use IRSpectra-Bench or report numbers on it, please cite:

```bibtex
@article{yabbarov2026irspectra,
  title   = {IRSpectra-Bench and {IRexp}: candidate recall, not verification,
             limits {LLM} elucidation from real experimental {IR} and {NMR}},
  author  = {Yabbarov, Ilkham and Sondhi, Rudra and Vargas-Hern{\'a}ndez, Rodrigo A.},
  year    = {2026},
  note    = {Manuscript in preparation}
}
```

*Last updated: 2026-08-24 (paper baseline rows). External submissions listed after verification.*
