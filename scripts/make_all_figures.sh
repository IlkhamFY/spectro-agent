#!/usr/bin/env bash
# Regenerate every manuscript figure (PNG + vector PDF twin). Run from repo root.
set -euo pipefail
export PYTHONPATH=scripts
python3 scripts/make_fig_wall.py
python3 scripts/make_figures.py
python3 scripts/make_fig_overview.py
python3 scripts/make_fig_robustness.py
python3 scripts/make_fig_forward_verify.py
python3 scripts/make_fig_generator_probe.py
python3 scripts/make_fig_verifier.py
python3 scripts/make_fig_electrolyte.py
python3 scripts/make_graphical_abstract.py
python3 scripts/score_models.py --fig
python3 scripts/make_fig_modality.py || true
echo "all figures written under docs/figures/"
