#!/usr/bin/env python3
"""Measure IRexp extraction fidelity against the source articles.

A dataset paper should report how accurately its records were extracted, not assert it.
IRexp records are band lists transcribed from the experimental section of open-access
papers, so fidelity is checkable: re-fetch the source article and ask, for a random
sample, whether every wavenumber we recorded actually appears in that article's text.

This measures *transcription fidelity* of the deterministic parser -- it catches
hallucinated, mis-parsed and unit-mangled values. It does not measure whether the parser
found every IR string in the paper (recall of records), which needs human reading; that
remains the manual audit described in the paper.

  python3 scripts/audit_extraction.py --n 60 --seed 0 [--out data/audit/extraction_audit.json]
"""
import argparse, gzip, json, random, re, sys, time, urllib.request

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"
CORPUS = "data/irexp/irexp.jsonl.gz"


def load_sample(n, seed):
    """Reservoir-sample n PMC-sourced records without holding the corpus in memory."""
    rng = random.Random(seed)
    keep, seen = [], 0
    with gzip.open(CORPUS, "rt") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not str(d.get("source_doi", "")).startswith("PMC"):
                continue          # Chemotion pool is peak-picked, not transcribed
            seen += 1
            if len(keep) < n:
                keep.append(d)
            else:
                j = rng.randrange(seen)
                if j < n:
                    keep[j] = d
    return keep, seen


def fetch(pmcid, retries=3):
    for a in range(retries):
        try:
            with urllib.request.urlopen(EPMC.format(pmcid), timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if a == retries - 1:
                return None
            time.sleep(2 ** a)


def audit_record(rec, text):
    """A band is CONFIRMED if its integer wavenumber appears in the article text.

    Sources write 1664, 1664.0, 1663.8 or 1,664 for the same band, so we match on the
    integer part and allow +/-1 cm-1 for rounding between the paper and our parse.
    """
    nums = set(re.findall(r"\d{3,4}", re.sub(r"[,  ]", "", text)))
    bands = rec.get("ir_bands_cm-1") or []
    hits = sum(1 for b in bands
               if any(str(int(round(b)) + d) in nums for d in (0, -1, 1)))
    return len(bands), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="data/audit/extraction_audit.json")
    a = ap.parse_args()

    sample, pool = load_sample(a.n, a.seed)
    print(f"sampled {len(sample)} of {pool} PMC-sourced records (seed {a.seed})")

    rows, fetched = [], 0
    for i, rec in enumerate(sample, 1):
        pmcid = str(rec["source_doi"]).replace("PMC:", "PMC")
        text = fetch(pmcid)
        if text is None:
            rows.append({"pmcid": pmcid, "status": "unfetchable"})
            continue
        fetched += 1
        nb, hits = audit_record(rec, text)
        rows.append({"pmcid": pmcid, "status": "ok", "bands": nb, "confirmed": hits})
        print(f"  [{i:>3}/{len(sample)}] {pmcid:<12} {hits}/{nb} bands confirmed in source")

    ok = [r for r in rows if r["status"] == "ok"]
    tb = sum(r["bands"] for r in ok)
    tc = sum(r["confirmed"] for r in ok)
    perfect = sum(1 for r in ok if r["confirmed"] == r["bands"])
    summary = {
        "sampled": len(sample), "fetched": fetched, "pool": pool, "seed": a.seed,
        "records_scored": len(ok), "bands_total": tb, "bands_confirmed": tc,
        "band_fidelity": round(tc / tb, 4) if tb else None,
        "records_fully_confirmed": perfect,
        "record_fidelity": round(perfect / len(ok), 4) if ok else None,
    }
    print("\n" + json.dumps(summary, indent=2))
    import os
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"summary": summary, "records": rows}, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
