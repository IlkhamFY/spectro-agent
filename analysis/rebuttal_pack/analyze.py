"""Score deposited predictions. Assert the locked integers before anything else is written."""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from chem import (
    HAC_ORDER,
    RING_ORDER,
    formula_of,
    functional_groups,
    hac_bin,
    mces,
    mol,
    ring_class,
    score_cands,
    tanimoto,
)
from stats import discordance, holm, mcnemar_p, paired_diff, wilson


def _rate(flags):
    flags = list(flags)
    k = int(sum(bool(x) for x in flags))
    n = len(flags)
    p, lo, hi = wilson(k, n)
    return {"k": k, "n": n, "p": p, "lo": lo, "hi": hi}


def _arm_flags(items, arm, key):
    return [it[key] for it in items if it["arm"] == arm]


def _group_rows(items, key, order, pred_key):
    rows = []
    buckets = defaultdict(list)
    for it in items:
        buckets[it[key]].append(it[pred_key])
    keys = list(order) + [k for k in buckets if k not in order]
    for name in keys:
        if name not in buckets:
            continue
        row = _rate(buckets[name])
        row["name"] = name
        rows.append(row)
    return rows


def score(bundle):
    headline = bundle["headline"]
    for it in headline:
        it["opus_top1"], it["opus_rec"] = score_cands(it["ik"], it["opus"])
        it["nmr_top1"], it["nmr_rec"] = score_cands(it["ik"], it["nmr"])
        top = it["opus"][0] if it["opus"] else None
        it["opus_formula_ok"] = formula_of(top) == it["formula"] and top is not None
        it["nmr_formula_ok"] = formula_of(it["nmr"][0] if it["nmr"] else None) == it["formula"]
        it["hac_bin"] = hac_bin(it["hac"])
        m = mol(it["smiles"])
        it["ring"] = ring_class(m) if m is not None else "unparsed"
        it["fgs"] = functional_groups(m) if m is not None else []
        it["tani"] = tanimoto(it["smiles"], top) if top else None
        it["mces"] = None

    # Locked integers. Stop if the join or the candidate files drifted.
    checks = {
        "locked194_top1": (sum(it["opus_top1"] for it in headline if it["arm"] == "locked194"), 55),
        "locked194_rec": (sum(it["opus_rec"] for it in headline if it["arm"] == "locked194"), 65),
        "plus106_top1": (sum(it["opus_top1"] for it in headline if it["arm"] == "plus106"), 63),
        "plus106_rec": (sum(it["opus_rec"] for it in headline if it["arm"] == "plus106"), 68),
        "expand200_top1": (sum(it["opus_top1"] for it in headline if it["arm"] == "expand200"), 109),
        "expand200_rec": (sum(it["opus_rec"] for it in headline if it["arm"] == "expand200"), 116),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if bad or len(headline) != 500:
        raise SystemExit(f"locked integers did not reproduce: {bad} n={len(headline)}")

    # Near-miss descriptors only where rank-1 is wrong. This is distance to the truth.
    for it in headline:
        if it["opus_top1"] or not it["opus"]:
            continue
        it["mces"] = mces(it["smiles"], it["opus"][0])

    simple = [it for it in headline if it["difficulty"] == "simple"]
    complex_ = [it for it in headline if it["difficulty"] == "complex"]
    if (len(simple), len(complex_)) != (248, 252):
        raise SystemExit(f"strata drifted: simple {len(simple)} complex {len(complex_)}")
    if sum(it["opus_top1"] for it in simple) != 161 or sum(it["opus_rec"] for it in simple) != 172:
        raise SystemExit("simple stratum does not match 161/248 and 172/248")
    if sum(it["opus_top1"] for it in complex_) != 66 or sum(it["opus_rec"] for it in complex_) != 77:
        raise SystemExit("complex stratum does not match 66/252 and 77/252")

    # NMRTrans official hits, as a cross-check of our join. Not a second gold source.
    mismatch = 0
    for it in headline:
        off = bundle["nmr_official"].get(it["uid"])
        if off is None:
            mismatch += 1
            continue
        if off != (it["nmr_top1"], it["nmr_rec"]):
            mismatch += 1

    # Sensitivity pools. Rest of expand-500 is scored the same way and is not the headline.
    for it in bundle["expand500_rest"]:
        it["opus_top1"], it["opus_rec"] = score_cands(it["ik"], it["opus"])
    e_all = bundle["expand500_all"]
    clean_ids = set(bundle["expand500_clean"])
    e_clean = [it for it in e_all if it["qid"] in clean_ids]

    def _sum(rows, key):
        return int(sum(it[key] for it in rows))

    h = headline
    arms = {
        "n500": h,
        "locked194": [it for it in h if it["arm"] == "locked194"],
        "plus106": [it for it in h if it["arm"] == "plus106"],
        "expand200": [it for it in h if it["arm"] == "expand200"],
        "simple": simple,
        "complex": complex_,
    }
    # 524 = 194 + 106 + clean 224. 530 = 194 + 106 + all 230.
    base_300 = arms["locked194"] + arms["plus106"]
    pool_524 = base_300 + e_clean
    pool_530 = base_300 + e_all

    def pack(name, rows):
        top = _rate(it["opus_top1"] for it in rows)
        rec = _rate(it["opus_rec"] for it in rows)
        top["name"] = name
        top["metric"] = "top-1"
        rec_row = dict(rec)
        rec_row["name"] = name
        rec_row["metric"] = "top-3"
        return [top, rec_row]

    headline_rows = []
    for name, rows in (
        ("Opus n=500", h),
        ("Opus simple", simple),
        ("Opus complex", complex_),
        ("Opus locked 194", arms["locked194"]),
        ("Opus +106", arms["plus106"]),
        ("Opus expand-500 200", arms["expand200"]),
        ("Opus n=300 (194+106)", base_300),
        ("Opus n=524 sensitivity", pool_524),
        ("Opus n=530 sensitivity", pool_530),
    ):
        headline_rows.extend(pack(name, rows))
    nmr_top = _rate(it["nmr_top1"] for it in h)
    nmr_rec = _rate(it["nmr_rec"] for it in h)
    nmr_top["name"] = "NMRTrans n=500"
    nmr_top["metric"] = "top-1"
    nmr_rec = dict(nmr_rec)
    nmr_rec["name"] = "NMRTrans n=500"
    nmr_rec["metric"] = "top-3"
    headline_rows.extend([nmr_top, nmr_rec])

    # Self-rank and wall, from locked counts.
    extra_props = [
        {"name": "Opus self-rank | recalled", "metric": "conditional", **dict(zip(("p", "lo", "hi"), wilson(227, 249))), "k": 227, "n": 249},
        {"name": "fverify verified", "metric": "wall", **dict(zip(("p", "lo", "hi"), wilson(204, 500))), "k": 204, "n": 500},
        {"name": "fverify misranked", "metric": "wall", **dict(zip(("p", "lo", "hi"), wilson(45, 500))), "k": 45, "n": 500},
        {"name": "fverify never proposed", "metric": "wall", **dict(zip(("p", "lo", "hi"), wilson(251, 500))), "k": 251, "n": 500},
        {"name": "fverify verified | recalled", "metric": "conditional", **dict(zip(("p", "lo", "hi"), wilson(204, 249))), "k": 204, "n": 249},
    ]

    # Paired Opus vs NMRTrans on all 500.
    a = np.array([it["opus_top1"] for it in h])
    b = np.array([it["nmr_top1"] for it in h])
    d, dlo, dhi = paired_diff(a, b)
    b_cell, c_cell = discordance(a, b)
    paired = [{
        "family": "n500",
        "a": "Opus",
        "b": "NMRTrans",
        "n": 500,
        "metric": "top-1",
        "diff": d,
        "lo": dlo,
        "hi": dhi,
        "b_only_a": b_cell,
        "c_only_b": c_cell,
        "p": mcnemar_p(b_cell, c_cell),
    }]
    ar = np.array([it["opus_rec"] for it in h])
    br = np.array([it["nmr_rec"] for it in h])
    d, dlo, dhi = paired_diff(ar, br, seed=1)
    b_cell, c_cell = discordance(ar, br)
    paired.append({
        "family": "n500",
        "a": "Opus",
        "b": "NMRTrans",
        "n": 500,
        "metric": "top-3",
        "diff": d,
        "lo": dlo,
        "hi": dhi,
        "b_only_a": b_cell,
        "c_only_b": c_cell,
        "p": mcnemar_p(b_cell, c_cell),
    })

    by_uid = {it["uid"]: it for it in h}
    mid_to_uid = bundle["mid_to_uid"]
    uid_to_mid = {v: k for k, v in mid_to_uid.items()}

    def flags_for(cands_by_mid, key="top1"):
        out = []
        mids = []
        for mid, uid in sorted(mid_to_uid.items()):
            it = by_uid[uid]
            cands = cands_by_mid.get(mid) or []
            top1, rec = score_cands(it["ik"], cands)
            formula_ok = formula_of(cands[0] if cands else None) == it["formula"]
            out.append({"mid": mid, "uid": uid, "top1": top1, "rec": rec, "formula_ok": formula_ok})
            mids.append(mid)
        return out

    # Opus production predictions on the same 60, keyed by M-id.
    opus60 = {}
    for uid, mid in uid_to_mid.items():
        opus60[mid] = by_uid[uid]["opus"]
    model60 = {"Opus": flags_for(opus60)}
    for name, raw in bundle["sweep"].items():
        model60[name] = flags_for(raw)
    model60_rows = []
    for name, rows in model60.items():
        for metric, field in (("top-1", "top1"), ("top-3", "rec"), ("formula", "formula_ok")):
            rate = _rate(r[field] for r in rows)
            rate["name"] = name
            rate["metric"] = metric
            model60_rows.append(rate)

    # Paired tests among the models that actually return structures on all 60.
    focus = [m for m in ("Opus", "grok-4.6", "gemini-3.7-flash", "gpt-5.6-sol") if m in model60]
    family = []
    for i, a_name in enumerate(focus):
        for b_name in focus[i + 1:]:
            aa = np.array([r["top1"] for r in model60[a_name]])
            bb = np.array([r["top1"] for r in model60[b_name]])
            # Align on mid order. flags_for sorts mids, so the vectors match.
            d, dlo, dhi = paired_diff(aa, bb, seed=2)
            b_cell, c_cell = discordance(aa, bb)
            family.append({
                "family": "cross60",
                "a": a_name,
                "b": b_name,
                "n": len(aa),
                "metric": "top-1",
                "diff": d,
                "lo": dlo,
                "hi": dhi,
                "b_only_a": b_cell,
                "c_only_b": c_cell,
                "p": mcnemar_p(b_cell, c_cell),
            })
    holm(family)
    paired.extend(family)

    # Grok original vs clean clone, same 60. Blindness check, not a training-set Tanimoto.
    if "grok-4.6" in model60 and "grok-4.6-clean" in model60:
        aa = np.array([r["top1"] for r in model60["grok-4.6"]])
        bb = np.array([r["top1"] for r in model60["grok-4.6-clean"]])
        d, dlo, dhi = paired_diff(aa, bb, seed=3)
        b_cell, c_cell = discordance(aa, bb)
        paired.append({
            "family": "grok_clean",
            "a": "grok-4.6",
            "b": "grok-4.6-clean",
            "n": len(aa),
            "metric": "top-1",
            "diff": d,
            "lo": dlo,
            "hi": dhi,
            "b_only_a": b_cell,
            "c_only_b": c_cell,
            "p": mcnemar_p(b_cell, c_cell),
        })

    # Ladder on the 24 main-round qids.
    subset, ladder_raw = bundle["ladder"]
    main_by_qid = {it["qid"]: it for it in h if it["cohort"] == "locked-main"}
    ladder_flags = {}
    ladder_rows = []
    for model, pred in ladder_raw.items():
        flags = []
        for q in subset:
            it = main_by_qid.get(q)
            cands = pred.get(q) or []
            if it is None or not cands:
                flags.append(None)
                continue
            top1, rec = score_cands(it["ik"], cands)
            flags.append({"qid": q, "top1": top1, "rec": rec})
        ladder_flags[model] = flags
        present = [f for f in flags if f is not None]
        if not present:
            continue
        for metric, field in (("top-1", "top1"), ("top-3", "rec")):
            rate = _rate(f[field] for f in present)
            rate["name"] = model
            rate["metric"] = metric
            rate["covered"] = len(present)
            ladder_rows.append(rate)
    ladder_family = []
    order = [m for m in ("Fable", "Opus", "Sonnet", "Haiku") if m in ladder_flags]
    # Pair only on qids scored for every model.
    common = []
    for i, q in enumerate(subset):
        if all(ladder_flags[m][i] is not None for m in order):
            common.append(i)
    for i, a_name in enumerate(order):
        for b_name in order[i + 1:]:
            aa = np.array([ladder_flags[a_name][j]["top1"] for j in common])
            bb = np.array([ladder_flags[b_name][j]["top1"] for j in common])
            d, dlo, dhi = paired_diff(aa, bb, seed=4)
            b_cell, c_cell = discordance(aa, bb)
            ladder_family.append({
                "family": "ladder24",
                "a": a_name,
                "b": b_name,
                "n": len(common),
                "metric": "top-1",
                "diff": d,
                "lo": dlo,
                "hi": dhi,
                "b_only_a": b_cell,
                "c_only_b": c_cell,
                "p": mcnemar_p(b_cell, c_cell),
            })
    holm(ladder_family)
    paired.extend(ladder_family)

    # Modality campaign. full vs each other condition, paired.
    ablation = bundle["ablation"]
    ab_flags = {cond: flags_for(raw) for cond, raw in ablation.items()}
    # committed June-style files, separate from the 2026-09-23 campaign
    committed = {cond: flags_for(raw) for cond, raw in bundle["committed_modality"].items()}
    ab_rows = []
    for label, table in (("campaign", ab_flags), ("committed", committed)):
        for cond, rows in table.items():
            for metric, field in (("top-1", "top1"), ("top-3", "rec")):
                rate = _rate(r[field] for r in rows)
                rate["name"] = cond
                rate["metric"] = metric
                rate["set"] = label
                ab_rows.append(rate)
    ab_tests = []
    if "full" in ab_flags:
        base = ab_flags["full"]
        for cond, rows in ab_flags.items():
            if cond == "full":
                continue
            aa = np.array([r["top1"] for r in base])
            bb = np.array([r["top1"] for r in rows])
            d, dlo, dhi = paired_diff(aa, bb, seed=5)
            b_cell, c_cell = discordance(aa, bb)
            ab_tests.append({
                "family": "modality",
                "a": "full",
                "b": cond,
                "n": len(aa),
                "metric": "top-1",
                "diff": d,
                "lo": dlo,
                "hi": dhi,
                "b_only_a": b_cell,
                "c_only_b": c_cell,
                "p": mcnemar_p(b_cell, c_cell),
            })
        holm(ab_tests)
    paired.extend(ab_tests)

    # Breakdowns on the headline Opus run.
    heavy = _group_rows(h, "hac_bin", HAC_ORDER, "opus_top1")
    heavy_nmr = {r["name"]: r for r in _group_rows(h, "hac_bin", HAC_ORDER, "nmr_top1")}
    for r in heavy:
        r["nmr"] = heavy_nmr.get(r["name"])
    rings = _group_rows(h, "ring", RING_ORDER, "opus_top1")
    fg_rows = []
    for name in [n for n, _ in __import__("chem", fromlist=["FG_SMARTS"]).FG_SMARTS]:
        members = [it for it in h if name in it["fgs"]]
        if len(members) < 15:
            continue
        rate = _rate(it["opus_top1"] for it in members)
        rate["name"] = name
        fg_rows.append(rate)
    fg_rows.sort(key=lambda r: r["p"])

    misses = [it for it in h if not it["opus_top1"]]
    tanis = [it["tani"] for it in misses if it["tani"] is not None]
    sims = [it["mces"]["sim"] for it in misses if it["mces"] and it["mces"]["sim"] is not None]
    dists = [it["mces"]["dist"] for it in misses if it["mces"]]
    formula_miss = sum(1 for it in misses if it["opus_formula_ok"])
    close_07 = sum(1 for t in tanis if t >= 0.7)
    close_085 = sum(1 for t in tanis if t >= 0.85)
    in_list = sum(1 for it in misses if it["opus_rec"])  # right structure at rank 2 or 3

    def _median(xs):
        if not xs:
            return None
        return float(np.median(xs))

    near = {
        "n_miss": len(misses),
        "n_tani": len(tanis),
        "median_tani": _median(tanis),
        "mean_tani": float(np.mean(tanis)) if tanis else None,
        "tani_ge_0.7": close_07,
        "tani_ge_0.85": close_085,
        "n_mces": len(sims),
        "median_mces_sim": _median(sims),
        "median_mces_dist": _median(dists),
        "formula_ok_misses": formula_miss,
        "formula_ok_all": int(sum(it["opus_formula_ok"] for it in h)),
        "right_structure_at_rank_2_or_3": in_list,
        "tanis": tanis,
        "mces_sims": sims,
        "mces_dists": dists,
    }

    modality_avail = {
        "n": len(h),
        "missing_ir": int(sum(not it["has_ir"] for it in h)),
        "missing_h": int(sum(not it["has_h"] for it in h)),
        "missing_c": int(sum(not it["has_c"] for it in h)),
    }

    # Repeated samples? A qid inside one arm should appear once.
    seen = defaultdict(int)
    for it in h:
        seen[it["uid"]] += 1
    repeats = {k: v for k, v in seen.items() if v != 1}

    return {
        "headline_rows": headline_rows,
        "extra_props": extra_props,
        "paired": paired,
        "model60_rows": model60_rows,
        "model60": model60,
        "ladder_rows": ladder_rows,
        "ablation_rows": ab_rows,
        "heavy": heavy,
        "rings": rings,
        "fg": fg_rows,
        "near": near,
        "modality_avail": modality_avail,
        "nmr_mismatch": mismatch,
        "repeats": len(repeats),
        "pool_524_top": _sum(pool_524, "opus_top1"),
        "pool_524_rec": _sum(pool_524, "opus_rec"),
        "pool_524_n": len(pool_524),
        "pool_530_top": _sum(pool_530, "opus_top1"),
        "pool_530_rec": _sum(pool_530, "opus_rec"),
        "pool_530_n": len(pool_530),
        "e_clean_n": len(e_clean),
        "e_all_n": len(e_all),
    }
