# Cross-vendor sweep — protocol (run on GPT, Gemini, open-weight models)

**Question.** Every headline number in the paper is single-vendor (Claude). Is the
central diagnosis — *recall, not verification, is the wall* — a property of the
elucidation task, or an artefact of one model family? This protocol runs the identical
blind, training-free forward-verification decomposition of §5 for any vendor, so the
claim can be replicated (or falsified) across models without touching the rest of the
pipeline.

The portable quantity is the **gap between two numbers**, measured per vendor on the
same compounds:

- **generation recall** — how often the true structure appears in the vendor's own
  candidate set; and
- **verification precision (conditional on recall)** — given the true structure *is* in
  the set, how often forward-prediction re-ranking selects it.

The claim replicates for a vendor iff **verification precision > generation recall**.
For Claude the inequality holds on the whole benchmark: generation recall is 65/194
(34%) against verification precision conditional on recall of 58/65 (89%), and 30/37
(81%) restricted to the compounds where a choice actually existed
(`scripts/forward_verify_all.py`). On the 60-compound arm this harness reproduces
exactly — `score` → `recall 32% / prec|rec 84%`, i.e. 19/60 and 16/19. The two
rates have different denominators, so the criterion is the inequality, not a difference.

## Design (implemented in `scripts/cross_vendor_sweep.py`)

1. **Two stages, both blind and identical across vendors.**
   - *Solve* (recall): the vendor sees formula + IR + ¹H + ¹³C and proposes 3 ranked
     candidate SMILES per compound. No name, structure, or hint.
   - *Verify* (precision): each unique candidate's ¹³C is forward-predicted in a
     **separate context with no access to the observed spectrum** (anonymized SMILES
     only), so a vendor cannot copy the observed peaks. Candidates are re-ranked by the
     symmetric ¹³C chamfer distance to the observed spectrum (`scripts/specmetrics.py`).
   This mirrors `forward_verify.py` exactly; only the model varies.
2. **Held-out key.** The true structures and observed ¹³C live in
   `data/cross_vendor/key.json`, written at `prepare` time and never shown to any model.
3. **Same scoring as §5.** Per vendor: recall, self-rank top-1, forward-verified top-1,
   and precision conditional on recall, with a bootstrap 95% CI on recall and a pairwise
   McNemar test of recall differences between vendors.
4. **Subsets.** `fverify60` (default; the §5 set, directly comparable to Table 5),
   `main` (n=140 headline set), or `main24` (the Fig. 3 cross-model subset).

## How to run

```bash
python scripts/cross_vendor_sweep.py prepare fverify60      # -> solve_prompt.md + key.json
```

For **each** vendor `V` (e.g. `gpt`, `gemini`, `llama`):

```bash
# 1. run V on each data/cross_vendor/solve_batches/solve_NN.md — six compounds per
#    file, ONE FRESH CONTEXT PER FILE, closed-book, no tools. Merge the ten JSON
#    replies into one object (id -> [smiles, ...]) and save it as:
#    data/cross_vendor/solve_<V>.json
python scripts/cross_vendor_sweep.py prep-verify <V>        # -> verify_prompt_<V>.md (blind)
# 2. run V on data/cross_vendor/verify_prompt_<V>.md.
#    Save its JSON output (anon id -> [13C shifts]) as:
#    data/cross_vendor/verify_<V>.json
```

Then, once one or more vendors are collected:

```bash
python scripts/cross_vendor_sweep.py score                  # cross-vendor decomposition
```

`score` discovers every `solve_<V>.json` automatically. A vendor with no
`verify_<V>.json` yet is still reported on recall + self-rank top-1 (the verification
columns show `n/a`), so you can collect generation first and add verification later.

Notes:
- **Context packing is part of the protocol, not a convenience.** §4.3 measures the same
  20 compounds at 5% top-1 in one long context against 15% across bounded, reset ones, so
  a vendor handed all 60 compounds at once is being run under the arm that depresses
  accuracy and would look weaker than Claude for a reason unrelated to the model.
  `prepare` therefore writes `solve_batches/solve_01..10.md` at six compounds each —
  matching the §4.4 cross-model protocol — and `solve_prompt.md` is a reading copy that
  says so at the top. Run one file per fresh context.
- **No paid API is required.** Both stages are plain text in, JSON out, so a vendor can
  be driven through its consumer chat interface exactly as Claude was, keeping the
  zero-paid-API property of the headline protocol. Whatever the route, disable web
  search and tools first: the closed-book guarantee is the one thing this harness cannot
  check for you.
- Both prompts ask for **JSON only**, with the exact schema spelled out in the file, so
  a model's raw response usually parses directly. SMILES are canonicalized and the
  formula-match constraint is stated, matching the headline protocol.
- The working directory `data/cross_vendor/` is git-ignored — it is fully regenerated by
  `prepare`/`prep-verify`, so nothing vendor-specific or answer-bearing is committed.

## Running it against an API — what actually goes wrong

`scripts/openrouter_run.py` drives models that have no chat UI. Everything below was
found the hard way on a first pilot (2026-08-13/14, recorded in `docs/MODELS.md`); each
one fails in a way that imitates a scientific result rather than announcing itself as a
bug, which is why they are written down.

**A reasoning model may never answer at all.** DeepSeek V4 Pro, given six blind
elucidations in one context, produced tens of thousands of reasoning tokens and exhausted
a 120,000-token ceiling *without emitting one answer token*, on seven of ten batches.
Dropping to three compounds per context did not fix it. The tokens are billed either way.
Before reading a low recall as a weak model, check how many compounds it answered — the
scorer now prints `answered/total` whenever an arm is incomplete, because an unanswered
compound scores as a miss and is indistinguishable from a wrong answer in the recall
column.

**Budget guards that watch replies are blind.** Summing the cost each reply reports
cannot see a request that is still running, and cannot see one that never returns. Those
are the same requests that run away. Read spend from the account balance
(`/api/v1/credits`) before dispatching each batch, as the runner now does, and keep an
external watchdog if the run is unattended.

**Long generations need streaming.** A non-streaming request sends nothing while the
model reasons, and an idle connection gets killed — here at ~5 minutes, with an HTTP/2
`INTERNAL_ERROR` that looks exactly like a model refusing the task. Stream, over
HTTP/1.1.

**Give the token ceiling real headroom.** It has to cover the reasoning trace *and* the
answer. A cap sized for the answer alone truncates mid-thought: full price, no output,
and a silent zero in the recall column.

**Leave decoding parameters alone.** Reasoning effort, temperature, top-p: the Claude
runs behind this paper came from a subscription harness that exposes none of them (§8), so
tuning them per vendor hands one arm a degree of freedom the reference arm never had.

## Interpretation

| outcome | reading |
|---|---|
| precision ≫ recall for every vendor | the wall is the **task**, not Claude — the paper's central claim generalises |
| precision > recall but the gap narrows on stronger models | recall improves with capability; verification saturates — consistent with the Fable > Opus > Sonnet > Haiku ordering of §4.4 |
| a vendor with recall ≈ precision | that model is generation-limited *and* verification-limited equally — a genuine counterexample worth its own paragraph |

A clean multi-vendor result turns the single-vendor caveat in the abstract into a
strength: the same `recall < verification` decomposition, reproduced across independent
model families, is the version of this finding that a Nature-family reviewer cannot
attribute to one lab's model. Report it as a short addition to §4.4 (a grouped
recall-vs-precision bar per vendor) and soften the single-vendor limitation in §6.
