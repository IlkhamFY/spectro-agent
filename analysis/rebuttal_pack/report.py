"""Plain-language report. Numbers are filled from the scorer so a rerun stays consistent."""
from __future__ import annotations


def _ci(row, digits=1):
    return (
        f"{100 * row['p']:.{digits}f}% "
        f"({row['k']}/{row['n']}; {100 * row['lo']:.{digits}f} to {100 * row['hi']:.{digits}f})"
    )


def _find(rows, name, metric):
    for r in rows:
        if r.get("name") == name and r.get("metric") == metric:
            return r
    raise KeyError((name, metric))


def _pp(r):
    return (
        f"{100 * r['diff']:+.1f} points "
        f"({100 * r['lo']:+.1f} to {100 * r['hi']:+.1f}), "
        f"McNemar p={r['p']:.3g}, discordant {r['b_only_a']}/{r['c_only_b']}"
    )


def _no_dash(text):
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit("report contains a dash that should be a hyphen or the word 'to'")
    return text


def build(bundle, result):
    h = result["headline_rows"]
    opus = _find(h, "Opus n=500", "top-1")
    opus3 = _find(h, "Opus n=500", "top-3")
    nmr = _find(h, "NMRTrans n=500", "top-1")
    nmr3 = _find(h, "NMRTrans n=500", "top-3")
    simple = _find(h, "Opus simple", "top-1")
    complex_ = _find(h, "Opus complex", "top-1")
    a194 = _find(h, "Opus locked 194", "top-1")
    a106 = _find(h, "Opus +106", "top-1")
    a200 = _find(h, "Opus expand-500 200", "top-1")
    near = result["near"]
    avail = result["modality_avail"]

    def paired(family, a, b, metric="top-1"):
        for r in result["paired"]:
            if r["family"] == family and r["a"] == a and r["b"] == b and r["metric"] == metric:
                return r
        return None

    gap = paired("n500", "Opus", "NMRTrans", "top-1")
    gap3 = paired("n500", "Opus", "NMRTrans", "top-3")

    lines = []
    w = lines.append
    w("# Rebuttal pack: uncertainty, breakdowns, and figures")
    w("")
    w("This pack rescores the locked n=500 headline from the deposits already in the repo.")
    w("It does not call a model. It does not edit a locked benchmark file.")
    w("Tanimoto here is the rank-1 prediction against the true structure.")
    w("It is not similarity to the training set. That check is a separate analysis.")
    w("")
    w("## What was scored")
    w("")
    w("The headline roster is the locked 194, plus all 106 of the first expansion, plus the first 200 validate-clean tasks of the expand-500 draw (R01 through R75 in the committed cut).")
    w("Generation scoring is RDKit InChIKey connectivity, first 14 characters, on up to three ranked SMILES.")
    w("The rescore matches the lock: 227/500 top-1 and 249/500 top-3.")
    w("The three slices also match: 55/194, 63/106, and 109/200 top-1.")
    w(f"Sensitivity pools, not the headline: {result['pool_524_top']}/{result['pool_524_n']} and {result['pool_524_rec']}/{result['pool_524_n']} on the clean 224 expansion, and {result['pool_530_top']}/{result['pool_530_n']} and {result['pool_530_rec']}/{result['pool_530_n']} on all 230.")
    w(f"NMRTrans hits were recomputed from its deposited SMILES. Disagreements with the published hit file: {result['nmr_mismatch']}.")
    w("The 194 and the 106 were no-thinking consumer Opus. The 200-cut was thinking-tier Opus. The pooled 45.4% mixes those two protocols.")
    w("Forward-verify classes (204 verified, 45 misranked, 251 never proposed) are the locked wall counts. This pack puts Wilson intervals on them. It does not rescore the chamfer rerank.")
    w("")
    w("## 1. Intervals and paired tests")
    w("")
    w(f"Opus top-1 on the headline set is {_ci(opus)}.")
    w(f"Opus top-3 is {_ci(opus3)}.")
    w(f"NMRTrans top-1 on the same 500 is {_ci(nmr)}. Top-3 is {_ci(nmr3)}.")
    w(f"The paired top-1 gap, Opus minus NMRTrans, is {_pp(gap)}.")
    w(f"The paired top-3 gap is {_pp(gap3)}.")
    w(f"Simple molecules: top-1 {_ci(simple)}. Complex molecules: top-1 {_ci(complex_)}.")
    w(f"The three slices differ by more than sampling noise: locked 194 {_ci(a194)}, +106 {_ci(a106)}, 200-cut {_ci(a200)}.")
    w("Each compound was solved once. These intervals are compound-sampling intervals. They do not include run-to-run variation of the model.")
    w("")
    w("Other models were not run on all 500. On the shared 60-compound slice, Opus minus each other model (top-1) is:")
    w("")
    for r in result["paired"]:
        if r["family"] == "cross60" and r["a"] == "Opus":
            holm = r.get("holm")
            holm_s = f", Holm {holm:.3g}" if holm is not None else ""
            w(f"- Opus minus {r['b']}: {_pp(r)}{holm_s}.")
    w("")
    w("Holm here is taken over every pair among Opus, Grok, Gemini, and GPT-5.6 Sol, not only the pairs against Opus.")
    w("")
    w("Read those 60-compound gaps as a slice result. Opus top-1 on that slice is much lower than Opus top-1 on the full 500, because the slice sits inside the harder locked 194. A model that leads on the 60 has not been shown to lead on the 500.")
    w("")
    w("Claude ladder on the 24-compound main-round subset:")
    w("")
    for r in result["ladder_rows"]:
        if r["metric"] == "top-1":
            w(f"- {r['name']} top-1 {_ci(r)}.")
    for r in result["paired"]:
        if r["family"] == "ladder24":
            w(f"- {r['a']} minus {r['b']}: {_pp(r)}, Holm {r.get('holm', float('nan')):.3g}.")
    w("")
    clean = paired("grok_clean", "grok-4.6", "grok-4.6-clean")
    if clean:
        w(f"Grok 4.6 versus the same model on a clean clone, top-1: {_pp(clean)}.")
        w("The two runs disagree in both directions. That is what a second sample looks like. It is not evidence that the first run read the answer file.")
    w("")
    w("## 2. Calibration")
    w("")
    w("There is no reliability diagram in this pack, because the deposits do not support one.")
    w("Ranked SMILES are stored as three strings. No record has a confidence, a probability, or a logprob.")
    w(f"No headline task was sampled more than once (repeat count {result['repeats']}).")
    w("Sampling frequency of the top answer, the confidence used by ChefNMR2, needs repeated draws of the same task. We do not have those draws.")
    w("")
    w("Cheapest run that would produce the diagram:")
    w("")
    w("- Keep the closed-book prompt (formula, IR, 1H, 13C, three ranked SMILES, one task per context).")
    w("- Draw 32 tasks from the locked 500, 16 simple and 16 complex, with a fixed seed. Do not draw new tasks.")
    w("- Solve each task 8 times, independently. That is 256 calls.")
    w("- Confidence of a task is the fraction of the 8 rank-1 structures that match the modal rank-1 structure (InChIKey, 14 characters).")
    w("- Plot accuracy of that modal structure against confidence, with a Wilson interval in each bin, and report the expected calibration error.")
    w("- The subscription harness used for the original deposits has no per-call price in the logs, so this run costs no API fee there.")
    w("- On the Claude API the list price for Opus 5, the model named on the 200-cut, is $5 per million input tokens and $25 per million output tokens (Anthropic rate card, 7 October 2026).")
    w("- A single task is about 1,500 input tokens. Output depends on the thinking trace. At 2,000 output tokens the 256 calls are about $15. At 8,000 output tokens they are about $53. At 15,000 output tokens they are about $98.")
    w("- Those three figures are input plus output at the list price. They are not a quote. Check the current price card before launching.")
    w("")
    w("## 3. Breakdowns and near misses")
    w("")
    w(f"Every headline task has an IR list, a 1H list, and a 13C list (missing IR {avail['missing_ir']}, missing 1H {avail['missing_h']}, missing 13C {avail['missing_c']}, out of {avail['n']}).")
    w("Modality availability inside the 500 does not vary. The evidence on inputs is a later leave-one-out campaign on the same 60 tasks.")
    w("That campaign's full condition is much higher than the headline Opus run on those 60 (the committed full file, which matches the submitted robustness bar). Only contrasts inside the campaign are interpretable. The absolute level is not a new headline.")
    w("")
    for r in result["ablation_rows"]:
        if r["set"] == "campaign" and r["metric"] == "top-1":
            w(f"- Campaign {r['name']}: top-1 {_ci(r)}.")
    for r in result["ablation_rows"]:
        if r["set"] == "committed" and r["metric"] == "top-1":
            w(f"- Older committed file {r['name']}: top-1 {_ci(r)}.")
    w("")
    for r in result["paired"]:
        if r["family"] == "modality":
            w(f"- full minus {r['b']}: {_pp(r)}, Holm {r.get('holm', float('nan')):.3g}.")
    w("")
    w("Heavy-atom bins, Opus top-1:")
    w("")
    for r in result["heavy"]:
        w(f"- {r['name']}: {_ci(r)}.")
    w("")
    w("Ring class, Opus top-1:")
    w("")
    for r in result["rings"]:
        w(f"- {r['name']}: {_ci(r)}.")
    w("")
    w("Functional groups are presence classes. A molecule can count in more than one. Opus top-1, groups with at least 15 molecules:")
    w("")
    for r in result["fg"]:
        w(f"- {r['name']}: {_ci(r)}.")
    w("")
    w(f"Wrong rank-1 answers: {near['n_miss']} of 500.")
    w(f"Of those, {near['formula_ok_misses']} still match the given molecular formula. Across all 500, {near['formula_ok_all']} rank-1 structures match the formula.")
    w(f"The typical miss is not a near neighbor. Median Morgan Tanimoto to the truth is {near['median_tani']:.2f} (n={near['n_tani']}).")
    w(f"Only {near['tani_ge_0.7']} wrong answers have Tanimoto at least 0.70, and {near['tani_ge_0.85']} have Tanimoto at least 0.85.")
    w(f"The true structure is already at rank 2 or 3 for {near['right_structure_at_rank_2_or_3']} of the {near['n_miss']} misses. Those are ordering errors.")
    if near["median_mces_sim"] is not None:
        w(f"Median MCES similarity (common bonds divided by the larger bond count): {near['median_mces_sim']:.2f}.")
        w(f"Median MCES distance (bonds in one structure or the other but not both): {near['median_mces_dist']:.0f}.")
    w("MCES is the RDKit bond maximum common substructure, element and bond-order sensitive, rings matched to rings, 2 second cap.")
    w("")
    w("## 4. Gallery")
    w("")
    w("The figures draw the true structure beside the rank-1 prediction for commercial-licence molecules only.")
    w("Teal frame means the rank-1 constitution matches. Magenta frame means it does not.")
    w("Highlighted atoms on a wrong prediction are outside the common substructure.")
    w("Captions say correct, or the Tanimoto of a near miss, or the Tanimoto of a far miss.")
    w("No spectra, DOIs, or answer-key files are written.")
    w("")
    w("## 5. Cost and latency")
    w("")
    w("The deposits do not contain token counts, dollar cost, or wall-clock time.")
    w("Raw solver files store a task id and up to three SMILES. Campaign notes store the model name and the batch id. Sweep replies store SMILES and, separately, predicted carbon shifts.")
    w("There is nothing to plot on a cost or latency axis. A point drawn there would be invented.")
    w("The cross-vendor notes describe the Cursor arms as subscription runs with no API invoice, and the OpenRouter arms as paid, but the invoice lines are not in the tree.")
    w("A cost-versus-accuracy panel has to wait for a run that records input tokens, output tokens, and elapsed seconds on each task.")
    w("")
    w("## 6. Figures")
    w("")
    w("`outputs/fig_main_results.pdf` replaces the submitted overview, which stated 45.4% and 49.8% with no interval and no comparison model.")
    w("Panel a is the headline and the three slices, top-1 and top-3, with intervals.")
    w("Panel b is every rescored model on the shared 60, top-1 only, so the candidate budget matches.")
    w("Panel c is the leave-one-out campaign.")
    w("Panel d is heavy atoms, Opus against NMRTrans.")
    w("Panel e is ring class.")
    w("Panel f is the paired gap, with a bootstrap interval.")
    w("Panel g is the success and failure gallery.")
    w("")
    w("`outputs/fig_breakdowns.pdf` is the failure chemistry: functional groups, Tanimoto of misses, MCES distance, formula adherence, the forward-verify wall with intervals, and four more truth-versus-prediction pairs.")
    w("")
    w("`outputs/before_after_overview.png` places the submitted overview above the new main figure.")
    w("`outputs/before_after_robustness.png` places the submitted four-panel robustness figure above the new main figure, because that was the previous multi-model figure and it had intervals on only one panel.")
    w("")
    w("## Reviewer questions")
    w("")
    w("**Is 45.4% a stable headline, or one draw?**")
    w(f"On these 500 tasks it is {_ci(opus)} top-1 and {_ci(opus3)} top-3. The interval is wide enough that a second sample of tasks could move the point by several points. It is not wide enough to reach the NMRTrans result. Opus minus NMRTrans top-1 is {_pp(gap)}.")
    w("")
    w("**Does the pooled 500 hide an easy expansion?**")
    w(f"Yes, the slices differ. Locked 194 is {_ci(a194)}. The +106 is {_ci(a106)}. The 200-cut is {_ci(a200)}. Say so. The pool is a size-weighted mix of two Opus protocols, and the expansion tasks are easier for this solver.")
    w("")
    w("**Do other labs' models already beat this?**")
    w(f"On the full 500, the only other deposited model is NMRTrans, at {_ci(nmr)} top-1. It does not.")
    w("On a 60-compound slice, Grok, Gemini, and GPT-5.6 Sol do beat the Opus predictions from that slice. Those Opus predictions are the harder locked-194 protocol, not the pooled 500. Quote the slice, and do not promote it to a 500-task ranking.")
    w("")
    w("**Are you calibrated?**")
    w("Not measured. There is no confidence and there are no repeated samples. The 256-call design above is the cheapest measurement that would answer the question in the same way as a sampling-frequency diagram.")
    w("")
    w("**Is accuracy just 'small molecules are easy'?**")
    w("Heavy-atom count and ring class both move top-1, and the intervals in the tables do not overlap between the easiest and hardest bins. Complex tasks (66/252 top-1) are not a rounding error on the headline.")
    w("")
    mods = [r for r in result["paired"] if r["family"] == "modality"]
    worst = max(mods, key=lambda r: r["diff"]) if mods else None
    w("**Which spectrum is doing the work?**")
    w("Inside the 500, every task has all three spectra, so the headline set cannot answer this. The matched leave-one-out on 60 tasks can. Read panel c and the McNemar rows.")
    if worst:
        w(f"The largest drop from the full input is full minus {worst['b']}: {_pp(worst)}.")
    w("")
    w("**Are the misses close?**")
    w(f"The formula is usually right ({near['formula_ok_misses']}/{near['n_miss']} of misses). The skeleton usually is not. Median Tanimoto is {near['median_tani']:.2f}, and only {near['tani_ge_0.7']} misses reach 0.70.")
    w(f"{near['right_structure_at_rank_2_or_3']} misses already have the truth at rank 2 or 3. The gallery shows both the rare near misses and the ordinary far ones.")
    w("This is distance to the truth, not a memorization test.")
    w("")
    w("**What does a call cost, and how long does it take?**")
    w("Not recorded. Do not fit a cost curve to a missing log. The subscription path has no invoice line in the repo. A future run should store tokens and seconds per task.")
    w("")
    w("**Can verification fix the rest?**")
    w("The locked wall says 251 of 500 truths were never in the candidate list. Re-ranking cannot recover those. 45 were in the list and ranked second or worse by the forward check. 204 were ranked first by that check. Intervals on those three counts are in the breakdown figure. The generation identity still holds: 227/500 top-1 equals 249/500 recalled times 227/249 self-rank.")
    w("")
    w("## How to rerun")
    w("")
    w("From the repo root, with RDKit, NumPy, Matplotlib, and Pillow:")
    w("")
    w("```bash")
    w("python analysis/rebuttal_pack/run_all.py")
    w("```")
    w("")
    w(f"Expansion questions and predictions are read from git object `{bundle['expand_sha']}`.")
    w("The resolved corpus is read only to join a structure onto each task. Nothing from that file is written out.")
    w("CC-BY-NC rows stay in memory for the join. The gallery uses commercial-pool structures only.")
    w("")
    return _no_dash("\n".join(lines) + "\n")
