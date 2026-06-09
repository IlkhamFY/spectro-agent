# Pilot benchmark — LLM structure elucidation on IRexp

**One line:** on 21 real scraped experimental compounds, blind structure
elucidation from **formula + IR + ¹H + ¹³C** recovered the exact constitution
**1/21 (4%)**, the right scaffold **6/21 (29%)**, and the right chemical family
**11/21 (52%)** (median Morgan-Tanimoto 0.30). The task is far from "solved" on
realistic data — but the model usually lands in the right neighbourhood and
fails on regiochemistry and exotic scaffolds.

This replicates the *inverse* task from Anthropic's
[*Making Claude a Chemist*](https://www.anthropic.com/research/making-claude-a-chemist),
which reported recovering "all eight simpler structures on every attempt" — but
on a curated 15-compound set, NMR-only, no natural products. We test on real
scraped data, **add the IR modality they did not use**, and deliberately span
molecule sizes (their stated gap).

## Protocol (blind, mechanically scored)
- **Sample:** 21 IRexp-resolved gold records (real IR + ¹H + ¹³C + a structure
  resolved from the in-text name), stratified small/medium/large by heavy-atom
  count (`scripts/benchmark_elucidation.py sample`).
- **Inputs given to the solver:** molecular formula (from the true SMILES) + IR
  band list + ¹H + ¹³C shift lists. **No** name, no SMILES, no hints.
- **Solver:** Claude Opus 4.8, answering all 21 in one pass, blind to ground
  truth (the answer key never entered its context — see threats below).
- **Scoring:** RDKit — exact constitution (InChIKey 1st block), full InChIKey
  (incl. stereo), Morgan(2,2048) Tanimoto. Per-compound table in
  [`data/benchmark/results.txt`](../data/benchmark/results.txt).

## Results
| metric | value |
|---|--:|
| exact constitution | **1/21 (4%)** |
| exact incl. stereochemistry | 1/21 (4%) |
| right scaffold (Tanimoto ≥ 0.45) | 6/21 (29%) |
| right family (Tanimoto ≥ 0.30) | 11/21 (52%) |
| mean / median Tanimoto | 0.37 / 0.30 |

By size: exact match came only from the **small/clean** bucket; **0/14** on
medium+large. Tanimoto was roughly flat across sizes (0.34–0.42) — even big
molecules share common motifs.

## Error analysis (where it breaks)
- **Exact (1):** Q04 bromo-1*H*-indazole-3-carbaldehyde — small, unambiguous
  scaffold, clean spectra → solved outright.
- **Scaffold right, regiochemistry wrong (≈6):** the dominant failure mode.
  e.g. Q21 — correct *N*-allyl-2-(pyridinecarbonyl)hydrazinecarbothioamide, but
  predicted the **3-pyridyl** isomer vs the true **2-pyridyl**; Q06 — correct
  tripropionyloxy-flavone, wrong acyl positions; Q02 — correct symmetric
  diselenide dimer, swapped which ring bears the amide. **1D NMR + formula
  genuinely underdetermines position** — this is what 2D NMR (HMBC/NOESY) is for,
  a limitation Anthropic also flagged.
- **Exotic scaffolds → miss:** fused polycyclics (Q05), organophosphorus +
  thiourea peptides (Q07), *N*-alkyl saccharins (Q11), pyridinium dye salts
  (Q19). These never appear in curated easy sets and are common in real
  literature.
- **Spectral misassignment → miss:** Q15 — read IR 2213 cm⁻¹ as a nitrile;
  it was an imine. A reminder that IR helps functional groups but can mislead.

## Threats to validity (read before quoting the 4%)
This is a **pilot (n=21)** and the absolute number is a *lower bound* under
deliberately hard conditions — do not read it as "Claude scores 4% at
elucidation":
1. **Degraded representation.** Our ¹³C is stored without multiplicity/J and ¹H
   without J — *less* information than a chemist (or Anthropic's setup) gets.
   This both lowers the score and flags a **dataset-improvement action: preserve
   coupling/multiplicity.**
2. **Single-pass solving.** All 21 answered in one context with limited
   per-compound reasoning, vs a careful per-item API run; a decoupled API harness
   (no key available here) would likely score higher.
3. **No hints.** Anthropic's *hard* set received the starting-material structure;
   we gave none.
4. **Harsh metric.** Exact InChIKey-connectivity is unforgiving for large
   molecules; the scaffold/family rates (29% / 52%) are the fairer signal of
   "useful but not exact."

## What it means
- **The benchmark design works.** Real IRexp data is large, diverse, and
  *discriminating* — it cleanly separates a solved case (Q04) from genuine hard
  ones, exactly what the field lacks. This is the value proposition vs Anthropic's
  35-compound eval.
- **Elucidation is not solved on realistic data.** The optimistic read of small
  curated evals does not transfer; there is large headroom, concentrated in
  **regiochemistry** and **exotic scaffolds**.
- **Representation matters as much as the model.** The single biggest cheap win
  for both training *and* benchmarking is to **keep J-values/multiplicities** (and
  add 2D NMR where available) — a concrete next step for the dataset.

## Reproduce
```bash
python scripts/benchmark_elucidation.py sample --n 21 --seed 7   # questions+answers
#   (solver writes data/benchmark/predictions.jsonl, blind to answers)
python scripts/benchmark_elucidation.py score                    # -> results.txt
```
Frozen artifacts: [`questions`](../data/benchmark/questions.jsonl) ·
[`answers`](../data/benchmark/answers.jsonl) ·
[`predictions`](../data/benchmark/predictions.jsonl) ·
[`results`](../data/benchmark/results.txt).
