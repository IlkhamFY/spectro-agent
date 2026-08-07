# Models and versions

This file is the reproducibility anchor referenced by `docs/PAPER.md` §8 (Methods,
"Models and versions"). It records **what the repository can prove** about the system
under test, and — separately and explicitly — **the small set of identifiers only the
authors can supply**.

Every LLM result in the paper was produced by Anthropic Claude models invoked as
independent sub-agents through the **Agent tool under a consumer claude.ai
subscription**. No paid API, no fine-tuning, no model training is involved in the core
protocol. (The two trained probes, §5.6 and §5.7, are *not* Claude models; see
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
| §4.5 | IRSpectra-Bench-Electrolyte, 48 curated / 46 scored, 8 batches | Claude Opus | `data/benchmark_electrolyte/` (raw `b1`–`b8`) | 2026-06-11 18:29 – 18:43 | `docs/PAPER.md` §4.5 ("identical decoupled-agent protocol (Opus, closed-book … RDKit only for formula/parse checks)"); commits `63a2963` … `5c81e3f` |

**Derived access window for the solver (elucidation) results in the paper:
2026-06-09 → 2026-06-11 (UTC), a 3-day window.** Every *candidate structure* scored
anywhere in the paper was generated inside it; no elucidation artifact was added outside
it. Three later additions exist and are listed above, all dated **2026-08-07** and all of
the same kind: they forward-predict ¹³C for candidates the June solver had already
produced (the §5.2 extension to all 194 compounds, the §5.3 coverage-gap closure, and
the §5.6 re-run whose original outputs were lost). None introduces a new candidate
structure or moves a recall number; they only supply the verifier's input where it was
missing. The §5.6 re-run does change that arm's *verified top-1*, because the number it
replaces was never reproducible — §5.6 states this explicitly. All other later commits
(figures, statistics, the §5.6/§5.7 trained probes) re-score frozen outputs and
re-query no model.

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
| headline benchmark (§4.1), controls (§4.3), forward-verification (§5.1–§5.3), electrolyte (§4.5), §4.4 Opus arm | Claude Opus | **`Claude Opus 4.8`** — recorded for the 2026-06-09 pilot only (`docs/BENCHMARK.md` L23). It is the only Claude version string anywhere in the repository. | *authors — see §6* |
| cross-model comparison (§4.4), strongest | Claude Fable 5 | **`Fable 5`** (`docs/PAPER.md` §4.4 Table 3; `scripts/score_models.py` docstring) | *authors — see §6* |
| cross-model comparison (§4.4); cross-model recall check (§7 *Independence checks*) | Claude Sonnet | **none** — no version number appears in any file | *authors — see §6* |
| cross-model comparison (§4.4), weakest (0% top-1) | Claude Haiku | **none** — no version number appears in any file | *authors — see §6* |

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
  and blind: SMILES only, shuffled and anonymised so isomers of the same target never
  co-occur in one context, and the observed spectrum is never shown
  (`docs/FORWARD_VERIFY.md` "Experiment"; `data/fverify/anon_map.json`,
  `data/fverify2/anon_map2.json`).
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

## 6. Authors must supply before submission

Five items. Everything else on this page is evidenced above.

1. **Dated snapshot identifier for Claude Opus** — the model behind the headline benchmark,
   both controls, forward-verification, generate-wide, the electrolyte case study, and the
   §4.4 Opus arm. → paste into the Opus row, "dated snapshot identifier" column, §2.
2. **Dated snapshot identifier for Claude Fable 5** (§4.4). → Fable row, same column, §2.
3. **Dated snapshot identifier *and* marketing version for Claude Sonnet** (§4.4 arm and
   the §7 *Independence checks* cross-model recall check). No version number for Sonnet exists anywhere in
   this repository. → Sonnet row, §2, both the version and snapshot columns.
4. **Dated snapshot identifier *and* marketing version for Claude Haiku** (§4.4). Same
   situation as Sonnet. → Haiku row, §2, both columns.
5. **Confirm one Opus build served all rounds** from 2026-06-09 to 2026-06-11, and that
   it is the `Claude Opus 4.8` recorded for the pilot. If the build changed mid-window,
   split the Opus row of §2 and annotate the affected rows of §1. → §2, Opus row caveats.

Also confirm §5 is correct — that no decoding parameters were set on any run. If any run
*did* use non-default settings, §5 must be rewritten, not annotated.

Do not guess any of these. An identifier that does not resolve to the checkpoint actually
used is worse for reproducibility than an acknowledged gap.

---

## Non-Claude components

Listed so no reader mistakes them for part of the LLM system under test.

| § | component | what it is |
|---|---|---|
| §5.4 | HOSE-code ¹³C verifier | deterministic lookup over the nmrshiftdb2 dump; `scripts/hose_predict.py`, `data/fverify/hose_results.txt` |
| §5.6 | trained-generator probe | ~16M-parameter ¹H/¹³C→SMILES transformer, ensemble of four, trained locally; `contrib/generator_probe/`, checkpoints on Zenodo |
| §5.7 | learned ¹³C verifier | 4-layer message-passing GNN trained on the same nmrshiftdb2 dump; `scripts/gnn_predict.py`, `data/nmrshiftdb/gnn_c13.pt` |

## Specified but never run — no model was invoked

- **Cross-vendor sweep** (`docs/CROSS_VENDOR.md`, `scripts/cross_vendor_sweep.py`): a
  protocol kit for GPT-/Gemini-class and open-weight models. No vendor was run; the
  working directory `data/cross_vendor/` is gitignored and absent. `docs/PAPER.md` §7 (iii)
  says so.
- **Modality ablation / formula-only memorisation arm** (`scripts/modality_ablation.py`,
  `data/modality/`): prompts staged 2026-06-16 (commit `f3fe901`); no `out_*.json` outputs
  exist. `docs/PAPER.md` §7 (i) says the arm is "specified but **not yet run**".
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
