# Generator–verifier elucidation: forward-predict to break the regiochemistry wall

**Idea.** Inverse elucidation (spectra→structure) is the model's *hard* direction
and is isomer-blind on 1D data. But the **forward** direction
(structure→spectrum) is its *easy* direction — Anthropic measured Opus at ~1.4 ppm
¹³C, beating commercial tools. And **regioisomers have different predicted ¹³C
shifts.** So invert the asymmetry: let the solver propose candidates, then *verify*
each by forward-predicting its ¹³C spectrum and re-ranking by match to the observed
spectrum. It's the classic **generator–verifier gap** (verifying is easier than
generating), and it mirrors how a chemist actually confirms a structure.

No training, no paid API — solver and verifier are both Claude-Opus sub-agents
under the subscription; matching is mechanical (chamfer distance on ¹³C peak sets).

## Experiment
- 60 benchmark compounds (v3 + v2-control), **126** unique candidate structures the
  solver agents had proposed.
- **8 forward-prediction agents** predicted ¹³C for every candidate **blind** — from
  the SMILES alone, no observed spectrum, candidates pooled across compounds and
  **shuffled+anonymised** so the predictor never learns a candidate's target or which
  candidates are siblings. (Shuffling does not keep a target's own candidates in
  separate batches — 7 of 8 batches held two candidates for some compound — but with
  no observed spectrum in hand there is nothing for co-occurrence to leak.)
  (Validity: pure reasoning, 0 tools.)
- Re-rank each compound's candidates by chamfer distance(predicted ¹³C, observed
  ¹³C); compare the top pick to the solver's own ranking.

## Extension to the whole benchmark
The arm above was later run over **all 194 compounds** — the 134 main-round targets add
247 more candidates, every one forward-predicted, giving 373 in total and no
prediction-coverage gap. `scripts/forward_verify_main.py` preps that arm;
`scripts/forward_verify_all.py` pools both and is what the paper's §5.2 reports.

The generate-wide arm's own coverage gap was closed at the same time: it had predicted
only 65 of its 217 new candidates, so its top-1 was a lower bound. All 217 are now
predicted (`scripts/forward_verify_gw.py`) and **no number moves** — the bound was tight.
On 18 of 60 compounds the verifier does switch to a newly-selectable candidate, but every
switch is wrong-structure → wrong-structure: more candidates, same ceiling.

## Result
| | 60-compound arm | **all 194** |
|---|--:|--:|
| generation recall (true structure in candidate set) | 19/60 (32%) | **65/194 (34%)** |
| top-1, solver self-rank | 14/60 (23%) | 55/194 (28%) |
| top-1, **forward-verified re-rank** | 16/60 (27%) | **58/194 (30%)** |
| **conditional on true-in-set — self-rank** | 14/19 (74%) | 55/65 (**85%**) |
| **conditional on true-in-set — forward-verify** | 16/19 (**84%**) | 58/65 (**89%**) |
| …multi-candidate only — self-rank | 8/13 (62%) | 27/37 (73%) |
| …multi-candidate only — forward-verify | 10/13 (77%) | **30/37 (81%)** |

Sanity check: the self-rank row on the full benchmark is 55/194 = **28.4%** top-1 and
65/194 = **33.5%** recall — the paper's headline numbers, re-derived here from the
released candidate files through an independent code path.

**The decomposition is the finding.** Forward verification is a *good* discriminator:
**when the true structure is among the candidates, it ranks it #1 89% of the time (81% on
the 37 where a choice actually existed), vs 85%/73% for the model's own ranking.** The
overall top-1 only moves 28%→30% because the binding constraint is **generation recall**
— the true structure was never proposed for 129/194 compounds, and no re-ranking can fix
that. The margin over self-ranking stays statistically unresolved (McNemar exact p=0.55);
what the extension buys is the *absolute* precision claim and the permutation control,
which sharpens from one-sided p=0.019 (n=19) to **p=0.001** (n=65).

So the system cleanly separates into two levers:
- **Verifier (forward prediction): already strong (84%).** The generator–verifier
  gap is real and exploitable at current LLM forward-prediction accuracy.
- **Generator (candidate recall): the bottleneck (32%).** This is where to invest.

**Limitation.** Forward-match distance is a weak *abstention* signal at LLM
precision: wrong regioisomers still match within ~2 ppm (chamfer 0–2 ppm bin is
only ~31% correct), because ~2-ppm prediction error blurs many isomer differences.
A stricter count-sensitive metric (sorted-RMSE) did not beat self-rank. A
deterministic HOSE-code/DFT ¹³C predictor as the verifier would sharpen this.

## The recipe this points to
**Generate wide, verify with forward prediction.** Since verification converts
~84% of recall into correct top-1, the high-leverage move is to raise recall
(more candidates per solver, ensemble of independent solvers, scaffold
enumeration) and let forward-verification pick. Projected: lift recall 31%→~60%
and top-1 should track to ~50% — the natural next experiment.

## Reproduce (free, under a Claude subscription)
```bash
python scripts/forward_verify.py prep            # candidate pool + shuffled SMILES batches
# dispatch batches to forward-prediction agents (Agent, model=opus, NO tools):
#   "predict 13C shifts per structure" -> data/fverify/raw/f*.json  {id:[shifts]}
python scripts/forward_verify.py score           # re-rank + conditional accuracy
```
Frozen: [`candidates`](../data/fverify/candidates.jsonl) ·
[`anon_map`](../data/fverify/anon_map.json) ·
[`raw/`](../data/fverify/raw) (per-agent forward ¹³C predictions).
