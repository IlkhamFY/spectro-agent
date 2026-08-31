#!/usr/bin/env python3
"""Turn a drawn round into solver batches, and put the answer key out of reach.

Blindness in this protocol has always rested on an instruction, and the paper says so in
its own Limitations: the answer keys are tracked files, so anything with workspace access
can read them. For a round solved by agents running *inside* the workspace that is not good
enough, so this does two things instead of asking nicely.

It writes the batches outside the repository, and it moves the round's answer key outside
too, returning a path to it. Nothing that reads the working tree can reach the answers
while the solvers run. The other rounds' keys stay where they are and cannot leak this
round: the sampler excludes every InChIKey-14 already revealed, so no compound here appears
in any of them.

  python scripts/export_round.py data/benchmark_expand /tmp/blind --batch 6
  ...solve...
  python scripts/export_round.py --restore data/benchmark_expand /tmp/blind
"""
import argparse
import json
import os
import shutil


def fmt(q):
    """One compound, in the format the released main-round batches already use."""
    return (f"{q['qid']} | formula {q['formula']}\n"
            f"  IR cm-1: {q['ir_bands_cm-1']}\n"
            f"  1H NMR: {q['h_nmr']}\n"
            f"  13C NMR: {q['c_nmr']}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round_dir")
    ap.add_argument("outside")
    ap.add_argument("--batch", type=int, default=6)
    ap.add_argument("--restore", action="store_true")
    a = ap.parse_args()

    name = os.path.basename(a.round_dir.rstrip("/"))
    dest = os.path.join(a.outside, name)
    key_in = os.path.join(a.round_dir, "answers2.jsonl")
    # Not beside the batches: a solver told to read one batch can list that
    # directory. The key goes to a separate vault so the batch folder holds
    # nothing but questions.
    vault = os.path.join(a.outside, "_key")
    key_out = os.path.join(vault, f"{name}.answers2.jsonl.withheld")

    if a.restore:
        if not os.path.exists(key_out):
            raise SystemExit(f"no withheld key at {key_out}")
        shutil.move(key_out, key_in)
        print(f"restored {key_in}")
        return

    os.makedirs(dest, exist_ok=True)
    os.makedirs(vault, mode=0o700, exist_ok=True)
    qs = [json.loads(l) for l in open(os.path.join(a.round_dir, "questions2.jsonl"))]
    n = 0
    for i in range(0, len(qs), a.batch):
        n += 1
        chunk = qs[i:i + a.batch]
        with open(os.path.join(dest, f"batch_{n:02d}.txt"), "w") as f:
            f.write("\n".join(fmt(q) for q in chunk))
    print(f"{len(qs)} compounds -> {n} batches of <= {a.batch} in {dest}")

    if os.path.exists(key_in):
        shutil.move(key_in, key_out)
        print(f"answer key withheld: {key_in} -> {key_out}")
    else:
        print(f"no key at {key_in} (already withheld?)")


if __name__ == "__main__":
    main()
