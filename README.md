# IRSpectra-Bench

An open, blind benchmark for molecular structure elucidation from real experimental
spectra by large language models, with the literature-mined dataset (IRexp) and a
training-free forward-verification method behind it.

Given molecular formula + IR + 1H + 13C, a frontier LLM recovers the exact constitution
of 28.4% of real, blind compounds (95% CI 22-35). The binding constraint is candidate
recall, not verification; a training-free generate-and-verify step lifts top-1 from
23% to 30%.

## Contents

- `docs/paper.pdf` (source `docs/PAPER.md`) - the manuscript.
- `data/irexp/`, `data/irexp_resolved/` - IRexp: 121,233 experimental-IR records,
  43,060 linked to a resolved structure, mined from open-access literature.
- `data/benchmark_*/` - IRSpectra-Bench (194 compounds) and the battery-electrolyte
  subset: blind questions, answer keys, and model predictions.
- `data/fverify/`, `data/gw/` - forward-verification and generate-wide results.
- `data/audit/`, `docs/EXPERT_AUDIT_PROTOCOL.md` - blinded expert-validation kit.
- `docs/CROSS_VENDOR.md` - turnkey protocol to replicate the recall/verification
  decomposition on other vendors (GPT, Gemini, open-weight).
- `scripts/` - scoring, forward-verification, and figure/PDF regeneration.
- `spectro_scraper/` - the dataset-mining pipeline.

## Reproduce

```
pip install -r requirements.txt
python scripts/score_main.py            # Table 2  - headline accuracy (n=194)
python scripts/forward_verify_all.py    # Table 6  - recall/verification decomposition (n=194)
python scripts/score_generate_wide.py   # Table 7  - generate-wide arm
python scripts/ladder_significance.py   # the paired tests behind §5.3
python scripts/check_manuscript.py      # manuscript integrity gate (must pass)
pip install scipy && python scripts/verify_statistics.py   # audit the hand-rolled stats
python scripts/build_pdf.py             # rebuild docs/paper.pdf
```

Table 8 (§5.4) additionally needs the two trained ¹³C predictors, which are rebuilt
from the nmrshiftdb2 dump rather than shipped:

```
curl -L -o data/nmrshiftdb/nmrshiftdb2.sd \
  https://sourceforge.net/projects/nmrshiftdb2/files/data/nmrshiftdb2withsignals.sd/download
python scripts/hose_predict.py build     # HOSE table (gate: held-out MAE 3.23 ppm)
python scripts/verifier_table.py --all   # Table 8 - four verifiers, n=65
python scripts/verifier_leakage.py --all # candidate/training overlap check
```

## Licensing

IRexp redistributes extracted numeric spectra under the source licences - PMC
Open-Access Subset (CC-BY-4.0) and Chemotion/RADAR4Chem (CC-BY-SA-4.0), kept as
separable pools; see `data/NOTICE`. Code is released under the MIT License.
