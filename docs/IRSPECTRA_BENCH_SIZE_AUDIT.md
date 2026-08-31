# IRSpectra-Bench size audit

**Question:** Is n=194 the maximum defensible benchmark size, or should we expand?

**Short answer:** **194 is not the theoretical maximum** — the eligible `irexp_resolved` pool is ~29k compounds — but **194 is the maximum for the current frozen benchmark** with complete Claude Opus predictions, forward-verification bundles, and pre-registered integrity filters. Expanding honestly requires new blind inference on additional held-out compounds, not relaxing QC on the existing cohort.

**Audit date:** 2026-08-31  
**Reproduce:** `python scripts/audit_bench_size.py` · `python scripts/score_main.py` · `python scripts/forward_verify_all.py`

---

## 1. What n=194 is

IRSpectra-Bench is the **union of three pre-registered rounds**, scored as one headline cohort:

| Round | Directory | Sampled | In cohort | Role |
|-------|-----------|--------:|----------:|------|
| Main (headline) | `data/benchmark_main/` | 140 | **134** | Spectrally validated; Opus predictions in `raw/` |
| Controlled v3 | `data/benchmark_v3/` | 40 | **40** | Difficulty control; pre-registered before audit |
| Within-compound control | `data/benchmark_v2_ctrl/` | 20 | **20** | Context/tooling control; pre-registered |
| **Total** | | **200** | **194** | |

**Composition:** 134 + 40 + 20 = **194**.

The six main-round compounds not in the cohort (R03, R14, R65, R67, R82, R131) fail automated ground-truth integrity checks (`scripts/validate_benchmark.py`): five have more reported ¹³C peaks than the structure has carbons (merged/contaminated spectra); one is too sparse to constrain. They were **never sent to the solver** (no entries in `data/benchmark_main/raw/`), so they cannot be added without new inference on spectra whose ground truth is itself flagged.

The controlled rounds (60 compounds) are included **whole** by design — fixed before the spectral audit existed. A strictly-validated alternative (134 + 39 + 18 = **191**) is *smaller*, reported in the paper as a robustness check, not an expansion path.

**Difficulty balance (by design):** 98 simple / 96 complex (50/50 stratification via `benchmark_v2.sample2` logic). Median heavy atoms in the cohort ≈ 20; the eligible corpus median is 26.

---

## 2. Diagnosis breakdown (fig_wall: 58 / 7 / 129)

The ICLR/combined diagnosis figure (`docs/figures/fig_wall.png`, `scripts/make_fig_wall.py`) decomposes **forward-verified top-1** on n=194:

| Segment | Count | Meaning |
|---------|------:|---------|
| **Verified** | 58 | True structure in top-3 *and* forward-verifier picks it top-1 |
| **Mis-ranked** | 7 | True structure in top-3 but verifier ranks a distractor first |
| **Never proposed** | 129 | True structure absent from the top-3 candidate pool |
| **Recalled (bracket)** | 65 | 58 + 7 = 34% generation recall |

Verified 2026-08-31 from `scripts/forward_verify_all.py`:

```
generation recall              65/194 (33.5%)
top-1, solver self-ranking     55/194 (28.4%)
top-1, forward-verified        58/194 (29.9%)
```

Self-ranking diagnosis would be 55 / 10 / 129 — the figure intentionally uses the forward-verified layer because that is the paper's central verification claim.

---

## 3. Where 194 is (and is not) hard-coded

| Location | How n arises |
|----------|----------------|
| `scripts/score_main.py` | Loads `clean_qids.json` (134) + all v3 (40) + v2_ctrl (20) |
| `scripts/make_fig_wall.py` | `N = 194` — must match `forward_verify_all.py` output |
| `scripts/check_manuscript.py` | Asserts cohort == 194 |
| `scripts/forward_verify_all.py` | Pools fverify (60) + fverify_main (134) arms |
| Paper / ICLR (`docs/iclr/iclr_paper.tex`) | Prose cites 194 throughout |

194 is **derived from released round manifests**, not an arbitrary constant — but the round sizes (140/40/20) were chosen at sampling time and are not recomputed from the corpus.

---

## 4. Theoretical maximum if filters were relaxed

### 4.1 IRexp / `irexp_resolved` scale

| Pool | Records | Notes |
|------|--------:|-------|
| IRexp (all IR band lists) | 121,233 | Full mined corpus |
| Structure-linked (`irexp_resolved`) | 43,060 | 100% resolved 2D structure |
| Full quadruples (IR + ¹H + ¹³C + structure) | 33,201 | Multimodal on one record |
| **Eligible for benchmark sampler** | **28,988** | + 8–60 heavy atoms, ≥3 NMR multiplets each, parseable SMILES |
| Eligible, not in any benchmark round | 28,793 | After excluding 194 unique InChIKey-14 in headline cohort |

Stratum composition of the eligible pool: **17.5% simple / 82.5% complex** (`scripts/corpus_reweight.py`). The benchmark oversamples simple compounds ~2.9× relative to the corpus — a deliberate difficulty-gradient design, not a random draw.

### 4.2 Filters that shrink the set

| Filter | Effect | Relaxable? |
|--------|--------|------------|
| Structure resolution | 121k → 43k | No — benchmark requires ground truth |
| IR + ¹H + ¹³C on same record | 43k → 33k | No — multimodal task definition |
| Heavy atoms 8–60 | −4,213 quadruples | Yes, but changes task difficulty |
| ≥3 parenthesised NMR entries | −~0 | Minor |
| J-enriched ¹H (controlled rounds) | Excludes compounds without recoverable J from PMC | Yes for main-style rounds |
| InChIKey-14 de-duplication across rounds | 269 unique structures used across all rounds | Required for integrity |
| Spectral ground-truth audit (`clean_qids`) | 140 → 134 main; would be 191 if applied to controls | **Should not relax post hoc** |
| Pre-registered round sizes | 140 + 40 + 20 | Expandable only with **new sampling + new inference** |
| Model predictions present | 194/194 have Opus top-3 | **Binding constraint today** |

### 4.3 Near-term expansion options (ranked)

| Option | New n | Feasibility | Integrity |
|--------|------:|-------------|-----------|
| **A. Status quo (defend 194)** | 194 | Immediate | Highest — frozen, fully instrumented |
| B. Add 6 spectrally-dirty main compounds | 200 | Requires new Opus runs on flagged spectra | **Low** — ground truths fail QC |
| C. Apply `clean_qids` to controlled rounds | 191 | Trivial code change | Smaller, not larger |
| D. New main-round sample (+N from eligible pool) | 194+N | Requires blind Opus + fverify pipeline | High if pre-registered before scoring |
| E. Corpus-matched reweighted reporting | — | Already in paper (15.2% corpus-reweighted top-1) | Complementary, not a size increase |

**Option D** is the honest expansion path: draw additional compounds from the ~28,793 eligible held-out structures (balanced by difficulty), run the decoupled Opus protocol, deposit predictions and forward-verification bundles, then update `score_main.py` cohort logic. A practical next tranche might be +100–200 compounds (→ ~300–400 total), still ≪1% of the eligible pool but materially larger for bootstrap CIs.

---

## 5. Why 194 was chosen (and is defensible)

1. **Cost of inference.** Each compound requires a blind Opus agent batch (2–12 per context) plus forward-prediction of all candidates. The deposited run covers 194 compounds with full verifier instrumentation.
2. **Pre-registration.** The 60 controlled compounds were fixed before results were known; the main round was sampled before solving. Post-hoc enlargement would need the same discipline.
3. **QC gate.** Automated spectral–structure consistency removes ambiguous ground truths rather than scoring against contaminated spectra.
4. **Corpus context.** IRexp provides **43,060 structure-linked** and **33,201 quadruple** records — the benchmark is a held-out *evaluation slice*, not the dataset size claim. The training release (`train_no_bench.jsonl.gz`, 42,808 records) deliberately de-leaks all benchmark InChIKey-14.
5. **Statistical power.** n=194 yields bootstrap 95% CIs of roughly ±6–7 points on top-1 (28.4% [22–35%]). The diagnosis (129/194 never proposed) is a *proportion*, not a noisy estimate — the bottleneck finding does not depend on n≫200.

---

## 6. Recommendation

### Do not expand the frozen benchmark in this release

No larger honest cohort exists in the repository without new model inference. The six excluded main-round compounds lack predictions and fail spectral QC. Merging pilot (n=21, no deposited Opus predictions) or electrolyte (n=46, held apart as a domain case study) would break the pre-registered design.

### Defend 194 to reviewers

Suggested text:

> IRSpectra-Bench comprises 194 blind, mechanically scored compounds drawn from a 33,201-record multimodal slice of IRexp (43,060 structure-linked records total). The benchmark size reflects (i) a pre-registered held-out evaluation protocol with spectrally validated ground truths, (ii) complete prediction and forward-verification traces for every compound, and (iii) intentional 50/50 simple/complex stratification — the eligible literature pool is ~29k compounds but 82% complex, so uniform sampling would yield a less informative difficulty gradient. Corpus-reweighted accuracy (15.2% top-1) reports the complementary “random-paper” estimate. Expansion to additional held-out compounds is straightforward from the released sampler (`scripts/benchmark_v2.py`) and scoring harness; the limiting step is blind frontier-model inference, not data availability.

### Future work (if expansion is desired)

1. Pre-register `benchmark_main_v2` draw parameters (seed, n, strata) in `docs/ESI.md` (currently a documented gap for the original 140).
2. Sample e.g. +106 compounds → 300 total (maintain 50/50 strata) from the ~28,793 eligible held-out structures.
3. Run Opus + `forward_verify_main.py` on new qids.
4. Regenerate `fig_wall.png` from `forward_verify_all.py` outputs (or teach `make_fig_wall.py` to read counts from a JSON sidecar).
5. Update `scripts/check_manuscript.py` expected n.

---

## 7. Files touched by this audit

| Artifact | Role |
|----------|------|
| `scripts/audit_bench_size.py` | Reproducible pool/cohort accounting (this audit) |
| `scripts/score_main.py` | Headline metric cohort definition |
| `scripts/validate_benchmark.py` | Spectral QC → `clean_qids.json` |
| `scripts/forward_verify_all.py` | Diagnosis numbers for fig_wall |
| `scripts/make_fig_wall.py` | ICLR/combined Fig. 1 (diagnosis plate) |
| `scripts/corpus_reweight.py` | Eligible corpus n=28,988 |
| `docs/iclr/iclr_paper.tex` | ICLR paper (n=194; not Sci Data) |

**Sci Data manuscript:** IRSpectra-Bench diagnosis figures do **not** belong in the data-only descriptor; IRexp scale (121k / 43k / 33k) is the relevant number there.
