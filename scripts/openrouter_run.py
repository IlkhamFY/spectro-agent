#!/usr/bin/env python3
"""
Drive the cross-vendor sweep against OpenRouter.

The sweep itself is vendor-agnostic (`scripts/cross_vendor_sweep.py`): it writes prompt
files and reads JSON back, so a model with a chat UI can be driven by hand. This is a
transport for models that have no such UI -- it sends each prompt file as its own request
and saves the reply where `score` expects it.

Two properties matter and are enforced here rather than trusted:

  * **One fresh context per batch.** Every request is independent -- no message history
    is carried between batches. §4.3 measures the same compounds at 5% top-1 in one long
    context against 15% across bounded ones, so pooling batches into a conversation would
    quietly run the vendor under the arm that depresses accuracy.
  * **Closed book.** No tools, no web plugin, no system prompt beyond the task file.

Decoding parameters are left at each vendor's default, including reasoning effort. The
Claude runs behind the paper were served by a subscription harness that exposes no
decoding controls (§8), so tuning them per vendor here would add a degree of freedom the
reference arm never had.

  export OPENROUTER_API_KEY=...        # never stored in the repo; see .gitignore
  python scripts/openrouter_run.py screen <model>            # one batch: is it usable?
  python scripts/openrouter_run.py solve  <model> <vendor> [--budget 2.00] [--jobs 5]
  python scripts/openrouter_run.py verify <model> <vendor> [--budget 2.00] [--jobs 5]

Spend is read back from OpenRouter's own usage accounting and the run stops the moment it
would cross --budget, so a runaway reasoning trace costs one request rather than the
balance.

Two transport details are load-bearing, both learned the hard way against a reasoning
model that thinks for ten minutes before its first answer token:

  * **Streaming, over HTTP/1.1.** A non-streaming request sends nothing while the model
    reasons; the idle connection was being killed at ~5 minutes with an HTTP/2
    INTERNAL_ERROR, which looks exactly like a model that refused to answer.
  * **A generous token ceiling.** Six blind elucidations in one context cost this model
    ~30k reasoning tokens before it emits any JSON. A 32k cap truncated it mid-thought:
    full price, no answer, and a silent zero in the recall column.
"""
import argparse, glob, json, os, re, subprocess, sys, tempfile, threading

OUT = "data/cross_vendor"
API = "https://openrouter.ai/api/v1/chat/completions"
MAX_TOKENS = 120_000          # headroom for a long reasoning trace *and* the answer


def key():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not k:
        sys.exit("OPENROUTER_API_KEY is not set (keep it out of the repo — see .gitignore)")
    return k


def account_usage(k):
    """Total USD this key has spent, per OpenRouter — or None if unreachable."""
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "30",
         "-H", f"Authorization: Bearer {k}", "https://openrouter.ai/api/v1/credits"],
        capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["data"]["total_usage"])
    except Exception:
        return None


def call(model, prompt, k, timeout=1800):
    """One request, one context. Returns (text, usd, error)."""
    body = {"model": model, "max_tokens": MAX_TOKENS, "stream": True,
            "messages": [{"role": "user", "content": prompt}],
            "usage": {"include": True}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(body, f); req = f.name
    try:
        r = subprocess.run(
            ["curl", "-sS", "--http1.1", "-N", "--max-time", str(timeout), API,
             "-H", f"Authorization: Bearer {k}",
             "-H", "Content-Type: application/json", "-d", f"@{req}"],
            capture_output=True, text=True)
    finally:
        os.unlink(req)
    if r.returncode != 0:
        return None, 0.0, f"curl {r.returncode}: {r.stderr.strip()[:120]}"

    text, usd, err = [], 0.0, None
    for line in r.stdout.splitlines():
        if not line.startswith("data: "):
            continue
        chunk = line[6:].strip()
        if chunk == "[DONE]":
            break
        try:
            d = json.loads(chunk)
        except Exception:
            continue
        if "error" in d:
            err = str(d["error"])[:160]; continue
        for c in d.get("choices") or []:
            # only the answer stream; a model's reasoning is not its reply
            text.append((c.get("delta") or {}).get("content") or "")
        if d.get("usage"):
            usd = float(d["usage"].get("cost") or 0.0)
    out = "".join(text)
    if not out and not err:
        err = "stream carried no answer content (truncated inside reasoning?)"
    return out, usd, err


def extract_json(txt):
    """Models wrap JSON in prose or fences often enough that this has to be tolerant."""
    if not txt:
        return {}
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
    return {}


def split_batches(text):
    """Split a prep-verify prompt into one self-contained prompt per '## batch N'."""
    head, *rest = re.split(r'\n## batch \d+\n', text)
    return [head + "\n" + r for r in rest] if rest else [text]


def screen(model, k=None):
    """One batch, one verdict: can this model meet the task's output contract at all?

    Worth a few cents before committing a full arm. The task hands over a molecular
    formula and asks for candidates matching it; a model that returns unparseable strings,
    or valid molecules of the wrong composition, is not going to be measured on
    elucidation no matter how many batches you buy. The first pilot spent real money
    discovering this the long way -- nemotron returned 180 candidates, 2% of which carried
    the requested formula, and scored a zero that reads like a chemistry result.

    Also catches the other cheap-to-detect failure: a model that never terminates.
    """
    from rdkit import Chem, RDLogger
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula
    RDLogger.DisableLog("rdApp.*")
    k = k or key()
    f = sorted(glob.glob(f"{OUT}/solve_batches/solve_*.md"))
    if not f:
        sys.exit("no solve batches — run: python scripts/cross_vendor_sweep.py prepare")
    keyf = json.load(open(f"{OUT}/key.json"))["key"]
    print(f"screening {model} on {os.path.basename(f[0])} …", flush=True)
    txt, usd, err = call(model, open(f[0]).read(), k)
    got = extract_json(txt)
    if err and not got:
        print(f"  VERDICT: unusable — {err}\n  cost ${usd:.4f}")
        return
    raw = parse = form = 0
    for mid, cands in got.items():
        if mid not in keyf:
            continue
        want = CalcMolFormula(Chem.MolFromSmiles(keyf[mid]["true_smiles"]))
        for c in (cands or [])[:3]:
            raw += 1
            m = Chem.MolFromSmiles(c or "")
            if m:
                parse += 1
                form += (CalcMolFormula(m) == want)
    if not raw:
        print(f"  VERDICT: unusable — replied, but no candidates parsed out of the JSON"
              f"\n  cost ${usd:.4f}")
        return
    p, fm = 100 * parse / raw, 100 * form / raw
    verdict = ("usable" if fm >= 50 else
               "marginal" if fm >= 25 else
               "NOT WORTH A FULL ARM — cannot meet the output contract")
    print(f"  compounds answered {len(got)}   candidates {raw}")
    print(f"  parse {p:.0f}%   match the given formula {fm:.0f}%   (Claude 78-95%)")
    print(f"  cost ${usd:.4f}  ->  extrapolated full 60-compound solve "
          f"${usd*len(f):.2f}")
    print(f"  VERDICT: {verdict}")


def run(stage, model, vendor, budget, jobs):
    k = key()
    if stage == "solve":
        files = sorted(glob.glob(f"{OUT}/solve_batches/solve_*.md"))
        if not files:
            sys.exit("no solve batches — run: python scripts/cross_vendor_sweep.py prepare")
        prompts, dest = [open(f).read() for f in files], f"{OUT}/solve_{vendor}.json"
    else:
        src = f"{OUT}/verify_prompt_{vendor}.md"
        if not os.path.exists(src):
            sys.exit(f"missing {src} — run: cross_vendor_sweep.py prep-verify {vendor}")
        prompts, dest = split_batches(open(src).read()), f"{OUT}/verify_{vendor}.json"

    base = account_usage(k)
    results, lock, spend = [None] * len(prompts), threading.Lock(), [0.0]
    stop = threading.Event()

    def over_budget():
        """True once the run has cost --budget, counted from the account, not the replies.

        Summing the usage each reply carries cannot see money already spent by requests
        still in flight -- and a model that reasons until it dies never sends a reply at
        all. That is not hypothetical: DeepSeek V4 Pro billed real tokens on seven of ten
        batches it never answered, and this guard, watching only completions, stayed
        silent throughout. Ask the account instead; it bills whether or not we get a
        reply. Falls back to the completion sum if the balance endpoint is unreachable,
        which is the weaker check but better than none.
        """
        now = account_usage(k)
        used = (now - base) if now is not None and base is not None else spend[0]
        return used >= budget, used

    def work(i):
        if stop.is_set():
            return
        txt, usd, err = call(model, prompts[i], k)
        with lock:
            spend[0] += usd
            results[i] = (extract_json(txt), usd, err)
            n = len(results[i][0])
            tag = f"ERROR {err[:60]}" if err and not n else f"{n:>3} keys"
            print(f"  batch {i+1:>2}/{len(prompts)}  {tag}  ${usd:.4f}  "
                  f"(replies ${spend[0]:.3f})", flush=True)

    # Batches are independent by construction, so they may as well run concurrently;
    # sequentially this is 20 x ~15 min of pure waiting for a reasoning model.
    threads = []
    for i in range(len(prompts)):
        hit, used = over_budget()
        if hit:
            stop.set()
            print(f"  ! account spend ${used:.3f} reached the ${budget:.2f} budget — "
                  f"not dispatching batch {i+1} or later", flush=True)
            break
        t = threading.Thread(target=work, args=(i,)); t.start(); threads.append(t)
        while sum(x.is_alive() for x in threads) >= jobs:
            threads = [x for x in threads if x.is_alive() or not x.join(1)]
    for t in threads:
        t.join()
    _, final = over_budget()
    print(f"\naccount spend for this run: ${final:.3f}", flush=True)

    merged, failed = {}, []
    for i, r in enumerate(results, 1):
        if r is None:
            failed.append(f"batch {i}: skipped (budget)")
        elif r[2] and not r[0]:
            failed.append(f"batch {i}: {r[2]}")
        else:
            merged.update(r[0])
    os.makedirs(OUT, exist_ok=True)
    json.dump(merged, open(dest, "w"), indent=0)
    print(f"\n{vendor} {stage}: {len(merged)} entries -> {dest}   spent ${spend[0]:.3f}")
    for f in failed:
        print(f"  ! {f}")
    return spend[0]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["solve", "verify", "screen"])
    ap.add_argument("model")
    ap.add_argument("vendor", nargs="?", default="screen")
    ap.add_argument("--budget", type=float, default=2.00, help="hard USD ceiling")
    ap.add_argument("--jobs", type=int, default=5, help="concurrent batches")
    a = ap.parse_args()
    if a.stage == "screen":
        screen(a.model)
    else:
        # `vendor` is optional only so `screen <model>` can omit it. Without this,
        # `solve <model>` would quietly write solve_screen.json and look like it worked.
        if a.vendor == "screen":
            ap.error(f"{a.stage} needs a vendor name: {a.stage} <model> <vendor>")
        run(a.stage, a.model, a.vendor, a.budget, a.jobs)
