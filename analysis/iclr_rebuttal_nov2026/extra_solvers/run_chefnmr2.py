#!/usr/bin/env python3
"""ChefNMR2 on the frozen formula + printed 1H/13C lists.

IR is not an input of this model. The gold structure is not an input.
Checkpoints are the public revision
38a741cce3e6f7e0d5a827a66f8d3dea0728daf5 of ziyux123/chefnmr2.
Set CHEFNMR2_CKPT to that directory. This script does not download them.

n_samples is the total draw budget across the 10 checkpoints, split evenly,
which is the non-adaptive setting in the ChefNMR2 README. "adaptive"
(100, then 1,000 or 3,000) is much heavier on CPU and is not the default here.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from payloads import load_arm  # noqa: E402
from peaks import parse_c, parse_h  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="60", choices=("60", "194"))
    ap.add_argument("--n-samples", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    ckpt = Path(os.environ.get("CHEFNMR2_CKPT", "/tmp/chefnmr2-ckpt"))
    members = [(d.name, d / "model.pt", d / "config.yaml") for d in sorted(ckpt.glob("chefnmr2-epoch*"))]
    if len(members) != 10:
        raise SystemExit(f"expected 10 checkpoints in {ckpt}, found {len(members)}")

    import torch
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))
    from chefnmr2.infer import ChefNMR2, Peaks

    t_load = time.time()
    model = ChefNMR2(members, device="cpu", recon_workers=0)
    print(f"loaded 10 checkpoints in {time.time()-t_load:.1f}s", flush=True)

    public, _gold = load_arm(args.arm)
    if args.limit:
        public = public[: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.out.exists():
        for line in args.out.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["uid"])
    with args.out.open("a") as fh:
        for i, row in enumerate(public, 1):
            if row["uid"] in done:
                continue
            h_peaks, h_info = parse_h(row["h_nmr"])
            c_peaks = parse_c(row["c_nmr"])
            t0 = time.time()
            status = "ok"
            out = None
            try:
                out = model.elucidate(
                    Peaks(c=c_peaks, h=[(a, b, m) for a, b, m in h_peaks]),
                    formula=row["formula"],
                    n_samples=args.n_samples,
                    seed=args.seed,
                )
            except Exception as exc:  # element outside the decoder, or a reconstruction failure
                status = f"{type(exc).__name__}: {exc}"
            rec = {
                "uid": row["uid"],
                "formula": row["formula"],
                "status": status,
                "n_h": len(h_peaks),
                "n_c": len(c_peaks),
                "h_dropped_no_integral": h_info["dropped_no_h"],
                "seconds": round(time.time() - t0, 2),
                "n_samples": None if out is None else out.get("n_samples"),
                "n_valid": None if out is None else out.get("n_valid"),
                "ranked": [] if out is None else out.get("candidates") or [],
            }
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"{i}/{len(public)} {row['uid']} {status} {rec['seconds']}s n={rec['n_samples']}", flush=True)


if __name__ == "__main__":
    main()
