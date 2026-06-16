# Modality ablation — corrected protocol (run on the Opus pipeline)

**Question.** How much does each spectral modality (IR, ¹H, ¹³C) contribute to
elucidation recovery? I.e., is IR pulling weight, or is ¹³C doing the work?

This is the SHAP-"where does the signal live" analog for our setting (see the
comparison to the BACE-1 representation benchmark). It is the one remaining experiment
that needs the real solver, not deterministic analysis.

## Why the first pilot was thrown out

The initial pilot used **one solver agent per condition**. Because each condition's 16
compounds were all solved by a single agent, the *agent/run quality* was a single draw
per condition — and that between-run variance swamped the modality effect. The tell:
the **full-modality** condition came out *worst* (3/16) while **−IR** came out best
(8/16), and −IR solved compounds that the full-information run missed — impossible if
modality were the driver. The pilot measured solver-run variance, not modality. Those
numbers are not used anywhere.

## Corrected design (implemented in `scripts/modality_ablation.py`)

1. **Leave-one-out conditions:** `full` (formula+IR+¹H+¹³C), `noIR`, `noH`, `noC`.
2. **Within-compound pairing, fresh contexts:** solve **every (compound, condition)
   in an independent fresh context with the SAME model and settings**. The only thing
   that varies across the four conditions for a given compound is which modality was
   removed. Pairing within compound also controls for compound difficulty.
3. **Same solver as the headline result** (decoupled-agent Opus pipeline), so the
   absolute numbers are comparable to §4–§5. Do **not** use weak/variable
   general-purpose sub-agents — they are too noisy to give a trustworthy absolute
   number even with the correct design.
4. **Full sample (n=60), not 16** — the larger n is what makes the paired test powered.

## How to run

```bash
python scripts/modality_ablation.py prepare          # writes data/modality/prompt_<cond>.txt + key.json
```

For each `prompt_<cond>.txt` (compounds are anonymized `M001…`, only the allowed
modalities are shown), run the Opus solver on **each compound separately, fresh
context**, closed-book, returning up to 3 ranked SMILES. Save results as
`data/modality/out_<cond>.json` mapping `id -> [smiles, ...]`. The answer key
(`data/modality/key.json`) is held out — never expose it to the solver.

```bash
python scripts/modality_ablation.py score            # paired top-1/recovery + McNemar full-vs-each
```

## Interpretation

- **Marginal value of modality X = (full) − (−X)**, measured *paired* over the same
  compounds. A positive, significant drop when X is removed means X carries unique
  signal the others don't replace.
- The scorer reports, for each leave-one-out condition vs `full`, McNemar's exact test
  on the discordant compounds (`b` = full-right/cond-wrong, `c` = cond-right/full-wrong).
- **Sanity check the design held:** `full` should be ≥ every leave-one-out condition
  (more information cannot hurt a competent, consistent solver). If any `−X` beats
  `full`, the run is confounded again (solver inconsistency) — investigate before
  reporting.

## Expected use in the paper

A clean result becomes a short §4 subsection + a four-bar figure. The figure is
already scriptable: after `score` passes the sanity check, run

```bash
python scripts/make_fig_modality.py          # -> docs/figures/fig_modality.png
```

(it renders nothing until real `out_*.json` exist, so no placeholder figure can ship).

### Ready-to-paste subsection draft (fill the bracketed numbers)

> ### 4.6 Which modality carries the signal?
>
> Aggregate accuracy does not say which spectral channel does the work. To attribute
> recovery to individual modalities we re-solved the [60]-compound forward-verify set
> under four leave-one-out conditions — full (formula+IR+¹H+¹³C), −IR, −¹H, −¹³C —
> holding the solver and settings fixed and running every (compound, condition) in an
> independent context, so the only variable is the available modality (Methods). Removing
> **¹³C** cost the most (top-1 [XX]%→[YY]%, a [Δ]-point paired drop, McNemar p=[p]),
> while removing **IR** cost the least (top-1 [XX]%→[ZZ]%, p=[p]); ¹H was intermediate
> ([…]). [So ¹³C is the dominant channel for constitution, IR contributes a smaller but
> [significant/marginal] increment, and ¹H […]]. The ¹³C dependence concentrates on
> regiochemistry-dense compounds, consistent with §4.1 and the picolinamide/nicotinamide
> example of §5. (Fig. [N].)
>
> | condition | top-1 | recovered | vs full (McNemar) |
> |---|--:|--:|--:|
> | full (IR+¹H+¹³C) | [..]% | [..]% | — |
> | −IR | [..]% | [..]% | p=[..] |
> | −¹H | [..]% | [..]% | p=[..] |
> | −¹³C | [..]% | [..]% | p=[..] |

### Wiring it in (once numbers exist)

1. Paste §4.6 above into `docs/PAPER.md` after §4.5 (battery-electrolyte), before §5.
2. Add the figure to `scripts/build_pdf.py` `FIGS` (it will become the next Fig number;
   renumber later figures + their in-text refs as in prior figure additions), e.g.:
   `("fig_modality.png", "Modality ablation (leave-one-out, n=60): top-1 and recovered by condition; removing ¹³C costs the most.")`
3. Add a Figures-list entry in `docs/PAPER.md` and one in-text `(Fig. N)` call in §4.6.
4. Rebuild: `python scripts/build_pdf.py`; verify refs with the usual consistency check.

Hold all of this out of the manuscript until the design-sanity check (full ≥ every
leave-one-out) passes on the real run.
