#!/usr/bin/env python3
"""Build a paraphrase-invariant copy of the benchmark, to separate reading from retrieval.

The benchmark hands the model the spectral strings *exactly as printed* in an open-access
paper -- down to the source's own typography, e.g. `7.17-7.26 (m, 2 H, Ar-H)`. Worse, the
sampler selects for that: `benchmark_v2.sample2` keeps a compound only when
`raw_1h_for()` can recover its raw 1H payload from the PMC-OA full text. Every benchmark
compound therefore has its 1H string present verbatim in a document the model may have
read, and that string is a high-entropy fingerprint of the document.

This makes the formula-only control ambiguous in a way the paper cannot resolve from the
data it has. Masking the spectra removes the chemistry *and* the retrieval key at the same
time, so a collapse from 23% to 5% is what reading predicts and also what retrieval
predicts. Publication recency does not separate them either: with no disclosed training
cutoff, uniform memorisation predicts flatness too.

What separates them is a spectrum that means the same thing and reads differently. This
script emits one:

  * shifts are perturbed within reporting precision -- 1H by +/-0.02 ppm, 13C by +/-0.2 ppm,
    IR bands by +/-2 cm-1 by default. These are below the differences a chemist reasons
    from and far above the zero a string match needs.
  * typography is normalised: assignment annotations (`Ar-H`), trailing `ppm`, the `d`
    prefix and irregular spacing are removed, and every peak is re-emitted in one house
    format.
  * multiplicity, J values and integration are preserved exactly, because they carry
    connectivity information the task depends on.

What it bounds and what it does not: this defeats *verbatim* retrieval, not fuzzy
retrieval. A model that recognises the compound from approximate shift patterns will still
recognise it. So a null result here is a strong bound on the string-matching route and no
evidence at all about semantic memorisation; a positive result -- accuracy collapsing under
chemically null perturbation -- would be decisive against the paper's own headline. Say
which was found.

  python scripts/jitter_control.py data/benchmark_v3 --out data/jitter/benchmark_v3
  python scripts/jitter_control.py data/benchmark_v3 --seed 7 --h 0.05 --c 0.4 --ir 5
"""
import argparse
import json
import os
import random
import re

# "3.86 (s, 3H)" / "7.17-7.26 (m, 2 H, Ar-H)" / "0.11 (s, 9H)"
PEAK = re.compile(r"""
    (?P<shift>\d+\.?\d*)                  # leading shift
    (?:\s*[-–]\s*(?P<shift2>\d+\.?\d*))?  # optional range
    \s*\((?P<body>[^)]*)\)                # the parenthetical
""", re.X)
INT = re.compile(r"(\d+)\s*([HC])\b")
JVAL = re.compile(r"J\s*=\s*([\d.,\s and]+?)\s*Hz", re.I)


def _fmt(x, nd):
    return f"{x:.{nd}f}"


def jitter_nmr(s, amp, nucleus, rng):
    """Re-emit every peak with a perturbed shift and house typography.

    Multiplicity, J and integration are copied through untouched -- they are connectivity
    evidence, and perturbing them would change the problem rather than its wording."""
    nd = 2 if nucleus == "H" else 1
    out = []
    for m in PEAK.finditer(s):
        d = float(m.group("shift")) + rng.uniform(-amp, amp)
        body = m.group("body")
        mult = body.split(",")[0].strip()
        # keep only multiplicity, J and integration; drop assignments like "Ar-H"
        parts = [mult] if mult and not mult[0].isdigit() else []
        j = JVAL.search(body)
        if j:
            parts.append(f"J = {j.group(1).strip()} Hz")
        i = INT.search(body)
        if i:
            parts.append(f"{i.group(1)}{i.group(2)}")
        out.append(f"{_fmt(d, nd)} ({', '.join(parts)})" if parts else _fmt(d, nd))
    return ", ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="directory holding questions2.jsonl")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--h", type=float, default=0.02, help="1H jitter, ppm")
    ap.add_argument("--c", type=float, default=0.2, help="13C jitter, ppm")
    ap.add_argument("--ir", type=float, default=2.0, help="IR jitter, cm-1")
    a = ap.parse_args()
    out = a.out or os.path.join("data/jitter", os.path.basename(a.src.rstrip("/")))
    os.makedirs(out, exist_ok=True)
    rng = random.Random(a.seed)

    n = 0
    identical = 0
    with open(f"{out}/questions2.jsonl", "w") as w:
        for line in open(f"{a.src}/questions2.jsonl"):
            q = json.loads(line)
            before = (q.get("h_nmr", ""), q.get("c_nmr", ""),
                      tuple(q.get("ir_bands_cm-1") or []))
            q["h_nmr"] = jitter_nmr(q.get("h_nmr", ""), a.h, "H", rng)
            q["c_nmr"] = jitter_nmr(q.get("c_nmr", ""), a.c, "C", rng)
            q["ir_bands_cm-1"] = [round(b + rng.uniform(-a.ir, a.ir), 1)
                                  for b in (q.get("ir_bands_cm-1") or [])]
            after = (q["h_nmr"], q["c_nmr"], tuple(q["ir_bands_cm-1"]))
            identical += sum(1 for x, y in zip(before, after) if x == y)
            n += 1
            w.write(json.dumps(q, ensure_ascii=False) + "\n")

    # The answer key is deliberately NOT copied. It is the same key as the source round --
    # same compounds, differently worded spectra -- and a second copy on disk is a second
    # thing an agent with repository access can read. Record where it lives instead.
    json.dump({"answers": f"{a.src}/answers2.jsonl", "seed": a.seed,
               "jitter_ppm_1h": a.h, "jitter_ppm_13c": a.c, "jitter_cm1_ir": a.ir},
              open(f"{out}/source.json", "w"), indent=1)

    print(f"wrote {n} jittered questions -> {out}/questions2.jsonl")
    print(f"  1H +/-{a.h} ppm, 13C +/-{a.c} ppm, IR +/-{a.ir} cm-1, seed {a.seed}")
    print(f"  fields left byte-identical to the source: {identical} of {3 * n}")
    if identical:
        print("  ^ a nonzero count means some field carried no parseable peak; check it,"
              " because an unjittered field leaves the fingerprint intact")


if __name__ == "__main__":
    main()
