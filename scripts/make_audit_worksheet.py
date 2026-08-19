#!/usr/bin/env python3
"""Generate the digital reviewer worksheet from the frozen blind sample.

The printable `data/audit/scoring_sheet.md` is fine on paper but produces answers
that have to be re-typed before anything can be computed. This emits an equivalent
*machine-readable* worksheet: one self-contained HTML file that renders the spectra
and the rendered structures inline, collects the same fields as the paper sheet, and
exports a response JSON that `scripts/score_audit.py` consumes directly.

It is a view over the frozen package -- it reads `sample.jsonl` and adds nothing.
The blind sample, the key and the printable sheet are untouched, so the seed=0
content-key of the audit package still holds.

  python3 scripts/make_audit_worksheet.py [--out data/audit/worksheet.html]

Open the result from inside `data/audit/` so the relative `structures/*.png` paths
resolve; it needs no network access and no server.
"""
import argparse, hashlib, json, sys

SAMPLE = "data/audit/sample.jsonl"
OUT = "data/audit/worksheet.html"
VERDICTS = ["correct", "wrong-regiochemistry", "wrong-scaffold", "uninterpretable"]

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Expert audit worksheet (blinded)</title>
<style>
:root {
  --bg:#faf9f7; --panel:#fff; --ink:#1a1a1a; --muted:#6b6b6b; --line:#e2e0dc;
  --accent:#2d5f8a; --warn:#8a5a2d; --ok:#2d7d4f; --field:#fff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#16181c; --panel:#1e2126; --ink:#e8e6e3; --muted:#9a9894; --line:#32363d;
    --accent:#7fb0d8; --warn:#d8a670; --ok:#7fc99a; --field:#14161a;
  }
}
* { box-sizing:border-box; }
body {
  margin:0; padding:0 0 6rem; background:var(--bg); color:var(--ink);
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}
header {
  position:sticky; top:0; z-index:10; background:var(--panel);
  border-bottom:1px solid var(--line); padding:.75rem 1.25rem;
  display:flex; gap:1rem; align-items:center; flex-wrap:wrap;
}
header h1 { font-size:1rem; margin:0; font-weight:600; letter-spacing:-.01em; }
header .sp { flex:1; }
#progress { font-variant-numeric:tabular-nums; color:var(--muted); font-size:.85rem; }
button {
  font:inherit; font-size:.85rem; padding:.4rem .8rem; border-radius:6px;
  border:1px solid var(--line); background:var(--field); color:var(--ink); cursor:pointer;
}
button.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
button:hover { filter:brightness(1.08); }
main { max-width:920px; margin:0 auto; padding:1.5rem 1.25rem; }
.intro { background:var(--panel); border:1px solid var(--line); border-radius:10px;
         padding:1rem 1.25rem; margin-bottom:1.5rem; }
.intro p { margin:.5rem 0; }
.intro code { background:var(--bg); padding:.1em .35em; border-radius:4px; font-size:.9em; }
label.name { display:block; margin:.75rem 0 0; font-size:.85rem; color:var(--muted); }
input[type=text], textarea, select {
  font:inherit; width:100%; padding:.45rem .6rem; border:1px solid var(--line);
  border-radius:6px; background:var(--field); color:var(--ink);
}
article {
  background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:1.25rem; margin-bottom:1.25rem;
}
article > h2 { margin:0 0 .75rem; font-size:1.05rem; display:flex; gap:.6rem; align-items:baseline; }
.tag { font-size:.72rem; font-weight:500; color:var(--muted); border:1px solid var(--line);
       padding:.1rem .45rem; border-radius:99px; }
.spectra { font-size:.86rem; line-height:1.55; }
.spectra div { margin:.35rem 0; }
.spectra b { color:var(--muted); font-weight:600; }
.spectra .val { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.92em;
                word-break:break-word; }
section.task { border-top:1px solid var(--line); margin-top:1rem; padding-top:1rem; }
section.task h3 { margin:0 0 .6rem; font-size:.9rem; letter-spacing:.02em; text-transform:uppercase;
                  color:var(--accent); }
.cands { display:flex; flex-wrap:wrap; gap:1rem; margin:.5rem 0 1rem; }
figure { margin:0; text-align:center; }
figure img, .t1img img {
  max-width:100%; background:#fff; border:1px solid var(--line); border-radius:8px; display:block;
}
figure img { width:210px; }
.t1img img { width:300px; margin:.5rem 0; }
figcaption { font-size:.85rem; font-weight:600; margin-top:.3rem; }
.row { display:flex; gap:1rem; flex-wrap:wrap; align-items:flex-end; margin:.6rem 0; }
.row > div { flex:1; min-width:190px; }
.row label, .fieldlabel { display:block; font-size:.82rem; color:var(--muted); margin-bottom:.25rem; }
.scale { display:flex; gap:.35rem; }
.scale button { flex:1; padding:.4rem 0; }
.scale button[aria-pressed=true] { background:var(--accent); border-color:var(--accent); color:#fff; }
.gate { background:var(--bg); border:1px dashed var(--line); border-radius:8px;
        padding:1rem; text-align:center; color:var(--muted); font-size:.88rem; }
.gate button { margin-top:.6rem; }
.done { color:var(--ok); font-weight:600; }
.err { color:var(--warn); font-size:.82rem; margin-top:.3rem; min-height:1.2em; }
footer { max-width:920px; margin:0 auto; padding:0 1.25rem; }
dialog { border:1px solid var(--line); border-radius:10px; background:var(--panel);
         color:var(--ink); max-width:min(760px,92vw); padding:1.25rem; }
dialog textarea { height:340px; font-family:ui-monospace,Menlo,monospace; font-size:.78rem; }
dialog::backdrop { background:rgba(0,0,0,.5); }
</style>

<header>
  <h1>Expert audit worksheet <span class="tag">blinded</span></h1>
  <span id="progress"></span>
  <span class="sp"></span>
  <button id="show-json">View JSON</button>
  <button id="export" class="primary">Export response</button>
</header>

<main>
  <div class="intro">
    <p><b>You are blind to the answer key and to model identity.</b> Judge each structure
    against the spectra only &mdash; do not consult the literature, and do not open
    <code>data/fverify/</code>, which carries the ground truth.</p>
    <p>Where a compound has a <b>Task&nbsp;2</b>, rank the candidates <b>before</b> revealing the
    Task&nbsp;1 structure. The model's top-1 is one of the Task&nbsp;2 candidates, so looking first
    would contaminate your ranking. Task&nbsp;1 stays collapsed until Task&nbsp;2 is answered;
    nothing is hidden from you permanently.</p>
    <p>Answers save to this browser automatically. When finished, click
    <b>Export response</b> and commit the file to <code>data/audit/responses/</code>.</p>
    <label class="name">Reviewer name or handle (goes in the exported file)
      <input type="text" id="reviewer" placeholder="e.g. r-sondhi" autocomplete="off">
    </label>
  </div>
  <div id="sheet"></div>
</main>

<footer>
  <button id="export2" class="primary">Export response</button>
</footer>

<dialog id="jsonbox">
  <p style="margin:0 0 .5rem"><b>Response JSON</b> &mdash; save as
     <code>data/audit/responses/&lt;reviewer&gt;.json</code></p>
  <textarea id="jsontext" readonly></textarea>
  <div style="display:flex;gap:.5rem;margin-top:.75rem">
    <button id="copy" class="primary">Copy to clipboard</button>
    <button onclick="jsonbox.close()">Close</button>
  </div>
</dialog>

<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
const PAYLOAD  = JSON.parse(document.getElementById('payload').textContent);
const SAMPLE   = PAYLOAD.sample, VERDICTS = PAYLOAD.verdicts;
const STORE    = 'spectro-audit-v1';
let state = JSON.parse(localStorage.getItem(STORE) || '{}');

const save = () => localStorage.setItem(STORE, JSON.stringify(state));
const rec  = id => (state[id] ||= {task1:{}, task2:{}});

function scaleWidget(value, onPick) {
  const wrap = document.createElement('div');
  wrap.className = 'scale';
  for (let n = 1; n <= 5; n++) {
    const b = document.createElement('button');
    b.textContent = n;
    b.setAttribute('aria-pressed', String(value === n));
    b.onclick = () => { onPick(n); render(); };
    wrap.append(b);
  }
  return wrap;
}

function buildCompound(c) {
  const r = rec(c.audit_id);
  const art = document.createElement('article');

  const h = document.createElement('h2');
  h.innerHTML = `${c.audit_id}
    <span class="tag">${c.difficulty}</span>
    <span class="tag">${c.heavy_atoms} heavy atoms</span>
    <span class="tag">${c.formula}</span>`;
  if (task1Done(r) && task2Done(r, c)) {
    const d = document.createElement('span');
    d.className = 'done'; d.textContent = '\\u2713';
    h.append(d);
  }
  art.append(h);

  const sp = document.createElement('div');
  sp.className = 'spectra';
  sp.innerHTML =
    `<div><b>IR (cm\\u207b\\u00b9)</b> <span class="val">${c['ir_bands_cm-1'].join(', ')}</span></div>
     <div><b>\\u00b9H NMR</b> <span class="val">${esc(c.h_nmr)}</span></div>
     <div><b>\\u00b9\\u00b3C NMR</b> <span class="val">${esc(c.c_nmr)}</span></div>`;
  art.append(sp);

  if (c.task2_applicable) art.append(task2Section(c, r));
  art.append(task1Section(c, r));
  return art;
}

function task2Section(c, r) {
  const s = document.createElement('section');
  s.className = 'task';
  s.innerHTML = `<h3>Task 2 &mdash; rank the candidates by spectral fit (do this first)</h3>`;

  const cands = document.createElement('div');
  cands.className = 'cands';
  for (const lbl of c.task2_candidate_labels) {
    const fig = document.createElement('figure');
    fig.innerHTML = `<img src="structures/${c.audit_id}_cand${lbl}.png" alt="candidate ${lbl}">
                     <figcaption>${lbl}</figcaption>`;
    cands.append(fig);
  }
  s.append(cands);

  const row = document.createElement('div');
  row.className = 'row';

  const rank = document.createElement('div');
  rank.innerHTML = `<label>Ranking, best \\u2192 worst (letters, e.g. ${
    c.task2_candidate_labels.slice().reverse().join(',')})</label>`;
  const inp = document.createElement('input');
  inp.type = 'text';
  inp.value = (r.task2.ranking || []).join(',');
  inp.placeholder = c.task2_candidate_labels.join(',');
  const err = document.createElement('div');
  err.className = 'err';
  inp.oninput = () => {
    const got = inp.value.toUpperCase().split(/[^A-Z]+/).filter(Boolean);
    const want = c.task2_candidate_labels;
    if (!got.length) { delete r.task2.ranking; err.textContent = ''; }
    else if (got.length !== want.length || new Set(got).size !== got.length
             || got.some(x => !want.includes(x))) {
      err.textContent = `must be each of ${want.join(', ')} exactly once`;
      delete r.task2.ranking;
    } else { r.task2.ranking = got; err.textContent = ''; }
    save(); updateProgress();
  };
  rank.append(inp, err);

  const conf = document.createElement('div');
  conf.innerHTML = `<label>Confidence in your top pick</label>`;
  conf.append(scaleWidget(r.task2.confidence, v => { r.task2.confidence = v; save(); }));

  row.append(rank, conf);
  s.append(row);
  return s;
}

function task1Section(c, r) {
  const s = document.createElement('section');
  s.className = 'task';
  s.innerHTML = `<h3>Task 1 &mdash; is the model's top-1 consistent with the spectra?</h3>`;

  // Order gate: on Task-2 compounds the top-1 is inside the candidate set, so
  // revealing it first would leak into the ranking. Collapsed, never removed.
  if (c.task2_applicable && !r.task2.ranking && !r.task1._revealed) {
    const g = document.createElement('div');
    g.className = 'gate';
    g.innerHTML = `<div>Answer the Task&nbsp;2 ranking above first.</div>`;
    const b = document.createElement('button');
    b.textContent = 'Reveal anyway';
    b.onclick = () => { r.task1._revealed = true; save(); render(); };
    g.append(b);
    s.append(g);
    return s;
  }

  const img = document.createElement('div');
  img.className = 't1img';
  img.innerHTML = `<img src="structures/${c.task1_structure_image}" alt="model top-1">`;
  s.append(img);

  const row = document.createElement('div');
  row.className = 'row';

  const cons = document.createElement('div');
  cons.innerHTML = `<label>Consistency with ALL spectra (1 = contradicted \\u2026 5 = fully)</label>`;
  cons.append(scaleWidget(r.task1.consistency, v => { r.task1.consistency = v; save(); }));

  const verd = document.createElement('div');
  verd.innerHTML = `<label>Verdict</label>`;
  const sel = document.createElement('select');
  sel.innerHTML = `<option value="">\\u2014 choose \\u2014</option>` +
    VERDICTS.map(v => `<option value="${v}">${v}</option>`).join('');
  sel.value = r.task1.verdict || '';
  sel.onchange = () => {
    if (sel.value) r.task1.verdict = sel.value; else delete r.task1.verdict;
    save(); updateProgress();
  };
  verd.append(sel);

  row.append(cons, verd);
  s.append(row);

  const pk = document.createElement('div');
  pk.innerHTML = `<span class="fieldlabel">Single most diagnostic peak (supporting or refuting)</span>`;
  const ta = document.createElement('textarea');
  ta.rows = 2;
  ta.value = r.task1.diagnostic_peak || '';
  ta.oninput = () => {
    const v = ta.value.trim();
    if (v) r.task1.diagnostic_peak = v; else delete r.task1.diagnostic_peak;
    save(); updateProgress();
  };
  pk.append(ta);
  s.append(pk);
  return s;
}

const esc = t => String(t).replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
const task1Done = r => r.task1.consistency && r.task1.verdict && r.task1.diagnostic_peak;
const task2Done = (r, c) => !c.task2_applicable || (r.task2.ranking && r.task2.confidence);

function updateProgress() {
  const t1 = SAMPLE.filter(c => task1Done(rec(c.audit_id))).length;
  const t2n = SAMPLE.filter(c => c.task2_applicable);
  const t2 = t2n.filter(c => task2Done(rec(c.audit_id), c)).length;
  document.getElementById('progress').textContent =
    `Task 1 ${t1}/${SAMPLE.length}  \\u00b7  Task 2 ${t2}/${t2n.length}`;
}

function render() {
  const root = document.getElementById('sheet');
  root.textContent = '';
  for (const c of SAMPLE) root.append(buildCompound(c));
  updateProgress();
}

function buildResponse() {
  const out = {};
  for (const c of SAMPLE) {
    const r = rec(c.audit_id), o = {};
    if (task1Done(r)) o.task1 = {
      consistency: r.task1.consistency,
      verdict: r.task1.verdict,
      diagnostic_peak: r.task1.diagnostic_peak,
    };
    if (c.task2_applicable && r.task2.ranking && r.task2.confidence)
      o.task2 = { ranking: r.task2.ranking, confidence: r.task2.confidence };
    if (o.task1 || o.task2) out[c.audit_id] = o;
  }
  return JSON.stringify({
    schema: 'spectro-audit-response/1',
    reviewer: document.getElementById('reviewer').value.trim() || 'UNNAMED',
    submitted_utc: new Date().toISOString(),
    sample_sha256: PAYLOAD.sample_sha256,
    responses: out,
  }, null, 2);
}

function exportFile() {
  const t1 = SAMPLE.filter(c => task1Done(rec(c.audit_id))).length;
  const t2n = SAMPLE.filter(c => c.task2_applicable);
  const t2 = t2n.filter(c => task2Done(rec(c.audit_id), c)).length;
  if (t1 < SAMPLE.length || t2 < t2n.length) {
    const msg = `Incomplete: Task 1 ${t1}/${SAMPLE.length}, Task 2 ${t2}/${t2n.length}.\n\n`
      + `Compounds missing any field are left out of the export entirely.\n`
      + `Export anyway?`;
    if (!confirm(msg)) return;
  }
  const name = (document.getElementById('reviewer').value.trim() || 'UNNAMED')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const blob = new Blob([buildResponse()], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${name}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

const jsonbox = document.getElementById('jsonbox');
document.getElementById('export').onclick  = exportFile;
document.getElementById('export2').onclick = exportFile;
document.getElementById('show-json').onclick = () => {
  document.getElementById('jsontext').value = buildResponse();
  jsonbox.showModal();
};
document.getElementById('copy').onclick = () => {
  const t = document.getElementById('jsontext');
  t.select(); navigator.clipboard.writeText(t.value);
};

const nameInput = document.getElementById('reviewer');
nameInput.value = localStorage.getItem(STORE + ':name') || '';
nameInput.oninput = () => localStorage.setItem(STORE + ':name', nameInput.value);

render();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=SAMPLE)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    raw = open(a.sample, "rb").read()
    sample = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
    digest = hashlib.sha256(raw).hexdigest()

    payload = json.dumps(
        {"sample": sample, "verdicts": VERDICTS, "sample_sha256": digest}
    ).replace("<", "\\u003c")          # cannot terminate the <script> early

    open(a.out, "w").write(PAGE.replace("__PAYLOAD__", payload))

    n2 = sum(c["task2_applicable"] for c in sample)
    degenerate = [c["audit_id"] for c in sample
                  if c["task2_applicable"] and c["n_candidates"] < 2]
    print(f"wrote {a.out}")
    print(f"  {len(sample)} compounds, {n2} with Task 2")
    print(f"  sample.jsonl sha256 = {digest[:16]}\u2026 (stamped into every export)")
    if degenerate:
        print(f"  note: {len(degenerate)} Task-2 set(s) hold a single candidate "
              f"({', '.join(degenerate)}) \u2014 nothing to rank, so they are excluded "
              f"from the precision figure, as \u00a75.2 excludes them there. They no "
              f"longer disclose anything: Task 2 is now shown on every compound, so a "
              f"lone candidate says only that the model proposed one structure.")


if __name__ == "__main__":
    sys.exit(main())
