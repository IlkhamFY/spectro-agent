#!/usr/bin/env python3
"""Build docs/PAPER_preview.md = PAPER.md + the proposed §5.6 (trained-generator probe),
inserted before §6 Discussion, with a reviewer banner. For preliminary author reading only."""
BANNER = """> **PRELIMINARY DRAFT FOR AUTHOR REVIEW (Ilkham & Rodrigo).** This copy adds one
> proposed subsection — **§5.6, a trained-generator probe** (highlighted below) — to test
> whether the recall wall is breakable. It is a *complement* to the training-free protocol,
> not part of it; inclusion and framing are your call. All §5.6 numbers are reproducible
> (`closing_the_gap_gen.py`, `forward_verify_gen.py`, `eval_sim_zeroshot.py`). The LLM
> forward-prediction step used blind in-house agents under your anonymized, isomer-separated,
> structure-only protocol (transcript-audited for zero tool/web access); please re-run it under
> your pinned model-snapshot pipeline to record the camera-ready number (it should land near
> the 41% reported here — precision already matches your generate-wide value, 73% vs 72%).

---

"""

# §5.6 is sourced verbatim from docs/GENERATOR_PROBE.md (single source of truth — the
# PDF/preview can never drift from the standalone draft).
_probe = open("docs/GENERATOR_PROBE.md").read()
SEC = _probe[_probe.index("## 5.6"):].rstrip() + "\n\n---\n\n"

md = open("docs/PAPER.md").read()
marker = "## 6. Discussion"
assert marker in md, "discussion marker not found"
out = BANNER + md.replace(marker, SEC + marker, 1)
open("docs/PAPER_preview.md", "w").write(out)
print(f"wrote docs/PAPER_preview.md ({len(out.splitlines())} lines; §5.6 inserted before §6)")
