# IRSpectra-Bench / spectro-agent

Research + benchmark repository for molecular structure elucidation from real IR/NMR
spectra by LLMs. It ships (a) the `spectro_scraper` dataset-mining pipeline, (b) the
committed benchmark data under `data/`, and (c) reproduction/scoring scripts under
`scripts/`. See `README.md` for the full "Reproduce" command list and `docs/` for the
manuscript and protocols.

## Cursor Cloud specific instructions

- Python deps live in a virtualenv at `.venv/` (gitignored). Run everything through it,
  e.g. `.venv/bin/python scripts/score_main.py`, or `source .venv/bin/activate` first.
  The startup update script recreates/refreshes `.venv` from `requirements.txt`.
- `python3 -m venv` needs the system package `python3.12-venv` (installed once during
  setup, captured in the base image). If venv creation ever fails with an `ensurepip`
  error on a fresh machine, reinstall it: `sudo apt-get install -y python3.12-venv`.
- `requirements.txt` pulls the full stack including `torch`/`torch-geometric` (only used
  by the optional §5.6/§5.7 probes in `contrib/` and `scripts/gnn_predict.py`) and the
  chemistry stack (`rdkit`, `selfies`, `py2opsin`). `py2opsin` needs a JRE — `java` is
  present on the image.
- `scipy`, `pytest`, and `flake8` are dev/test-only tools not listed in
  `requirements.txt`; the update script installs them so lint/tests/`verify_statistics.py`
  run out of the box.
- Everything runs fully offline — all benchmark data is committed under `data/`. No API
  keys or network are required for tests, scoring, or the extraction pipeline. Network is
  only needed by `scripts/verify_citations.py` (CrossRef/arXiv) and live scraping via
  `spectro_scraper.cli` (fetching real DOIs); avoid those unless specifically testing them.
- Lint: there is no committed linter config. Use `.venv/bin/python -m flake8
  --select=E9,F63,F7,F82 scripts spectro_scraper tests contrib` for meaningful
  (syntax/undefined-name) errors; a bare `flake8` reports style noise only.
- Tests: `.venv/bin/python -m pytest tests/` (parser unit tests),
  `.venv/bin/python scripts/test_harness.py` (offline reply-parsing), and
  `.venv/bin/python scripts/check_manuscript.py` (manuscript integrity gate — should end
  with "all checks pass"; the 3 "AWAITING THE AUTHORS" items are expected, not failures).
- `scripts/build_pdf.py` (manuscript PDF rebuild) additionally needs `pandoc` + `tectonic`
  on PATH, which are NOT installed by default. Skip it unless PDF regeneration is the task.
- Scoring/analysis scripts must be run from the repo root (they read relative `data/`
  paths). Headline check: `.venv/bin/python scripts/score_main.py` prints
  `top1 28.4%` for n=194 — matches `README.md`.
