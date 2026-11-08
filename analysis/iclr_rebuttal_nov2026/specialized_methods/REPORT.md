# Specialized methods named but not run on IRSpectra-Bench

Date of this note: 2026-11-08. No model was run. No paid API was called. No number below was produced on IRSpectra-Bench except numbers already printed in the submitted manuscript or its appendix.

## Which manuscript the reviewers read

Reviewer ebxW’s “Point 4 / line 97” matches contribution item 4 of the submitted ICLR manuscript, not the file currently at `docs/iclr/iclr_paper.tex` on spectro-agent `main`.

| Source | What it is |
|---|---|
| [IlkhamFY/IRSpectra-Bench `main.tex`](https://github.com/IlkhamFY/IRSpectra-Bench/blob/main/main.tex) | The submitted text. Title matches the OpenReview submission. Roster \(n=500\). Contribution item 4 (source lines 231–235) is **“Systems not scored.”** Section 2 is Related work, including the paragraph labelled `sec:not-on-roster` (source lines 351–360). |
| `si/appendix_body.tex` in that repo, `\subsection{Offline peak-list baseline (NMRTrans)}` (`si:nmrtrans`) and the reproducibility paragraph at source lines 896–903 | How NMRTrans was run, and the manuscript’s own list of systems that were not run. |
| `docs/iclr/iclr_paper.tex` in this checkout | An earlier draft. Title differs. Roster \(n=194\). Line 97 is the sentence that the two rates must not be differenced. Contribution item 4 is the literature decomposition, not a list of unevaluated systems. |

The OpenReview PDF (`https://openreview.net/pdf?id=k3ANnHd50t`) returned HTTP 403 from this environment, so the printed margin line “97” was not re-counted on the PDF. The item ebxW describes is contribution 4 of the submitted TeX. This note does not edit `docs/iclr/iclr_paper.tex`.

Locked headline figures used below, from the submitted abstract and `si/appendix_body.tex`: top-1 \(227/500 = 45.4\%\), recall \(249/500 = 49.8\%\), precision given recall \(227/249 = 91.2\%\).

## Recommendation on Point 4

Stop listing unevaluated systems as a contribution.

Contribution item 4 currently says that Section `sec:not-on-roster` names elucidators that were not run, and that the factorisation is what the harness measures without them. The factorisation is already contribution 2. A list of systems that were not run is a limitation, not a result. Delete item 4 from the contribution list. Keep one Limitations paragraph that states, system by system, the input the system actually requires and the concrete blocker (format, missing weights, paid API, or the retrieval database). Do not repeat the manuscript’s single clause that “API access, licence, and input do not match” for every name in that list. That clause is accurate for some rows and inaccurate for others; the table below separates them.

Two NMR-only comparisons are feasible on the printed shift lists with public code and no paid API (NMR-Solver, and Hu et al. on \(^{13}\)C only). They were not run. They are not IR+\(^1\)H+\(^{13}\)C peers. They should be offered as follow-up experiments, not claimed as done.

## What “evaluated on IRSpectra-Bench” means here

A system is counted as evaluated only if the submitted manuscript reports an InChIKey-14 score on the frozen 500-item roster (or on a named slice of that roster). Published top-\(k\) numbers copied into the literature-decomposition table are not on-bench scores. The manuscript says so: `si:lit` caption, “Separate settings, not scores on this roster.”

The bench input, from the submitted Section 3 and `si:closed-book`, is four fields per question: molecular formula, IR band positions in cm\(^{-1}\), a printed \(^1\)H list (shifts, integrals, couplings as printed), and a printed \(^{13}\)C shift list. No spectrum image, no absorbance trace, no FID, no vendor folder, no HSQC/COSY/HMBC, no mass-spectral peak list.

## Section 2 systems

Order follows Related work in the submitted `main.tex`. “On bench?” is IRSpectra-Bench, not the system’s own paper.

| System (as named in Section 2) | On bench? | Input the system requires | Why excluded, or how it was run |
|---|---|---|---|
| Spectro (Chacko et al., ChemRxiv 2024, doi 10.26434/chemrxiv-2024-37v2j) | No | IR through a vision encoder pretrained on functional-group peaks in IR spectra; NMR passed as text through LLM2Vec; decoder emits SELFIES. | Input mismatch on IR: the published IR channel is a spectrum image, not a wavenumber list. No public code or weights were located from the ChemRxiv record. The “API access” half of the manuscript’s lumped sentence does not apply. |
| NMIRacle (Ottomano et al., arXiv 2512.19733) | No | Concatenated binned traces in `spectra.h5`: IR (1,800 bins), \(^1\)H (10,000), \(^{13}\)C (10,000). | Input mismatch: fixed-length intensity traces, not printed lists. Code is public (`fedeotto/nmiracle`). The README says checkpoints will be released upon publication. A Hugging Face repo `fedeotto/miracle-models` exists; this note did not confirm that weight files are downloadable. Building a stick spectrum from the printed lists would be an adapter the manuscript says was not built (`si:repro`). |
| Hu et al. 2024 multitask model (ACS Cent. Sci., doi 10.1021/acscentsci.4c01132); code name NMR2Struct | No | End-to-end model reads a concatenated binned \(^1\)H+\(^{13}\)C vector (source size 28,045 in the released config). Single-example CLI: \(^1\)H file is `(ppm, intensity)` pairs interpolated onto `HNMR_shifts.p`; \(^{13}\)C file is a comma-separated ppm list discretized with `CNMR_shifts.p`. Formula is not an input. No IR channel. | The joint \(^1\)H+\(^{13}\)C mode needs a proton intensity trace. The bench’s \(^1\)H field is a multiplet table (shift, integral, \(J\)), not `(ppm, intensity)`. A \(^{13}\)C-only run is a documented mode (`--hnmr_file None`) and is feasible; it was not run. See the experiment outline below. Code: `MarklandGroup/NMR2Struct`. Checkpoints: Zenodo record cited in that README, `10.5281/zenodo.13892026`. No paid API. |
| NMRTrans (Yang et al., KDD 2026, arXiv 2602.10158) | Yes, NMR-only | Molecular formula plus unordered \(^1\)H and \(^{13}\)C peak sets. No IR channel. | Run as specified in `si:nmrtrans`. Offline CPU, beam 3, no sampling, no paid API. Code commit `9a72756`, checkpoint `little1d/C-H-Formula`, file `nmrtrans-c-h-nmr-formula.ckpt` (499/499 weights loaded). Questions: frozen roster at spectro-agent `48fcd30`. IR bands were not passed. Multiplicity mapped onto the model’s split vocabulary (87 peaks left unknown). 76 of 4,298 proton peaks had no printed integral and were stored as 0, not imputed as 1H. \(^{13}\)C repeated only when the list prints an \(n\)C count. 19 shifts outside \([0,220]\) ppm clamped by the published `/220` normalisation. Nine formulae contain Se or Sn, which the released 12-element formula vector drops. Scores (InChIKey-14): **79/500 top-1 (15.8%)**, **102/500 recall (20.4%)**; simple 62/248 and 79/248; complex 17/252 and 23/252; held out of the released NMRTrans splits **70/489 top-1**, **92/489 recall**. Nine gold InChIKey-14 values are in the released training split (8/9 top-1, 9/9 inside the beam); two in validation (1/2 top-1); none of the 500 are in the released test split. 86/500 rank-1 strings were not valid RDKit SMILES. The SI names a deposit at `data/baseline_nmrtrans/`. That path is not in spectro-agent commit `48fcd30` and not on current `main`. |
| Alberts et al. 2024 (Commun. Chem., doi 10.1038/s42004-024-01341-w) and Alberts et al. 2025 (Digital Discovery, doi 10.1039/d5dd00131e) | No | 2024: IR absorbance interpolated onto a token grid, normalised to integers 0–99, concatenated with the formula. Not a wavenumber list. 2025 reports the same IR-trace setting on NIST. | Input mismatch. 2024 training and data-generation code is public (`rxn4chemistry/rxn-ir-to-structure`). That repository sentence is a training release, not a peak-list inference API. The literature-decomposition row “Alberts, 6–13 atoms, NIST IR (3,455): top-1 63.8%, top-10 84.0%” is their published NIST figure, not a score on this roster. |
| ChemCrow (M. Bran et al., Nat. Mach. Intell. 2024) | No | Tool-using chemistry agent (synthesis and database tools) driven by an LLM API. | Wrong task. It is not an elucidator of a formula plus three printed lists. Not run. |
| Coscientist (Boiko et al., Nature 2023) | No | LLM agent for autonomous laboratory planning and execution. | Wrong task. Not an elucidator of printed peak lists. Not run. |
| Tree-search over MolPuzzle (Zhuang et al., ACL 2025; Guo et al., NeurIPS 2024) | No | MolPuzzle’s spectrum stage is spectral **images** (IR, MS, \(^1\)H, \(^{13}\)C), plus formula. The reported tree-search gains use LLM calls (the manuscript’s own GPT-4o range, 1.4% vs 57.8%, is on MolPuzzle, not on this roster). | Input mismatch (images) and a paid LLM API for the search the paper cites. Not run here. |
| SpecMol, which is MolSpectLLM (Shen et al., arXiv 2509.21861). The submission cites it as SpecMol. Reviewer ndRh’s “MolSpectLLM” is this paper. | No | Text. \(^{13}\)C is a shift list. \(^1\)H is centroid, multiplicity, \(J\), and integral. IR is frequency–intensity pairs over 500–4000 cm\(^{-1}\). MS is \(m/z\):abundance, with mode and collision energy. Example prompts in `Eurekashen/SpecMol` `examples/example_spec2smiles/` show all of these. | The \(^1\)H/\(^{13}\)C text is close to the bench. IR intensities and MS fragments are not in the roster, so a full multimodal prompt cannot be built. The public repo contains metrics, formatters, and prompt examples. It does not contain a checkpoint or a generation script. No public weights were located. A \(^1\)H+\(^{13}\)C-only prompt is not runnable until weights exist. Not outlined as an experiment. |
| Priessner et al. 2026, reasoning-capable LLMs (Digital Discovery, doi 10.1039/D5DD00359H) | No | A **guess structure** plus \(^1\)H, \(^{13}\)C, HSQC, COSY, and MS. Candidate generators include Chemformer, Mol2Mol, and MMST. The reasoning stage calls Claude and DeepSeek. | Input mismatch: the bench has no seed structure, no 2D correlations, and no MS. The published reasoning step is a paid LLM API. Code is public (`mpriessner/ChemStructLLM_`; Zenodo 10.5281/zenodo.17877209). Not a drop-in. |
| NMR-Solver (Jin et al., Nat. Commun. 2026, doi 10.1038/s41467-026-71315-0) | No | Literature-style \(^1\)H and \(^{13}\)C paragraphs (shift, integral, multiplicity, \(J\) for \(^1\)H; shifts for \(^{13}\)C). Formula is an optional element/formula constraint. No IR. Demo file `data/demo/test.txt` is exactly that prose. | **Feasible as an NMR-only run. Not run.** The published literature numbers in `si:lit` (top-1 52.9%, top-10 67.3%, \(n=450\)) are a different set. See the experiment outline. The manuscript’s “not run” sentence does not name NMR-Solver in the main-text lump; `si:nmrtrans` says it was not rerun. |
| NMRAgent (Fang et al., arXiv 2606.29776) | No | CLI is `--formula`, `--h-shifts`, `--c-shifts` (ppm lists). That matches printed \(^1\)H/\(^{13}\)C shifts. Multiplicity and \(J\) are not arguments. No IR. The planner is an OpenAI-compatible chat API; the example config is `gpt-4o-mini` with `OPENAI_API_KEY`. Retrieval/de novo checkpoints and the FAISS index are not in the git tree. | Not run because the published runner requires a paid (OpenAI-compatible) API and artifacts that are outside the git repo. The shift-list interface itself is compatible. The `si:lit` row (top-1 61.6%, top-10 70.0%, literature \(n=450\)) is their Exp450 figure, not this roster. Do not start a paid sweep for the rebuttal. |
| SpectraLLM (Su et al., ICLR 2026, arXiv 2508.08441) | No | JSON peak records that store coordinates **and relative intensities** for IR and for \(^1\)H/\(^{13}\)C, plus HSQC and MS metadata when used. Prompts are instruction–response text. | Public adapters exist (`ccjh/SpectraLLM_32B`, `ccjh/widthIrplus_msg_qm9s_mb_msd`). No paid API is required to run those adapters. The blocker is the intensity channel: bench IR lists are wavenumbers without intensities, and printed NMR integrals are not SpectraLLM’s normalised peak intensities. Filling intensities with a constant would be an untested adapter. Not outlined. The manuscript’s “API access” reason does not fit this row. |
| IR-Agent (Noh et al., arXiv 2508.16112) | No | An absorbance vector \(\mathcal{X}\in\mathbb{R}^{1\times L}\). The default task does **not** take a formula. Expert agents are OpenAI models (gpt-4o-mini-2024-07-18, gpt-4o-2024-08-06, o3-mini-2025-01-31) via `langchain-openai`. Code: `HeewoongNoh/IR-Agent`. | Input mismatch (absorbance trace, not a wavenumber list) and a paid OpenAI API. Not run. |
| MolQuest (Han et al., arXiv 2603.25253) | No | A separate agentic benchmark for abductive structure elucidation, not a released weight file. | Not a model to score. No MolQuest agent was run on this roster. Listing it locates a concurrent suite. It is not a missing baseline until a specific public agent is named. |
| NMRGym (Fang et al., arXiv 2601.15763) | No | A benchmark of NMR elucidation tasks and datasets. | Not a model. The manuscript cites it as a concurrent suite. NMRAgent’s paper evaluates on NMRGym; that is not an IRSpectra-Bench score. |
| Espejo Morales et al. (arXiv 2607.19406) | No | Starts from FID / instrument files, builds a partially processed peak table, then an OpenAI Agents SDK driver with formula. Reported settings are education instrument files (\(n=236\)) and industrial instrument files (\(n=34\)). | Paid OpenAI API, and the published object is an instrument file rather than a literature IR+\(^1\)H+\(^{13}\)C section. The `si:lit` rows (education top-1 80.9%, industrial top-1 20.6%) are their numbers, not this roster. Not run. |
| DP4 (Smith and Goodman, 2010) | No | GIAO-DFT shifts for candidate **diastereomers**, compared with experimental shifts, to assign relative stereo. | Not a constitution proposer. The bench headline scores connectivity, and the roster has no 3D conformer set. Not run as a ranker. The rankers that were run are chamfer, a HOSE-style lookup, and a GNN (see HOSE row). |
| HOSE-code lookup (Bremser 1978), as cited in Section 2 | Verifier only, on an existing pool | Substructure HOSE codes used to predict \(^{13}\)C and re-rank candidates that were already proposed. | The appendix states that a HOSE-style lookup on the protocol-slice candidate sets ties self-ranking. It does not give a separate numerator for that tie. A modest GNN on the same slice reaches 59/65 (91%) against the LLM verifier’s 58/65 (89%). This is not de novo elucidation and not an \(n=500\) row. |
| CASE (Elyashberg 2012, Elyashberg and Williams 2015, Buevich and Martin 2016) | No | Formula plus spectral constraints, in the cited systems especially 2D correlations (HSQC, HMBC, COSY), then isomer generation and ranking. | Input mismatch: the roster has no COSY, HSQC, or HMBC tables. The implementations the manuscript calls “commercial CASE” are additionally license-blocked. An open formula-only enumerator would be a different experiment (reviewer ebxW Q5’s exhaustive isomer pool) and was not run here. |
| SpecX (Xiang et al., arXiv 2605.18791) | No | A multi-modal spectroscopy benchmark on **simulated** traces. | Different object. The `si:lit` row (scaffold split, simulated \(n=99{,}439\), top-1 29.7%, top-10 50.6%) is their published split, not this roster. |
| NIST WebBook and nmrshiftdb2 | Not systems | Spectral corpora cited as the usual training/evaluation source for the models above. | Nothing to run. |

The manuscript’s own summary (`si:repro`, source lines 896–899) says on-bench scores for IR-Agent, CASE, SpectraLLM, NMR-Solver, Spectro, NMIRacle, and the Alberts transformers were not obtained, that those systems are “blocked on input, licence, or compute,” and that no adapter was built. That sentence should be replaced by the row-level reasons above. NMR-Solver is blocked on the retrieval database and on a gold-SMILES leak in `run.py`, not on the peak-list format. SpectraLLM is blocked on missing intensities, not on an API. Spectro and NMIRacle are blocked on the spectrum representation and, for NMIRacle, on checkpoints the README still marks as forthcoming.

## Reviewer-named systems that are not in Section 2

ndRh Q5 also names MMST and SECS. They are not cited in the submitted Related work. MolSpectLLM is the SpecMol row above.

| System | In Section 2? | Input required | Why a comparison was not run |
|---|---|---|---|
| MMST, MultiModalSpectralTransformer (Priessner et al., Angew. Chem. Int. Ed., doi 10.1002/anie.202517611) | No | \(^1\)H, \(^{13}\)C, HSQC, COSY, IR, and MS. IR is a simulated or measured intensity vector (Chemprop-IR pipeline; Zenodo also stores manually peak-picked experimental NMR and IR). Multinomial candidates are ranked by simulated-versus-experimental **HSQC**. Their ablation on held-out ZINC (not this bench): greedy exact match 59.7% with all modalities, 7.7% without HSQC, 8.1% without COSY. | Input mismatch. The roster has no HSQC, COSY, or MS, and the IR field has no intensities. HSQC is both an input and the published ranker. Code and weights are public (`mpriessner/MultiModalSpectralTransformer`; Zenodo 10.5281/zenodo.14712886 and the three-part records linked from that README). The GitHub license text is CC BY-NC, which allows a non-commercial academic run; license is not the blocker. A reduced-modality run would be a new adapter, not the published system. Not outlined. |
| SECS (Mirza, Patiny, and Jablonka, Nat. Commun. 2026, doi 10.1038/s41467-026-73846-y) | No | Raw spectra. The paper’s \(^1\)H encoder is a length-10,000 intensity vector. HSQC is a \(512\times 512\) matrix rebuilt from peak ranges. The public web app takes JCAMP-DX or a Bruker/Varian folder. The paper contrasts this with peak-list methods. | Input mismatch. Printed lists are not raw traces or vendor files. Code is public (`lamalab-org/secs`); the README points checkpoints to Zenodo `10.5281/zenodo.14634449`. Synthesising a stick or broadened trace from the printed lists is an adapter the SECS paper does not provide and this manuscript did not build. Not outlined as a faithful experiment. |
| MolSpectLLM | Yes, under the name SpecMol | See the SpecMol row. | Same row. Do not treat it as a third, separate system. |

## Feasible experiments (not run)

Both are NMR-only. Neither uses the IR list. Neither was executed for this note. Score any future deposit with the existing InChIKey-14 scorer and report top-1, recall, and precision given recall separately. Do not difference those rates.

### 1. NMR-Solver on the frozen roster, formula + printed \(^1\)H + printed \(^{13}\)C

This is feasible with public code and no paid API. It is the comparison most directly aligned with the bench’s NMR text.

Resources, all public:

- Code, MIT: `https://github.com/YongqiJin/NMR-Solver`
- NMRNet weights: Zenodo `10.5281/zenodo.16952024` (place them where that README says)
- Retrieval database: Hugging Face `yqj01/SimNMR-PubChem`. The NMR-Solver README gives the processed set as 373 GB and the index as 128 GB
- No OpenAI/Anthropic/Google call

Blind-input constraint, from their `run.py` as retrieved 2026-11-08:

- `config/demo.yaml` sets `use_elements: True`.
- `run.py` then sets the allowed element set by calling `get_elements_from_mol` on the record’s `smiles` field, and it also raises `max_cycle_length` from that molecule’s rings.
- Passing the gold SMILES would leak the element set and the ring-size cap. Do not do that.
- Patch the runner so the element whitelist comes from the roster formula (a legitimate bench field) and `max_cycle_length` stays at the config default of 6. Keep `use_candidates: False`.

Protocol:

1. For each of the 500 qids, write one record in the style of `data/demo/test.txt`: a \(^1\)H paragraph and a \(^{13}\)C paragraph built only from `h_nmr` and `c_nmr`. Do not write `ir_bands_cm-1`. Do not write the gold SMILES into the file the solver reads.
2. `python data_process.py -i blind.txt` to build the LMDB the demo config points at.
3. `python src/faiss_server/server.py` after the index is in `database/`.
4. Run `script/run.sh` with the patched config (`nmr_type: 'HC'`).
5. Take the returned SMILES list. Score two budgets with the bench scorer: \(k=3\) (the roster contract) and \(k=10\) (the budget in their published literature table). Report top-1 \(= a/500\), recall \(= b/500\), precision given recall \(= a/b\). Label the row “NMR-only; IR unused.”
6. State the patch (formula-derived elements, ring cap not taken from gold) next to the number.

This was not run. The database size is the practical blocker, not the text format. The result would still not be an IR+\(^1\)H+\(^{13}\)C peer of the headline harness.

### 2. Hu et al. / NMR2Struct, \(^{13}\)C list only

Feasible for the carbon list. Not feasible for joint \(^1\)H without inventing intensities.

Resources:

- Code: `https://github.com/MarklandGroup/NMR2Struct`
- Checkpoints: Zenodo `10.5281/zenodo.13892026` (the record named in that README)
- Shift grid shipped in the repo: `example_configs/CNMR_shifts.p`
- No paid API

Protocol:

1. For each qid, write `c_nmr` as one comma-separated ppm line. That is the `--cnmr_file` format in the README.
2. Call `nmr_infer_single_spectrum` with `--hnmr_file None`, `--cnmr_file` that line, `--cnmr_shifts example_configs/CNMR_shifts.p`, the paper checkpoint, and `--normalize`. Set the start/stop tokens from the README’s spectrum-to-structure table.
3. Score with InChIKey-14. The paper reports a top-15; also cut the same list at \(k=3\) so it can sit next to the roster contract.
4. Label the row “\(^{13}\)C only; \(^1\)H and IR unused; formula unused.” The 2024 paper’s evaluated domain is molecules up to 19 heavy atoms. The roster is not restricted to that, so report the heavy-atom split rather than pooling it away.

Do not build a fake \(^1\)H intensity trace in order to turn on the proton channel.

## What is still missing

- The rendered OpenReview PDF, so margin line 97 was not re-measured. The contribution item is identified from the submitted TeX.
- `data/baseline_nmrtrans/` is named in the SI and is absent from spectro-agent `48fcd30` and from current `main`. The NMRTrans numerators above are the SI table, not a rescore of a local deposit.
- Downloadable NMIRacle weight files were not confirmed.
- A public MolSpectLLM / SpecMol checkpoint was not found. Until one exists, the \(^1\)H+\(^{13}\)C prompt that would otherwise match the bench cannot be scored.
- No NMR-Solver or NMR2Struct output exists, so there is no on-bench numerator for either feasible experiment.
- Commercial CASE was not given a license check beyond the manuscript’s statement that it is commercial. The 2D-correlation gap is sufficient on its own.

## Paste-ready comment, reviewer ndRh, question 5

Question 5 asked for a direct comparison to MMST (doi 10.1002/anie.202517611), MolSpectLLM (arXiv 2509.21861), SECS (doi 10.1038/s41467-026-73846-y), and other specialized methods, or for a concrete reason those comparisons are not feasible.

> We did not run MMST, MolSpectLLM, or SECS on IRSpectra-Bench, and we will stop presenting that omission as a contribution.
>
> IRSpectra-Bench gives each system the molecular formula and three printed lists: IR band positions (cm\(^{-1}\)), a \(^1\)H multiplet list, and a \(^{13}\)C shift list. It does not include an absorbance trace, a spectrum image, a FID, a vendor folder, HSQC, COSY, HMBC, or a mass spectrum.
>
> MMST (doi 10.1002/anie.202517611) takes \(^1\)H, \(^{13}\)C, HSQC, COSY, IR, and MS, and ranks multinomial candidates by HSQC. The roster has no HSQC, COSY, or MS, and the IR field has no intensities. In the authors’ own ZINC ablation, greedy exact match falls from 59.7% with all modalities to 7.7% without HSQC. Code and weights are public; the blocker is the missing channels, not the license (the code is CC BY-NC). We are not reporting an adapted run.
>
> MolSpectLLM is the model we cited as SpecMol (arXiv 2509.21861). Its \(^1\)H and \(^{13}\)C text (shift, multiplicity, \(J\), integral) is close to our lists. Its IR channel is frequency–intensity pairs and its MS channel is \(m/z\):abundance. Those intensities are not in the roster. The public repository contains metrics and prompt examples and no checkpoint, so we cannot score even a \(^1\)H+\(^{13}\)C prompt.
>
> SECS (doi 10.1038/s41467-026-73846-y) takes raw spectra: a length-10,000 \(^1\)H intensity vector, and JCAMP-DX or Bruker/Varian files in the public app. Printed peak lists are the representation SECS distinguishes itself from. Code and Zenodo checkpoints are public. We did not synthesize traces from the lists.
>
> Of the other systems in Section 2, one trained model was run. NMRTrans reads a formula and printed \(^1\)H/\(^{13}\)C peak sets and has no IR channel. On the same 500 questions, offline, beam 3, no paid API: top-1 79/500 (15.8%), recall 102/500 (20.4%). Nine gold connectivity keys appear in its released training split. That row is an NMR-only baseline, not an IR+\(^1\)H+\(^{13}\)C peer. The closed-book harness on the full three-list input remains top-1 227/500 (45.4%), recall 249/500 (49.8%), precision given recall 227/249 (91.2%).
>
> Two further NMR-only comparisons are feasible with public code and no paid API, and we have not run them. NMR-Solver already parses literature \(^1\)H/\(^{13}\)C paragraphs; a blind run must take the element whitelist from our formula and must not pass the gold SMILES (the released `run.py` reads the element set and the ring-size cap from that SMILES). It also needs the public SimNMR-PubChem index (about 373 GB plus a 128 GB index). Hu et al. (NMR2Struct) accept a comma-separated \(^{13}\)C list with the proton file set to None; their proton file requires `(ppm, intensity)` pairs, which we do not have. Neither experiment uses the IR list. We will not quote their published accuracies as IRSpectra-Bench scores. Those published figures (NMR-Solver 52.9% top-1 and 67.3% top-10 on a different literature set of 450; NMRAgent 61.6% and 70.0% on that same style of set) stay in the literature table, labelled as other settings.
>
> Systems that need a paid LLM API (IR-Agent’s OpenAI agents, NMRAgent’s OpenAI-compatible planner, Espejo Morales et al., the Priessner reasoning stage) were not called. IR-Agent’s native input is also an absorbance vector, not a band list. Priessner et al. (Digital Discovery 2026) additionally require a seed structure plus HSQC, COSY, and MS.

## Paste-ready comment, reviewer ebxW, question 1

Question 1 asked what contribution 4 (line 97) adds, and asked for every Section 2 system that was not evaluated, with a specific reason.

> Point 4 does not add a result. It points at a list of systems we did not run. The measurement in this paper is the frozen roster, the InChIKey-14 contract, and the split of top-1 into recall and precision given recall (227/500, 249/500, 227/249). Naming systems that were not scored is a limitation. We will delete Point 4 from the contribution list and state the exclusions in Limitations, one reason per system, instead of one clause about “API access, licence, and input.”
>
> Evaluated from Section 2: NMRTrans, on formula and printed \(^1\)H/\(^{13}\)C only, IR unused (79/500 top-1, 102/500 recall, beam 3, no paid API). A HOSE-style \(^{13}\)C lookup was used only as a ranker of an existing candidate pool on the protocol slice, where it ties self-ranking; that is not de novo elucidation.
>
> Not evaluated, and why:
>
> - Spectro: IR channel is a spectrum image; no public code or weights located.
> - NMIRacle: binned IR/\(^1\)H/\(^{13}\)C intensity traces (1,800 / 10,000 / 10,000). Code is public; the README still says checkpoints come at publication.
> - Hu et al. 2024: the proton file is `(ppm, intensity)` pairs. A \(^{13}\)C-only mode matches our carbon list and was not run.
> - Alberts 2024 and 2025: interpolated IR absorbance (integers 0–99) plus formula, not a band list. Their NIST top-\(k\) in our literature table is not a score on this roster.
> - ChemCrow and Coscientist: laboratory agents, not peak-list elucidators.
> - MolPuzzle tree search: spectral images, and the reported search uses an LLM API.
> - SpecMol (MolSpectLLM, arXiv 2509.21861): \(^1\)H/\(^{13}\)C text matches; IR and MS need intensities we do not have; no checkpoint in the public repo.
> - Priessner et al. 2026 (Digital Discovery): needs a guess structure plus HSQC, COSY, and MS, then a paid reasoning API.
> - NMR-Solver: the \(^1\)H/\(^{13}\)C text format matches. Not run. A blind run must not feed the gold SMILES to `run.py`, and it needs the public ~500 GB SimNMR-PubChem index. IR is unused. The 52.9% / 67.3% figures are their literature set of 450.
> - NMRAgent: the CLI is formula plus \(^1\)H and \(^{13}\)C shifts, which we can supply, but the runner requires an OpenAI-compatible API and retrieval artifacts that are not in the git repo. Not called.
> - SpectraLLM: public weights, but every peak is stored with a relative intensity we do not have for IR.
> - IR-Agent: absorbance vector, formula not used by default, OpenAI agents. Not called.
> - MolQuest, NMRGym, SpecX: other benchmarks, not models we could deposit. SpecX’s published row is simulated traces.
> - Espejo Morales et al.: instrument files and an OpenAI agent. The 80.9% and 20.6% figures are their sets, not ours.
> - DP4: stereo ranking by GIAO-DFT given candidate diastereomers, not constitution from these lists.
> - CASE, as cited: 2D correlation constraints we do not provide; the commercial packages are also licensed.
>
> MMST and SECS are not in Section 2. MMST ranks on HSQC and takes an IR intensity vector; SECS takes raw spectra or vendor files. Neither was run. We will not add them to the contribution list.

## Related work / Limitations paragraph for the revised PDF

Paste as Limitations prose. It replaces contribution item 4 and the lumped sentence at the end of Related work.

> The only trained elucidator scored on the frozen roster is NMRTrans, and only as an NMR-only baseline: formula and printed \(^1\)H/\(^{13}\)C lists, IR unused, beam 3, no paid API (79/500 top-1, 102/500 recall). Nine gold connectivity keys occur in its released training split. Spectro, NMIRacle, and the Alberts infrared transformers consume an IR image or a binned absorbance trace, which this roster does not contain. SpectraLLM’s public adapters encode peak intensities we do not have. IR-Agent consumes an absorbance vector and calls a paid OpenAI agent; NMRAgent’s shift-list interface matches our \(^1\)H/\(^{13}\)C fields but its published runner also calls an OpenAI-compatible API. MMST ranks candidates by HSQC and was trained with COSY and an IR intensity vector; SECS reads raw intensity vectors or vendor files. MolSpectLLM’s \(^1\)H/\(^{13}\)C text is compatible, but the public repository ships no weights, and its IR and MS channels need intensities. Priessner et al. (Digital Discovery, 2026) require a seed structure and 2D/MS data. CASE, as cited, uses 2D correlations that are absent here. NMR-Solver is the specialized system whose published parser already accepts literature \(^1\)H/\(^{13}\)C paragraphs; it was not run, because a blind execution must not pass the gold structure into the released runner and because the retrieval index is a separate download of several hundred gigabytes. A \(^{13}\)C-only run of Hu et al. (2024) is likewise unimplemented. Neither would be an IR+\(^1\)H+\(^{13}\)C result. Published top-\(k\) figures for other systems are left in the literature table and are not scores on this roster.
