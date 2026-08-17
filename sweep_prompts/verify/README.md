# Verify prompts — forward ¹³C prediction, one per model

The second half of the cross-vendor sweep, and the half that carries the claim. `solve`
measures generation recall; only this stage yields verification precision, and the
portable result is the *inequality* between them, not either number alone.

One file per model, because the candidate pool is that model's own output. Each holds
176–180 anonymised SMILES in batches of 17. They are committed for the same reason as the
solve prompts: an agent working from a clean clone would otherwise run
`cross_vendor_sweep.py prep-verify`, which writes the held-out answer key into its
workspace.

## Why this stage is hard to contaminate, and where it still is

The task is *structure → spectrum*. Knowing which candidate is correct does not tell you
its shifts, so the answer key is close to useless here — which is the point of running
verification blind in the first place.

The exposure is the **observed** spectrum. A model that could see the spectrum each
candidate will be scored against could tune its prediction toward it, and the chamfer
re-ranking would then measure copying rather than chemistry. These files are checked to
carry none: no observed ¹³C list, no compound id, nothing linking a `P###` back to a
target. The observed spectra live in `data/benchmark_*/questions2.jsonl`, which **is**
tracked — so the same instruction that governs the solve stage governs this one. Do not
open other repository files.

## Running

Batches of 17 within each file, marked `## batch N`. One fresh subagent per batch, closed
book, exactly as for solve. Write replies to `sweep_out/<model>/verify_NN.json` as
`{"P001": [21.0, 60.5, 171.2], ...}` — a list of predicted shifts in ppm per id, nothing
else.

Then, back in the repository:

```
python scripts/manual_collect.py collect sweep_out/<model> <model>   # solve, if not done
# copy verify replies to data/cross_vendor/verify_<model>.json
python scripts/cross_vendor_sweep.py score
```

`score` prints `prec|rec` once a verify file exists, and flags the vendor as replicating
the paper's claim if verification precision exceeds generation recall.

Composer 2.5 and GPT-5.6 Luna are deliberately absent: at 67% and 76% formula adherence
they are below the line where a recall number can be read as chemistry at all, so a
precision measured on their candidate pools would not mean much either.
