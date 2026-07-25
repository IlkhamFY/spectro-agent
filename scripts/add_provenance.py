#!/usr/bin/env python3
"""Attach per-compound source provenance to every benchmark answer file.

A released benchmark must let a reader trace each item to the paper it came from --
to audit the extraction, to check licensing, and (the reason it matters most here) to
reason about pretraining contamination: every compound was mined from open-access
literature that a frontier model may have trained on. Without a source id, that
exposure cannot be assessed at all.

Adds a `source_doi` field (the PMC accession recorded by the IRexp mining pipeline) by
joining on the InChIKey connectivity layer. Idempotent; writes only if something changed.

Run from the repo root:  python3 scripts/add_provenance.py [--check]
"""
import gzip, json, sys, os

RESOLVED = "data/irexp_resolved/irexp_resolved.jsonl.gz"
TARGETS = ["data/benchmark_main", "data/benchmark_v3", "data/benchmark_v2_ctrl",
           "data/benchmark_electrolyte"]


def index_sources():
    """InChIKey-14 -> source accession. First occurrence wins (the mining pipeline
    already de-duplicates by InChIKey, so collisions are the same compound re-reported)."""
    idx = {}
    with gzip.open(RESOLVED, "rt") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ik, src = d.get("inchikey"), d.get("source_doi")
            if ik and src:
                idx.setdefault(ik[:14], src)
    return idx


def main():
    check = "--check" in sys.argv
    idx = index_sources()
    total = hit = changed = 0
    for d in TARGETS:
        path = f"{d}/answers2.jsonl"
        if not os.path.exists(path):
            continue
        rows = [json.loads(l) for l in open(path) if l.strip()]
        out, n_hit = [], 0
        for r in rows:
            src = idx.get((r.get("inchikey") or "")[:14])
            if src:
                n_hit += 1
                if r.get("source_doi") != src:
                    r["source_doi"] = src
                    changed += 1
            out.append(r)
        total += len(rows); hit += n_hit
        print(f"  {d:34} {n_hit}/{len(rows)} traced")
        if not check and changed:
            with open(path, "w") as f:
                for r in out:
                    f.write(json.dumps(r) + "\n")
    print(f"provenance coverage: {hit}/{total} = {100*hit/max(total,1):.0f}%"
          + ("  (--check: nothing written)" if check else f"; {changed} records updated"))


if __name__ == "__main__":
    main()
