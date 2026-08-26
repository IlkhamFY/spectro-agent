#!/usr/bin/env python3
"""
Split IRexp into its two licence pools.

IRexp redistributes two source pools under different terms: PMC Open-Access Subset
records are **not** uniformly CC-BY-4.0 (mixed CC BY / CC BY-NC* / other — see
data/NOTICE); Chemotion RADAR4Chem records are CC-BY-SA-4.0. This script separates
*source* pools on `source_doi` only. Its PMC stamp of CC-BY-4.0 is a **legacy
overclaim** until per-article licences are joined — treat PMC output as
"PMC-sourced", not as a verified commercial CC-BY pool.

The discriminator is each record's `source_doi`, which is lossless and always present:
Chemotion records carry the RADAR4Chem DOI prefix 10.22000, PMC records carry a PMC:
accession. Most PMC rows do not yet carry a stamped licence; this script is the
(source) labelling.

  python scripts/split_license_pools.py               # report the split
  python scripts/split_license_pools.py --write OUT/  # write the two pools out
"""
import gzip, json, os, sys

SRC = "data/irexp/irexp.jsonl.gz"
CHEMOTION_DOI_PREFIX = "10.22000"


def pool_of(rec):
    """-> 'chemotion' (CC-BY-SA-4.0) or 'pmc' (PMC-sourced; licence mix — see NOTICE)."""
    doi = (rec.get("source_doi") or "")
    return "chemotion" if doi.startswith(CHEMOTION_DOI_PREFIX) else "pmc"


# Legacy labels written into --write output. PMC is NOT verified CC-BY.
LICENCE = {"pmc": "PMC-OA-MIXED-UNVERIFIED", "chemotion": "CC-BY-SA-4.0"}


def main():
    out = None
    if "--write" in sys.argv:
        out = sys.argv[sys.argv.index("--write") + 1]
        os.makedirs(out, exist_ok=True)
    handles, counts = {}, {"pmc": 0, "chemotion": 0}
    if out:
        handles = {k: gzip.open(f"{out}/irexp_{k}.jsonl.gz", "wt") for k in counts}
    for line in gzip.open(SRC, "rt"):
        rec = json.loads(line)
        k = pool_of(rec)
        counts[k] += 1
        if out:
            rec["license"] = LICENCE[k]     # the label the released file does not carry
            handles[k].write(json.dumps(rec) + "\n")
    for h in handles.values():
        h.close()
    total = sum(counts.values())
    print(f"{SRC}: {total:,} records")
    for k in ("pmc", "chemotion"):
        print(f"  {k:<10} {counts[k]:>7,}  {LICENCE[k]}")
    if out:
        print(f"\nwrote {out}/irexp_pmc.jsonl.gz and {out}/irexp_chemotion.jsonl.gz "
              f"(each record stamped with its `license`)")
    else:
        print("\nRe-run with --write OUT/ to materialise the two source pools.\n"
              "WARNING: PMC rows are NOT verified CC-BY — see data/NOTICE. "
              "Taking Chemotion alone is CC-BY-SA-4.0.")


if __name__ == "__main__":
    main()
