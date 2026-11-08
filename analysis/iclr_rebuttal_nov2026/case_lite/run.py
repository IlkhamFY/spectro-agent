#!/usr/bin/env python3
"""CASE-lite on the locked n=500 roster.

Oracle proposer: surge 2.0 enumerates constitutional isomers of the printed
formula. Ranker: the repository HOSE-style 13C lookup (scripts/hose_predict.py)
with the symmetric chamfer distance used in the paper. Gold SMILES are read
only after the pool exists, to compute rank.

Primary isomer count is surge's count for the printed formula at surge's
lowest valences, with -R so Kekulé duplicates of one aromatic constitution
are one structure. Higher valences (N 5, S 4/6, P 5) are a separate
formula-only sensitivity: they are included only when every valence state
finishes and the sum of counts is still within the cutoff.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from rdkit import Chem
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

import hose_predict as hp  # noqa: E402
from roster import load  # noqa: E402

SURGE = os.environ.get("SURGE", "/tmp/surgebin/surge")
SURGE_SHA256 = "0910de00e9b7373184a62914e1c34bf26b5fefce4f487a4088b938c0c410e9c2"
SURGE_RELEASE = "https://github.com/StructureGenerator/surge/releases/download/v2.0/surge-linux-x86_64.tar.gz"

START_CUTOFF = 5000
EXPAND_CUTOFF = 20000
# Finished counts above this are "over the cutoff". Unfinished counts are
# not assigned an N_iso. Retries cover the small formulas a short timeout
# could have mis-labelled.
PASS_TIMEOUT = [
    (4.0, 10**9),
    (20.0, 18),
    (45.0, 14),
]
WORKERS = 3
HOSE_MAE = 3.23  # reproduced held-out gate from scripts/hose_predict.py build

OUT = HERE / "outputs"
CARBONYL = Chem.MolFromSmarts("[CX3]=[OX1]")
NITRILE = Chem.MolFromSmarts("[CX2]#[NX1]")
NITRO = Chem.MolFromSmarts("[$([NX3](=O)=O),$([NX3+](=O)[O-])]")
ELEM_RE = re.compile(r"([A-Z][a-z]?)(\d*)")
RENDER_ORDER = ["C", "H", "B", "Br", "Cl", "F", "I", "N", "Nx", "O", "P", "Px",
                "S", "Sx", "Sy", "Se", "Si", "Sn"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_formula(formula):
    counts = {}
    for el, n in ELEM_RE.findall(formula):
        counts[el] = counts.get(el, 0) + (int(n) if n else 1)
    return counts


def heavy_atoms(counts):
    return sum(n for el, n in counts.items() if el != "H")


def surge_flags(formula):
    flags = ["-R"]
    if "Se" in parse_formula(formula):
        flags.append("-ESe2")
    if "Sn" in parse_formula(formula):
        flags.append("-ESn4")
    return flags


def parse_surge_count(text):
    if "impossible parity" in text or "impossible" in text and ">E" in text:
        if "impossible parity" in text:
            return 0, "ok"
    m = re.findall(r">Z (?:generated|wrote) (.+?) in ", text)
    if not m:
        err = " ".join(ln.strip() for ln in text.splitlines() if ln.startswith(">E"))
        return None, err or "no-count"
    nums = [int(x) for x in re.findall(r"\d+", m[-1])]
    if not nums:
        return None, "no-integer"
    return nums[-1], "ok"


def surge_count(formula, flags, timeout):
    cmd = [SURGE, "-u", *flags, formula]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"formula": formula, "status": "timeout", "n_iso": None, "timeout": timeout}
    text = (p.stdout or "") + "\n" + (p.stderr or "")
    n, status = parse_surge_count(text)
    if status != "ok":
        return {"formula": formula, "status": "error", "n_iso": None, "detail": status[:300],
                "timeout": timeout}
    return {"formula": formula, "status": "ok", "n_iso": int(n), "timeout": timeout}


def surge_smiles(formula, flags, timeout):
    cmd = [SURGE, "-S", *flags, formula]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    text = (p.stdout or "") + "\n" + (p.stderr or "")
    n, status = parse_surge_count(text)
    if status != "ok":
        return None, status
    smi = []
    for ln in (p.stdout or "").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith(">"):
            smi.append(ln)
    return {"n_iso": int(n), "smiles": smi}, "ok"


def compositions(n, k):
    if k == 1:
        yield (n,)
        return
    for i in range(n + 1):
        yield from ((i,) + rest for rest in compositions(n - i, k - 1))


def render_counts(counts):
    parts = []
    for el in RENDER_ORDER:
        n = counts.get(el, 0)
        if n:
            parts.append(el + (str(n) if n != 1 else ""))
    extra = [el for el in counts if el not in RENDER_ORDER and counts[el]]
    if extra:
        raise SystemExit(f"unrendered elements {extra} in {counts}")
    return "".join(parts)


def valence_specs(counts):
    """Every standard-valence assignment. The all-lowest assignment is first."""
    n_n = counts.get("N", 0)
    n_s = counts.get("S", 0)
    n_p = counts.get("P", 0)
    specs = []
    for k_n in range(n_n + 1):
        for s2, s4, s6 in compositions(n_s, 3):
            for k_p in range(n_p + 1):
                c = dict(counts)
                c["N"] = n_n - k_n
                if k_n:
                    c["Nx"] = k_n
                c["S"] = s2
                if s4:
                    c["Sx"] = s4
                if s6:
                    c["Sy"] = s6
                c["P"] = n_p - k_p
                if k_p:
                    c["Px"] = k_p
                default = k_n == 0 and s4 == 0 and s6 == 0 and k_p == 0
                specs.append((default, c))
    return specs


def unique_shifts(xs):
    out, seen = [], set()
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def ik14_mol(m):
    if m is None:
        return None
    return Chem.MolToInchiKey(m)[:14]


def n_unique_carbons(m):
    ranks = Chem.CanonicalRankAtoms(m, breakTies=False)
    return len({int(ranks[a.GetIdx()]) for a in m.GetAtoms() if a.GetSymbol() == "C"})


def passes_printed_filters(m, n_obs, bands):
    """Filters use the printed IR / peak count and the candidate, never gold."""
    if n_unique_carbons(m) < n_obs:
        return False
    if any(1650.0 <= b <= 1820.0 for b in bands) and not m.HasSubstructMatch(CARBONYL):
        return False
    if any(2200.0 <= b <= 2280.0 for b in bands) and not m.HasSubstructMatch(NITRILE):
        return False
    nitro_pair = (any(1480.0 <= b <= 1570.0 for b in bands)
                  and any(1300.0 <= b <= 1390.0 for b in bands))
    if nitro_pair and not m.HasSubstructMatch(NITRO):
        return False
    return True


def competition_rank(rows, gold_ik):
    """1 + number of other constitutions with a strictly smaller chamfer."""
    gold = [d for ik, d in rows if ik == gold_ik]
    if not gold:
        return None
    g = min(gold)
    better = sum(1 for ik, d in rows if ik != gold_ik and d < g - 1e-9)
    tied = sum(1 for ik, d in rows if ik != gold_ik and abs(d - g) <= 1e-9)
    return 1 + better, g, better, tied


def count_all(formulas, meta):
    """meta[formula] = {flags, heavy, counts}. Returns formula -> count record."""
    pending = set(formulas)
    done = {}
    for timeout, max_heavy in PASS_TIMEOUT:
        batch = [f for f in pending if meta[f]["heavy"] <= max_heavy]
        if not batch:
            continue
        print(f"count pass timeout={timeout}s n={len(batch)}", flush=True)
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {
                ex.submit(surge_count, f, meta[f]["flags"], timeout): f for f in batch
            }
            for i, fut in enumerate(as_completed(futs), 1):
                rec = fut.result()
                f = futs[fut]
                if rec["status"] == "timeout":
                    continue
                done[f] = rec
                pending.discard(f)
                if i % 25 == 0 or rec["status"] != "ok":
                    print(f"  {i}/{len(batch)} last={f} {rec['status']} {rec.get('n_iso')}",
                          flush=True)
        print(f"  finished so far {len(done)} still pending {len(pending)}", flush=True)
    for f in pending:
        done[f] = {"formula": f, "status": "timeout", "n_iso": None,
                   "timeout": PASS_TIMEOUT[-1][0]}
    return done


def self_check():
    if sha256_file(SURGE) != SURGE_SHA256:
        raise SystemExit(f"surge binary hash mismatch: {SURGE}")
    expect = {("C6H6", 217), ("C4H10O", 7), ("C8H18", 18)}
    for formula, n in expect:
        rec = surge_count(formula, ["-R"], 10)
        if rec["status"] != "ok" or rec["n_iso"] != n:
            raise SystemExit(f"surge self-check {formula}: {rec}, expected {n}")
    print("surge self-check ok", flush=True)


def pool_from_smiles(smiles):
    """Distinct constitutions. Keyed by connectivity InChIKey."""
    pool = {}
    fail = 0
    for s in smiles:
        m = Chem.MolFromSmiles(s)
        if m is None:
            fail += 1
            continue
        ik = ik14_mol(m)
        if ik is None:
            fail += 1
            continue
        if ik not in pool:
            pool[ik] = Chem.Mol(m)
    return pool, fail


def enumerate_default(formula, flags, n_iso):
    rec, status = surge_smiles(formula, flags, timeout=max(30.0, n_iso / 5000))
    if status != "ok":
        return None, status
    if rec["n_iso"] != n_iso:
        return None, f"count drift {rec['n_iso']} != {n_iso}"
    pool, fail = pool_from_smiles(rec["smiles"])
    return {"pool": pool, "fail": fail, "n_lines": len(rec["smiles"]), "n_iso": rec["n_iso"]}, "ok"


def union_count(formula, meta, base_n):
    counts = meta["counts"]
    if counts.get("N", 0) + counts.get("S", 0) + counts.get("P", 0) == 0:
        return {"status": "same", "n_iso": base_n, "n_variants": 1}
    specs = valence_specs(counts)
    total = 0
    n_ok = 0
    for default, c in specs:
        if default:
            total += base_n
            n_ok += 1
            continue
        rendered = render_counts(c)
        rec = surge_count(rendered, meta["flags"], 8.0)
        if rec["status"] != "ok":
            return {"status": rec["status"], "n_iso": None, "n_variants": len(specs),
                    "finished_sum": total, "detail": rec.get("detail", "")}
        total += rec["n_iso"]
        n_ok += 1
        if total > EXPAND_CUTOFF:
            return {"status": "over", "n_iso": total, "n_variants": len(specs),
                    "finished_variants": n_ok}
    return {"status": "ok", "n_iso": total, "n_variants": len(specs)}


def enumerate_union(formula, meta):
    smiles = []
    n_sum = 0
    for default, c in valence_specs(meta["counts"]):
        rendered = formula if default else render_counts(c)
        rec, status = surge_smiles(rendered, meta["flags"], timeout=60)
        if status != "ok":
            return None, status
        n_sum += rec["n_iso"]
        smiles.extend(rec["smiles"])
    pool, fail = pool_from_smiles(smiles)
    return {"pool": pool, "fail": fail, "n_lines": len(smiles), "n_iso_sum": n_sum}, "ok"


def score_pool(pool, obs, bands, gold_ik):
    n_obs = len(obs)
    dists = []
    kept = []
    for ik, m in pool.items():
        pred = hp.predict_c13(Chem.MolToSmiles(m))
        dist = hp.chamfer(pred, obs) if pred else 999.0
        dists.append((ik, dist))
        if passes_printed_filters(m, n_obs, bands):
            kept.append((ik, dist))
    ranked = competition_rank(dists, gold_ik)
    filtered = competition_rank(kept, gold_ik)
    best = min((d for _, d in dists), default=None)
    return {
        "n_pool": len(dists),
        "n_kept": len(kept),
        "best_chamfer": best,
        "rank": None if ranked is None else ranked[0],
        "gold_chamfer": None if ranked is None else ranked[1],
        "n_better": None if ranked is None else ranked[2],
        "n_tied": None if ranked is None else ranked[3],
        "rank_filtered": None if filtered is None else filtered[0],
        "gold_kept": filtered is not None,
    }


def list_incompatible(n_obs, n_carbon, n_unique_gold):
    """Printed 13C list cannot be the carbon set of this constitution."""
    reasons = []
    if n_obs > n_carbon:
        reasons.append("more_shifts_than_carbons")
    if n_unique_gold is not None and n_obs > n_unique_gold:
        reasons.append("more_shifts_than_symmetry")
    return reasons


def cdf_rows(ranks):
    cuts = [1, 3, 10, 50, 100, 500, 1000, 5000, 20000]
    n = len(ranks)
    rows = []
    for c in cuts:
        k = sum(1 for r in ranks if r <= c)
        rows.append((c, k, n))
    return rows


def prove_lower_bound(formula, flags, limit=20001, timeout=3.0):
    """Stream SMILES until `limit`, the generator exits, or `timeout` seconds.

    Surge block-buffers stdout and a full `-u` count prints only at the end, so
    the reader runs in a thread and the process is killed on the clock. Emitting
    `limit` structures proves N_iso is above the cutoff. It is not an exact count.
    A generator that exits with fewer lines yields that exact length.
    """
    import threading
    cmd = ["stdbuf", "-o0", "-e0", SURGE, "-S", *flags, formula]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = 0
    err = []

    def _read():
        nonlocal n
        try:
            for raw in proc.stdout:
                line = raw.decode("utf-8", "replace").strip()
                if line.startswith(">E"):
                    err.append(line)
                if line and not line.startswith(">"):
                    n += 1
                if n >= limit:
                    break
        except Exception as exc:
            err.append(str(exc))

    t0 = time.time()
    thread = threading.Thread(target=_read, daemon=True)
    thread.start()
    thread.join(timeout)
    exited = proc.poll() is not None and not thread.is_alive()
    proc.kill()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    thread.join(1.0)
    seconds = round(time.time() - t0, 3)
    if n >= limit:
        return {"status": "proved_over", "n_iso": None, "lower_bound": n, "seconds": seconds}
    if err and n == 0:
        return {"status": "error", "n_iso": None, "lower_bound": 0,
                "detail": err[0][:300], "seconds": seconds}
    if exited and n == 0:
        return {"status": "error", "n_iso": None, "lower_bound": 0,
                "detail": "generator exited with no structures", "seconds": seconds}
    if exited:
        return {"status": "ok", "n_iso": n, "lower_bound": n, "seconds": seconds}
    return {"status": "timeout", "n_iso": None, "lower_bound": n, "seconds": seconds}


def _as_bool(v):
    if v in ("", None):
        return None
    if isinstance(v, bool):
        return v
    if v == "True":
        return True
    if v == "False":
        return False
    return v


def _as_num(v):
    if v in ("", None):
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v)
    if any(c in s for c in ".eE"):
        return float(s)
    return int(s)


def load_items_csv(path):
    rows = []
    bools = {"llm_proposed_k_le_3", "list_incompatible", "enumerable", "gold_in_pool",
             "top3", "top10", "top50", "gold_kept"}
    nums = {"heavy", "n_iso", "n_obs_c13", "n_carbon", "n_unique_c_gold", "n_pool",
            "parse_fail", "rank", "gold_chamfer", "best_chamfer", "n_better", "n_tied",
            "n_kept", "rank_filtered", "n_iso_lower_bound"}
    with open(path, newline="") as fh:
        for rec in csv.DictReader(fh):
            for k in bools:
                if k in rec:
                    rec[k] = _as_bool(rec[k])
            for k in nums:
                if k in rec:
                    rec[k] = _as_num(rec[k])
            rows.append(rec)
    return rows


def write_report(summary, items):
    chosen = summary["chosen_cutoff"]
    enum = [r for r in items if r["enumerable"]]
    ranked = [r for r in enum if r["gold_in_pool"]]
    absent = [r for r in enum if not r["gold_in_pool"]]
    ranks = [r["rank"] for r in ranked]
    n_enum = len(enum)
    n_ranked = len(ranked)

    def bucket(pred):
        return [r for r in ranked if pred(r)]

    le10 = bucket(lambda r: r["rank"] <= 10)
    gt50 = bucket(lambda r: r["rank"] > 50)
    miss = [r for r in le10 if r["llm_class"] == "never"]
    poor = [r for r in gt50 if r["list_incompatible"]]
    ambiguous = [r for r in gt50 if not r["list_incompatible"]]
    outside = [r for r in gt50 if r["gold_chamfer"] is not None and r["gold_chamfer"] > HOSE_MAE]
    inside = [r for r in gt50 if r["gold_chamfer"] is not None and r["gold_chamfer"] <= HOSE_MAE]

    lines = []
    w = lines.append
    w("# CASE-lite on the locked n=500 roster")
    w("")
    w("Formula-constrained constitutional-isomer enumeration, ranked by the")
    w("repository's HOSE-style 13C lookup. No language model proposes or ranks")
    w("structures in this diagnostic. Gold is applied only after the pool is built,")
    w("to read off rank.")
    w("")
    w("## Method")
    w("")
    w("The roster is the locked headline of 500: the validated main round, all of")
    w("`benchmark_v3`, all of `benchmark_v2_ctrl`, every compound in")
    w("`data/benchmark_expand` at `48fcd30153df5e331fab43cfa514763db8ee3891`, and the")
    w("committed 200-qid cut `headline500_expand200_qids.json`. Expansion gold is the")
    w("unique `(formula, IR, 13C)` join to `data/irexp_resolved` used by the locked")
    w("rescore. The loader checks the generation wall before any enumeration:")
    w(f"{summary['wall']['top1']} top-1, {summary['wall']['proposed_not_top1']} proposed at k≤3 but not rank 1, and {summary['wall']['never']} never proposed.")
    w("Those three labels are the 227/22/251 wall. A molecule was proposed at k≤3")
    w("when its label is top-1 or proposed-not-top-1.")
    w("")
    w("The enumerator is surge 2.0")
    w(f"(`{SURGE_RELEASE}`, sha256 `{SURGE_SHA256}`),")
    w("invoked as `surge -u -R <formula>` for the count and `surge -S -R` for SMILES.")
    w("`-R` collapses Kekulé duplicates of one aromatic constitution. Valences are")
    w("surge's lowest defaults (C 4, N 3, O 2, S 2, P 3, halogen 1, Si 4). Se and Sn,")
    w("which surge does not enable by default, are passed as `-ESe2` and `-ESn4`.")
    w("The printed formula is the only structural input. Gold SMILES are not passed")
    w("to surge and are not used to choose a valence, a badlist, or a filter.")
    w("")
    w(f"`N_iso` is the integer on surge's final `>Z generated` record. Formulas with")
    w(f"`N_iso` ≤ {START_CUTOFF} were the starting set. The cutoff was expanded to")
    w(f"{EXPAND_CUTOFF} because every formula whose count finished at or below")
    w(f"{EXPAND_CUTOFF} was generated and ranked. The chosen cutoff is {chosen}.")
    w("A formula whose count did not finish is not given an exact `N_iso` and is not")
    w("called enumerable. Exact-count timeouts were 4 s for every formula, then 20 s")
    w("for any still unfinished formula with ≤18 heavy atoms, then 45 s for any still")
    w("unfinished formula with ≤14 heavy atoms. Formulas that still had no exact count")
    w("were streamed with unbuffered `surge -S -R` until 20001 structures or 12 seconds.")
    w("Emitting 20001 structures proves `N_iso` > 20000. It is not an exact count, and")
    w("those molecules stay outside the ranked set. A formula that emits nothing in")
    w("that window stays unfinished, and no `N_iso` is stated for it. Self-checks")
    w("before the roster run: `C6H6` = 217, `C4H10O` = 7, `C8H18` = 18, all with `-R`.")
    w("")
    w("Each generated SMILES is parsed with RDKit and keyed by the first 14")
    w("characters of the standard InChIKey, the same connectivity key as the")
    w("benchmark. Rank uses one structure per key. The ranker is")
    w("`scripts/hose_predict.py`: Morgan spheres r = 4…1, minimum bin count 3,")
    w("hybridisation prior as the fallback. The table was rebuilt from")
    w("`nmrshiftdb2withsignals.sd` with `random.seed(7)`. Held-out 13C MAE is")
    w(f"{summary['hose_mae']} ppm (median {summary['hose_median']} ppm), the published gate.")
    w("Distance to the printed 13C list is the symmetric chamfer in")
    w("`hose_predict.chamfer`. Printed shifts are the assignment-parenthesis")
    w("numbers used by the locked join, made unique after rounding to 0.01 ppm.")
    w("Gold rank is 1 plus the number of other constitutions with a strictly")
    w("smaller chamfer. Ties keep the best rank.")
    w("")
    w("An optional filter, reported separately from the headline rank, keeps a")
    w("candidate when its symmetry-distinct carbon count (RDKit canonical ranks,")
    w("ties not broken) is at least the number of distinct printed 13C shifts, and")
    w("when a printed IR band in [1650, 1820] cm⁻¹ requires a carbonyl, a band in")
    w("[2200, 2280] requires a nitrile, and a band in both [1480, 1570] and")
    w("[1300, 1390] requires a nitro group. Absence of a band eliminates nothing.")
    w("")
    w("A printed list is counted as incompatible with the gold constitution when")
    w("the number of distinct printed 13C shifts exceeds the carbon count in the")
    w("formula, or exceeds the number of symmetry-distinct carbons in gold. That")
    w("test is applied only at scoring time. It is the meaning of \"the printed")
    w("lists themselves poorly identify the constitution\" in the table below.")
    w(f"Separately, gold chamfer is compared with the lookup MAE of {HOSE_MAE} ppm.")
    w("A chamfer above that line means the printed shifts disagree with the shifts")
    w("the lookup predicts for gold; a chamfer on or below it means the list matches")
    w("gold within the lookup's own error and the rank is carried by other isomers")
    w("that match at least as well.")
    w("")
    w("Higher valences are not in the headline `N_iso`. For every formula whose")
    w(f"default `N_iso` is ≤ {EXPAND_CUTOFF} and that contains N, S, or P, the run")
    w("also counts N-valence-5, S-valence-4, S-valence-6, and P-valence-5")
    w("assignments. When every assignment finishes and the sum is still ≤")
    w(f"{EXPAND_CUTOFF}, that union is enumerated and ranked as a sensitivity.")
    w("")
    w("## How many of the 500 were enumerable")
    w("")
    w(f"Of the 500 molecules, {summary['n_under_5000']}/500 have a finished default-valence")
    w(f"`N_iso` ≤ {START_CUTOFF}, and {summary['n_under_20000']}/500 have a finished")
    w(f"default-valence `N_iso` ≤ {EXPAND_CUTOFF}.")
    w(f"The chosen cutoff is {chosen}, so the enumerable set is {n_enum}/500.")
    w(f"Finished exact counts above {EXPAND_CUTOFF}: {summary['n_exact_over']}/500.")
    if summary.get("n_proved_over"):
        w(f"Proved `N_iso` > {EXPAND_CUTOFF} by streaming 20001 structures, without an exact count: {summary['n_proved_over']}/500.")
    w(f"Counts still unfinished after that stream: {summary['n_timeout']}/500.")
    unfinished = [r for r in items if r["count_status"] == "timeout"]
    if unfinished:
        zero = sum(1 for r in unfinished if not r.get("n_iso_lower_bound"))
        minh = min(int(r["heavy"]) for r in unfinished)
        w(f"Of those, {zero}/{len(unfinished)} emitted 0 structures before the clock.")
        w(f"The smallest unfinished formula has {minh} heavy atoms.")
    anions = [r for r in items if str(r["formula"]).endswith("-")]
    w(f"Surge rejected the formula: {summary['n_error']}/500.")
    if anions and len(anions) == summary["n_error"]:
        w(f"All {len(anions)} rejected formulas end in a charge mark that surge does not parse.")
    w(f"These categories partition the roster: {summary['n_under_20000']} enumerable + "
      f"{summary['n_exact_over']} exact counts above the cutoff + "
      f"{summary.get('n_proved_over', 0)} proved above the cutoff + "
      f"{summary['n_timeout']} unfinished + {summary['n_error']} rejected = 500.")
    if summary.get("min_exact_above"):
        above = summary["min_exact_above"]
        w(f"The smallest finished exact count above {EXPAND_CUTOFF} is {above['n_iso']} ({above['formula']}, {above['n_molecules']}/500).")
    w(f"Gold's connectivity key is in the generated pool for {n_ranked}/{n_enum} enumerable")
    w(f"molecules and absent for {len(absent)}/{n_enum}.")
    w("Ranks below use the molecules whose gold key is in the pool.")
    if absent:
        w("Absent gold means surge did not produce that connectivity at the default valence.")
    w("")
    w("## Distribution of gold spectroscopic rank")
    w("")
    if n_ranked == 0:
        w("No enumerable molecule had gold in the generated pool, so the rank CDF is empty.")
    else:
        w(f"Denominator: {n_ranked} molecules with gold in the surge pool.")
        w("")
        w("| gold rank | count | fraction of ranked |")
        w("|---:|---:|---:|")
        for cut, k, n in cdf_rows(ranks):
            w(f"| ≤ {cut} | {k} | {k}/{n} |")
        w("")
        w(f"Top 3: {sum(1 for r in ranks if r <= 3)}/{n_ranked}.")
        w(f"Top 10: {sum(1 for r in ranks if r <= 10)}/{n_ranked}.")
        w(f"Top 50: {sum(1 for r in ranks if r <= 50)}/{n_ranked}.")
        med = summary["median_rank"]
        w(f"Median gold rank: {med}.")
        w(f"Best rank: {min(ranks)}. Worst rank: {max(ranks)}.")
    w("")
    w("## Generation miss where the ranker already places gold in the top 10")
    w("")
    if not le10:
        w("No ranked molecule has gold rank ≤ 10, so this conditional fraction is 0/0.")
    else:
        w(f"Among molecules with gold rank ≤ 10, the locked deposit never proposed gold")
        w(f"at k≤3 in {len(miss)}/{len(le10)}.")
        top1 = sum(1 for r in le10 if r["llm_class"] == "top1")
        mid = sum(1 for r in le10 if r["llm_class"] == "proposed_not_top1")
        w(f"On the same {len(le10)} molecules the deposit's label is top-1 in {top1}/{len(le10)}")
        w(f"and proposed-but-not-top-1 in {mid}/{len(le10)}.")
        if miss:
            w("Each never-proposed molecule is a generation miss on this slice: surge")
            w("produced gold from the formula alone, the HOSE chamfer placed it at rank ≤ 10,")
            w("and the locked list of three SMILES does not contain it.")
        else:
            w("On this slice the deposit already proposed gold at k≤3 whenever the")
            w("HOSE chamfer placed gold at rank ≤ 10. The conditional generation-miss")
            w(f"count is {len(miss)}/{len(le10)}.")
    w("")
    w("## Printed lists on molecules with gold rank worse than 50")
    w("")
    if not gt50:
        w("No ranked molecule has gold rank > 50, so this conditional fraction is 0/0.")
    else:
        w(f"Among molecules with gold rank > 50, the printed 13C list is incompatible")
        w(f"with the gold constitution in {len(poor)}/{len(gt50)}.")
        w(f"The list is compatible with gold's carbon count and symmetry, and more than")
        w(f"50 other constitutions still match it at least as well, in {len(ambiguous)}/{len(gt50)}.")
        w(f"Gold chamfer is above the HOSE MAE ({HOSE_MAE} ppm) in {len(outside)}/{len(gt50)}")
        w(f"and at or below that MAE in {len(inside)}/{len(gt50)}.")
        w("Incompatible means the printed shift count exceeds the formula's carbon")
        w("count or gold's symmetry-distinct carbon count. The complementary count is")
        w("ambiguity: the list fits gold's carbon count and symmetry, and it fits more")
        w("than 50 other constitutions of the same formula at least as well.")
        spheres = summary.get("rank_gt50_spheres") or []
        for sp in spheres:
            w(f"For {sp['uid']} ({sp['formula']}), the matched constitution resolves")
            w(f"{sp['by_sphere']} of its {sp['n_carbon']} carbons. Gold chamfer is {sp['chamfer']:.3f} ppm")
            w(f"and the best other chamfer is {sp['best']:.3f} ppm.")
    w("")
    w("## Optional printed-list filter")
    w("")
    if n_ranked == 0:
        w("No ranked molecule, so the filter has no gold ranks.")
    else:
        rej = [r for r in ranked if not r["gold_kept"]]
        kept_ranks = [r["rank_filtered"] for r in ranked if r["rank_filtered"] is not None]
        empty = [r for r in ranked if r.get("n_kept") == 0]
        w(f"The peak-count and IR rules reject gold in {len(rej)}/{n_ranked} ranked molecules.")
        if empty:
            ids = ", ".join(r["uid"] for r in empty)
            w(f"The kept pool is empty for {len(empty)}/{n_ranked} ({ids}): every constitution fails a printed-list rule, so the filter has no ranking left.")
        if kept_ranks:
            w(f"Where gold survives the filter ({len(kept_ranks)}/{n_ranked}), filtered gold")
            w(f"rank is ≤ 3 in {sum(1 for r in kept_ranks if r <= 3)}/{len(kept_ranks)},")
            w(f"≤ 10 in {sum(1 for r in kept_ranks if r <= 10)}/{len(kept_ranks)}, and")
            w(f"≤ 50 in {sum(1 for r in kept_ranks if r <= 50)}/{len(kept_ranks)}.")
        w("Headline ranks above are the unfiltered chamfer ranks.")
    w("")
    w("## Higher-valence sensitivity")
    w("")
    w(f"Formulas with default `N_iso` ≤ {EXPAND_CUTOFF} that contain N, S, or P:")
    w(f"{summary['union_attempted']}.")
    w(f"Unions that finished with `N_iso` ≤ {EXPAND_CUTOFF}: {summary['union_enumerable']}.")
    w(f"Unions over the cutoff: {summary['union_over']}.")
    w(f"Unions that did not finish: {summary['union_incomplete']}.")
    if summary["union_ranked"]:
        ur = summary["union_ranked_stats"]
        w(f"On the {ur['n']} union pools that were ranked, gold is in the pool for")
        w(f"{ur['gold_in']}/{ur['n']}. Gold rank ≤ 10 in {ur['le10']}/{ur['gold_in']},")
        w(f"and the deposit never proposed gold for {ur['miss_le10']}/{ur['le10']} of those")
        w("with rank ≤ 10.")
    else:
        w("No higher-valence union stayed inside the cutoff, so there is no second rank table.")
    w("")
    w("## Reading")
    w("")
    w("The oracle proposer in this diagnostic is exhaustive only inside the cutoff.")
    w(f"That set is {n_enum}/500. On it, gold is in the surge pool for {n_ranked}/{n_enum}.")
    if le10:
        w(f"Where the HOSE chamfer already places gold at rank ≤ 10, the locked deposit")
        w(f"never proposed gold at k≤3 in {len(miss)}/{len(le10)}.")
    if gt50:
        w(f"Where gold rank is worse than 50, the printed 13C list is incompatible with")
        w(f"the gold constitution in {len(poor)}/{len(gt50)}, and gold's chamfer is above")
        w(f"the lookup MAE in {len(outside)}/{len(gt50)}.")
    w("Molecules outside the cutoff are not given a spectroscopic rank. An unfinished")
    w("count is not treated as a small `N_iso`.")
    w("")
    w("## Enumerable molecules")
    w("")
    w("| uid | formula | N_iso | pool | gold in pool | gold rank | ≤3 | ≤10 | ≤50 | LLM label | list incompatible | gold chamfer |")
    w("|---|---|---:|---:|---|---:|---|---|---|---|---|---:|")
    for r in sorted(enum, key=lambda x: (x["n_iso"], x["uid"])):
        rank = "" if r["rank"] is None else str(r["rank"])
        cham = "" if r["gold_chamfer"] is None else f"{r['gold_chamfer']:.3f}"
        w(f"| {r['uid']} | {r['formula']} | {r['n_iso']} | {r['n_pool']} | "
          f"{'yes' if r['gold_in_pool'] else 'no'} | {rank} | "
          f"{_yn(r.get('top3'))} | {_yn(r.get('top10'))} | {_yn(r.get('top50'))} | "
          f"{r['llm_class']} | {'yes' if r['list_incompatible'] else 'no'} | {cham} |")
    w("")
    w("Pool is the number of distinct connectivity keys ranked. `N_iso` is surge's")
    w("count before RDKit parsing. LLM label is the locked deposit: `top1`,")
    w("`proposed_not_top1`, or `never`.")
    w("")
    w("## Files")
    w("")
    w("- `roster.py` loads the 500 and checks 227/22/251.")
    w("- `run.py` counts, enumerates, ranks, and writes this report.")
    w("- `outputs/per_molecule.csv` and `outputs/summary.json` are the numeric source")
    w("  of every fraction above.")
    w("")
    text = "\n".join(lines) + "\n"
    (HERE / "REPORT.md").write_text(text)
    return text


def _yn(v):
    if v is None:
        return ""
    return "yes" if v else "no"


def main():
    t0 = time.time()
    self_check()
    # Confirm the rebuilt lookup is the one this process will score with.
    db = hp._load()
    if db.get("minn") != 3 or db.get("radii") != [4, 3, 2, 1]:
        raise SystemExit(f"unexpected HOSE db header { {k: db.get(k) for k in ('minn','radii')} }")
    rows = load()
    print(f"roster {len(rows)}", flush=True)
    wall = {"top1": 0, "proposed_not_top1": 0, "never": 0}
    for r in rows:
        wall[r["gold"]["llm_class"]] += 1

    meta = {}
    for r in rows:
        f = r["public"]["formula"]
        if f not in meta:
            counts = parse_formula(f)
            meta[f] = {
                "flags": surge_flags(f),
                "heavy": heavy_atoms(counts),
                "counts": counts,
            }
    print(f"unique formulas {len(meta)}", flush=True)
    counts = count_all(list(meta), meta)
    n_under_5k = sum(1 for f, rec in counts.items() if rec["status"] == "ok" and rec["n_iso"] <= START_CUTOFF)
    n_under_20k = sum(1 for f, rec in counts.items() if rec["status"] == "ok" and rec["n_iso"] <= EXPAND_CUTOFF)
    # Molecule-level, not formula-level.
    mol_under_5k = mol_under_20k = mol_over = mol_timeout = mol_error = 0
    for r in rows:
        rec = counts[r["public"]["formula"]]
        if rec["status"] == "ok" and rec["n_iso"] <= START_CUTOFF:
            mol_under_5k += 1
        if rec["status"] == "ok" and rec["n_iso"] <= EXPAND_CUTOFF:
            mol_under_20k += 1
        elif rec["status"] == "ok":
            mol_over += 1
        elif rec["status"] == "timeout":
            mol_timeout += 1
        else:
            mol_error += 1
    chosen = EXPAND_CUTOFF if mol_under_20k else START_CUTOFF
    print(f"molecules ≤5k {mol_under_5k} ≤20k {mol_under_20k} over {mol_over} "
          f"timeout {mol_timeout} error {mol_error}", flush=True)

    # Enumerate each formula at most once.
    pools = {}
    enum_formulas = [f for f, rec in counts.items()
                     if rec["status"] == "ok" and rec["n_iso"] <= chosen and rec["n_iso"] > 0]
    # n_iso == 0 is a finished count under the cutoff but an empty pool.
    zero = [f for f, rec in counts.items() if rec["status"] == "ok" and rec["n_iso"] == 0]
    print(f"enumerating {len(enum_formulas)} formulas; zero-count {len(zero)}", flush=True)
    for f in enum_formulas:
        t = time.time()
        got, status = enumerate_default(f, meta[f]["flags"], counts[f]["n_iso"])
        if status != "ok":
            print(f"  ENUM FAIL {f}: {status}", flush=True)
            counts[f] = {"formula": f, "status": "error", "n_iso": counts[f]["n_iso"],
                         "detail": f"enumerate {status}"}
            continue
        pools[f] = got
        print(f"  {f} N_iso={got['n_iso']} pool={len(got['pool'])} fail={got['fail']} "
              f"in {time.time()-t:.2f}s", flush=True)

    union_info = {}
    union_pools = {}
    union_attempted = union_enumerable = union_over = union_incomplete = 0
    for f in enum_formulas:
        if f not in pools:
            continue
        c = meta[f]["counts"]
        if c.get("N", 0) + c.get("S", 0) + c.get("P", 0) == 0:
            continue
        union_attempted += 1
        info = union_count(f, meta[f], counts[f]["n_iso"])
        union_info[f] = info
        print(f"  union {f} {info['status']} {info.get('n_iso')}", flush=True)
        if info["status"] == "over":
            union_over += 1
        elif info["status"] != "ok":
            union_incomplete += 1
        elif info["n_iso"] <= chosen:
            union_enumerable += 1
            got, status = enumerate_union(f, meta[f])
            if status != "ok":
                union_incomplete += 1
                union_enumerable -= 1
                union_info[f] = {"status": status, "n_iso": None}
            else:
                union_pools[f] = got
        else:
            union_over += 1

    items = []
    union_rows = []
    for r in rows:
        pub, gold = r["public"], r["gold"]
        f = pub["formula"]
        rec = counts[f]
        obs = unique_shifts(pub["c_nmr_shifts"])
        gmol = Chem.MolFromSmiles(gold["smiles"])
        gik = ik14_mol(gmol)
        if gik != gold["ik"]:
            raise SystemExit(f"{pub['uid']}: recomputed gold key {gik} != stored {gold['ik']}")
        n_carbon = meta[f]["counts"].get("C", 0)
        n_unique_gold = n_unique_carbons(gmol) if gmol is not None else None
        reasons = list_incompatible(len(obs), n_carbon, n_unique_gold)
        item = {
            "uid": pub["uid"],
            "arm": pub["arm"],
            "cohort": pub["cohort"],
            "qid": pub["qid"],
            "formula": f,
            "heavy": meta[f]["heavy"],
            "n_iso": rec.get("n_iso") if rec["status"] == "ok" else None,
            "count_status": rec["status"],
            "count_detail": rec.get("detail", ""),
            "llm_class": gold["llm_class"],
            "llm_proposed_k_le_3": gold["llm_class"] != "never",
            "n_obs_c13": len(obs),
            "n_carbon": n_carbon,
            "n_unique_c_gold": n_unique_gold,
            "list_incompatible": bool(reasons),
            "list_incompatible_reasons": ";".join(reasons),
            "gold_ik": gik,
            "enumerable": False,
            "gold_in_pool": False,
            "n_pool": None,
            "parse_fail": None,
            "rank": None,
            "top3": None,
            "top10": None,
            "top50": None,
            "gold_chamfer": None,
            "best_chamfer": None,
            "n_better": None,
            "n_tied": None,
            "n_kept": None,
            "rank_filtered": None,
            "gold_kept": None,
        }
        if rec["status"] == "ok" and rec["n_iso"] is not None and rec["n_iso"] <= chosen and f in pools:
            item["enumerable"] = True
            got = pools[f]
            item["parse_fail"] = got["fail"]
            scored = score_pool(got["pool"], obs, pub["ir_bands_cm-1"], gik)
            item.update({
                "n_pool": scored["n_pool"],
                "gold_in_pool": scored["rank"] is not None,
                "rank": scored["rank"],
                "gold_chamfer": scored["gold_chamfer"],
                "best_chamfer": scored["best_chamfer"],
                "n_better": scored["n_better"],
                "n_tied": scored["n_tied"],
                "n_kept": scored["n_kept"],
                "rank_filtered": scored["rank_filtered"],
                "gold_kept": scored["gold_kept"],
            })
            if scored["rank"] is not None:
                item["top3"] = scored["rank"] <= 3
                item["top10"] = scored["rank"] <= 10
                item["top50"] = scored["rank"] <= 50
        elif rec["status"] == "ok" and rec["n_iso"] == 0:
            item["enumerable"] = True
            item["n_pool"] = 0
            item["gold_in_pool"] = False
        items.append(item)

        if f in union_pools:
            uscored = score_pool(union_pools[f]["pool"], obs, pub["ir_bands_cm-1"], gik)
            union_rows.append({
                "uid": pub["uid"],
                "formula": f,
                "n_iso_union": union_info[f].get("n_iso"),
                "n_pool": uscored["n_pool"],
                "rank": uscored["rank"],
                "llm_class": gold["llm_class"],
                "gold_chamfer": uscored["gold_chamfer"],
            })

    ranked_ranks = [it["rank"] for it in items if it["rank"] is not None]
    median_rank = None
    if ranked_ranks:
        srt = sorted(ranked_ranks)
        mid = len(srt) // 2
        median_rank = srt[mid] if len(srt) % 2 else (srt[mid - 1] + srt[mid]) / 2

    u_gold = [u for u in union_rows if u["rank"] is not None]
    u_le10 = [u for u in u_gold if u["rank"] <= 10]
    union_ranked_stats = {
        "n": len(union_rows),
        "gold_in": len(u_gold),
        "le10": len(u_le10),
        "miss_le10": sum(1 for u in u_le10 if u["llm_class"] == "never"),
    }

    summary = {
        "n_roster": 500,
        "wall": wall,
        "chosen_cutoff": chosen,
        "start_cutoff": START_CUTOFF,
        "expand_cutoff": EXPAND_CUTOFF,
        "n_under_5000": mol_under_5k,
        "n_under_20000": mol_under_20k,
        "n_over": mol_over,
        "n_exact_over": mol_over,
        "n_proved_over": 0,
        "n_timeout": mol_timeout,
        "n_error": mol_error,
        "n_formulas": len(meta),
        "n_formulas_under_5000": n_under_5k,
        "n_formulas_under_20000": n_under_20k,
        "hose_mae": HOSE_MAE,
        "hose_median": 1.73,
        "hose_gate_source": "scripts/hose_predict.py build, random.seed(7), this environment",
        "surge_sha256": SURGE_SHA256,
        "median_rank": median_rank,
        "union_attempted": union_attempted,
        "union_enumerable": union_enumerable,
        "union_over": union_over,
        "union_incomplete": union_incomplete,
        "union_ranked": len(union_rows),
        "union_ranked_stats": union_ranked_stats,
        "seconds": round(time.time() - t0, 1),
    }
    # Molecule-level under-counts were computed before enumeration errors.
    # Recompute from items so a failed enumeration cannot inflate the enumerable set.
    summary["n_enumerable"] = sum(1 for it in items if it["enumerable"])
    summary["n_gold_in_pool"] = sum(1 for it in items if it["gold_in_pool"])
    summary["n_under_5000"] = sum(1 for it in items if it["n_iso"] is not None and it["n_iso"] <= START_CUTOFF
                                  and it["count_status"] == "ok")
    summary["n_under_20000"] = sum(1 for it in items if it["n_iso"] is not None and it["n_iso"] <= EXPAND_CUTOFF
                                   and it["count_status"] == "ok")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "formula_counts.json").write_text(json.dumps(counts, indent=2) + "\n")
    (OUT / "union_counts.json").write_text(json.dumps(union_info, indent=2) + "\n")
    (OUT / "union_ranks.json").write_text(json.dumps(union_rows, indent=2) + "\n")
    fields = list(items[0].keys())
    with open(OUT / "per_molecule.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)
    write_report(summary, items)
    print(json.dumps(summary, indent=2), flush=True)
    print(f"wrote {HERE / 'REPORT.md'}", flush=True)


def _sphere_phrase(counter):
    parts = []
    for key in [4, 3, 2, 1, None]:
        if counter.get(key):
            label = "prior" if key is None else f"r={key}"
            parts.append(f"{label} {counter[key]}")
    return ", ".join(parts)


def cmd_prove():
    """Prove N_iso > cutoff for formulas whose exact count did not finish."""
    counts = json.loads((OUT / "formula_counts.json").read_text())
    items = load_items_csv(OUT / "per_molecule.csv")
    summary = json.loads((OUT / "summary.json").read_text())
    pending = []
    seen = set()
    for it in items:
        f = it["formula"]
        if it["count_status"] == "timeout" and f not in seen:
            seen.add(f)
            pending.append(f)
    print(f"streaming {len(pending)} unfinished formulas", flush=True)
    proofs = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(prove_lower_bound, f, surge_flags(f)): f for f in pending}
        for i, fut in enumerate(as_completed(futs), 1):
            f = futs[fut]
            proofs[f] = fut.result()
            rec = proofs[f]
            if i % 40 == 0 or rec["status"] != "proved_over":
                print(f"  {i}/{len(pending)} {f} {rec['status']} bound={rec.get('lower_bound')} "
                      f"n={rec.get('n_iso')}", flush=True)
    new_small = []
    for it in items:
        rec = proofs.get(it["formula"])
        if rec is None:
            continue
        it["n_iso_lower_bound"] = rec.get("lower_bound")
        if rec["status"] == "proved_over":
            it["count_status"] = "proved_over"
            it["count_detail"] = f"streamed {rec['lower_bound']} structures"
        elif rec["status"] == "ok":
            it["count_status"] = "ok"
            it["n_iso"] = rec["n_iso"]
            it["count_detail"] = "exact count from a completed stream"
            if rec["n_iso"] <= EXPAND_CUTOFF:
                new_small.append(it["formula"])
        elif rec["status"] == "timeout":
            it["count_status"] = "timeout"
            it["count_detail"] = f"stream lower bound {rec.get('lower_bound')}"
        else:
            it["count_status"] = "error"
            it["count_detail"] = rec.get("detail", "")
        counts[it["formula"]] = {
            "formula": it["formula"],
            "status": it["count_status"],
            "n_iso": it["n_iso"],
            "lower_bound": it.get("n_iso_lower_bound"),
            "detail": it.get("count_detail", ""),
        }
    if new_small:
        raise SystemExit(
            "stream finished under the cutoff for "
            + ", ".join(sorted(set(new_small)))
            + "; enumerate these before publishing"
        )
    summary["n_exact_over"] = sum(
        1 for it in items if it["count_status"] == "ok" and it["n_iso"] is not None and it["n_iso"] > EXPAND_CUTOFF
    )
    summary["n_proved_over"] = sum(1 for it in items if it["count_status"] == "proved_over")
    summary["n_timeout"] = sum(1 for it in items if it["count_status"] == "timeout")
    summary["n_error"] = sum(1 for it in items if it["count_status"] == "error")
    summary["n_under_5000"] = sum(
        1 for it in items if it["count_status"] == "ok" and it["n_iso"] is not None and it["n_iso"] <= START_CUTOFF
    )
    summary["n_under_20000"] = sum(
        1 for it in items if it["count_status"] == "ok" and it["n_iso"] is not None and it["n_iso"] <= EXPAND_CUTOFF
    )
    above = [it for it in items if it["count_status"] == "ok" and it["n_iso"] is not None and it["n_iso"] > EXPAND_CUTOFF]
    if above:
        best = min(above, key=lambda it: it["n_iso"])
        summary["min_exact_above"] = {
            "formula": best["formula"],
            "n_iso": best["n_iso"],
            "n_molecules": sum(1 for it in above if it["formula"] == best["formula"] and it["n_iso"] == best["n_iso"]),
        }
        # molecules sharing that minimum count, not only the same formula if ties differ
        nmin = best["n_iso"]
        summary["min_exact_above"]["n_molecules"] = sum(1 for it in above if it["n_iso"] == nmin)
        summary["min_exact_above"]["formula"] = ", ".join(sorted({it["formula"] for it in above if it["n_iso"] == nmin}))
    # Sphere coverage for rank>50, on the surge structure that matched gold.
    spheres = []
    for it in items:
        if it.get("rank") is None or it["rank"] <= 50:
            continue
        got, status = enumerate_default(it["formula"], surge_flags(it["formula"]), it["n_iso"])
        if status != "ok":
            continue
        hit = None
        for ik, mol in got["pool"].items():
            if ik == it["gold_ik"]:
                hit = Chem.MolToSmiles(mol)
                break
        if hit is None:
            continue
        from collections import Counter
        rs = hp.resolved_sphere(hit)
        spheres.append({
            "uid": it["uid"],
            "formula": it["formula"],
            "by_sphere": _sphere_phrase(Counter(rs)),
            "n_carbon": len(rs),
            "chamfer": it["gold_chamfer"],
            "best": it["best_chamfer"],
        })
    summary["rank_gt50_spheres"] = spheres
    accounted = (summary["n_under_20000"] + summary["n_exact_over"] + summary["n_proved_over"]
                 + summary["n_timeout"] + summary["n_error"])
    if accounted != 500:
        raise SystemExit(f"status partition {accounted} != 500: {summary}")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "formula_counts.json").write_text(json.dumps(counts, indent=2) + "\n")
    (OUT / "stream_proofs.json").write_text(json.dumps(proofs, indent=2) + "\n")
    fields = list(items[0].keys())
    if "n_iso_lower_bound" not in fields:
        fields.append("n_iso_lower_bound")
    with open(OUT / "per_molecule.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items)
    write_report(summary, items)
    print(json.dumps({k: summary[k] for k in (
        "n_under_5000", "n_under_20000", "n_exact_over", "n_proved_over",
        "n_timeout", "n_error", "min_exact_above")}, indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prove":
        cmd_prove()
    else:
        main()
