# Models and versions

This file is the reproducibility anchor referenced by `docs/PAPER.md` §8 (Methods,
"Models and versions"). It records **what the repository can prove** about the system
under test, and — separately and explicitly — **the small set of identifiers only the
authors can supply**.

Every LLM result in the paper was produced by Anthropic Claude models invoked as
independent sub-agents through the **Agent tool under a consumer claude.ai
subscription**. No paid API, no fine-tuning, no model training is involved in the core
protocol. (The two trained probes, §5.4's GNN verifier and §5.6's generator, are *not*
Claude models; see
[Non-Claude components](#non-claude-components).)

---

## 1. Which model ran which experiment

Every row below is checkable from the committed artifacts. "Collected" is the UTC
author-date of the commit that **first added** the prediction artifact
(`git log --diff-filter=A --date=format:'%Y-%m-%d %H:%M' -- <path>`); the history is
linear and each raw agent-output file was committed once, in the same working session
in which it was produced, so first-add is the best available proxy for collection time.
It is a proxy, not a timestamp emitted by the harness.

| § | experiment | model | data directory | collected (UTC) | evidence |
|---|---|---|---|---|---|
| `docs/BENCHMARK.md` | pilot, n=21 (single context, no tools) | Claude **Opus 4.8** | `data/benchmark/` | 2026-06-09 04:40 | `docs/BENCHMARK.md` L23; commit `d4e7513` |
| §4.3 arm (a) | within-compound control, n=20, one context, **no tools** | Claude Opus | `data/benchmark_v2/` | 2026-06-09 06:28 | `data/benchmark_v2/results2.txt` (5% recovered / 0% top-1); commit `893e8ce` |
| §4.1, §4.3 arm (b) | controlled round v3, n=40, decoupled agents | Claude Opus | `data/benchmark_v3/` (raw `b1`–`b8`) | 2026-06-09 06:47 – 07:37 | commits `c2b2f5b`, `8cde140`, `28bbda7`, `74007ec`, `c21b211` ("decoupled Opus agents") |
| §4.1, §4.3 arm (b) | within-compound control, same n=20, **4 agents × 5 compounds**, RDKit formula check | Claude Opus | `data/benchmark_v2_ctrl/` (raw `c1`–`c4`) | 2026-06-09 17:43 | `results2.txt` (15% recovered / 15% top-1); commit `8c47dc7` |
| §5.1–§5.2 | forward-verification: **8** blind forward-prediction agents over 126 candidates, 60 compounds | Claude Opus | `data/fverify/` (raw `f1`–`f8`) | 2026-06-09 19:51 | `docs/FORWARD_VERIFY.md` ("solver and verifier are both Claude-Opus sub-agents under the subscription"); commit `41df0eb` |
| §5.3 | generate-wide: **10** solver agents partitioning the same 60 compounds (6 compounds each), up to 6 regiochemistry-aware candidates per compound | Claude Opus | `data/gw/` (raw `g1`–`g10`) | 2026-06-10 18:15 | commit `bdb0532` ("10 Opus agents, 6 regio-aware each") |
| §5.3 | expanded forward-verification of the widened pool: **4** forward-prediction agents, 65 new candidates | Claude Opus | `data/fverify2/` (raw `f1`–`f4`) | 2026-06-10 18:19 | commit `bea1c3e` |
| §5.2 | forward-verification **extended to the whole benchmark**: **15** blind forward-prediction agents over the 247 main-round candidates (373 across both arms) | Claude Opus | `data/fverify_main/` (raw `f1`–`f15`) | 2026-08-07 02:45 – 02:53 | `data/fverify_main/results.txt`; pooled by `scripts/forward_verify_all.py` |
| §5.3 | **closing the generate-wide coverage gap**: **9** forward-prediction agents over the 152 wide candidates that had none (217/217 now predicted) | Claude Opus | `data/fverify_gw/` (raw `g1`–`g9`) | 2026-08-07 03:20 – 03:30 | `data/fverify_gw/results.txt`; scored by `scripts/score_generate_wide.py` |
| §5.6 | **re-run** of the trained-generator forward-verified arm (the original outputs were never committed): **5** blind forward-prediction agents over the 75 outstanding candidates | Claude Opus | `data/fverify_gen/` (raw `g1`–`g5`) | 2026-08-07 03:55 – 04:05 | `scripts/forward_verify_gen.py score` (0 missing predictions) |
| §7 *Independence checks* | cross-model recall check on V3-R01…R12 (n=12), identical blind 6-candidate protocol | Claude Sonnet | `data/gw/raw/sonnet_b1.json`, `sonnet_b2.json` | 2026-06-10 18:33 – 18:38 | `data/gw/crossmodel.txt`; commits `c1c1924`, `bb7c73a` |
| §4.1 | **headline** main round, 140 problems (134 spectrally validated), decoupled agents, 6- and 12-compound contexts | Claude Opus | `data/benchmark_main/raw/` | 2026-06-11 06:48 – 09:16 | commits `9e7fb90` … `4faf5e1`; headline scored in `52e03a2` |
| §4.4 | cross-model comparison, fixed 24-compound subset | Claude Haiku | `data/benchmark_main/haiku/` (`b1`–`b4`) | 2026-06-11 16:16 | commits `a797904`, `f5edfc9` |
| §4.4 | cross-model comparison, same subset | Claude Sonnet | `data/benchmark_main/sonnet/` (`b1`–`b4`) | 2026-06-11 16:41 – 17:10 | commits `e850469`, `dc6da42`, `bbceeaa`, `43ba5ec` |
| §4.4 | cross-model comparison, same subset | Claude **Fable 5** | `data/benchmark_main/fable/` (`b1`–`b4`) | 2026-06-11 23:06 – 23:32 | commits `2ba74c4`, `1cb1029`, `1408830`, `9500517`, `efcdba6`; scored in `18c7963` |
| §4.6 | **formula-only contamination control**: the same 60 compounds re-solved with the spectra masked, paired against the full-modality arm | Claude Opus | `data/modality/` (`out_full.json`, `out_formulaonly.json`) | 2026-07-28 18:37 | commit `a98d01a`; scored by `scripts/modality_ablation.py score` (3/60 vs 14/60, b=11 c=0, p=0.001) |
| §4.5 | IRSpectra-Bench-Electrolyte, 48 curated / 46 scored, 8 batches | Claude Opus | `data/benchmark_electrolyte/` (raw `b1`–`b8`) | 2026-06-11 18:29 – 18:43 | `docs/PAPER.md` §4.5 ("identical decoupled-agent protocol (Opus, closed-book … RDKit only for formula/parse checks)"); commits `63a2963` … `5c81e3f` |

**Access windows.** Every model invocation behind a number in the paper falls into one of
three dated windows. They are listed separately rather than collapsed, because a single
"3-day window" claim would be false.

1. **Main solver window, 2026-06-09 → 2026-06-11 (UTC).** Every candidate structure
   behind the *headline* results — §4.1 top-1 and recall, §4.3, §4.4, §4.5, and the
   candidate pools all of §5 re-ranks — was generated here. No headline elucidation
   artifact exists outside it.
2. **Formula-only contamination control, 2026-07-28.** This arm re-solves the same 60
   compounds with the spectra masked, so it *does* generate new candidate structures
   (3/60 correct) outside window 1 — by design, since the control only means anything as
   a fresh run. It affects §4.6 and Table 5 alone and changes no headline number.
3. **Forward-prediction additions, 2026-08-07.** Three of them: the §5.2 extension to all
   194 compounds, the §5.3 coverage-gap closure, and the §5.6 re-run whose original
   outputs were lost. These predict ¹³C for candidates the June solver had already
   produced. None introduces a new candidate structure or moves a recall number. The
   §5.6 re-run does change that arm's *verified top-1*, because the number it replaces
   was never reproducible — §5.6 states this explicitly.

All other later commits (figures, statistics, the §5.4/§5.6 trained probes) re-score
frozen outputs and re-query no model.

### One asymmetry in §4.4, stated plainly

The Opus arm of the four-model comparison is **not a fresh 24-compound run**. It is a
re-scoring of the main-round Opus predictions on the fixed subset — see the `SRC` map in
`scripts/score_models.py` (L14–19), where `"Opus"` points at
`data/benchmark_main/raw/*.json` while the other three point at their own directories.
Those 24 items came from one 6-compound context (`raw/b1.json`) and two 12-compound
contexts (`raw/redo_b23.json`, `raw/redo_b45.json`), whereas Sonnet, Haiku and Fable each
saw four 6-compound contexts. The prompts and the compound set are identical; the context
packing is not. This is worth stating because §4.3 measures a large effect of exactly
that variable.

---

## 2. Model roster and version strings

| role in paper | display name | version string recorded **in this repository** | dated snapshot identifier |
|---|---|---|---|
| headline benchmark (§4.1), controls (§4.3), forward-verification (§5.1–§5.3), electrolyte (§4.5), §4.4 Opus arm | Claude Opus | **`Claude Opus 4.8`** — recorded for the 2026-06-09 pilot only (`docs/BENCHMARK.md` L23). It is the only Claude version string anywhere in the repository. | **not exposed by the harness** — see §6 |
| cross-model comparison (§4.4), strongest | Claude Fable 5 | **`Fable 5`** (`docs/PAPER.md` §4.4 Table 3; `scripts/score_models.py` docstring) | **not exposed by the harness** — see §6 |
| cross-model comparison (§4.4); cross-model recall check (§7 *Independence checks*) | Claude Sonnet | **none** — no version number appears in any file | **not exposed by the harness** — see §6 |
| cross-model comparison (§4.4), weakest (0% top-1) | Claude Haiku | **none** — no version number appears in any file | **not exposed by the harness** — see §6 |

Two honest caveats on the Opus row:

- `Claude Opus 4.8` is a **display version, not a snapshot identifier**. It does not pin a
  checkpoint.
- It is evidenced **only for the pilot round** (2026-06-09 04:40). The main round ran two
  days later. Nothing in the repository states that the same build served both, and the
  authors must confirm it rather than have a reader assume it.

---

## 3. Harness, tool access, and prompt inputs

- **Harness.** Independent sub-agents dispatched with the **Agent tool** under a single
  consumer claude.ai subscription; **no API key, no paid API, no fine-tuning**.
  Evidence: `scripts/score_models.py` L3–5 ("all via the Agent tool under one
  subscription; no API"); `docs/FORWARD_VERIFY.md` L12–13 and L60
  ("dispatch batches to forward-prediction agents (Agent, model=opus, NO tools)");
  `docs/PAPER.md` §3 and §8.
- **Context discipline.** Each solver agent handles one small batch in a bounded context
  that is reset between batches — 6 compounds per released batch file
  (`data/benchmark_main/batch_*.txt`, 23 files: 22 × 6 + 1 × 2 = 134, i.e. the
  spectrally-validated subset of the 140 sampled problems, matching
  `clean_qids.json`), with some batch pairs merged into a single 12-compound context
  (`data/benchmark_main/raw/redo_*.json`). Range actually released: **2–12 compounds per
  context**.
- **Tool access — solver agents:** closed-book, **no web access, no ground-truth access,
  and no tools beyond an RDKit molecular-formula/parse check** (`docs/PAPER.md` §3, §4.3,
  §4.5). The §4.3 arm (a) baseline had **no tools at all** — that is the variable it
  isolates.
- **Tool access — forward-prediction (verifier) agents:** **zero tools**, pure reasoning,
  and blind: SMILES only, pooled across compounds, shuffled and anonymised, and the
  observed spectrum is never shown. Shuffling does **not** keep a target's own candidates
  in separate batches — in the §5.2 arm 7 of 8 batches held two candidates for some one
  compound — but with no observed spectrum in hand there is nothing for co-occurrence to
  leak (`docs/PAPER.md` §5.1; `docs/FORWARD_VERIFY.md` "Experiment";
  `data/fverify/anon_map.json`, `data/fverify2/anon_map2.json`,
  `data/fverify_main/anon_map.json`).
- **Audit of closed-book status.** Task transcripts were grep-audited at run time for zero
  web / zero ground-truth access (`docs/PAPER.md` §3; `data/gw/crossmodel.txt`).
  **The transcripts themselves are not committed** — the released artifacts are the parsed
  per-compound predictions. A reader cannot re-verify the audit from this repository.
- **Inputs given to the model.** Molecular formula + IR band list + ¹H and ¹³C shift lists
  with multiplicities/J where reported; no name, SMILES, or hint. The exact prompts are
  released as the batch files (`data/*/batch_*.txt`, `data/*/fbatch_*.txt`).

## 4. Scoring code path

Scoring is mechanical and model-independent — RDKit InChIKey **connectivity layer**
(first 14 characters) for correctness, Morgan(2, 2048) Tanimoto for the graded signal.

| result | script | inputs |
|---|---|---|
| §4.1 headline, n=194 (134 main-clean + 40 v3 + 20 v2-ctrl) | `scripts/score_main.py` (`--stereo` for the full-InChIKey variant) | `benchmark_main/{answers2,clean_qids}` + `raw/*.json`; `benchmark_v3/`, `benchmark_v2_ctrl/` |
| §4.4 four-model comparison + CIs + McNemar/Holm | `scripts/score_models.py` (`--stats`, `--fig`) | the `SRC` map, L14–19 |
| §4.5 electrolyte, per class | `scripts/score_electrolyte.py` | `benchmark_electrolyte/` |
| §5.1–§5.3 forward verification, chamfer re-rank | `scripts/forward_verify.py`, `scripts/specmetrics.py` | `fverify/`, `fverify2/`, `gw/` |
| §5.5 permutation control, selective prediction | `scripts/verifier_diagnostics.py` | `fverify/` |

## 5. Sampling and determinism — not controlled, not recorded

**No sampling parameters were set for any run, and none are recorded anywhere in this
repository.** There is no temperature, `top_p`, `top_k`, `max_tokens`, seed, or
thinking-budget value in any script, doc, config, or committed artifact (verified by
exhaustive grep across `*.py`, `*.md`, `*.txt`, `*.json`, `*.yaml`). The `seed=` values
that do appear are for *analysis* determinism only — bootstrap resampling, benchmark
sampling, audit-sample selection (`scripts/score_main.py`, `scripts/score_models.py`,
`scripts/make_audit_sample.py`, `scripts/build_electrolyte_bench.py`) — not for
generation.

This is a property of the harness, not an omission in the write-up: sub-agents dispatched
through the Agent tool under a consumer subscription do not expose decoding parameters,
so every run used whatever defaults that surface applied at the time. **Reproduction is
therefore distributional, not exact**, and a re-run will not reproduce the per-compound
predictions byte-for-byte even against an identical checkpoint. `docs/PAPER.md` §7 (vi)
states the consequence for the reported numbers: each headline compound is scored from a
single solver run, so the bootstrap CIs reflect compound sampling only and carry no
run-to-run LLM-sampling variance; §5.3 pooling ten generation passes lifted recall
31%→41%, which bounds how much single-pass scoring understates generator stochasticity.

## 6. What the authors must supply — and what nobody can

### Not obtainable: dated model snapshot identifiers

The four Claude rows of §2 have no dated snapshot identifier, and **none can be
supplied.** The consumer claude.ai harness the whole protocol runs on does not expose a
checkpoint identifier to the caller, announce build changes, or record which build served
a given request. This is a property of the surface, not an oversight by the authors, and
no amount of after-the-fact work recovers it. §1 of `docs/PAPER.md` already states it
("the subscription harness pins no model snapshot, exposes no temperature or seed");
§2 and §8 now agree rather than promising an identifier that will never arrive.

Two consequences follow and are stated rather than hedged:

- **A mid-window build change cannot be excluded.** `Claude Opus 4.8` is evidenced only
  for the 2026-06-09 pilot. Nothing in the repository, and nothing available to the
  authors, establishes that the same build served the main round two days later. The
  paper does not claim it did.
- **Re-running reproduces the protocol, not the numbers.** A reader who repeats these
  experiments will be served whatever build is current, which will not be the June 2026
  one. Distributional agreement is the most that can be expected; exact agreement is not
  a meaningful target and is not claimed.

What stands in place of a checkpoint pin is everything that *is* fixed: the dated
collection windows of §1, the display string where one was recorded, the frozen
per-compound outputs, and mechanical scorers that regenerate every number from them. That
is the honest boundary of a zero-cost subscription protocol — it buys reproducibility of
*scoring and analysis*, not of *inference*.

### Still needed from the authors

Three items, all outside the repository's reach:

1. **ORCID iDs** for all three authors → `docs/PAPER.md` author block, visible
   `[TODO: 0000-0000-0000-0000]` placeholders. RSC requires the corresponding author's.
2. **Zenodo DOI** for the data/code deposit → `docs/PAPER.md`, *Data and code
   availability*. Mint at submission.
3. **Funding sources and acknowledgements** → `docs/PAPER.md`, *Acknowledgements*,
   currently the only empty section.

Also confirm §5 is correct — that no decoding parameters were set on any run. If any run
*did* use non-default settings, §5 must be rewritten, not annotated.

Do not guess an ORCID or a DOI. An identifier that does not resolve is worse for
reproducibility than an acknowledged gap.

---

## Non-Claude components

Listed so no reader mistakes them for part of the LLM system under test.

| § | component | what it is |
|---|---|---|
| §5.4 | HOSE-code ¹³C verifier | deterministic lookup over the nmrshiftdb2 dump; `scripts/hose_predict.py`, `data/fverify/hose_results.txt` |
| §5.6 | trained-generator probe | ~16M-parameter ¹H/¹³C→SMILES transformer, ensemble of four, trained locally; `contrib/generator_probe/`, checkpoints on Zenodo |
| §5.4 | learned ¹³C verifier | 4-layer message-passing GNN trained on the same nmrshiftdb2 dump; `scripts/gnn_predict.py`, `data/nmrshiftdb/gnn_c13.pt` |

## Cross-vendor sweep — pilot run, nothing reported

Two non-Claude models were run through `scripts/cross_vendor_sweep.py` on 2026-08-13/14
via OpenRouter (`scripts/openrouter_run.py`), on the `fverify60` subset. **No number from
these runs appears in `docs/PAPER.md`,** and §7 (iii) stands unchanged: the paper remains
single-vendor. They are recorded here because they were run, and this file's purpose is to
say what was.

| model | ctx | answered | recall | parsing | matching the given formula |
|---|--:|--:|--:|--:|--:|
| `nvidia/nemotron-3.5-lightning` | 6 | 60/60 | **0/60** | 61% | **2%** |
| `deepseek/deepseek-v4-pro-0813` | 6 | 18/60 | **1/18** | 93% | **35%** |
| `deepseek/deepseek-v4-pro-0813` | **3** | 18/60 | **8/18** | 94% | **94%** |
| *Claude, same constraint (§3)* | 2–12 | — | — | — | *78–95%* |

**Context packing moved this model more than anything else we varied.** The two DeepSeek
rows differ only in how many compounds shared a context — same model, same prompt, same
constraint. At six it returned molecules of the wrong composition 65% of the time; at
three it obeyed the formula 94% of the time, inside Claude's own band, and recall on the
compounds it answered went 1/18 to 8/18 (McNemar over the paired 60, b=8 c=1, p=0.039).
This is the §4.3 effect appearing in an unrelated model lineage, and larger there than the
paper measures for Claude. Two caveats: the arms answered different subsets, so the recall
comparison is partly confounded by *which* compounds got through, and 14 of 20 batches
still failed to terminate. The formula-adherence half is the cleaner comparison, being
measured over each arm's own output.

**The central inequality replicates.** On the 3-per-context arm, forward verification is
right far more often than generation is:

| quantity | DeepSeek V4 Pro | Claude (Table 6, n=194) |
|---|--:|--:|
| generation recall (all 60, unanswered = miss) | 8/60 = 13% [7, 24] | 65/194 = 34% |
| generation recall (18 answered only) | 8/18 = 44% [25, 66] | — |
| verification precision, conditional on recall | 5/8 = **62%** [31, 86] | 58/65 = **89%** |

Read against the full cohort, as the paper's own convention does, precision (62%) exceeds
recall (13%) with non-overlapping intervals. Read against answered compounds only, 62%
against 44%, the intervals overlap and the ordering is directional. Either way the sign
matches Claude's, on a model from a different lab. This is the first non-Claude evidence
for the paper's central decomposition — but it rests on **8 recall-positive compounds** in
an arm that is 30% complete, so it belongs here rather than in the paper, and it is not
reported in `docs/PAPER.md`.

Neither has the power to test the claim, for two independent reasons.

The first is arithmetic: the portable quantity is the inequality *verification precision >
generation recall*, and precision is conditional on recall — at zero recall there is
nothing to condition on, so the comparison is undefined rather than negative.

The second is more basic and easier to misread. **Neither model can meet the output
contract.** The task hands over a molecular formula and asks for candidates matching it;
nemotron returned 180 candidates of which 61% parsed as molecules at all and 2% carried
the right composition, several with literal spaces inside the SMILES. A model that cannot
return a well-formed structure of the requested formula is not being measured on
elucidation, and reading its 0/60 as a statement about chemistry is the mistake this table
most invites. `cross_vendor_sweep.py score` now prints the parse and formula-adherence
rates beside recall, and flags any vendor below 50% as too low to interpret.

Read these as a demonstration that the harness runs end to end, not as evidence about any
vendor.

The DeepSeek failure is worth recording separately because it is a property of the model
rather than of the transport: on seven batches it produced tens of thousands of reasoning
tokens and exhausted a 120,000-token ceiling **without emitting a single answer token**.
Six blind elucidations in one context is apparently past what it will commit to an answer
on. The headline Claude run used 2–12 compounds per context, so a smaller context is still
protocol-consistent and is the obvious thing to try first
(`cross_vendor_sweep.py prepare <subset> <n>`).

Outputs live in `data/cross_vendor/`, which is gitignored — it holds the held-out answer
key, so nothing under it is committed.

## Specified but never run — no model was invoked

- **Modality ablation** (`scripts/modality_ablation.py`, `data/modality/`): the *leave-one-
  modality-out* arms (`noIR`, `noH`, `noC`) remain staged only — `prompt_noIR.txt`,
  `prompt_noH.txt`, `prompt_noC.txt` exist (2026-06-16, commit `f3fe901`) with no
  corresponding `out_*.json`. The paper reports no leave-one-out result. (One `noIR`
  attempt was made and **discarded as confounded**; `docs/MODALITY_ABLATION.md` records
  why.)
- **Expert-chemist audit** (`data/audit/`, `docs/EXPERT_AUDIT_PROTOCOL.md`): human
  protocol, frozen and blinded, not yet run (`docs/PAPER.md` §7 (ii)).
- ~~**§5.6 forward-verified arm**: `data/fverify_gen/raw/` is an empty directory.~~
  **Resolved 2026-08-07.** The original blind forward-prediction JSONs behind the
  provisional 41% top-1 were never committed and are lost. Rather than keep citing an
  unverifiable number, the arm was **re-run from scratch** under the identical blind
  protocol (75 candidates, 5 agents, anonymised SMILES only) and every prediction is now
  deposited at `data/fverify_gen/raw/` (`g1`–`g5`). `scripts/forward_verify_gen.py score`
  regenerates the arm with zero missing predictions. The re-run gives **46% top-1
  (28/60)** at **82%** precision conditional on recall (28/34), against the retired
  provisional 41% / 73%; recall is 56% (34/60), unchanged. §5.6 reports the re-run and
  says plainly that it is a re-run, not a reproduction. Note the collection date differs
  from the June solver window — see the access-window note above.

---

## External numeric attributions — verified against primary sources

Numbers this paper attributes to other people's work were checked against the source,
because nothing in this repository can contradict a sentence about someone else's paper.
Audited 2026-08-07.

| claim in `PAPER.md` | source | status |
|---|---|---|
| Alberts et al.: ~635k simulated spectra, 3,453-spectrum experimental fine-tune, top-1 44% on 6–13 heavy atoms | *Commun. Chem.* **7**, 268 abstract via EuropePMC (PMC11569215) | **exact** — "634,585 simulated IR spectra … fine-tune it on 3,453 experimental spectra … top–1 accuracy of 44.4% … 6 to 13 heavy atoms" |
| NMIRacle: 48% top-1 / 66% top-15 on IR+¹H+¹³C | arXiv:2512.19733 full text | **exact** — "attains a Top-1 accuracy of 0.48 and a Top-15 accuracy of 0.66" |
| NMIRacle evaluated on a simulated, in-distribution split | arXiv:2512.19733 | **exact** — 8:1:1 split of the ~790k simulated Alberts set; their own limitations section is headed "Simulated vs experimental spectra" |
| NMIRacle uses "no hints, like us" | arXiv:2512.19733 | **was wrong, corrected** — NMIRacle takes *no molecular formula* and names formula/scaffold priors as a limitation of prior work. We supply the formula. §4.2 now states the asymmetry. |
| GPT-4o on MolPuzzle: 1.4% | Guo et al., NeurIPS 2024 D&B | **exact** |
| GPT-4o at 27.8% "using knowledge-enhanced tree-search reasoning" | Zhuang et al., arXiv:2506.23056 Table 1 | **was wrong, corrected** — 27.8% is their plain-CoT *baseline*; their tree-search result is 57.8%. The true spread is ~40×, not ~20×. |
| Spectro: accuracy on a 1,366-molecule held-out split | Crossref abstract for 10.26434/chemrxiv-2024-37v2j | **partly verified** — the abstract reports **93%** joint / **82%** fixed-embedding overall test accuracy, now quoted as such (we previously wrote "~90% top-1 exact recovery", which is neither figure and renames the metric). The 6,833/1,366 split sizes and the "software-predicted NMR" characterisation are in the full text, which ChemRxiv serves only behind a 403 — **two co-authors of this paper wrote Spectro and should confirm them.** |

### Related-work completeness sweep (2026-08-07)

Searched for recent work the bibliography missed, since no script in this repository can
surface a missing citation. Four additions, two of which required correcting claims:

| work | why it matters | action |
|---|---|---|
| **NMR-Solver** (Jin et al., arXiv:2509.00640) | implements §5's generate-and-forward-verify loop *without* an LLM (NMRNet, ¹³C MAE 1.098 ppm); 52.89% top-1 on ~450 experimental literature spectra with formula | cited; §1.1 and Contribution 3 now state the loop is prior art and that its sharper predictor **corroborates** the §5.1 resolution diagnosis |
| **Alberts, Zipoli & Laino** (*Digital Discovery* **4**, 1936, 2025) | successor to the 2024 paper we cite, **in our target journal**; 63.8% top-1 / 84.0% top-10 on *experimental* NIST gas-phase IR with formula | cited; falsified our claim that "the strongest trained baselines report accuracy in-distribution on simulated spectra" — corrected, and the real/curated distinction restated as literature-heterogeneous vs single-instrument |
| **NMRAgent** (Fang et al., arXiv:2606.29776) | closest LLM-agent counterpart; validates on newly isolated natural products | cited as complementary |
| **NMRArena** (odanchem, GitHub) | 105 molecules, experimental ¹H/¹³C, benchmarks six general LLMs *including Claude Opus 4.8* against four specialist models | **not cited** — publication is a placeholder ("final citation to be added on publication"), so it is concurrent unpublished work. Contribution 2's priority claim is hedged "to our knowledge"; **authors should re-check before submission** in case it has since appeared. |
