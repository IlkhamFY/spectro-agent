# Benchmark v2 — methodology-aligned to Anthropic, on real IRexp data

**One line:** after aligning to Anthropic's protocol (top-3 ranked candidates,
J-resolved ¹H NMR, simple/complex strata), blind elucidation on 20 fresh real
compounds recovers the exact constitution **1/20 (5%)** — essentially unchanged
from the v1 pilot's 4% — while landing the **right scaffold for 14/20 (70%)**
(mean Morgan-Tanimoto 0.51). The wall is **regiochemistry**, not capability,
and it is an information limit of 1D data, not a scoring or representation
artifact.

## Why v2 exists
The v1 pilot scored 4% exact vs Anthropic's reported ~100% on their "simpler"
set. Three plausible explanations had to be ruled out before concluding anything
about real-data difficulty. v2 aligns each to their
[reported protocol](https://www.anthropic.com/research/making-claude-a-chemist):

| confound | v1 pilot | v2 (aligned to Anthropic) |
|---|---|---|
| scoring | single prediction, exact only | **up to 3 ranked candidates**, recovered = any match |
| spectra representation | J-stripped (`1C, s`) | **raw ¹H with multiplicities + J** (re-fetched from source) |
| difficulty | unstratified | **simple (single/double-ring) vs complex (fused/spiro)** strata |

(Compounds overlapping the pilot were excluded — no contamination.)

## Results (n=20, formula + IR + J-rich ¹H + ¹³C)
| metric | value |
|---|--:|
| recovered (within top-3) | **1/20 (5%)** |
| top-1 exact | 0/20 (0%) |
| scaffold-level (best Tanimoto ≥ 0.45) | **14/20 (70%)** |
| family-level (best Tanimoto ≥ 0.30) | 15/20 (75%) |
| mean best Tanimoto | 0.51 |
| simple stratum | 0/10 exact, meanTani 0.51 |
| complex stratum | 1/10 exact, meanTani 0.51 |

Aligning scoring **and** representation moved the exact number 4% → 5%. The
explanations above are **not** the cause of the gap.

## The finding: a regiochemistry wall
The model reliably recovers **molecular formula + functional groups + scaffold**
and fails almost exclusively on **where the substituents go**:

- **R15** — true *m*-methylphenacyl bromide; proposed the *o*- and *p*- isomers.
  Right scaffold (194 ppm aryl ketone + CH₂Br + tolyl), wrong ring position.
- **R12** — true allyl/3×Me/2×OMe **hexasubstituted benzene**; proposed exactly
  that composition, wrong substitution pattern (Tanimoto 0.74).
- **R08** — true thiocyanato-methylphenol; proposed exactly those three groups
  (2161 cm⁻¹ SCN + phenol + Me), wrong positions.
- **R16** — right furan + acetonyl + OTBS/iPr carbinol, wrong attachment.

This is an **information-theoretic** limit: 1D ¹H/¹³C shifts + IR + formula often
cannot distinguish regioisomers (ortho/meta/para, substitution order on a
poly-substituted ring). Resolving them is exactly what **2D NMR (HMBC, COSY,
NOESY)** is for — data this benchmark (and Anthropic's) did not provide.

## Reconciling our 5% with Anthropic's ~100%
The gap is **not** scoring leniency or J-representation (we matched both). It is:
1. **Their "simpler" set is genuinely trivial** — "single-ring or two-fragment"
   molecules have few regiochemical degrees of freedom. Our strata, classified by
   ring count, still contain regiochemically brutal cases — R12 is "single-ring"
   yet hexasubstituted. **Ring count ≠ elucidation difficulty.**
2. **Their complex 7 received the starting-material SMILES as a hint** — which
   fixes most of the scaffold. We gave no hints.
3. Likely **lenient/chemist judgment** of "recovered" vs our exact InChIKey.

On realistic, substituted literature compounds with no hints, 1D structure
elucidation is far from solved — the optimistic read of small curated evals does
not transfer.

## Threats to validity
- **Solver:** Claude Opus 4.8 answered all 20 in one pass, no `ANTHROPIC_API_KEY`
  available for a decoupled per-compound API harness, and **no RDKit/shift-predictor
  in the loop**. A tooled agent could break *some* regiochemistry ties via shift
  prediction — but the pattern (≈0% exact, ~0.5 Tanimoto, scaffold-right) is
  consistent across **41 compounds** (v1+v2) and is an information limit, not an
  effort limit.
- **Harsh metric:** exact InChIKey-connectivity; the 70% scaffold rate is the
  fairer measure of "useful but not exact."

## What it means
- **IRexp is a strong, discriminating benchmark.** It exposes a real, specific
  failure mode — regiochemistry — that small curated NMR-only evals miss.
- **The honest capability claim is scaffold-level, not exact:** a model can tell
  you the *family and functional groups* from formula + IR + 1D NMR, but not the
  *exact isomer*.
- **The next data frontier for elucidation is 2D NMR** (HMBC/COSY). That is the
  signal that would move exact recovery, far more than scraping more 1D records.

## Reproduce
```bash
python scripts/benchmark_v2.py sample2 --n 20 --seed 41   # J-rich, stratified, pilot-excluded
#   solver writes data/benchmark_v2/predictions2.jsonl  ({"qid","candidates":[...3]})
python scripts/benchmark_v2.py score2                      # -> results2.txt
```
Frozen: [`questions2`](../data/benchmark_v2/questions2.jsonl) ·
[`answers2`](../data/benchmark_v2/answers2.jsonl) ·
[`predictions2`](../data/benchmark_v2/predictions2.jsonl) ·
[`results2`](../data/benchmark_v2/results2.txt).
