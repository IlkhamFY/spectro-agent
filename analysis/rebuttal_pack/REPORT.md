# Rebuttal pack: uncertainty, breakdowns, and figures

This pack rescores the locked n=500 headline from the deposits already in the repo.
It does not call a model. It does not edit a locked benchmark file.
Tanimoto here is the rank-1 prediction against the true structure.
It is not similarity to the training set. That check is a separate analysis.

## What was scored

The headline roster is the locked 194, plus all 106 of the first expansion, plus the first 200 validate-clean tasks of the expand-500 draw (R01 through R75 in the committed cut).
Generation scoring is RDKit InChIKey connectivity, first 14 characters, on up to three ranked SMILES.
The rescore matches the lock: 227/500 top-1 and 249/500 top-3.
The three slices also match: 55/194, 63/106, and 109/200 top-1.
Sensitivity pools, not the headline: 245/524 and 268/524 on the clean 224 expansion, and 247/530 and 271/530 on all 230.
NMRTrans hits were recomputed from its deposited SMILES. Disagreements with the published hit file: 0.
The 194 and the 106 were no-thinking consumer Opus. The 200-cut was thinking-tier Opus. The pooled 45.4% mixes those two protocols.
Forward-verify classes (204 verified, 45 misranked, 251 never proposed) are the locked wall counts. This pack puts Wilson intervals on them. It does not rescore the chamfer rerank.

## 1. Intervals and paired tests

Opus top-1 on the headline set is 45.4% (227/500; 41.1 to 49.8).
Opus top-3 is 49.8% (249/500; 45.4 to 54.2).
NMRTrans top-1 on the same 500 is 15.8% (79/500; 12.9 to 19.3). Top-3 is 20.4% (102/500; 17.1 to 24.2).
The paired top-1 gap, Opus minus NMRTrans, is +29.6 points (+25.2 to +34.2), McNemar p=4.21e-33, discordant 162/14.
The paired top-3 gap is +29.4 points (+25.0 to +33.8), McNemar p=1.66e-34, discordant 158/11.
Simple molecules: top-1 64.9% (161/248; 58.8 to 70.6). Complex molecules: top-1 26.2% (66/252; 21.1 to 31.9).
The three slices differ by more than sampling noise: locked 194 28.4% (55/194; 22.5 to 35.1), +106 59.4% (63/106; 49.9 to 68.3), 200-cut 54.5% (109/200; 47.6 to 61.3).
Each compound was solved once. These intervals are compound-sampling intervals. They do not include run-to-run variation of the model.

Other models were not run on all 500. On the shared 60-compound slice, Opus minus each other model (top-1) is:

- Opus minus grok-4.6: -15.0 points (-26.7 to -5.0), McNemar p=0.0225, discordant 2/11, Holm 0.135.
- Opus minus gemini-3.7-flash: -15.0 points (-26.7 to -3.3), McNemar p=0.0225, discordant 2/11, Holm 0.135.
- Opus minus gpt-5.6-sol: -11.7 points (-23.3 to +0.0), McNemar p=0.0923, discordant 3/10, Holm 0.369.

Holm here is taken over every pair among Opus, Grok, Gemini, and GPT-5.6 Sol, not only the pairs against Opus.

Read those 60-compound gaps as a slice result. Opus top-1 on that slice is much lower than Opus top-1 on the full 500, because the slice sits inside the harder locked 194. A model that leads on the 60 has not been shown to lead on the 500.

Claude ladder on the 24-compound main-round subset:

- Opus top-1 25.0% (6/24; 12.0 to 44.9).
- Sonnet top-1 20.8% (5/24; 9.2 to 40.5).
- Haiku top-1 0.0% (0/24; 0.0 to 13.8).
- Fable top-1 45.8% (11/24; 27.9 to 64.9).
- Fable minus Opus: +20.8 points (+4.2 to +37.5), McNemar p=0.0625, discordant 5/0, Holm 0.188.
- Fable minus Sonnet: +25.0 points (+8.3 to +41.7), McNemar p=0.0313, discordant 6/0, Holm 0.156.
- Fable minus Haiku: +45.8 points (+25.0 to +66.7), McNemar p=0.000977, discordant 11/0, Holm 0.00586.
- Opus minus Sonnet: +4.2 points (+0.0 to +12.5), McNemar p=1, discordant 1/0, Holm 1.
- Opus minus Haiku: +25.0 points (+8.3 to +41.7), McNemar p=0.0313, discordant 6/0, Holm 0.156.
- Sonnet minus Haiku: +20.8 points (+8.3 to +37.5), McNemar p=0.0625, discordant 5/0, Holm 0.188.

Grok 4.6 versus the same model on a clean clone, top-1: +6.7 points (-3.3 to +16.7), McNemar p=0.344, discordant 7/3.
The two runs disagree in both directions. That is what a second sample looks like. It is not evidence that the first run read the answer file.

## 2. Calibration

There is no reliability diagram in this pack, because the deposits do not support one.
Ranked SMILES are stored as three strings. No record has a confidence, a probability, or a logprob.
No headline task was sampled more than once (repeat count 0).
Sampling frequency of the top answer, the confidence used by ChefNMR2, needs repeated draws of the same task. We do not have those draws.

Cheapest run that would produce the diagram:

- Keep the closed-book prompt (formula, IR, 1H, 13C, three ranked SMILES, one task per context).
- Draw 32 tasks from the locked 500, 16 simple and 16 complex, with a fixed seed. Do not draw new tasks.
- Solve each task 8 times, independently. That is 256 calls.
- Confidence of a task is the fraction of the 8 rank-1 structures that match the modal rank-1 structure (InChIKey, 14 characters).
- Plot accuracy of that modal structure against confidence, with a Wilson interval in each bin, and report the expected calibration error.
- The subscription harness used for the original deposits has no per-call price in the logs, so this run costs no API fee there.
- On the Claude API the list price for Opus 5, the model named on the 200-cut, is $5 per million input tokens and $25 per million output tokens (Anthropic rate card, 7 October 2026).
- A single task is about 1,500 input tokens. Output depends on the thinking trace. At 2,000 output tokens the 256 calls are about $15. At 8,000 output tokens they are about $53. At 15,000 output tokens they are about $98.
- Those three figures are input plus output at the list price. They are not a quote. Check the current price card before launching.

## 3. Breakdowns and near misses

Every headline task has an IR list, a 1H list, and a 13C list (missing IR 0, missing 1H 0, missing 13C 0, out of 500).
Modality availability inside the 500 does not vary. The evidence on inputs is a later leave-one-out campaign on the same 60 tasks.
That campaign's full condition is much higher than the headline Opus run on those 60 (the committed full file, which matches the submitted robustness bar). Only contrasts inside the campaign are interpretable. The absolute level is not a new headline.

- Campaign formulaIR: top-1 5.0% (3/60; 1.7 to 13.7).
- Campaign full: top-1 58.3% (35/60; 45.7 to 69.9).
- Campaign noC: top-1 56.7% (34/60; 44.1 to 68.4).
- Campaign noFormula: top-1 41.7% (25/60; 30.1 to 54.3).
- Campaign noH: top-1 35.0% (21/60; 24.2 to 47.6).
- Campaign noIR: top-1 56.7% (34/60; 44.1 to 68.4).
- Older committed file full: top-1 23.3% (14/60; 14.4 to 35.4).
- Older committed file formulaonly: top-1 5.0% (3/60; 1.7 to 13.7).

- full minus formulaIR: +53.3 points (+40.0 to +66.7), McNemar p=4.66e-10, discordant 32/0, Holm 2.33e-09.
- full minus noC: +1.7 points (-5.0 to +8.3), McNemar p=1, discordant 3/2, Holm 1.
- full minus noFormula: +16.7 points (+6.7 to +28.3), McNemar p=0.00635, discordant 11/1, Holm 0.019.
- full minus noH: +23.3 points (+11.7 to +35.0), McNemar p=0.000519, discordant 15/1, Holm 0.00208.
- full minus noIR: +1.7 points (-6.7 to +10.0), McNemar p=1, discordant 4/3, Holm 1.

Heavy-atom bins, Opus top-1:

- <=15: 75.0% (69/92; 65.3 to 82.7).
- 16-20: 56.4% (88/156; 48.6 to 63.9).
- 21-25: 37.2% (35/94; 28.1 to 47.3).
- 26-30: 27.8% (22/79; 19.2 to 38.6).
- >30: 16.5% (13/79; 9.9 to 26.1).

Ring class, Opus top-1:

- acyclic: 81.5% (22/27; 63.3 to 91.8).
- single aliphatic ring: 40.0% (8/20; 21.9 to 61.3).
- single aromatic ring: 73.2% (60/82; 62.7 to 81.6).
- polycyclic aliphatic: 57.1% (4/7; 25.0 to 84.2).
- polycyclic aromatic: 36.5% (133/364; 31.8 to 41.6).

Functional groups are presence classes. A molecule can count in more than one. Opus top-1, groups with at least 15 molecules:

- amide: 33.1% (39/118; 25.2 to 42.0).
- amine: 33.6% (42/125; 25.9 to 42.3).
- heteroaromatic: 33.7% (69/205; 27.5 to 40.4).
- aryl halide: 35.6% (48/135; 28.0 to 43.9).
- phenol: 37.0% (17/46; 24.5 to 51.4).
- ketone: 37.1% (33/89; 27.8 to 47.5).
- nitrile: 38.7% (12/31; 23.7 to 56.2).
- nitro: 42.9% (18/42; 29.1 to 57.8).
- ether: 43.3% (68/157; 35.8 to 51.1).
- carboxylic acid: 52.0% (13/25; 33.5 to 70.0).
- ester: 52.6% (41/78; 41.6 to 63.3).
- alcohol: 61.5% (24/39; 45.9 to 75.1).
- aldehyde: 66.7% (14/21; 45.4 to 82.8).

Wrong rank-1 answers: 273 of 500.
Of those, 239 still match the given molecular formula. Across all 500, 466 rank-1 structures match the formula.
The typical miss is not a near neighbor. Median Morgan Tanimoto to the truth is 0.36 (n=271).
Only 16 wrong answers have Tanimoto at least 0.70, and 4 have Tanimoto at least 0.85.
The true structure is already at rank 2 or 3 for 22 of the 273 misses. Those are ordering errors.
Median MCES similarity (common bonds divided by the larger bond count): 0.48.
Median MCES distance (bonds in one structure or the other but not both): 24.
MCES is the RDKit bond maximum common substructure, element and bond-order sensitive, rings matched to rings, 2 second cap.

## 4. Gallery

The figures draw the true structure beside the rank-1 prediction for commercial-licence molecules only.
Teal frame means the rank-1 constitution matches. Magenta frame means it does not.
Highlighted atoms on a wrong prediction are outside the common substructure.
Captions say correct, or the Tanimoto of a near miss, or the Tanimoto of a far miss.
No spectra, DOIs, or answer-key files are written.

## 5. Cost and latency

The deposits do not contain token counts, dollar cost, or wall-clock time.
Raw solver files store a task id and up to three SMILES. Campaign notes store the model name and the batch id. Sweep replies store SMILES and, separately, predicted carbon shifts.
There is nothing to plot on a cost or latency axis. A point drawn there would be invented.
The cross-vendor notes describe the Cursor arms as subscription runs with no API invoice, and the OpenRouter arms as paid, but the invoice lines are not in the tree.
A cost-versus-accuracy panel has to wait for a run that records input tokens, output tokens, and elapsed seconds on each task.

## 6. Figures

`outputs/fig_main_results.pdf` replaces the submitted overview, which stated 45.4% and 49.8% with no interval and no comparison model.
Panel a is the headline and the three slices, top-1 and top-3, with intervals.
Panel b is every rescored model on the shared 60, top-1 only, so the candidate budget matches.
Panel c is the leave-one-out campaign.
Panel d is heavy atoms, Opus against NMRTrans.
Panel e is ring class.
Panel f is the paired gap, with a bootstrap interval.
Panel g is the success and failure gallery.

`outputs/fig_breakdowns.pdf` is the failure chemistry: functional groups, Tanimoto of misses, MCES distance, formula adherence, the forward-verify wall with intervals, and four more truth-versus-prediction pairs.

`outputs/before_after_overview.png` places the submitted overview above the new main figure.
`outputs/before_after_robustness.png` places the submitted four-panel robustness figure above the new main figure, because that was the previous multi-model figure and it had intervals on only one panel.

## Reviewer questions

**Is 45.4% a stable headline, or one draw?**
On these 500 tasks it is 45.4% (227/500; 41.1 to 49.8) top-1 and 49.8% (249/500; 45.4 to 54.2) top-3. The interval is wide enough that a second sample of tasks could move the point by several points. It is not wide enough to reach the NMRTrans result. Opus minus NMRTrans top-1 is +29.6 points (+25.2 to +34.2), McNemar p=4.21e-33, discordant 162/14.

**Does the pooled 500 hide an easy expansion?**
Yes, the slices differ. Locked 194 is 28.4% (55/194; 22.5 to 35.1). The +106 is 59.4% (63/106; 49.9 to 68.3). The 200-cut is 54.5% (109/200; 47.6 to 61.3). Say so. The pool is a size-weighted mix of two Opus protocols, and the expansion tasks are easier for this solver.

**Do other labs' models already beat this?**
On the full 500, the only other deposited model is NMRTrans, at 15.8% (79/500; 12.9 to 19.3) top-1. It does not.
On a 60-compound slice, Grok, Gemini, and GPT-5.6 Sol do beat the Opus predictions from that slice. Those Opus predictions are the harder locked-194 protocol, not the pooled 500. Quote the slice, and do not promote it to a 500-task ranking.

**Are you calibrated?**
Not measured. There is no confidence and there are no repeated samples. The 256-call design above is the cheapest measurement that would answer the question in the same way as a sampling-frequency diagram.

**Is accuracy just 'small molecules are easy'?**
Heavy-atom count and ring class both move top-1, and the intervals in the tables do not overlap between the easiest and hardest bins. Complex tasks (66/252 top-1) are not a rounding error on the headline.

**Which spectrum is doing the work?**
Inside the 500, every task has all three spectra, so the headline set cannot answer this. The matched leave-one-out on 60 tasks can. Read panel c and the McNemar rows.
The largest drop from the full input is full minus formulaIR: +53.3 points (+40.0 to +66.7), McNemar p=4.66e-10, discordant 32/0.

**Are the misses close?**
The formula is usually right (239/273 of misses). The skeleton usually is not. Median Tanimoto is 0.36, and only 16 misses reach 0.70.
22 misses already have the truth at rank 2 or 3. The gallery shows both the rare near misses and the ordinary far ones.
This is distance to the truth, not a memorization test.

**What does a call cost, and how long does it take?**
Not recorded. Do not fit a cost curve to a missing log. The subscription path has no invoice line in the repo. A future run should store tokens and seconds per task.

**Can verification fix the rest?**
The locked wall says 251 of 500 truths were never in the candidate list. Re-ranking cannot recover those. 45 were in the list and ranked second or worse by the forward check. 204 were ranked first by that check. Intervals on those three counts are in the breakdown figure. The generation identity still holds: 227/500 top-1 equals 249/500 recalled times 227/249 self-rank.

## How to rerun

From the repo root, with RDKit, NumPy, Matplotlib, and Pillow:

```bash
python analysis/rebuttal_pack/run_all.py
```

Expansion questions and predictions are read from git object `48fcd30153df5e331fab43cfa514763db8ee3891`.
The resolved corpus is read only to join a structure onto each task. Nothing from that file is written out.
CC-BY-NC rows stay in memory for the join. The gallery uses commercial-pool structures only.

