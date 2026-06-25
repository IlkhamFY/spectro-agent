# Reply to Ilkham's three blockers

Thanks — all three are fair, and (2) especially is exactly the right thing to check. Resolved below; a reproducer bundle is in `contrib/generator_probe/`.

## (2) Leakage / holdout — the important one

Your 117/200 is real and I reproduce it exactly: it's **(benchmark_main + v3 + v2_ctrl) ∩ `irexp_release/train`** = 89 + 18 + 10 = **117/200** (over all cohorts it's 145/248). *Can you confirm your "200" = those three cohorts, so I can cite your exact number?*

But that overlap is with the **public release split**, which doesn't hold out the benchmark. **We did not train on it.** The generator was trained on a *separately de-leaked* split built from `irexp_resolved` with **every benchmark IK-14 removed** (`build_exp_manifest.py`: `if ik in bench_ik: continue`). Verified on the actual split:

- **train ∩ benchmark = 0**, **val ∩ benchmark = 0** (by IK-14) — see `artifacts/split_ik14.json`.

Honest caveat I want to be upfront about: the generator is **sim-pretrained** (generic ~768K corpus) then exp-finetuned, and **13/194 benchmark compounds do occur in that sim-pretrain corpus** (sim isn't benchmark-specific, so it isn't de-leaked). Two things neutralize it, both checkable (`verify_leakage_exact40.py`):

1. **None of the 40 compounds the generator newly recovers** — its entire recall contribution — are in sim-pretrain *or* exp-finetune (0/40 and 0/40).
2. **Sim-only zero-shot scores 0/248** on the benchmark. If sim-pretraining were leaking answers, it would score >0 on those 13. It scores 0 → sim contributes representation, not answer-recall.

So the precise claim (which I'll fix in the draft) is *"the 40 rescues are absent from both training stages,"* not "no benchmark compound was ever seen." Net: your finding is a genuine flaw **in the public release split** — anyone training on `irexp_release/train` and testing on the benchmark leaks 145 compounds. The de-leaked split + manifest are in the bundle; worth flagging in the data section for downstream users.

## (3) Where 35.1% and 54.1% come from

Good catch on the coincidence — it tripped you because there are *two different* 35.1%s. In the **original** `closing_the_gap.py` (enumeration), `+enumerate`'s **proj@0.84** = 0.84×41.8 = 35.1% (the optimistic projection; real HOSE there is 16%). My 35.1% is **not** that. From `closing_the_gap_gen.py` (run it):

| pool | recall | **HOSE top-1** | proj@0.84 |
|---|--:|--:|--:|
| Claude only | 33.5% | 28.4% | 28.1% |
| + enumeration | 41.8% | 16.0% | 35.1% |
| **+ generator** | **54.1%** | **35.1%** | 45.5% |

- **35.1%** = `+generator` **real HOSE re-rank** = 68/194 (the HOSE top-1 column). The projection for *my* pool is 45.5%, which I deliberately did **not** headline. The two 35.1%s (enum-projection vs generator-real) are an unlucky numeric coincidence on different pools.
- **54.1%** = `+generator` **recall** = 105/194 (truth present in the formula-filtered gen∪Claude pool).

Why the generator's real HOSE (35.1%) beats enumeration's (16%) when both add candidates: enumeration adds *near-degenerate regioisomers* that crater the verifier; the generator's candidates are formula-correct and ¹³C-separable, so they convert (rescue-conditional precision 47.5% > chance; McNemar p=0.015).

## (1) Artifacts in the repo

`contrib/generator_probe/` — `gen_candidates.jsonl`, `split_ik14.json`, the four scripts
(`gen_candidates_for_verify.py`, `eval_sim_zeroshot.py`, `build_exp_manifest.py`, plus
`closing_the_gap_gen.py` / `forward_verify_gen.py` / `verify_leakage_exact40.py` in `scripts/`),
and a README with exact repro commands. Tier A (verify 54.1%/35.1% + de-leak) needs no model;
Tier B (regenerate candidates) needs the checkpoints — happy to share.

## Two notes

- The zero-shot ablation you liked (0/248 → 25%) doubles as the anti-memorization evidence above — glad it's useful for the data section.
- Corrected number since the first PDF: the forward-verify (strong-verifier) top-1 is **41%** (precision 73% ≈ your generate-wide 72%), after re-running with isomer-separated batches + zero-tool audit; the earlier 46%/82% was inflated by isomer co-occurrence. Updated PDF attached.
