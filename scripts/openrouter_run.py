#!/usr/bin/env python3
"""
Drive the cross-vendor sweep against OpenRouter.

The sweep itself is vendor-agnostic (`scripts/cross_vendor_sweep.py`): it writes prompt
files and reads JSON back. This is just a transport for models that have no chat UI we
can drive by hand -- it sends each prompt file as its own request and saves the reply
where `score` expects it.

Two properties matter and are enforced here rather than trusted:

  * **One fresh context per batch.** Every request is independent -- no message history
    is carried between batches. §4.3 measures the same compounds at 5% top-1 in one long
    context against 15% across bounded ones, so pooling batches into a conversation would
    quietly run the vendor under the arm that depresses accuracy.
  * **Closed book.** No tools, no web plugin, no system prompt beyond the task file.

  export OPENROUTER_API_KEY=...        # never stored in the repo; see .gitignore
  python scripts/openrouter_run.py solve  <model> <vendor> [--budget 2.00]
  python scripts/openrouter_run.py verify <model> <vendor> [--budget 2.00]

Spend is read back from OpenRouter's own usage accounting after every call and the run
aborts the moment it would cross --budget, so a runaway reasoning trace costs one request
rather than the balance.
"""
import argparse, glob, json, os, re, subprocess, sys, time

OUT = "data/cross_vendor"
API = "https://openrouter.ai/api/v1/chat/completions"


def key():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not k:
        sys.exit("OPENROUTER_API_KEY is not set (keep it out of the repo — see .gitignore)")
    return k


def call(model, prompt, k, max_tokens=32000, tries=3):
    """One request, one context. Returns (text, usd)."""
    payload = {"model": model, "max_tokens": max_tokens,
               "messages": [{"role": "user", "content": prompt}],
               "usage": {"include": True}}
    for attempt in range(tries):
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "900", API,
             "-H", f"Authorization: Bearer {k}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            time.sleep(3 * (attempt + 1)); continue
        if "error" in d:
            msg = d["error"].get("message", "")
            # a rate limit is worth waiting out; a bad model id or empty balance is not
            if "rate" in msg.lower() and attempt < tries - 1:
                time.sleep(10 * (attempt + 1)); continue
            return None, 0.0, msg
        txt = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        usd = float((d.get("usage") or {}).get("cost") or 0.0)
        return txt, usd, None
    return None, 0.0, "no parseable reply after retries"


def extract_json(txt):
    """Models wrap JSON in prose or fences often enough that this has to be tolerant."""
    if not txt:
        return {}
    m = re.search(r'```(?:json)?\s*(.*?)```', txt, re.S)
    body = m.group(1) if m else txt
    try:
        return json.loads(body)
    except Exception:
        pass
    # fall back to the outermost balanced {...}
    i, j = body.find("{"), body.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(body[i:j + 1])
        except Exception:
            pass
    return {}


def split_batches(text):
    """Split a prep-verify prompt into one self-contained prompt per '## batch N'."""
    head, *rest = re.split(r'\n## batch \d+\n', text)
    return [head + "\n" + r for r in rest] if rest else [text]


def run(stage, model, vendor, budget):
    k = key()
    if stage == "solve":
        files = sorted(glob.glob(f"{OUT}/solve_batches/solve_*.md"))
        if not files:
            sys.exit("no solve batches — run: python scripts/cross_vendor_sweep.py prepare")
        prompts = [open(f).read() for f in files]
        dest = f"{OUT}/solve_{vendor}.json"
    else:
        src = f"{OUT}/verify_prompt_{vendor}.md"
        if not os.path.exists(src):
            sys.exit(f"missing {src} — run: python scripts/cross_vendor_sweep.py prep-verify {vendor}")
        prompts = split_batches(open(src).read())
        dest = f"{OUT}/verify_{vendor}.json"

    merged, spent, failed = {}, 0.0, []
    for i, p in enumerate(prompts, 1):
        if spent >= budget:
            failed.append(f"batch {i}+: stopped, ${spent:.3f} of ${budget:.2f} budget spent")
            break
        txt, usd, err = call(model, p, k)
        spent += usd
        if err:
            failed.append(f"batch {i}: {err}")
            print(f"  batch {i:>2}/{len(prompts)}  ERROR  {err[:70]}")
            continue
        got = extract_json(txt)
        merged.update(got)
        print(f"  batch {i:>2}/{len(prompts)}  {len(got):>3} keys  ${usd:.4f}  (running ${spent:.3f})")
    os.makedirs(OUT, exist_ok=True)
    json.dump(merged, open(dest, "w"), indent=0)
    print(f"\n{vendor} {stage}: {len(merged)} entries -> {dest}   spent ${spent:.3f}")
    for f in failed:
        print(f"  ! {f}")
    return spent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["solve", "verify"])
    ap.add_argument("model")
    ap.add_argument("vendor")
    ap.add_argument("--budget", type=float, default=2.00, help="hard USD ceiling for this run")
    a = ap.parse_args()
    run(a.stage, a.model, a.vendor, a.budget)
