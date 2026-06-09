# Generator–verifier elucidation: forward-predict to break the regiochemistry wall

**Idea.** Inverse elucidation (spectra→structure) is the model's *hard* direction
and is isomer-blind on 1D data (BENCHMARK_v2/v3). But the **forward** direction
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
  the SMILES alone, no observed spectrum, candidates **shuffled+anonymised** so
  isomers of the same target never co-occur. (Validity: pure reasoning, 0 tools.)
- Re-rank each compound's candidates by chamfer distance(predicted ¹³C, observed
  ¹³C); compare the top pick to the solver's own ranking.

## Result
| | value |
|---|--:|
| generation recall (true structure in candidate set) | 19/60 (**31%**) |
| top-1, solver self-rank | 14/60 (23%) |
| top-1, **forward-verified re-rank** | 16/60 (**26%**) |
| **conditional on true-in-set — self-rank** | 14/19 (**73%**) |
| **conditional on true-in-set — forward-verify** | 16/19 (**84%**) |

**The decomposition is the finding.** Forward verification is a *good* discriminator:
**when the true structure is among the candidates, it ranks it #1 84% of the time,
vs 73% for the model's own ranking (+11 pts).** The overall top-1 only moves
23%→26% because the binding constraint is **generation recall** — the true
structure was never proposed for 41/60 compounds, and no re-ranking can fix that.

So the system cleanly separates into two levers:
- **Verifier (forward prediction): already strong (84%).** The generator–verifier
  gap is real and exploitable at current LLM forward-prediction accuracy.
- **Generator (candidate recall): the bottleneck (31%).** This is where to invest.

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
