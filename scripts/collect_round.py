#!/usr/bin/env python3
"""Assemble one blind round's solver replies into predictions2.jsonl.

Counterpart to scripts/export_round.py. That script cuts a drawn round into
batches outside the repository and withholds the key; this one takes the batch
replies back and lays them down in the deposit format the scorer reads.

Replies are accepted in either shape -- the mapping a solver naturally returns

    {"R01": ["SMILES", ...], "R02": [...]}

or the deposited list form

    [{"qid": "R01", "candidates": ["SMILES", ...]}, ...]

and are normalised to the list form in <round>/raw/, one file per batch, so the
round can be rescored from the released replies alone.

Candidates are written through VERBATIM. An unparseable or wrong-formula
candidate is a real solver failure and scores as a miss; silently repairing or
dropping it would flatter the model. They are counted and reported instead.

    python scripts/collect_round.py data/benchmark_expand /tmp/blind/replies
"""
import argparse, glob, json, os, sys
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors
RDLogger.DisableLog("rdApp.*")


def normalise(payload, src):
    """Return [(qid, [smiles, ...]), ...] from either accepted reply shape."""
    if isinstance(payload, dict):
        items = payload.items()
    elif isinstance(payload, list):
        items = [(r["qid"], r.get("candidates", [])) for r in payload]
    else:
        sys.exit(f"{src}: expected a JSON object or list, got {type(payload).__name__}")
    out = []
    for qid, cands in items:
        if isinstance(cands, str):          # a lone SMILES rather than a list
            cands = [cands]
        out.append((str(qid), [str(c) for c in cands if c]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round", help="round directory, e.g. data/benchmark_expand")
    ap.add_argument("replies", help="directory of per-batch JSON replies")
    ap.add_argument("--limit", type=int, default=3, help="candidates kept per compound")
    ap.add_argument("--partial", action="store_true",
                    help="deposit an unfinished round instead of failing on it. For "
                         "banking replies mid-run; a round scored while partial would "
                         "count the unanswered compounds as misses.")
    a = ap.parse_args()

    qfile = os.path.join(a.round, "questions2.jsonl")
    qs = {json.loads(l)["qid"]: json.loads(l) for l in open(qfile)}

    preds, seen_in = {}, {}
    files = sorted(glob.glob(os.path.join(a.replies, "*.json")))
    if not files:
        sys.exit(f"no *.json replies under {a.replies}")
    raw = os.path.join(a.round, "raw")
    os.makedirs(raw, exist_ok=True)
    for f in files:
        batch = normalise(json.load(open(f)), f)
        for qid, cands in batch:
            if qid not in qs:
                sys.exit(f"{f}: qid {qid} is not in {qfile}")
            if qid in preds:
                sys.exit(f"qid {qid} answered twice: {seen_in[qid]} and {f}")
            preds[qid], seen_in[qid] = cands[:a.limit], f
        # deposit the batch in the released shape, so the round rescores from raw/
        name = os.path.splitext(os.path.basename(f))[0]
        with open(os.path.join(raw, f"{name}.json"), "w") as fh:
            json.dump([{"qid": q, "candidates": preds[q]} for q, _ in batch], fh)

    missing = sorted(set(qs) - set(preds))
    bad_parse, bad_formula, empty = [], [], []
    for qid, cands in preds.items():
        if not cands:
            empty.append(qid)
        for smi in cands:
            m = Chem.MolFromSmiles(smi)
            if m is None:
                bad_parse.append((qid, smi))
            elif rdMolDescriptors.CalcMolFormula(m) != qs[qid]["formula"]:
                bad_formula.append((qid, smi, rdMolDescriptors.CalcMolFormula(m),
                                    qs[qid]["formula"]))

    # predictions2.jsonl is the scoreable artefact, so it is only written for a complete
    # round: a partial one left lying around scores every unanswered compound as a miss,
    # which looks like a result rather than an unfinished run. The per-batch deposit under
    # raw/ is written either way, and is what banks replies mid-run.
    out = os.path.join(a.round, "predictions2.jsonl")
    ncand = sum(len(c) for c in preds.values())
    if missing:
        print(f"{len(files)} batch file(s) -> {len(preds)}/{len(qs)} compounds, "
              f"{ncand} candidates -> {raw}/ (no predictions2.jsonl yet)")
    else:
        with open(out, "w") as fh:
            for qid in sorted(preds):
                fh.write(json.dumps({"qid": qid, "candidates": preds[qid]},
                                    ensure_ascii=False) + "\n")
        print(f"{len(files)} batch file(s) -> {len(preds)}/{len(qs)} compounds, "
              f"{ncand} candidates -> {out}")
    if empty:
        print(f"  {len(empty)} compound(s) with no candidate: {', '.join(empty)}")
    if bad_parse:
        print(f"  {len(bad_parse)} unparseable candidate(s) (kept, scored as misses):")
        for qid, smi in bad_parse[:6]:
            print(f"    {qid}: {smi[:60]}")
    if bad_formula:
        print(f"  {len(bad_formula)} candidate(s) off the given formula "
              f"(kept, scored on structure):")
        for qid, smi, got, want in bad_formula[:6]:
            print(f"    {qid}: {got} != {want}  {smi[:48]}")
    if missing:
        msg = (f"{len(missing)} compound(s) not yet answered: "
               + ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else ""))
        if not a.partial:
            sys.exit(f"\nINCOMPLETE -- {msg}\n"
                     f"Re-run with --partial to bank what has come back so far; the "
                     f"round is not scoreable until every compound has a response.")
        print(f"  PARTIAL -- {msg}")


if __name__ == "__main__":
    main()
