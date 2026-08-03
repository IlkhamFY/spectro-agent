#!/usr/bin/env python3
"""Contamination control 2: does accuracy depend on when the source paper was published?

The formula-only control (scripts/modality_ablation.py, condition `formulaonly`) shows the
spectra carry the signal, but it cannot rule out that memorisation contributes to the part
of the headline number the spectra do explain. This is the complementary test.

Logic: a model can only have memorised a compound if the paper reporting it was in the
training corpus. Older papers have had more time in more corpora and are more heavily
cited, replicated and reviewed; the most recent ones may postdate the training cutoff
entirely. So if the headline accuracy is substantially driven by recall, accuracy should
fall with publication recency. If accuracy is flat in publication year, memorisation is
not doing the work.

This is a correlational test, not a randomised one -- publication year also correlates
with chemistry (newer papers skew to larger, more exotic targets), so the size-adjusted
comparison matters as much as the raw one. Both are reported.

  python3 scripts/contamination_recency.py [--out data/audit/recency_control.json]
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_main as sm
from specmetrics import ik14
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

EPMC = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        "?query={}&format=json&resultType=lite&pageSize=1")


def pub_year(pmcid, retries=3):
    for a in range(retries):
        try:
            url = EPMC.format(urllib.parse.quote(pmcid))
            with urllib.request.urlopen(url, timeout=45) as r:
                res = json.load(r)["resultList"]["result"]
            if not res:
                return None
            y = res[0].get("pubYear")
            return int(y) if y else None
        except Exception:
            if a == retries - 1:
                return None
            time.sleep(2 ** a)


def wilson(k, n, z=1.96):
    from math import sqrt
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (100 * (c - m) / d, 100 * (c + m) / d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/audit/recency_control.json")
    a = ap.parse_args()

    rows = sm.load()
    recs = []
    for ans, cands in rows:
        src = ans.get("source_doi")
        if not src or not str(src).startswith("PMC"):
            continue
        gold = ik14(ans["smiles"])
        cs = (cands or [])[:3]
        m = Chem.MolFromSmiles(ans["smiles"])
        recs.append({
            "pmcid": str(src).replace("PMC:", "PMC"),
            "top1": bool(cs) and ik14(cs[0]) == gold,
            "rec": any(ik14(c) == gold for c in cs),
            "hac": m.GetNumHeavyAtoms() if m else None,
            "difficulty": ans.get("difficulty"),
        })
    print(f"{len(recs)} benchmark compounds carry a PMC accession")

    cache = {}
    for i, r in enumerate(recs, 1):
        if r["pmcid"] not in cache:
            cache[r["pmcid"]] = pub_year(r["pmcid"])
        r["year"] = cache[r["pmcid"]]
        if i % 25 == 0:
            print(f"  resolved {i}/{len(recs)}")
    got = [r for r in recs if r["year"]]
    print(f"publication year resolved for {len(got)}/{len(recs)}")

    years = sorted(r["year"] for r in got)
    med = years[len(years) // 2]
    print(f"year range {years[0]}-{years[-1]}, median {med}\n")

    def block(sub, label):
        n = len(sub); k = sum(r["top1"] for r in sub)
        lo, hi = wilson(k, n)
        print(f"  {label:<28} {k:>3}/{n:<4} = {100*k/n:5.1f}%   [{lo:.0f}, {hi:.0f}]")
        return {"label": label, "n": n, "top1": k, "pct": round(100 * k / n, 1),
                "ci": [round(lo), round(hi)]}

    print("Top-1 by publication-year half (median split):")
    old = [r for r in got if r["year"] <= med]
    new = [r for r in got if r["year"] > med]
    out_halves = [block(old, f"<= {med} (older)"), block(new, f"> {med} (newer)")]

    print("\nTop-1 by year bucket:")
    buckets, out_buckets = {}, []
    for r in got:
        b = "<2015" if r["year"] < 2015 else "2015-2019" if r["year"] < 2020 else \
            "2020-2023" if r["year"] < 2024 else ">=2024"
        buckets.setdefault(b, []).append(r)
    for b in ["<2015", "2015-2019", "2020-2023", ">=2024"]:
        if buckets.get(b):
            out_buckets.append(block(buckets[b], b))

    # size is the known driver (PAPER.md 4.1); check it does not confound the year split
    print("\nMolecular size by half (the known driver of accuracy):")
    for sub, lab in ((old, f"<= {med}"), (new, f"> {med}")):
        h = [r["hac"] for r in sub if r["hac"]]
        print(f"  {lab:<28} median heavy atoms {sorted(h)[len(h)//2]}, mean {sum(h)/len(h):.1f}")

    # point-biserial correlation between year and correctness
    n = len(got)
    ys = [r["year"] for r in got]; ts = [1 if r["top1"] else 0 for r in got]
    my = sum(ys) / n; mt = sum(ts) / n
    num = sum((y - my) * (t - mt) for y, t in zip(ys, ts))
    den = (sum((y - my) ** 2 for y in ys) * sum((t - mt) ** 2 for t in ts)) ** 0.5
    r_pb = num / den if den else 0.0
    print(f"\npoint-biserial r(publication year, correct) = {r_pb:+.3f} over n={n}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"n_resolved": len(got), "n_total": len(recs),
               "year_min": years[0], "year_max": years[-1], "median_year": med,
               "halves": out_halves, "buckets": out_buckets,
               "point_biserial_r": round(r_pb, 4),
               "per_compound": [{k: r[k] for k in ("pmcid", "year", "top1", "hac", "difficulty")}
                                for r in got]},
              open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
