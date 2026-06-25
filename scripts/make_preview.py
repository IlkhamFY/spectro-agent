#!/usr/bin/env python3
"""Build docs/PAPER_preview.md = PAPER.md + the proposed §5.6 (trained-generator probe),
inserted before §6 Discussion, with a reviewer banner. For preliminary author reading only."""
BANNER = """> **PRELIMINARY DRAFT FOR AUTHOR REVIEW (Ilkham & Rodrigo).** This copy adds one
> proposed subsection — **§5.6, a trained-generator probe** (highlighted below) — to test
> whether the recall wall is breakable. It is a *complement* to the training-free protocol,
> not part of it; inclusion and framing are your call. All §5.6 numbers are reproducible
> (`closing_the_gap_gen.py`, `forward_verify_gen.py`, `eval_sim_zeroshot.py`). The LLM
> forward-prediction step used blind in-house agents under your anonymized, isomer-separated,
> structure-only protocol (transcript-audited for zero tool/web access); please re-run it under
> your pinned model-snapshot pipeline to record the camera-ready number (it should land near
> the 41% reported here — precision already matches your generate-wide value, 73% vs 72%).

---

"""

SEC = r"""## 5.6 The recall wall is not task-intrinsic: a trained generator closes it *(proposed addition — author review)*

§5.3 localises the bottleneck as generation recall and shows that even wide,
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
**0/248** zero-shot — so the recall gain is not memorization.

**Result — the generator supplies the candidates enumeration cannot, and they are
verifiable (Fig. 6).** On the 194 compounds, the truth enters the candidate set for 54.1%
of compounds with the generator, versus 41.8% for scaffold enumeration and 33.5% for Claude
alone (Fig. 6A). The contrast is the point (Fig. 6B): re-ranked by the deterministic HOSE
¹³C verifier, scaffold enumeration's near-degenerate regioisomers *collapse* top-1
(28.4→16.0%, the §5.3 precision-loss mechanism), whereas the generator's formula-correct,
¹³C-separable candidates *improve* it (28.4→35.1%; McNemar exact p=0.015; ΔTop-1 +6.7 pts,
95% CI [+2.1, +11.9]). Conditional precision falls 84.6%→64.8% as the pool grows, but on the
40 newly-recalled compounds the verifier still selects truth 47.5% of the time — above
per-pool chance. **The recall ceiling was LLM-elicitation-specific, not task-intrinsic.**

**With the strong (LLM forward-prediction) verifier the recall converts almost fully.** On
the 60 forward-verify compounds, pooling the generator's candidates and re-ranking by the
paper's own blind forward-prediction protocol (§5.1):

| (60 forward-verify compounds) | generate-wide (§5.3) | + trained generator |
|---|--:|--:|
| recall (truth in pool) | 41% | **56%** |
| forward-verified top-1 | 30% | **41%** |
| conditional precision | 72% | **73%** |

Top-1 rises 30→41% (+11 pts) through the *same* verifier; conditional precision is **73%,
essentially the generate-wide value (72%)** — the generator's candidates are verified at the
same rate as the LLM's own, so the higher recall converts to top-1 rather than being lost to
verifier confusion (contrast near-degenerate enumeration, which collapses the deterministic
verifier to 16%).

**The released data is the active ingredient.** The same architecture pretrained on
simulated spectra alone recovers **0/248** experimental structures zero-shot (valid but
wrong molecules — the simulated→experimental gap is total), versus 25% after IRexp
fine-tuning and 8% from IRexp alone. IRexp fine-tuning is the entire bridge from 0 to ~25%
standalone recall — the open experimental data this paper releases is what makes a cheap,
deployable generator possible.

**Scope and honesty.** (i) A *trained* probe, reported as a complement to — not part of —
the training-free protocol; it answers whether the wall is breakable, not whether to abandon
training-free methods. (ii) Two verifiers concur (HOSE 35.1% on 194; forward-verify 41% on
60); the forward-prediction step used blind in-house agents under the §5.1 anonymized,
isomer-separated protocol (transcript-audited for zero tool/web access), to be re-run under
the authors' pinned model snapshot for the camera-ready (precision parity, 73% vs 72%,
indicates the predictor is comparable). (iii) Single-vendor, as elsewhere. (iv) The
generator uses ¹H/¹³C only — a strict subset of the benchmark input (formula + IR + NMR) —
so the rescues are achieved with *less* information than Claude receives.

---

"""

md = open("docs/PAPER.md").read()
marker = "## 6. Discussion"
assert marker in md, "discussion marker not found"
out = BANNER + md.replace(marker, SEC + marker, 1)
open("docs/PAPER_preview.md", "w").write(out)
print(f"wrote docs/PAPER_preview.md ({len(out.splitlines())} lines; §5.6 inserted before §6)")
