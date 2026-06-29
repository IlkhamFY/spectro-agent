# Generator-probe reproducer (proposed §5.6)

Everything needed to regenerate every §5.6 number. Two tiers: **(A)** verify the headline
numbers + de-leak from shipped artifacts (no model needed); **(B)** regenerate candidates
from the trained model.

## Tier A — verify numbers + de-leak (no model, ~2 min)
Everything runs from the repo root with no external files. `artifacts/` contains:
`gen_candidates.jsonl` (generator candidate SMILES per benchmark qid), `split_ik14.json`
(train/val/benchmark IK-14 lists + the benchmark∩sim-pretrain overlap), and the full
de-leaked split Ilkham asked for: `manifest.jsonl.gz` (32,396 rows: ik14/smiles/selfies/
h_nmr/c_nmr) + `train_indices.npy`/`val_indices.npy`/`test_indices.npy` + `split_stats.json`.

```bash
# 54.1% recall / 35.1% HOSE top-1 + significance (McNemar, bootstrap):
python3 scripts/closing_the_gap_gen.py
# 41% forward-verified top-1 (needs data/fverify_gen/raw/*.json predictions):
python3 scripts/forward_verify_gen.py score
# leakage tied to the EXACT 40 rescues (both training stages):
python3 scripts/verify_leakage_exact40.py
```

### Where each number comes from (re: reviewer Q3)
`closing_the_gap_gen.py` prints four columns — **recall | HOSE top-1 | proj@0.84**:

| pool | recall | HOSE top-1 | proj@0.84 |
|---|--:|--:|--:|
| Claude only | 33.5% | 28.4% | 28.1% |
| + enumeration | 41.8% | 16.0% | 35.1% |
| **+ generator** | **54.1%** | **35.1%** | 45.5% |

- **54.1%** = `+ generator` **recall** = 105/194 (truth in the formula-filtered gen∪Claude pool).
- **35.1%** = `+ generator` **real HOSE top-1** = 68/194 (a real re-rank, *not* a projection).
  The projection column for the generator is **45.5%** (0.84×54.1), which is *not* headlined.
  N.B. the enumeration row's **proj@0.84** is also 35.1% (0.84×41.8) — a numeric coincidence;
  the two 35.1%s are different computations on different pools.

## De-leak (re: reviewer Q2)
`split_ik14.json` shows: **train ∩ benchmark = 0**, **val ∩ benchmark = 0**. The pool was built
from `irexp_resolved` minus every benchmark IK-14 (`build_exp_manifest.py`, line ~105:
`if ik in bench_ik: continue`). The public `irexp_release/train` is a *different* split that
does **not** hold out the benchmark (it overlaps 117/200 over main+v3+v2_ctrl, 145/248 over all
cohorts) — we did not train on it. `benchmark_inter_simpretrain` in the JSON lists the 13/194
(15/248) compounds that occur in the generic sim-pretrain corpus; `verify_leakage_exact40.py`
confirms **none of the 40 generator rescues** are in sim-pretrain or exp-finetune, and the
sim-only model recovers 0/248 zero-shot.

## Tier B — regenerate candidates from the model
Needs the spectro_v2 repo + checkpoints (4 sim-pretrained, exp-finetuned configs +
the sim SELFIES checkpoint). All `init_weights_from = sim_init_smiles_112.pt`.
- `gen_candidates_for_verify.py` → `gen_candidates.jsonl` (beam-10, formula-agnostic dump)
- `eval_sim_zeroshot.py` → the 0/248 sim-only ablation
- `build_exp_manifest.py` → the de-leaked split (test = benchmark; train/val = irexp minus benchmark)

Checkpoint paths are under `spectro_v2/logs/.../{wave2_aug_light,wave1_smiles_transfer,
wave1_smiles_adapter,wave2_aug_mod}/`; available on request (ask Rudra).
