#!/usr/bin/env python3
"""Score the completed expert-audit sheets into Table A and Table B.

Consumes the response JSONs exported by `data/audit/worksheet.html` (one per
reviewer, committed under `data/audit/responses/`) and the held-out answer key,
and emits the two tables the protocol promises. Scoring is mechanical: no model
is consulted here, and nothing in this script can change a reviewer's answer.

  python3 scripts/score_audit.py [--responses data/audit/responses] [--json out.json]

The key is git-ignored. If it is absent, regenerate it deterministically:

  python3 scripts/make_audit_sample.py     # seed=0, rewrites sample + key

Table A (Task 1, validates §4)
  mean consistency, verdict distribution, Fleiss' kappa, human verdict against the
  mechanical InChIKey score, and the load-bearing read-out -- of the top-1s the
  string match calls wrong, what fraction a chemist judges a spectrally consistent
  regioisomer.

Table B (Task 2, validates §5)
  human top-1 against the LLM forward-verifier and the HOSE predictor on identical
  candidate sets. Task-2 sets holding a single candidate are reported separately:
  there is nothing to rank, so they carry no concordance information.
"""
import argparse, glob, json, os, re, sys
from collections import Counter, defaultdict

AUDIT = "data/audit"
VERDICTS = ["correct", "wrong-regiochemistry", "wrong-scaffold", "uninterpretable"]


# ---------------------------------------------------------------- loading

def load_key(path=f"{AUDIT}/key.jsonl"):
    if not os.path.exists(path):
        sys.exit(f"missing {path}\n"
                 f"  the answer key is git-ignored by design; regenerate it with:\n"
                 f"    python3 scripts/make_audit_sample.py")
    return {r["audit_id"]: r for r in map(json.loads, open(path))}


def load_sample(path=f"{AUDIT}/sample.jsonl"):
    return {r["audit_id"]: r for r in map(json.loads, open(path))}


def load_responses(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        r = json.load(open(f))
        if r.get("schema") != "spectro-audit-response/1":
            print(f"  ! {os.path.basename(f)}: unknown schema {r.get('schema')!r}, skipped")
            continue
        r["_file"] = os.path.basename(f)
        out.append(r)
    return out


# ---------------------------------------------------------------- statistics

def fleiss_kappa(table):
    """table: list of per-item category counts, all rows summing to the same n."""
    table = [row for row in table if sum(row) > 1]
    if len(table) < 2:
        return None
    n = sum(table[0])
    if any(sum(row) != n for row in table):
        return None                      # unequal raters per item; kappa undefined
    N, k = len(table), len(table[0])
    P_i = [(sum(x * x for x in row) - n) / (n * (n - 1)) for row in table]
    p_j = [sum(row[j] for row in table) / (N * n) for j in range(k)]
    P_bar, P_e = sum(P_i) / N, sum(p * p for p in p_j)
    return None if P_e >= 1 else (P_bar - P_e) / (1 - P_e)


def pct(a, b):
    return f"{a}/{b} ({round(100 * a / b)}%)" if b else f"{a}/0 (n/a)"


# ---------------------------------------------------------------- machine verifiers

def chamfer(pred, obs):
    """Kept byte-identical to forward_verify.chamfer -- duplicated rather than
    imported so this scorer runs without rdkit (that module imports Chem at load)."""
    if not pred or not obs: return 999.0
    a = sum(min(abs(p - o) for o in obs) for p in pred) / len(pred)
    b = sum(min(abs(o - p) for p in pred) for o in obs) / len(obs)
    return (a + b) / 2


def machine_picks(key):
    """Per audit compound, which candidate label the LLM forward-verifier and the
    HOSE predictor choose. Reuses the §5 scoring path so the numbers are the same
    ones the paper reports, not a reimplementation."""
    sys.path.insert(0, "scripts")
    cands = [json.loads(l) for l in open("data/fverify/candidates.jsonl")]
    by_comp = defaultdict(list)
    for c in cands:
        by_comp[f'{c["dir"]}:{c["qid"]}'].append(c)

    amap = json.load(open("data/fverify/anon_map.json"))
    pred = {}
    for f in glob.glob("data/fverify/raw/*.json"):
        pred.update(json.load(open(f)))

    try:
        from hose_predict import predict_c13, _load
        _load()
        hose_ok = True
    except Exception:
        hose_ok = False

    llm, hose = {}, {}
    for aid, k in key.items():
        group = by_comp.get(k["source"])
        if not group or not k.get("candidates"):
            continue                     # not recall-positive: no labelled set exists
        label = {c["smiles"]: c["label"] for c in (k["candidates"] or [])}
        obs = group[0]["obs_c13"]

        best, bd = None, 1e9
        for c in group:
            d = chamfer(pred.get(amap.get(c["smiles"])), obs)
            if d < bd:
                bd, best = d, c
        if best and best["smiles"] in label:
            llm[aid] = label[best["smiles"]]

        if hose_ok:
            best, bd = None, 1e9
            for c in group:
                try:
                    d = chamfer(predict_c13(c["smiles"]), obs)
                except Exception:
                    continue
                if d < bd:
                    bd, best = d, c
            if best and best["smiles"] in label:
                hose[aid] = label[best["smiles"]]

    if not llm:
        print("  ! no LLM forward-verify picks resolved "
              "(data/fverify raw predictions missing or unmatched)")
    if not hose_ok:
        print("  ! HOSE model not built; its column is omitted "
              "(build with: python3 scripts/hose_predict.py build)")
    return llm, hose


# ---------------------------------------------------------------- tables

def table_a(resp, key, out):
    print("\n" + "=" * 74)
    print("TABLE A  -- human audit of top-1 elucidations (Task 1)")
    print("=" * 74)

    cons, verd = defaultdict(list), defaultdict(list)
    for r in resp:
        for aid, a in r["responses"].items():
            if "task1" not in a:
                continue
            cons[aid].append(a["task1"]["consistency"])
            verd[aid].append(a["task1"]["verdict"])

    if not verd:
        print("  no Task-1 answers yet")
        return

    flat = [v for vs in verd.values() for v in vs]
    allc = [c for cs in cons.values() for c in cs]
    print(f"\n  compounds scored : {len(verd)}")
    print(f"  reviewers        : {len(resp)}  ({', '.join(r['reviewer'] for r in resp)})")
    print(f"  mean consistency : {sum(allc)/len(allc):.2f}  (n={len(allc)} judgements)")

    print("\n  verdict distribution")
    dist = Counter(flat)
    for v in VERDICTS:
        print(f"    {v:<24} {pct(dist.get(v, 0), len(flat))}")

    k = fleiss_kappa([[Counter(vs).get(v, 0) for v in VERDICTS] for vs in verd.values()])
    print(f"\n  Fleiss' kappa on verdict : "
          + (f"{k:.3f}" if k is not None
             else "n/a (needs >=2 reviewers on the same compounds)"))

    # The load-bearing read-out: what the mechanical score calls a miss, a chemist
    # may call a spectrally consistent regioisomer. That is the §4 claim.
    miss_verd, hit_verd, agree, n_cmp = [], [], 0, 0
    for aid, vs in verd.items():
        if aid not in key:
            continue
        correct = key[aid]["top1_correct"]
        (hit_verd if correct else miss_verd).extend(vs)
        for v in vs:
            n_cmp += 1
            agree += (v == "correct") == correct

    print(f"\n  human verdict vs mechanical InChIKey score : {pct(agree, n_cmp)} agree")
    if miss_verd:
        d = Counter(miss_verd)
        regio = d.get("wrong-regiochemistry", 0)
        print(f"\n  of the {len(miss_verd)} judgements on mechanically-WRONG top-1s:")
        for v in VERDICTS:
            print(f"    {v:<24} {pct(d.get(v, 0), len(miss_verd))}")
        print(f"\n  >> misses judged a consistent regioisomer : {pct(regio, len(miss_verd))}")
        print("     (this is the number that substantiates the regiochemistry bottleneck)")
    if hit_verd:
        d = Counter(hit_verd)
        print(f"\n  of the {len(hit_verd)} judgements on mechanically-CORRECT top-1s: "
              f"{pct(d.get('correct', 0), len(hit_verd))} judged correct")

    out["table_a"] = {
        "compounds_scored": len(verd), "reviewers": len(resp),
        "mean_consistency": round(sum(allc) / len(allc), 3),
        "verdict_distribution": dict(dist), "fleiss_kappa": k,
        "human_vs_mechanical_agreement": [agree, n_cmp],
        "miss_verdicts": dict(Counter(miss_verd)),
    }


def table_b(resp, key, sample, out):
    print("\n" + "=" * 74)
    print("TABLE B  -- verifier concordance on recall-positive compounds (Task 2)")
    print("=" * 74)

    picks = defaultdict(list)                      # aid -> [reviewer top pick]
    conf = defaultdict(list)
    for r in resp:
        for aid, a in r["responses"].items():
            if "task2" in a and a["task2"].get("ranking"):
                picks[aid].append(a["task2"]["ranking"][0])
                conf[aid].append(a["task2"]["confidence"])

    if not picks:
        print("  no Task-2 answers yet")
        return

    degenerate = {aid for aid, s in sample.items()
                  if s["task2_applicable"] and s["n_candidates"] < 2}
    scored = {a: p for a, p in picks.items() if a not in degenerate}

    llm, hose = machine_picks(key)

    hdr = f"\n  {'id':<5} {'cands':>5}  {'human':<8} {'llm-fwd':<8} {'hose':<6} {'true':<5} conf"
    print(hdr)
    print("  " + "-" * (len(hdr) - 4))
    h_ok = l_ok = s_ok = n = 0
    for aid in sorted(scored):
        k, s = key[aid], sample[aid]
        true = k["true_candidate_label"]
        hp = Counter(scored[aid]).most_common(1)[0][0]      # majority reviewer pick
        lp, sp = llm.get(aid, "-"), hose.get(aid, "-")
        n += 1
        h_ok += hp == true
        l_ok += lp == true
        s_ok += sp == true
        c = sum(conf[aid]) / len(conf[aid])
        print(f"  {aid:<5} {s['n_candidates']:>5}  {hp:<8} {lp:<8} {sp:<6} {true:<5} {c:.1f}")

    na = "not run"
    print(f"\n  compounds with a real choice : {n}")
    print(f"    human (majority pick) correct : {pct(h_ok, n)}")
    print(f"    LLM forward-verify correct    : {pct(l_ok, n) if llm else na}")
    print(f"    HOSE re-rank correct          : {pct(s_ok, n) if hose else na}")
    if llm:
        agree = sum(1 for aid in scored
                    if llm.get(aid) == Counter(scored[aid]).most_common(1)[0][0])
        print(f"    human/LLM agreement           : {pct(agree, n)}")

    answered_deg = degenerate & picks.keys()
    if answered_deg:
        print(f"\n  excluded, single-candidate Task-2 sets : {', '.join(sorted(answered_deg))}")
        print("    Nothing to rank, so they carry no concordance information. They also")
        print("    self-disclose: Task 2 appears only on recall-positive compounds, so a")
        print("    lone candidate is necessarily the true structure -- which also reveals")
        print("    the compound's Task-1 answer. Treat their Task 1 as unblinded.")

    out["table_b"] = {
        "n_with_choice": n, "human_correct": h_ok,
        "llm_correct": l_ok if llm else None,
        "hose_correct": s_ok if hose else None,
        "excluded_single_candidate": sorted(degenerate),
    }


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", default=f"{AUDIT}/responses")
    ap.add_argument("--sample", default=f"{AUDIT}/sample.jsonl")
    ap.add_argument("--key", default=f"{AUDIT}/key.jsonl")
    ap.add_argument("--json", help="also write the read-outs here")
    a = ap.parse_args()

    sample, key = load_sample(a.sample), load_key(a.key)
    resp = load_responses(a.responses)
    if not resp:
        sys.exit(f"no response files in {a.responses}/\n"
                 f"  fill in data/audit/worksheet.html and export one JSON per reviewer")

    digest = __import__("hashlib").sha256(open(a.sample, "rb").read()).hexdigest()
    for r in resp:
        if r.get("sample_sha256") not in (None, digest):
            print(f"  ! {r['_file']}: scored a DIFFERENT sample.jsonl "
                  f"({r['sample_sha256'][:12]}... vs {digest[:12]}...)")

    n1 = len(sample)
    n2 = sum(s["task2_applicable"] for s in sample.values())
    print(f"loaded {len(resp)} response file(s) from {a.responses}/")
    for r in resp:
        t1 = sum("task1" in v for v in r["responses"].values())
        t2 = sum("task2" in v for v in r["responses"].values())
        print(f"  {r['_file']:<28} {r['reviewer']:<16} "
              f"Task 1 {t1}/{n1}, Task 2 {t2}/{n2}")

    out = {}
    table_a(resp, key, out)
    table_b(resp, key, sample, out)

    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    sys.exit(main())
