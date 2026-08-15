#!/usr/bin/env python3
"""Cross-vendor sweep harness: does "recall, not verification, is the wall" hold
across model vendors (GPT, Gemini, open-weight), or is it specific to Claude?

Every headline number in the paper is single-vendor (Claude). This harness runs the
identical blind, training-free forward-verification protocol of §5 for any vendor,
so the central diagnosis can be replicated without touching the rest of the code. It
emits vendor-agnostic prompt files; you paste each vendor's raw output back as JSON;
scoring reports, per vendor, generation recall vs verification precision — the two
quantities whose gap is the claim.

The verifier is kept blind and identical across vendors: forward prediction of 13C is
done in a SEPARATE context with NO access to the observed spectrum (anonymized SMILES
only), exactly as in forward_verify.py — so a vendor cannot copy the observed peaks.

Pipeline (per vendor V):
  python scripts/cross_vendor_sweep.py prepare [subset] [n]  # -> solve batches + key
  #   n = compounds per fresh context (default 6, as in §4.4)
  #   run V on solve_prompt.md, save -> data/cross_vendor/solve_<V>.json  {mid:[smiles,...]}
  python scripts/cross_vendor_sweep.py prep-verify <V>    # -> verify_prompt_<V>.md (blind)
  #   run V on verify_prompt_<V>.md, save -> data/cross_vendor/verify_<V>.json {anon:[shifts]}
  python scripts/cross_vendor_sweep.py score              # cross-vendor decomposition

subset: fverify60 (default; the §5 set, directly comparable to Table 5) | main (n=140)
        | main24 (the Fig. 3 cross-model subset). See docs/CROSS_VENDOR.md.
"""
import json, glob, re, os, sys, random, math
from itertools import combinations
from specmetrics import chamfer, ik14

OUT = "data/cross_vendor"
K = 3                                          # candidates requested per compound
SOLVE_BATCH = 6      # compounds per fresh context; six matches the §4.4 cross-model arm.
                     # Override with `prepare <subset> <n>`: the headline run used 2-12 per
                     # context, so anything in that range stays protocol-consistent, and a
                     # reasoning model that exhausts its token budget thinking about six at
                     # once may only finish at two or three.

SUBSETS = {
    "fverify60": ["data/benchmark_v3", "data/benchmark_v2_ctrl"],
    "main":      ["data/benchmark_main"],
    "main24":    ["data/benchmark_main"],
}
MAIN24 = ['R01','R02','R04','R05','R06','R07','R08','R09','R10','R11','R12','R13',
          'R15','R16','R17','R18','R19','R20','R21','R22','R23','R24','R25','R26']

SOLVE_HEADER = """\
# Blind structure-elucidation task

You are given real experimental spectra (from the published literature) for a set of
organic molecules. For EACH compound you are given the molecular formula (from HRMS),
the IR band list, and the 1H and 13C NMR shift lists. No name, SMILES, or hint is given.

For each compound, propose the {K} most likely structures, best first, as SMILES.

Rules:
  - Use only the spectra provided. Do not use external lookups or tools.
  - Candidates must match the given molecular formula exactly.
  - Order candidates by your own confidence (most likely first).

Return ONLY a JSON object mapping each id to a list of {K} SMILES strings, e.g.:
  {{"M001": ["CCO", "COC", "..."], "M002": ["...", "...", "..."], ...}}

Compounds:

"""

VERIFY_HEADER = """\
# Forward 13C prediction task

For each candidate structure below (given as SMILES), predict its 13C NMR chemical
shift list (in ppm) from the structure alone. This is the forward direction only:
you are NOT given any observed spectrum and must not assume one.

Return ONLY a JSON object mapping each id to a list of predicted 13C shifts (numbers
in ppm), e.g.: {"P001": [21.0, 60.5, 171.2], "P002": [...], ...}

Candidates:

"""


# ----------------------------------------------------------------------------- IO
def obs_c13(c_nmr):
    """observed 13C shifts = the number before each '(' (matches forward_verify.py)."""
    return [float(x) for x in re.findall(r'(-?\d+\.?\d*)\s*\(', c_nmr or "")]


def load_rows(subset):
    """Unified loader -> list of dicts with formula/ir/h/c + held-out truth."""
    dirs = SUBSETS[subset]
    rows = []
    for d in dirs:
        q = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/questions2.jsonl")}
        a = {json.loads(l)["qid"]: json.loads(l) for l in open(f"{d}/answers2.jsonl")}
        for qid, ans in a.items():
            if subset == "main24" and qid not in MAIN24:
                continue
            qq = q.get(qid)
            if not qq:
                continue
            rows.append(dict(
                src=f"{d.split('/')[-1]}:{qid}", difficulty=ans.get("difficulty", "?"),
                formula=qq["formula"], ir=qq.get("ir_bands_cm-1"),
                h=qq.get("h_nmr"), c=qq.get("c_nmr"),
                true_smiles=ans["smiles"], true_ik=ans["inchikey"][:14],
                obs_c13=obs_c13(qq.get("c_nmr"))))
    rows.sort(key=lambda r: (r["difficulty"], r["src"]))
    for i, r in enumerate(rows, 1):
        r["mid"] = f"M{i:03d}"
    return rows


# ------------------------------------------------------------------------- stages
def prepare(subset="fverify60", batch=SOLVE_BATCH):
    if subset not in SUBSETS:
        sys.exit(f"unknown subset {subset!r}; choose from {list(SUBSETS)}")
    rows = load_rows(subset)
    os.makedirs(OUT, exist_ok=True)
    blocks = []
    for r in rows:
        b = [f"### {r['mid']}", f"Molecular formula: {r['formula']}"]
        if r["ir"]: b.append(f"IR bands (cm-1): {r['ir']}")
        if r["h"]:  b.append(f"1H NMR: {r['h']}")
        if r["c"]:  b.append(f"13C NMR: {r['c']}")
        blocks.append("\n".join(b))
    # One file per batch, not one file for the run. Context packing is not a detail
    # here: §4.3 measures the same 20 compounds at 5% top-1 in a single long context
    # against 15% in bounded, reset contexts. A vendor handed all 60 at once is being
    # run under the arm that depresses accuracy, and would look weaker than Claude for
    # a reason that has nothing to do with the model. Six per context matches the §4.4
    # cross-model protocol, which is the comparison this sweep is an extension of.
    os.makedirs(f"{OUT}/solve_batches", exist_ok=True)
    for old in glob.glob(f"{OUT}/solve_batches/solve_*.md"):
        os.remove(old)
    nb = (len(blocks) + batch - 1) // batch
    for i in range(nb):
        chunk = blocks[i * batch:(i + 1) * batch]
        open(f"{OUT}/solve_batches/solve_{i+1:02d}.md", "w").write(
            SOLVE_HEADER.format(K=K) + "\n\n".join(chunk) + "\n")
    open(f"{OUT}/solve_prompt.md", "w").write(
        f"""# DO NOT RUN THIS FILE AS ONE PROMPT

It holds all {len(blocks)} compounds so you can read the set in one place. Running it as a
single prompt puts the vendor in the long-context arm that §4.3 measures at 5% top-1
against 15% for bounded contexts, so the result would not be comparable to Claude's.

Run `{OUT}/solve_batches/solve_01.md` … `solve_{nb:02d}.md` instead — {batch} compounds each,
**a fresh context per file**, no history carried between them. Merge the {nb} JSON replies
into one object and save it as {OUT}/solve_<vendor>.json.

---

""" + SOLVE_HEADER.format(K=K) + "\n\n".join(blocks) + "\n")
    # held-out key (never shown to any vendor)
    key = {r["mid"]: {k: r[k] for k in
                      ("src", "difficulty", "true_smiles", "true_ik", "obs_c13")}
           for r in rows}
    json.dump({"subset": subset, "k": K, "key": key}, open(f"{OUT}/key.json", "w"))
    json.dump({r["mid"]: [] for r in rows}, open(f"{OUT}/template_out.json", "w"), indent=0)
    print(f"subset {subset}: {len(rows)} compounds -> {OUT}/solve_prompt.md")
    print(f"held-out answer key -> {OUT}/key.json   (do NOT show to the model)")
    print(f"per-vendor template -> {OUT}/template_out.json")
    print(f"batched solve prompts -> {OUT}/solve_batches/solve_01..{nb:02d}.md "
          f"({batch} compounds each)")
    print("\nNext, for each vendor V:")
    print(f"  1. run V on each {OUT}/solve_batches/solve_NN.md in a FRESH context "
          f"(never all {len(blocks)} at once — see §4.3), merge the replies,")
    print(f"     save -> {OUT}/solve_<V>.json")
    print(f"  2. python scripts/cross_vendor_sweep.py prep-verify <V>")
    print(f"  3. run V on {OUT}/verify_prompt_<V>.md, save -> {OUT}/verify_<V>.json")
    print(f"  4. python scripts/cross_vendor_sweep.py score")


def _formula(smi):
    """Molecular formula of a SMILES, or None if it does not parse."""
    from rdkit import Chem
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula
    m = Chem.MolFromSmiles(smi) if smi else None
    return CalcMolFormula(m) if m else None


def _canon(smi):
    from rdkit import Chem
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None


def prep_verify(vendor, batch=17):
    """Build a blind forward-prediction prompt for THIS vendor's own candidates."""
    sp = f"{OUT}/solve_{vendor}.json"
    if not os.path.exists(sp):
        sys.exit(f"missing {sp} (run the vendor on solve_prompt.md first)")
    solve = json.load(open(sp))
    uniq = sorted({c for cands in solve.values() for c in
                   (_canon(s) for s in (cands or [])[:K]) if c})
    random.seed(5); random.shuffle(uniq)
    amap = {s: f"P{i:03d}" for i, s in enumerate(uniq)}
    json.dump(amap, open(f"{OUT}/anon_{vendor}.json", "w"))
    lines = [f"{amap[s]}  {s}" for s in uniq]
    body = "\n".join(f"## batch {i//batch + 1}\n" + "\n".join(lines[i:i+batch])
                     for i in range(0, len(lines), batch))
    open(f"{OUT}/verify_prompt_{vendor}.md", "w").write(VERIFY_HEADER + body + "\n")
    print(f"{vendor}: {len(uniq)} unique candidate SMILES to forward-predict "
          f"-> {OUT}/verify_prompt_{vendor}.md")
    print(f"  run {vendor} on it, save predicted 13C -> {OUT}/verify_{vendor}.json")


# --------------------------------------------------------------------- statistics
def _boot(vec, B=10000, seed=0):
    rng = random.Random(seed); n = len(vec)
    if n == 0:
        return (0.0, 0.0, 0.0)
    bs = sorted(sum(vec[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return (sum(vec) / n, bs[int(.025 * B)], bs[int(.975 * B)])


def _mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def score():
    meta = json.load(open(f"{OUT}/key.json"))
    key = meta["key"]
    vendors = sorted(os.path.basename(f)[6:-5]
                     for f in glob.glob(f"{OUT}/solve_*.json"))
    if not vendors:
        sys.exit("no solve_<vendor>.json found; run a vendor first.")
    print(f"subset {meta['subset']}  ({len(key)} compounds)  k={meta['k']}\n")
    print(f"{'vendor':<10}{'recall':>9}{'top1self':>10}{'top1ver':>9}"
          f"{'prec|rec':>10}{'  recall vs precision':>24}")
    rec_recall = {}                                  # vendor -> recall vector (for CIs)
    for V in vendors:
        solve = json.load(open(f"{OUT}/solve_{V}.json"))
        vp = f"{OUT}/verify_{V}.json"; amp = f"{OUT}/anon_{V}.json"
        pred = json.load(open(vp)) if os.path.exists(vp) else {}
        amap = json.load(open(amp)) if os.path.exists(amp) else {}
        recall, self1, ver1, condn, cond_ver = [], [], [], 0, 0
        n_raw = n_parse = n_formula = 0          # output-contract adherence
        for mid, info in key.items():
            tik = info["true_ik"]; obs = info["obs_c13"]
            raw = (solve.get(mid) or [])[:meta["k"]]
            n_raw += len(raw)
            cands = [_canon(s) for s in raw]
            cands = [c for c in cands if c]
            n_parse += len(cands)
            n_formula += sum(1 for c in cands if _formula(c) == _formula(info["true_smiles"]))
            iks = [ik14(c) for c in cands]
            has = tik in iks
            recall.append(int(has))
            self1.append(int(bool(iks) and iks[0] == tik))
            if pred and cands:                       # forward-verified re-rank
                dist = [chamfer(pred.get(amap.get(c)), obs) for c in cands]
                best = iks[min(range(len(cands)), key=lambda i: dist[i])]
                ver1.append(int(best == tik))
                if has:
                    condn += 1; cond_ver += int(best == tik)
        n = len(recall)
        r_mean, r_lo, r_hi = _boot(recall)
        rec_recall[V] = recall
        prec = cond_ver / condn if condn else float("nan")
        v1 = sum(ver1) / n if ver1 else float("nan")
        gap = (prec - r_mean) if ver1 else float("nan")
        flag = ""
        if ver1:
            flag = (f"{'recall<prec' if prec > r_mean else 'recall>=prec':>13}"
                    f"  {100*gap:+.0f}pt")
        print(f"{V:<10}{r_mean:>8.0%}{sum(self1)/n:>10.0%}"
              f"{v1:>9.0%}".replace('nan%', '  n/a') +
              (f"{prec:>10.0%}" if condn else f"{'n/a':>10}") +
              f"{flag:>24}")
        # Three distinct states used to collapse into one misleading footer. A vendor
        # whose recall is zero has nothing to condition precision on, and telling its
        # operator to go run a verify stage they already ran sends them chasing a file
        # that is sitting on disk. And a partly-collected arm scores its unanswered
        # compounds as misses, which is the right default but reads as a measured recall
        # unless the coverage is printed beside it.
        answered = sum(1 for mid in key if solve.get(mid))
        note = (f"; verification precision {cond_ver}/{condn}" if condn else
                "; no recall-positive compounds, so precision is undefined" if pred else
                "; no verify_*.json yet -> recall + self-rank only")
        if answered < len(key):
            note += (f"; NOTE only {answered}/{len(key)} compounds answered — the other "
                     f"{len(key)-answered} score as misses, so recall is a lower bound")
        print(f"{'':12}recall 95% CI [{100*r_lo:.0f}, {100*r_hi:.0f}]" + note)
        # A vendor is only being measured on elucidation once it can return a parseable
        # SMILES of the composition it was handed. Below that, a zero recall is a
        # statement about instruction-following, and reading it as chemistry is the
        # easiest mistake this table invites: the first pilot model returned 180
        # candidates of which 2% carried the right formula and scored 0/60.
        if n_raw:
            adh = 100 * n_formula / n_raw
            warn = "   <-- too low to interpret recall" if adh < 50 else ""
            print(f"{'':12}output contract: {100*n_parse/n_raw:.0f}% parse, "
                  f"{adh:.0f}% match the given formula "
                  f"(Claude 78-95%, §3){warn}")
    # cross-vendor recall comparison (the portable claim is about recall)
    if len(rec_recall) > 1:
        print("\nPairwise recall difference (McNemar exact, paired compounds):")
        for a, b in combinations(sorted(rec_recall), 2):
            va, vb = rec_recall[a], rec_recall[b]
            bcell = sum(x and not y for x, y in zip(va, vb))
            ccell = sum(y and not x for x, y in zip(va, vb))
            print(f"  {a:8} vs {b:8}  b={bcell} c={ccell}  p={_mcnemar(bcell, ccell):.4f}")
    print("\nClaim replicates for a vendor iff verification precision (prec|rec) "
          "exceeds generation recall.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if cmd == "prepare":
        prepare(sys.argv[2] if len(sys.argv) > 2 else "fverify60",
                int(sys.argv[3]) if len(sys.argv) > 3 else SOLVE_BATCH)
    elif cmd == "prep-verify":
        prep_verify(sys.argv[2])
    elif cmd == "score":
        score()
    else:
        print(__doc__)
