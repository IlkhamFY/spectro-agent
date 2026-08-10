#!/usr/bin/env python3
"""
Split IRexp into its two licence pools.

IRexp redistributes two source pools under different terms: PMC Open-Access Subset
records are CC-BY-4.0, Chemotion RADAR4Chem records are CC-BY-SA-4.0. A downstream user
who wants the CC-BY pool alone -- i.e. who does not want the ShareAlike obligation --
needs to separate them, and must be able to do so from the released file itself.

The discriminator is each record's `source_doi`, which is lossless and always present:
Chemotion records carry the RADAR4Chem DOI prefix 10.22000, PMC records carry a PMC:
accession. There is no separate `license` column; this script is the labelling.

  python scripts/split_license_pools.py               # report the split
  python scripts/split_license_pools.py --write OUT/  # write the two pools out
"""
import gzip, json, os, sys

SRC = "data/irexp/irexp.jsonl.gz"
CHEMOTION_DOI_PREFIX = "10.22000"


def pool_of(rec):
    """-> 'chemotion' (CC-BY-SA-4.0) or 'pmc' (CC-BY-4.0)."""
    doi = (rec.get("source_doi") or "")
    return "chemotion" if doi.startswith(CHEMOTION_DOI_PREFIX) else "pmc"


LICENCE = {"pmc": "CC-BY-4.0", "chemotion": "CC-BY-SA-4.0"}


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
        print("\nRe-run with --write OUT/ to materialise the two pools, each record "
              "stamped\nwith its licence. Taking irexp_pmc alone avoids the ShareAlike "
              "obligation.")


if __name__ == "__main__":
    main()
