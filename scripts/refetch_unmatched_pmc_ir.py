#!/usr/bin/env python3
"""Focused PMC OA re-fetch + IR re-extract for unmatched curated IRexp rows (F1).

Fetches plain text from S3 pmc-oa-opendata (Europe PMC XML fallback), extracts
IR with fixed _parse_ir_bands via extract_records, checkpoints progress, and
optionally merges new bands into staged rebuild curated files by (pmcid, old_bands)
or id when a confident join exists.

Does NOT publish to HF / Zenodo.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spectro_scraper.extract import extract_records, normalize_text  # noqa: E402

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = "spectro-agent-irexp-refetch/1.0 (Ilkham Yabbarov; research)"


def _open_in(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def _open_out(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        return gzip.open(path, "wt", encoding="utf-8")
    return open(path, "w", encoding="utf-8")


def _band_key(bands) -> tuple:
    if not bands:
        return tuple()
    return tuple(float(x) for x in bands)


def s3_txt(num: str) -> str:
    num = str(num).replace("PMC", "").strip()
    for v in (1, 2, 3):
        url = f"{S3}/PMC{num}.{v}/PMC{num}.{v}.txt"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception:
            continue
    return ""


def epmc_txt(num: str) -> str:
    """Europe PMC full-text XML -> rough text fallback."""
    num = str(num).replace("PMC", "").strip()
    url = f"{EPMC}/PMC{num}/fullTextXML"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as resp:
            xml = resp.read().decode("utf-8", "replace")
    except Exception:
        return ""
    # crude tag strip — enough for regex IR extract
    import re

    text = re.sub(r"<[^>]+>", " ", xml)
    text = re.sub(r"\s+", " ", text)
    return text


def fetch_txt(num: str) -> tuple[str, str]:
    txt = s3_txt(num)
    if txt:
        return txt, "s3"
    txt = epmc_txt(num)
    if txt:
        return txt, "epmc"
    return "", "miss"


def collect(num: str) -> dict:
    txt, src = fetch_txt(num)
    recs = []
    if txt:
        for rec in extract_records(normalize_text(txt)):
            if not rec.ir_bands:
                continue
            recs.append(
                {
                    "ir_bands_cm-1": list(rec.ir_bands),
                    "ir_raw": rec.ir,
                    "name": rec.name,
                    "h_nmr": getattr(rec, "h_nmr", None),
                    "c_nmr": getattr(rec, "c_nmr", None),
                    "source_doi": f"PMC:{num}",
                    "pmcid": f"PMC{num}",
                    "fetch_source": src,
                }
            )
            # attach spectro-normalized NMR if helpers available
    return {
        "pmc_num": str(num).replace("PMC", ""),
        "fetch_source": src,
        "n_chars": len(txt),
        "n_ir": len(recs),
        "records": recs,
        "ts": time.time(),
    }


def load_checkpoint(path: Path) -> dict:
    done = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                done[o["pmc_num"]] = o
    return done


def append_checkpoint(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        # store without huge raw? keep ir_raw — needed for audit
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def merge_into_curated(
    curated_in: Path,
    curated_out: Path,
    fetch_by_pmc: dict,
    unmatched_ids: set[str] | None = None,
) -> dict:
    """Propagate newly extracted bands into curated rows.

    Join strategy for unmatched rows on a PMC:
      1. (pmcid/source_doi, old_bands) exact against new extract old? — new extract
         has FIXED bands; we match when old curated bands equal a RE-PARSE of the
         same ir_raw under the OLD parser is hard. Instead:
      2. Prefer: if curated row unmatched and paper has exactly 1 new IR record -> use it
         only when old max<1000 and new max>=1000 and lengths compatible? Too heuristic.
      3. Practical: build map from (doi, band_key(OLD-style?)) —

    Better approach: for each new record with ir_raw, compute both nothing — we only
    have fixed parser. Match curated unmatched rows on same PMC by:
      - if single curated unmatched + single new record: assign
      - else match by sorted-float proximity / identical after thousands fix on
        reconstructing from comparing set of new bands vs old truncated.

    Truncation signature: old bands look like new bands with thousands commas dropped
    (2976 -> 976). Detect: for each old band b<1000, exists new band n where
    n % 1000 == b or n == b.
    """
    # index new records by pmc
    by_pmc: dict[str, list] = defaultdict(list)
    for pmc, packet in fetch_by_pmc.items():
        for r in packet.get("records") or []:
            by_pmc[pmc].append(r)

    n = changed = unmatched_still = updated = skipped_no_fetch = confirmed = 0
    max_lt_before = max_lt_after = 0
    examples = []

    with _open_in(curated_in) as fin, _open_out(curated_out) as fout:
        for line in fin:
            o = json.loads(line)
            n += 1
            old = list(o.get("ir_bands_cm-1") or o.get("ir_bands_old_cm-1") or [])
            # prefer original old if present from prior rebuild
            if o.get("ir_bands_old_cm-1"):
                # current bands may already be reparsed; for merge use current as baseline
                baseline = list(o.get("ir_bands_cm-1") or [])
            else:
                baseline = old
            bands_now = list(o.get("ir_bands_cm-1") or [])
            if bands_now and max(float(x) for x in bands_now) < 1000:
                max_lt_before += 1

            pmc = str(o.get("pmcid") or "").replace("PMC", "")
            if not pmc:
                doi = str(o.get("source_doi") or "")
                if doi.startswith("PMC:"):
                    pmc = doi.split(":", 1)[1]

            max_lt = bool(bands_now and max(float(x) for x in bands_now) < 1000)
            is_target = False
            if unmatched_ids is not None:
                is_target = o.get("id") in unmatched_ids
            else:
                # extras: only touch refetch PMCs that still look truncated
                is_target = bool(pmc and pmc in by_pmc and max_lt)
            new_bands = None
            if is_target and pmc and pmc in by_pmc and by_pmc[pmc]:
                candidates = by_pmc[pmc]
                new_bands = _best_match_bands(bands_now, candidates)
                if new_bands is None and len(candidates) == 1 and (
                    not bands_now or max(float(x) for x in bands_now) < 1000
                ):
                    new_bands = list(candidates[0]["ir_bands_cm-1"])

            if new_bands is not None and new_bands != bands_now:
                o["ir_bands_old_cm-1"] = o.get("ir_bands_old_cm-1") or bands_now
                o["ir_bands_cm-1"] = new_bands
                o["ir_refetch_merged"] = True
                changed += 1
                updated += 1
                if len(examples) < 12:
                    examples.append(
                        {
                            "id": o.get("id"),
                            "pmcid": o.get("pmcid"),
                            "old": bands_now,
                            "new": new_bands,
                        }
                    )
            elif new_bands is not None:
                o["ir_refetch_confirmed"] = True
                confirmed += 1
            elif is_target and pmc and pmc not in by_pmc:
                skipped_no_fetch += 1
                unmatched_still += 1
            elif is_target:
                unmatched_still += 1

            bands_out = list(o.get("ir_bands_cm-1") or [])
            if bands_out and max(float(x) for x in bands_out) < 1000:
                max_lt_after += 1
            fout.write(json.dumps(o, ensure_ascii=False) + "\n")

    return {
        "source": str(curated_in),
        "output": str(curated_out),
        "n": n,
        "updated": updated,
        "changed": changed,
        "confirmed_identical": confirmed,
        "target_unmatched_still": unmatched_still,
        "skipped_no_fetch": skipped_no_fetch,
        "max_lt_1000_before": max_lt_before,
        "max_lt_1000_after": max_lt_after,
        "examples": examples,
    }


def _best_match_bands(old_bands: list, candidates: list) -> list | None:
    """Match truncated old bands to a re-extracted candidate via modulo-1000 signature."""
    if not old_bands:
        return None
    old = [float(x) for x in old_bands]
    best = None
    best_score = -1
    for c in candidates:
        new = [float(x) for x in (c.get("ir_bands_cm-1") or [])]
        if not new:
            continue
        score = _truncation_score(old, new)
        if score > best_score:
            best_score = score
            best = new
    # require at least half of old bands explained by truncation/identity
    if best is not None and best_score >= max(1, len(old) / 2):
        return best
    return None


def _truncation_score(old: list[float], new: list[float]) -> float:
    """How well old looks like thousands-truncated new (or identical)."""
    used = [False] * len(new)
    score = 0.0
    for b in old:
        hit = False
        for i, n in enumerate(new):
            if used[i]:
                continue
            if abs(n - b) < 0.6:
                used[i] = True
                score += 1.0
                hit = True
                break
            # thousands drop: 2976 -> 976, 1730 -> 730
            if b < 1000 and abs((n % 1000) - b) < 0.6 and n >= 1000:
                used[i] = True
                score += 1.5  # prefer truncation explanation
                hit = True
                break
        if not hit:
            score -= 0.25
    return score


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pmcids",
        default=str(ROOT / "data/irexp_rebuild_20260910/unmatched_priority_pmcids.txt"),
    )
    ap.add_argument(
        "--outdir",
        default=str(ROOT / "data/irexp_rebuild_20260910/refetch"),
    )
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="Max PMCs to fetch (0=all)")
    ap.add_argument("--sleep", type=float, default=0.05, help="Delay between submits")
    ap.add_argument("--merge", action="store_true", help="Merge into staged curated")
    ap.add_argument(
        "--unmatched-ids",
        default=str(ROOT / "data/irexp_rebuild_20260910/unmatched_irexp_ids.jsonl"),
    )
    ap.add_argument(
        "--curated-in",
        default=str(ROOT / "data/irexp_rebuild_20260910/irexp_reparsed.jsonl.gz"),
    )
    ap.add_argument(
        "--curated-out",
        default=str(ROOT / "data/irexp_rebuild_20260910/irexp_reparsed_refetch.jsonl.gz"),
    )
    args = ap.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ckpt = outdir / "pmc_refetch_checkpoint.jsonl"
    harvest_out = outdir / "refetch_ir_records.jsonl.gz"

    pmcids = []
    with open(args.pmcids, encoding="utf-8") as f:
        for line in f:
            n = line.strip().replace("PMC", "")
            if n:
                pmcids.append(n)
    if args.limit and args.limit > 0:
        pmcids = pmcids[: args.limit]

    done = load_checkpoint(ckpt)
    todo = [p for p in pmcids if p not in done]
    print(
        f"PMCs total={len(pmcids)} done={len(done)} todo={len(todo)} workers={args.workers}",
        flush=True,
    )

    t0 = time.time()
    ok = miss = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {}
        for i, p in enumerate(todo):
            futs[ex.submit(collect, p)] = p
            if args.sleep:
                time.sleep(args.sleep)
        for j, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                p = futs[fut]
                row = {
                    "pmc_num": p,
                    "fetch_source": "error",
                    "n_chars": 0,
                    "n_ir": 0,
                    "records": [],
                    "error": str(e),
                    "ts": time.time(),
                }
            append_checkpoint(ckpt, row)
            done[row["pmc_num"]] = row
            if row["fetch_source"] == "miss" or row["n_chars"] == 0:
                miss += 1
            else:
                ok += 1
            if j % 10 == 0 or j == len(todo):
                rate = j / max(time.time() - t0, 1)
                print(
                    f"  {j}/{len(todo)} ok={ok} miss={miss} "
                    f"{rate:.1f} pmc/s last=PMC{row['pmc_num']} "
                    f"src={row['fetch_source']} ir={row['n_ir']}",
                    flush=True,
                )

    # write flat harvest of all records
    n_rec = 0
    with _open_out(harvest_out) as fout:
        for p in pmcids:
            row = done.get(p)
            if not row:
                continue
            for r in row.get("records") or []:
                fout.write(json.dumps(r, ensure_ascii=False) + "\n")
                n_rec += 1

    src_counts = Counter(done[p].get("fetch_source") for p in pmcids if p in done)
    ir_counts = sum(done[p].get("n_ir", 0) for p in pmcids if p in done)
    summary = {
        "pmcids_requested": len(pmcids),
        "pmcids_fetched": sum(1 for p in pmcids if p in done),
        "fetch_sources": dict(src_counts),
        "total_ir_records": ir_counts,
        "checkpoint": str(ckpt),
        "records_out": str(harvest_out),
        "elapsed_s": round(time.time() - t0, 1),
    }
    print(json.dumps(summary, indent=2), flush=True)
    with open(outdir / "refetch_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if args.merge:
        unmatched_ids = set()
        up = Path(args.unmatched_ids)
        if up.exists():
            with open(up, encoding="utf-8") as f:
                for line in f:
                    unmatched_ids.add(json.loads(line)["id"])
        # only merge for PMCs we have
        fetch_by_pmc = {p: done[p] for p in pmcids if p in done}
        st = merge_into_curated(
            Path(args.curated_in),
            Path(args.curated_out),
            fetch_by_pmc,
            unmatched_ids=unmatched_ids or None,
        )
        print("MERGE", json.dumps({k: v for k, v in st.items() if k != "examples"}, indent=2))
        with open(outdir / "merge_stats.json", "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
        # also merge resolved + release if present
        extras = [
            (
                ROOT / "data/irexp_rebuild_20260910/irexp_resolved_reparsed.jsonl.gz",
                ROOT / "data/irexp_rebuild_20260910/irexp_resolved_reparsed_refetch.jsonl.gz",
            ),
            (
                ROOT / "data/irexp_rebuild_20260910/release_train_reparsed.jsonl.gz",
                ROOT / "data/irexp_rebuild_20260910/release_train_reparsed_refetch.jsonl.gz",
            ),
            (
                ROOT / "data/irexp_rebuild_20260910/release_pretrain_ir_reparsed.jsonl.gz",
                ROOT / "data/irexp_rebuild_20260910/release_pretrain_ir_reparsed_refetch.jsonl.gz",
            ),
        ]
        extra_stats = {}
        for src, dst in extras:
            if not src.exists():
                continue
            est = merge_into_curated(src, dst, fetch_by_pmc, unmatched_ids=None)
            # For release/resolved, allow merge on any row matching truncation on these PMCs
            extra_stats[dst.name] = {k: v for k, v in est.items() if k != "examples"}
            print(f"MERGE {dst.name} updated={est['updated']} max_lt {est['max_lt_1000_before']}->{est['max_lt_1000_after']}")
        with open(outdir / "merge_stats_extras.json", "w", encoding="utf-8") as f:
            json.dump(extra_stats, f, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

