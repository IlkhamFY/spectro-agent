#!/usr/bin/env python3
"""
Build the EXPERIMENTAL training manifest + fixed train/val/test split + a
sim-extended SELFIES vocab for IRSpectra-Bench transfer experiments.

Design (see benchmark_paper/initial_dev/CONTRIBUTIONS.md):
  - TARGET  : SELFIES (valid by construction), regenerated from canonical SMILES.
  - TEST    : the benchmark compounds (unique IK-14). Inputs (h_nmr/c_nmr) come
              from each cohort's questions2.jsonl — i.e. exactly what the LLM saw —
              NOT re-pulled from irexp. Targets from answers2.jsonl SMILES.
  - TRAIN/VAL: irexp_resolved records with BOTH H+C NMR, minus every benchmark
              IK-14, deduped to one record per IK-14 (keep richest C-NMR).
  - VOCAB   : sim SELFIES vocab IDs preserved (so a sim-pretrained checkpoint's
              embedding rows still align for the FINE-TUNE run); experimental-only
              tokens appended with fresh IDs; max_len raised to cover all of TEST.
              The SAME vocab/cache then serves both from-scratch and fine-tune.

Outputs (data/experimental/):
  manifest.jsonl        ordered rows; row i  ==  cache row i (built next step)
  vocab.json            sim-extended SELFIES vocab (SELFIESTokenizer schema)
  train_indices.npy / val_indices.npy / test_indices.npy   (contiguous over manifest)
  split_stats.json      provenance + the OOV/length/dedup accounting

This script is deterministic (seed=42) and does NOT tokenize NMR — that is the
next step (cache build), which consumes manifest.jsonl in order.
"""
import json, gzip, glob, os, re
import numpy as np
import selfies as sf
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")

SEED        = 42
VAL_FRAC    = 0.10
SPECTRO     = "/home/rudra/spectro_v2"
BENCH       = "/home/rudra/Spectro/benchmark_paper/initial_dev/data"
OUT         = f"{SPECTRO}/data/experimental"
SIM_VOCAB   = f"{SPECTRO}/data/simulated_data/tokenized_selfies/vocab.json"
# cohort priority when an IK-14 appears in >1 benchmark cohort (keep the higher one)
COHORT_PRIORITY = ["benchmark_main", "benchmark_v3", "benchmark_v2_ctrl",
                   "benchmark_v2", "benchmark_electrolyte"]

os.makedirs(OUT, exist_ok=True)
_num = re.compile(r'-?\d+\.?\d*')

def canon(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    return Chem.MolToSmiles(m) if m else None

def to_selfies(smi):
    cs = canon(smi)
    if not cs:
        return None, None
    try:
        return sf.encoder(cs), cs
    except Exception:
        return None, cs

def toks(s):
    try:
        return list(sf.split_selfies(s))
    except Exception:
        return None

def has(x):
    return bool(x and str(x).strip())

# ───────────────────────── 1. TEST rows (benchmark, what the LLM saw) ──────────
test_by_ik = {}          # ik14 -> row (best cohort)
cohort_rank = {c: i for i, c in enumerate(COHORT_PRIORITY)}
test_unparseable = []
for qf in sorted(glob.glob(f"{BENCH}/benchmark_*/questions2.jsonl")):
    cohort = qf.split("/")[-2]
    af = qf.replace("questions2", "answers2")
    if not os.path.exists(af):
        continue
    ans = {json.loads(l)["qid"]: json.loads(l) for l in open(af)}
    for l in open(qf):
        q = json.loads(l); qid = q["qid"]; a = ans.get(qid)
        if not a or not a.get("inchikey"):
            continue
        ik = a["inchikey"][:14]
        s, cs = to_selfies(a["smiles"])
        if s is None:
            test_unparseable.append((cohort, qid, a.get("smiles")))
            continue
        row = {"source": "benchmark", "cohort": cohort, "qid": qid,
               "ik14": ik, "inchikey": a["inchikey"], "smiles": cs, "selfies": s,
               "h_nmr": q.get("h_nmr", ""), "c_nmr": q.get("c_nmr", "")}
        # keep the highest-priority cohort for a duplicated IK-14
        if ik not in test_by_ik or cohort_rank.get(cohort, 99) < cohort_rank.get(test_by_ik[ik]["cohort"], 99):
            if ik in test_by_ik:
                row.setdefault("also_in", []).append(test_by_ik[ik]["cohort"])
            test_by_ik[ik] = row
test_rows = list(test_by_ik.values())
bench_ik = set(test_by_ik.keys())

# ───────────────────────── 2. TRAIN/VAL pool (irexp minus benchmark) ───────────
recs = [json.loads(l) for l in gzip.open(f"{BENCH}/irexp_resolved/irexp_resolved.jsonl.gz", "rt")]
# keep one record per IK-14: richest C-NMR (most shifts), tiebreak by id for determinism
best = {}
for r in recs:
    if not (has(r.get("h_nmr")) and has(r.get("c_nmr")) and r.get("inchikey")):
        continue
    ik = r["inchikey"][:14]
    if ik in bench_ik:
        continue
    score = (len(_num.findall(r["c_nmr"])), len(_num.findall(r["h_nmr"])), r.get("id", ""))
    if ik not in best or score > best[ik][0]:
        best[ik] = (score, r)

pool_rows = []
pool_bad = 0
for ik, (_, r) in best.items():
    s, cs = to_selfies(r["smiles"])
    if s is None:
        pool_bad += 1
        continue
    pool_rows.append({"source": "irexp", "cohort": None, "qid": None,
                      "ik14": ik, "inchikey": r["inchikey"], "smiles": cs, "selfies": s,
                      "h_nmr": r["h_nmr"], "c_nmr": r["c_nmr"],
                      "source_doi": r.get("source_doi", "")})

# ───────────────────────── 3. max_len + length filtering ───────────────────────
def slen(row):
    t = toks(row["selfies"]); return (len(t) + 2) if t else 10**9

test_lens = [slen(r) for r in test_rows]
test_max = max(test_lens)
pool_lens = np.array([slen(r) for r in pool_rows])
p99 = int(np.percentile(pool_lens, 99))
MAX_LEN = int(max(test_max, p99))                 # never truncate a TEST target
kept_pool = [r for r, L in zip(pool_rows, pool_lens) if L <= MAX_LEN]
dropped_long = len(pool_rows) - len(kept_pool)

# ───────────────────────── 4. sim-extended vocab ──────────────────────────────
simv = json.load(open(SIM_VOCAB))
tok2idx = dict(simv["token2idx"])                 # preserve sim IDs (0..54)
all_chem = set()
for r in kept_pool + test_rows:
    all_chem.update(toks(r["selfies"]) or [])
new_tokens = sorted(t for t in all_chem if t not in tok2idx)
nxt = max(tok2idx.values()) + 1
for t in new_tokens:
    tok2idx[t] = nxt; nxt += 1
vocab = {
    "token2idx": tok2idx,
    "idx2token": {str(i): t for t, i in tok2idx.items()},
    "special_tokens": simv["special_tokens"],
    "method": simv.get("method", "regex"),
    "vocab_len": len(tok2idx),
    "max_len": MAX_LEN,
}

# ───────────────────────── 5. shuffle pool → train/val; append test ────────────
rng = np.random.default_rng(SEED)
order = rng.permutation(len(kept_pool))
n_val = int(len(kept_pool) * VAL_FRAC)
val_sel = set(order[:n_val].tolist())
train_rows = [kept_pool[i] for i in range(len(kept_pool)) if i not in val_sel]
val_rows   = [kept_pool[i] for i in range(len(kept_pool)) if i in val_sel]

manifest = train_rows + val_rows + test_rows
for i, r in enumerate(manifest):
    r["row_idx"] = i
n_tr, n_va, n_te = len(train_rows), len(val_rows), len(test_rows)
train_idx = np.arange(0, n_tr)
val_idx   = np.arange(n_tr, n_tr + n_va)
test_idx  = np.arange(n_tr + n_va, n_tr + n_va + n_te)

# ───────────────────────── 6. write outputs ───────────────────────────────────
with open(f"{OUT}/manifest.jsonl", "w") as f:
    for r in manifest:
        f.write(json.dumps(r) + "\n")
json.dump(vocab, open(f"{OUT}/vocab.json", "w"), indent=2)
np.save(f"{OUT}/train_indices.npy", train_idx)
np.save(f"{OUT}/val_indices.npy",   val_idx)
np.save(f"{OUT}/test_indices.npy",  test_idx)

# sanity: 0 OOV by construction; verify test reachability
def has_oov(r):
    return any(t not in tok2idx for t in (toks(r["selfies"]) or ["<unk>"]))
test_oov  = sum(has_oov(r) for r in test_rows)
test_cohorts = {}
for r in test_rows:
    test_cohorts[r["cohort"]] = test_cohorts.get(r["cohort"], 0) + 1

stats = {
    "seed": SEED, "target": "selfies", "use_hsqc": False,
    "MAX_LEN": MAX_LEN, "test_max_selfies_len": test_max, "pool_p99_len": p99,
    "vocab_size": len(tok2idx), "sim_vocab_size": len(simv["token2idx"]),
    "new_tokens_count": len(new_tokens), "new_tokens": new_tokens,
    "n_train": n_tr, "n_val": n_va, "n_test": n_te,
    "test_cohorts": test_cohorts,
    "test_oov_after_extend": test_oov,        # must be 0
    "test_unparseable": len(test_unparseable),
    "pool_records_before_dedup": sum(1 for r in recs if has(r.get("h_nmr")) and has(r.get("c_nmr")) and r.get("inchikey") and r["inchikey"][:14] not in bench_ik),
    "pool_unique_ik14": len(best),
    "pool_unparseable_selfies": pool_bad,
    "pool_dropped_too_long": dropped_long,
    "benchmark_unique_ik14_heldout": len(bench_ik),
}
json.dump(stats, open(f"{OUT}/split_stats.json", "w"), indent=2)

print("=== EXPERIMENTAL MANIFEST BUILT ===")
for k, v in stats.items():
    if k == "new_tokens":
        print(f"  {k:32s}: {v}")
    else:
        print(f"  {k:32s}: {v}")
print(f"\nwrote: {OUT}/manifest.jsonl  vocab.json  {{train,val,test}}_indices.npy  split_stats.json")
assert test_oov == 0, "TEST has OOV after vocab extension — investigate!"
print("OK: 0 test OOV (every benchmark answer is reachable).")
