# Draft subsection — "A trained generator breaks the recall wall" (extends §5.3)

*Proposed addition for author review. Two verifiers are reported: the deterministic HOSE
verifier (§5.4, in-repo) and the LLM forward-verifier (§5.1). Not yet merged into PAPER.md —
positioning (a trained model in a training-free paper) is the authors' call.*

---

## 5.6 The recall wall is not task-intrinsic: a trained generator closes it

§5.3 localises the bottleneck as **generation recall** and shows that even wide,
regiochemistry-aware LLM generation plateaus (recall 41%), with the residual misses
identified as *deeper constitutional rearrangements that enumeration cannot reach*
(`closing_the_gap.py`). This raises a question the training-free pipeline cannot answer:
is the ~42% recall ceiling **intrinsic to 1D-data elucidation**, or specific to **LLM
elicitation**? We test it with a complementary probe — a small supervised generator,
trained on IRexp — held deliberately separate from the paper's training-free protocol.

**Setup.** A ~16M-parameter ¹H/¹³C-NMR→SMILES transformer (simulated-spectra pretraining,
then fine-tuned on IRexp; an ensemble of four runs) proposes candidate structures for each
benchmark compound. Candidates are filtered to the given molecular formula and pooled with
Claude's, then re-ranked by the **same** verifiers used above. The benchmark is held out of
the IRexp fine-tuning set by InChIKey-14 (train ∩ benchmark = 0); 13/194 compounds also occur
in the generic ~768K simulated-pretraining corpus, but **none of the 40 compounds the generator
newly recovers** appear in either training stage, and the sim-pretrained model alone recovers
**0/248** zero-shot — so the recall gain is not memorization (`verify_leakage_exact40.py`).

**Result — the generator supplies exactly the candidates enumeration cannot, and they are
verifiable.** On the 194 compounds, through the deterministic HOSE ¹³C verifier:

| candidate pool | recall (truth in set) | HOSE top-1 |
|---|--:|--:|
| Claude only | 33.5% | 28.4% |
| + scaffold enumeration (§5.4) | 41.8% | 16.0% |
| **+ trained generator** | **54.1%** | **35.1%** |

The contrast is the point. Scaffold enumeration lifts recall but its near-degenerate
regioisomers *collapse* the verifier (28.4→16.0, the §5.3 precision-loss mechanism). The
generator's candidates are formula-correct and ¹³C-separable, so the **same** verifier
*improves* (28.4→35.1, McNemar exact p=0.015; bootstrap ΔTop-1 +6.7 pts, 95% CI [+2.1,
+11.9]). Decomposing by recall: conditional precision falls 84.6%→64.8% as the pool grows,
but on the 40 newly-recalled compounds the verifier still selects the truth 47.5% of the
time — above the per-pool chance rate. The recall ceiling was **LLM-elicitation-specific,
not task-intrinsic.**

**With the strong (LLM forward-prediction) verifier, the added recall converts.** On the 60
forward-verify compounds, pooling the generator's candidates and re-ranking by the paper's own
blind forward-prediction protocol (§5.1; isomer-separated batches, transcript-audited zero-tool):

| (60 forward-verify compounds) | generate-wide (§5.3) | + trained generator |
|---|--:|--:|
| recall (truth in pool) | 41% | **56%** |
| forward-verified top-1 | 30% | **41%** |
| conditional precision | 72% | **73%** |

Top-1 rises 30%→41% (+11 pts) through the *same* verifier. Conditional precision is **73%,
essentially the generate-wide value (72%)** — the generator's candidates are verified at the
same rate as the LLM's own, so the higher recall converts to top-1 rather than being lost to
verifier confusion (contrast the near-degenerate enumeration pool, which collapses the
deterministic verifier to 16%, Fig. 6B).

**The released data is the active ingredient.** The same architecture pretrained on
simulated spectra alone recovers **0/248** experimental structures zero-shot (it emits
valid but wrong molecules; the simulated→experimental distribution gap is total),
versus 25% after IRexp fine-tuning and 8% from IRexp alone (no pretraining). IRexp
fine-tuning is the entire bridge from 0 to ~25% standalone recall — the open
experimental data this paper releases is what makes a cheap, deployable generator possible.

**Scope and honesty.** (i) This is a *trained* probe, reported as a complement to — not part
of — the training-free protocol; it answers whether the wall is breakable, not whether to
abandon training-free methods. (ii) Two verifiers concur: the weak deterministic HOSE
gives 35.1% top-1 (194), the strong LLM forward-verifier gives 41% (60). The forward-prediction
run here used blind in-house agents under the paper's anonymized, isomer-separated,
structure-only protocol (transcript-audited for zero tool/web access); the authors should
re-run it under their pinned model-snapshot pipeline for the camera-ready number (the
conditional precision matching their generate-wide value, 73% vs 72%, indicates parity). (iii) Like all
results here, single-vendor (Claude as the LLM half). (iv) The generator uses ¹H/¹³C only — a
strict subset of the benchmark input (formula + IR + NMR) — so the rescues are achieved with
*less* information than Claude receives.

*Artifacts:* generator + candidate dump (`spectro_v2`), `closing_the_gap_gen.py` (HOSE
comparison + significance), `eval_sim_zeroshot.py` (ablation), `forward_verify_gen.py`
(Phase-2 LLM forward-verify prep/score).
