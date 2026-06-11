#!/usr/bin/env python3
"""Recover agent benchmark outputs from task transcripts (robust to disk wipes).
Each transcript line is a JSON event; parsing it un-escapes the agent's text /
tool contents, where the answer JSON {"M-R<n>":[smiles,...]} lives."""
import json, re, glob, os, sys

TASKS = sys.argv[1]
collected = {}
pair = re.compile(r'"(M-R\d+)"\s*:\s*(\[[^\[\]]*\])')   # id : [ list-without-nesting ]

def harvest(s):
    for k, lst in pair.findall(s):
        if k in collected:
            continue
        try:
            v = json.loads(lst)
            if isinstance(v, list) and v:
                collected[k] = [x for x in v if isinstance(x, str)]
        except Exception:
            pass

def rec(o):
    if isinstance(o, str):
        if "M-R" in o:
            harvest(o)
    elif isinstance(o, dict):
        for v in o.values():
            rec(v)
    elif isinstance(o, list):
        for v in o:
            rec(v)

for f in glob.glob(TASKS + "/*.output"):
    try:
        data = open(f, errors="replace").read()
    except Exception:
        continue
    if '"M-R' not in data:
        continue
    for ln in data.splitlines():
        try:
            rec(json.loads(ln))
        except Exception:
            # not a clean JSON line: try unescaping common forms then harvest
            harvest(ln.replace('\\"', '"'))

os.makedirs("data/benchmark_main/raw", exist_ok=True)
json.dump(collected, open("data/benchmark_main/raw/recovered.json", "w"))
print(f"recovered {len(collected)} unique M-R compounds")
