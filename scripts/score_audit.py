#!/usr/bin/env python3
"""
Score the completed expert-audit sheets. The protocol promised this and nothing did it.

`docs/EXPERT_AUDIT_PROTOCOL.md` states that scoring is mechanical with no further model
involvement -- but `scripts/` held only the sample generator and an unrelated
IR-transcription audit, so three reviewers had no defined way to submit and no code to
score them. This is that code, and the format it reads is the format the protocol needs.

  python scripts/score_audit.py data/audit/responses/*.tsv

INPUT — one tab-separated file per reviewer, first line a header, one row per compound:

  audit_id  task1_verdict  task1_confidence  task2_ranking  task2_confidence
  A01       consistent     4                 -              -
  A09       inconsistent   5                 B,A,C          3

  task1_verdict     consistent | inconsistent | unsure
  task1_confidence  1-5
  task2_ranking     candidate letters, best first, comma-separated; "-" where Task 2
                    does not apply (the sheet simply has no Task 2 block there)
  task2_confidence  1-5, or "-"

Reviewer identity is the filename stem. Rows for compounds outside the frozen sample, and
Task-2 rankings on compounds where Task 2 does not apply, are reported rather than
silently dropped -- a sheet filled against the wrong version of the kit should be visible.

WHAT IT REPORTS

Task 1 asks whether the model's proposed structure is consistent with the spectra. Two
things matter: whether the reviewers agree with each other (Fleiss' kappa, which corrects
for the agreement you would get by chance from the marginals alone), and how their
majority verdict lines up with the mechanical InChIKey scoring the paper uses. The second
is the one §4 rests on -- a "consistent" verdict on a structure the scorer counted wrong
means the miss was chemically defensible, and that is exactly what an expert can settle
and RDKit cannot.

Task 2 asks the reviewer to rank the candidate set. The paper's claim is that forward
verification picks the true structure 84% of the time it is present; the audit asks
whether an expert, given the same candidates and the same spectra, does better or worse.
"""
import glob, json, os, sys
from collections import Counter, defaultdict

SAMPLE = "data/audit/sample.jsonl"
KEY = "data/audit/key.jsonl"
VERDICTS = ("consistent", "inconsistent", "unsure")


def fleiss_kappa(table):
    """table: {item: Counter(category)} with the same number of raters per item."""
    items = [c for c in table.values() if sum(c.values()) > 1]
    if not items:
        return None, 0
    n = sum(items[0].values())
    if any(sum(c.values()) != n for c in items):
        return None, len(items)          # unequal rater counts: kappa is not defined
    N, cats = len(items), VERDICTS
    p_j = {c: sum(it[c] for it in items) / (N * n) for c in cats}
    P_i = [(sum(it[c] ** 2 for c in cats) - n) / (n * (n - 1)) for it in items]
    P_bar, Pe = sum(P_i) / N, sum(v * v for v in p_j.values())
    return ((P_bar - Pe) / (1 - Pe) if Pe < 1 else 1.0), N


def load(paths):
    out = {}
    for p in paths:
        who = os.path.splitext(os.path.basename(p))[0]
        rows = {}
        with open(p, encoding="utf-8") as f:
            head = f.readline()
            if "audit_id" not in head:
                sys.exit(f"{p}: first line must be a header containing audit_id")
            for ln in f:
                if not ln.strip():
                    continue
                parts = [x.strip() for x in ln.rstrip("\n").split("\t")]
                parts += ["-"] * (5 - len(parts))
                aid, v, c1, rank, c2 = parts[:5]
                rows[aid] = dict(verdict=v.lower(), conf1=c1,
                                 rank=[x.strip() for x in rank.split(",") if x.strip()
                                       and rank != "-"], conf2=c2)
        out[who] = rows
    return out


def main(paths):
    if not paths:
        sys.exit(__doc__)
    blind = {json.loads(l)["audit_id"]: json.loads(l) for l in open(SAMPLE)}
    if not os.path.exists(KEY):
        sys.exit(f"{KEY} not found — regenerate with scripts/make_audit_sample.py")
    key = {json.loads(l)["audit_id"]: json.loads(l) for l in open(KEY)}
    R = load(paths)
    print(f"reviewers: {', '.join(sorted(R))}   compounds in sample: {len(blind)}\n")

    # ---- integrity of the submissions themselves ----------------------------
    problems = []
    for who, rows in R.items():
        for aid, r in rows.items():
            if aid not in blind:
                problems.append(f"{who}: {aid} is not in the frozen sample")
                continue
            if r["verdict"] not in VERDICTS and r["verdict"] != "-":
                problems.append(f"{who}: {aid} verdict {r['verdict']!r} not one of {VERDICTS}")
            t2 = blind[aid]["task2_applicable"]
            if r["rank"] and not t2:
                problems.append(f"{who}: {aid} has a Task-2 ranking but Task 2 does not "
                                f"apply — sheet may be from an older kit")
            if t2 and not r["rank"]:
                problems.append(f"{who}: {aid} Task 2 applies but no ranking given")
        missing = sorted(set(blind) - set(rows))
        if missing:
            problems.append(f"{who}: {len(missing)} compound(s) unanswered "
                            f"({', '.join(missing[:6])}{' …' if len(missing) > 6 else ''})")
    for p in problems:
        print(f"  !! {p}")
    print()

    # ---- Task 1: agreement, and agreement with the mechanical scorer --------
    table = defaultdict(Counter)
    for who, rows in R.items():
        for aid, r in rows.items():
            if aid in blind and r["verdict"] in VERDICTS:
                table[aid][r["verdict"]] += 1
    k, n_used = fleiss_kappa(table)
    print("TASK 1 — is the model's structure consistent with the spectra?")
    print(f"  compounds with a full set of verdicts: {n_used}")
    print(f"  Fleiss' kappa: {k:.3f}" if k is not None else
          "  Fleiss' kappa: not defined (reviewers rated different numbers of compounds)")

    agree = disagree = 0
    defensible = []
    for aid, c in table.items():
        maj, cnt = c.most_common(1)[0]
        if cnt * 2 <= sum(c.values()):
            continue                                  # no majority: not counted either way
        mech = key[aid]["top1_correct"]
        if (maj == "consistent") == bool(mech):
            agree += 1
        else:
            disagree += 1
            if maj == "consistent" and not mech:
                defensible.append(aid)
    tot = agree + disagree
    if tot:
        print(f"  majority verdict vs mechanical InChIKey scoring: {agree}/{tot} agree "
              f"({100*agree/tot:.0f}%)")
    if defensible:
        print(f"  {len(defensible)} structure(s) the scorer counted WRONG that the panel "
              f"calls consistent: {', '.join(defensible)}")
        print(f"    → these are the chemically defensible misses §4 cannot see; "
              f"they bound how much of the miss rate is scoring strictness")

    # ---- Task 2: expert ranking against truth and against the verifier ------
    t2ids = [a for a in blind if blind[a]["task2_applicable"]]
    print(f"\nTASK 2 — rank the candidates ({len(t2ids)} compounds with a real choice)")
    hit = tot2 = 0
    per = Counter()
    for aid in t2ids:
        true_lbl = key[aid].get("true_candidate_label")
        picks = [r["rank"][0] for r in (R[w].get(aid, {"rank": []}) for w in R) if r["rank"]]
        if not picks:
            continue
        tot2 += 1
        top, cnt = Counter(picks).most_common(1)[0]
        if cnt * 2 > len(picks) and top == true_lbl:
            hit += 1
        for w in R:
            rr = R[w].get(aid)
            if rr and rr["rank"]:
                per[w] += int(rr["rank"][0] == true_lbl)
    if tot2:
        print(f"  panel majority picks the true structure: {hit}/{tot2} "
              f"({100*hit/tot2:.0f}%)")
        for w in sorted(per):
            n = sum(1 for a in t2ids if R[w].get(a, {}).get("rank"))
            print(f"    {w}: {per[w]}/{n}")
        print("  compare against forward verification on the full arm: 16/19 (84%), §5.2")
    if tot2 and tot2 < 8:
        print(f"  NOTE n={tot2} is small. The full forward-verify set has 19 "
              f"recall-positive compounds; raise N_PER_STRATUM in make_audit_sample.py "
              f"for a higher-power panel.")


if __name__ == "__main__":
    args = [a for p in sys.argv[1:] for a in (glob.glob(p) or [p])]
    main(args)
