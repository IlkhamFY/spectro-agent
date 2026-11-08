#!/usr/bin/env python3
"""Hu et al. 2024 NMR2Struct, 13C-only checkpoint, on printed carbon lists.

The proton file is the published "None" mode: a zero 1H vector, not a synthesized
trace. The molecular formula and the IR list are not inputs. Rank is the model's
log-probability over 15 samples (the example config's num_pred_per_tgt).

Requires a checkout of MarklandGroup/NMR2Struct and its checkpoints. This script
does not download them. Set NMR2STRUCT_ROOT.
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
from peaks import parse_c  # noqa: E402


def _nmr_root() -> Path:
    root = Path(os.environ.get("NMR2STRUCT_ROOT", "/tmp/NMR2Struct"))
    if not (root / "nmr").is_dir():
        raise SystemExit(f"NMR2STRUCT_ROOT does not contain the package: {root}")
    return root


def _load_model(root: Path):
    import torch
    import yaml
    from nmr.models import create_model
    from nmr.scripts.top_level_utils import dtype_convert, seed_everything

    cfg_path = HERE / "nmr2struct_cnmr_only.yaml"
    doc = yaml.safe_load(cfg_path.read_text())
    # Paths inside the committed yaml are filled from the checkout.
    doc["model"]["load_model"] = str(root / "checkpoints" / "cnmr_only_checkpoint.pt")
    doc["inference"]["run_inference_args"]["pred_gen_opts"]["alphabet"] = str(
        root / "example_configs" / "alphabet.npy"
    )
    seed_everything(doc["global_args"]["seed"])
    dtype = dtype_convert(doc["global_args"]["dtype"])
    device = torch.device("cpu")
    model, _ = create_model(doc["model"], dtype, device)
    model.to(dtype).to(device)
    ckpt = torch.load(doc["model"]["load_model"], map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model, doc, device, dtype


def _predict_one(model, doc, device, dtype, cnmr_path: Path, root: Path) -> list[tuple[str, float]]:
    from torch.utils.data import DataLoader
    from nmr.data.dataset_base import SingleNMRDataset
    from nmr.inference.inference import run_inference

    dataset = SingleNMRDataset(
        hnmr_file=None,
        cnmr_file=str(cnmr_path),
        hnmr_shifts=str(root / "example_configs" / "HNMR_shifts.p"),
        cnmr_shifts=str(root / "example_configs" / "CNMR_shifts.p"),
        normalize=True,
        device=device,
        dtype=dtype,
    )
    loader = DataLoader(dataset, batch_size=1, shuffle=False)
    inf = doc["inference"]["run_inference_args"]
    predictions = run_inference(
        model=model,
        dataloader=loader,
        pred_gen_fn=inf["pred_gen_fn"],
        pred_gen_opts=inf["pred_gen_opts"],
        write_freq=inf["write_freq"],
        device=device,
    )
    _target, smiles, _echo, scores = predictions[0]
    order = sorted(range(len(smiles)), key=lambda i: float(scores[i]), reverse=True)
    return [(smiles[i], float(scores[i])) for i in order]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="60", choices=("60", "194", "306"))
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = _nmr_root()
    sys.path.insert(0, str(root))
    os.environ.setdefault("OMP_NUM_THREADS", "1")

    public, _gold = load_arm(args.arm)
    mine = [row for i, row in enumerate(public) if i % args.nshards == args.shard]
    model, doc, device, dtype = _load_model(root)
    tmp = args.out.parent / f".cnmr_{args.shard}.txt"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        for i, row in enumerate(mine, 1):
            shifts = parse_c(row["c_nmr"])
            tmp.write_text(", ".join(f"{x:.4f}" for x in shifts))
            t0 = time.time()
            ranked = _predict_one(model, doc, device, dtype, tmp, root)
            rec = {
                "uid": row["uid"],
                "n_c_shifts": len(shifts),
                "seconds": round(time.time() - t0, 2),
                "ranked": [{"smiles": s, "logprob": sc} for s, sc in ranked],
            }
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"shard {args.shard} {i}/{len(mine)} {row['uid']} {rec['seconds']}s", flush=True)
    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
