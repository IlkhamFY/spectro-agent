# Benchmark v3 — decoupled multi-agent solver (corrects v1/v2)

**One line:** running the elucidation as **8 independent Claude-Opus solver agents
(one per batch, fresh context, RDKit-for-formula-check, blind & closed-book)**
instead of one fatigued single pass raises exact recovery from **5% to 40%**
(top-3) / **27% top-1** on 40 fresh real compounds — **55% / 40% on the simple
stratum**. The earlier "regiochemistry wall" was largely a *solver-effort
artifact*, not an information limit.

## Why v3 (and why it's free)
v1/v2 had me (the orchestrator) solve every compound in a single context — no
tools, fatigued across 20+ molecules. That under-measures capability and does not
match Anthropic's setup, which is **one fresh model call per problem**. v3 fixes
this *without a paid API* by spawning **sub-agents inside the Claude Code session**
(billed under the existing subscription): 8 `general-purpose` agents on **Opus**,
each given one batch of 5 questions and nothing else.

- **Solver ≠ scorer:** each agent sees only its 5 questions (never the answer key,
  never the orchestrator's reasoning); scoring is mechanical RDKit.
- **Closed-book, validity-checked:** transcript grep across all 8 agents shows
  **0 WebSearch/WebFetch and 0 answer-key/InChIKey access** — the only tool use
  was RDKit (15–39 calls/agent) to check candidate validity + molecular formula.
- 40 fresh compounds (none in the pilot or v2), J-resolved ¹H, stratified, up to
  3 ranked candidates each.

## Results (n=40, formula + IR + J-rich ¹H + ¹³C, blind)
| metric | v1 pilot (single-pass) | v2 (single-pass, +J, top-3) | **v3 (decoupled agents)** |
|---|--:|--:|--:|
| exact recovered (top-3) | 4% | 5% | **40% (16/40)** |
| top-1 exact | 4% | 0% | **27% (11/40)** |
| scaffold-level (Tanimoto ≥ 0.45) | 33% | 70% | **67% (27/40)** |
| mean best Tanimoto | 0.37 | 0.51 | **0.66** |

By stratum (v3):
| stratum | recovered | top-1 | mean Tanimoto |
|---|--:|--:|--:|
| **simple** (single/double-ring) | **11/20 (55%)** | 8/20 (40%) | 0.80 |
| **complex** (fused/spiro/large) | 5/20 (25%) | 3/20 (15%) | 0.52 |

## The correction
**The 5% in v1/v2 was a methodology artifact.** Three legitimate factors recover
the lost performance, none of them cheating:
1. **Per-compound fresh context** — no attention dilution across 20 molecules.
2. **Full reasoning budget per compound** — each agent spent ~33–70k tokens and
   many RDKit checks on its 5; the single pass gave each compound a fraction of that.
3. **RDKit-in-the-loop formula verification** — catches atom-count errors and
   prunes candidates. A legitimate, disclosed "tooled agent" condition.

So the honest capability claim is **not** "≈0% / regiochemistry is an
insurmountable wall." It is: **a tooled Opus agent recovers the exact constitution
of ~40% of real, blind, no-hint literature compounds (≈55% of simpler ones), and
the right scaffold for ~67%.** The difficulty gradient is still real and is where
1D underdetermination bites — simple 55% vs complex 25%, Tanimoto 0.80 vs 0.52.

## Reconciling with Anthropic (~100% on their "simple")
Now much closer, and the residual gap is explained, not mysterious:
- Their "simple" = trivial **single-ring/two-fragment** molecules; ours include
  poly-substituted real compounds (ring count ≠ difficulty).
- They scored **best-of-3 runs × top-3 candidates** (we used **1 run** × top-3 —
  stricter) and complex targets got a **starting-material hint** (we gave none).
- Their compounds were curated; ours are scraped, messier, unfiltered for solvability.

On a like-for-like easy/lenient/hinted setup our numbers would rise further; on
the realistic, hint-free, scraped regime, 40%/55% is the honest figure.

## Threats to validity
- **Solver = Claude Opus sub-agents; scorer = mechanical RDKit.** Decoupled and
  grep-verified closed-book, but solver and orchestrator are both Claude.
- **RDKit formula-check tool** was available to solvers (disclosed). Anthropic's
  exact tooling is unspecified.
- **1 run × top-3** (no multi-run voting) — conservative vs their 3×3.
- **Across-sample vs v2:** v3 uses a different compound draw than v2, so the
  5%→40% jump is across samples. The cleanest confirmation is a **within-compound
  control** — have decoupled agents re-solve the *identical* v2 compounds (which
  the agents have never seen) and compare to the single-pass 5%. Recommended next.
- Exact InChIKey-connectivity is harsh; scaffold rate (67%) is the fairer "useful".

## Reproduce (no paid API — runs under a Claude subscription)
```bash
python scripts/benchmark_v2.py sample2 --n 40 --seed 71 --outdir data/benchmark_v3
# dispatch the 40 questions to N sub-agents (Agent tool, model=opus), 5 each,
#   blind + closed-book + RDKit-formula-check only; collect each agent's JSON to
#   data/benchmark_v3/raw/b*.json
python scripts/assemble_v3.py                                   # -> predictions2.jsonl
python scripts/benchmark_v2.py score2 --outdir data/benchmark_v3   # -> results2.txt
```
Frozen: [`questions2`](../data/benchmark_v3/questions2.jsonl) ·
[`answers2`](../data/benchmark_v3/answers2.jsonl) ·
[`raw/`](../data/benchmark_v3/raw) (per-agent outputs) ·
[`predictions2`](../data/benchmark_v3/predictions2.jsonl) ·
[`results2`](../data/benchmark_v3/results2.txt).
