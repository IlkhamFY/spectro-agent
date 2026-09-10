#!/usr/bin/env python3
"""
Run the cross-vendor sweep by hand, through a chat UI, without leaking the answers.

Some of the models worth testing have no API budget behind them but are already paid for
in a subscription -- a Cursor or ChatGPT or Gemini window. Both stages of the sweep are
text in, JSON out, so those models can be driven by hand exactly as Claude was, which
also keeps the zero-paid-API property of the headline protocol.

Two things make that harder than pasting, and both are handled here.

**The answer key is on disk.** `data/cross_vendor/key.json` holds all 60 true structures,
and an IDE assistant that indexes the workspace can read it. Answering from the key is
indistinguishable, in the score, from solving the spectra. `export` copies only the
prompts to a directory outside the repo, so the window you paste into has nothing else to
find.

**Merging ten or twenty replies by hand invites silent loss.** A batch pasted twice, or
skipped, shows up as a lower recall rather than as an error. `collect` merges whatever
replies are present, reports coverage against the roster, and refuses to write a file
that would quietly under-report.

  python scripts/manual_collect.py export  ~/sweep_gpt        # prompts only, no key
  #   … paste each solve_NN.md into a FRESH chat, save the reply as reply_NN.json …
  python scripts/manual_collect.py collect ~/sweep_gpt gpt    # -> solve_gpt.json
"""
import glob, json, os, re, shutil, sys

OUT = "data/cross_vendor"


def export(dest):
    if not os.path.exists(f"{OUT}/solve_batches"):
        sys.exit("no prompts — run: python scripts/cross_vendor_sweep.py prepare [subset] [n]")
    dest = os.path.abspath(os.path.expanduser(dest))
    if os.path.abspath(".") in dest:
        sys.exit(f"refusing to export inside the repo ({dest}) — the point is to leave the "
                 f"answer key behind. Choose a directory outside it.")
    os.makedirs(dest, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(f"{OUT}/solve_batches/solve_*.md")):
        shutil.copy(f, dest); n += 1
    for f in glob.glob(f"{OUT}/verify_prompt_*.md"):
        shutil.copy(f, dest)
    leaked = [f for f in os.listdir(dest) if "key" in f or f.startswith("answers")]
    assert not leaked, f"answer-bearing file reached the export: {leaked}"
    print(f"{n} solve prompt(s) -> {dest}")
    print("\nNothing in that directory reveals an answer. Then, per model:")
    print("  1. open the chat on THAT folder (or no folder). Turn OFF codebase indexing,")
    print("     @-context, web search and tools — the closed-book guarantee is the one")
    print("     thing nothing here can check for you.")
    print("  2. paste solve_01.md, save the JSON reply as reply_01.json in that folder.")
    print(f"  3. repeat for each of the {n}, in a NEW chat every time. Carrying history")
    print("     across batches puts the model in the long-context arm §4.3 measures at")
    print("     5% top-1 against 15%, and the result stops being comparable.")
    print("  4. python scripts/manual_collect.py collect <folder> <vendor>")


def extract(txt):
    """Chat UIs wrap JSON in fences and commentary; be tolerant, but never guess."""
    m = re.search(r'```(?:json)?\s*(.*?)```', txt, re.S)
    for body in ([m.group(1)] if m else []) + [txt]:
        try:
            return json.loads(body)
        except Exception:
            i, j = body.find("{"), body.rfind("}")
            if i >= 0 and j > i:
                try:
                    return json.loads(body[i:j + 1])
                except Exception:
                    pass
    return None


def collect_verify(src, vendor):
    """Merge the forward-prediction replies the way `collect` merges the solve replies.

    Both stages are run by hand through a chat window and both drop numbered JSON files
    into the same folder, but only the solve stage had a collector. That left the raw
    verify replies committed and the verification-precision column unregenerable from
    them -- the one place the cross-vendor claim actually lives. The roster here is the
    anonymised candidate map rather than the compound key, because the verify stage is
    blind: it sees `P000`, not a compound.
    """
    src = os.path.abspath(os.path.expanduser(src))
    amap = f"{OUT}/anon_{vendor}.json"
    if not os.path.exists(amap):
        sys.exit(f"no {amap}; run: cross_vendor_sweep.py prep-verify {vendor}")
    roster = set(json.load(open(amap)).values())
    files = sorted(sum((glob.glob(f"{src}/verify_*{e}") for e in (".json", ".txt", ".md")), []))
    if not files:
        sys.exit(f"no verify_*.json in {src}")
    merged, bad = {}, []
    for f in files:
        got = extract(open(f, encoding="utf-8").read())
        if not isinstance(got, dict) or not got:
            bad.append(os.path.basename(f)); continue
        merged.update(got)
        print(f"  {os.path.basename(f):<18} {len(got):>3} candidate(s)")
    missing = sorted(roster - set(merged))
    print(f"\n  coverage {len(roster & set(merged))}/{len(roster)} candidates")
    if bad:
        print(f"  !! {len(bad)} unparseable file(s): {', '.join(bad)}")
    if missing:
        print(f"  !! {len(missing)} without a prediction: {', '.join(missing[:8])}"
              f"{' …' if len(missing) > 8 else ''}")
    out = f"{OUT}/verify_{vendor}.json"
    json.dump(merged, open(out, "w"), indent=1)
    print(f"\nwrote {out}")


def collect(src, vendor):
    src = os.path.abspath(os.path.expanduser(src))
    key = json.load(open(f"{OUT}/key.json"))["key"]
    files = sorted(sum((glob.glob(f"{src}/reply_*{e}") for e in (".json", ".txt", ".md")), [])
                   or sum((glob.glob(f"{src}/**/reply_*{e}") for e in (".json", ".txt", ".md")), []))
    if not files:
        sys.exit(f"no reply_*.json in {src}")
    merged, bad, dupes = {}, [], []
    for f in files:
        got = extract(open(f, encoding="utf-8").read())
        if not isinstance(got, dict) or not got:
            bad.append(os.path.basename(f)); continue
        for k, v in got.items():
            if k in merged and merged[k] != v:
                dupes.append(k)
            merged[k] = v
        print(f"  {os.path.basename(f):<18} {len(got):>3} compound(s)")
    stray = sorted(set(merged) - set(key))
    missing = sorted(set(key) - set(merged))
    if stray:
        print(f"\n  !! {len(stray)} id(s) not in the roster (typo or wrong subset?): "
              f"{', '.join(stray[:6])}")
        for k in stray:
            merged.pop(k)
    if bad:
        print(f"\n  !! {len(bad)} file(s) held no parseable JSON: {', '.join(bad)}")
    if dupes:
        print(f"\n  !! {len(set(dupes))} id(s) answered twice with different candidates — "
              f"kept the last: {', '.join(sorted(set(dupes))[:6])}")
    print(f"\ncoverage {len(merged)}/{len(key)} compounds")
    if missing:
        print(f"  missing: {', '.join(missing[:12])}{' …' if len(missing) > 12 else ''}")
        print("  These score as misses, so recall comes out a lower bound. Paste the "
              "outstanding batches before trusting the number.")
    dest = f"{OUT}/solve_{vendor}.json"
    json.dump(merged, open(dest, "w"), indent=0)
    print(f"\nwrote {dest}")
    print(f"next: python scripts/cross_vendor_sweep.py prep-verify {vendor}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("export", "collect", "collect-verify"):
        sys.exit(__doc__)
    if sys.argv[1] == "export":
        export(sys.argv[2])
    else:
        if len(sys.argv) < 4:
            sys.exit("collect needs a vendor name: collect <folder> <vendor>")
        (collect_verify if sys.argv[1] == "collect-verify" else collect)(
            sys.argv[2], sys.argv[3])
