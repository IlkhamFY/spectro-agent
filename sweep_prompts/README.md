# Cross-vendor sweep — prompts for agent-driven runs

Ten blind structure-elucidation prompts, six compounds each, covering the 60-compound
`fverify60` arm of `docs/CROSS_VENDOR.md`. They are committed so a cloud agent working
from a clean clone can read them without first running
`scripts/cross_vendor_sweep.py prepare` — which would also write the held-out answer key
into its own workspace.

**Nothing here reveals an answer.** Each block gives a molecular formula, an IR band list
and ¹H/¹³C shift lists, and nothing else. The true structures live in
`data/cross_vendor/key.json`, which is git-ignored and is never committed; the file is
regenerated deterministically at scoring time, so an agent never needs it and should
never create it.

## Running these

Two properties decide whether the result means anything, and both are easy to lose:

**One fresh context per file.** §4.3 measures the same compounds at 5% top-1 in a single
long context against 15% across bounded, reset ones. Ten files answered inside one
conversation is the depressed arm, and the number stops being comparable to the paper's.
Give each file its own subagent or its own chat.

**Closed book.** No web search, no other repository file, no tools beyond reading the
prompt and writing the reply. The scoring harness cannot check this for you — it is the
one guarantee that rests entirely on how the run is set up.

Write each reply as strict JSON, `{"M001": ["smiles", "smiles", "smiles"], ...}`, to
`sweep_out/<model>/reply_NN.json`. Then:

```
python scripts/manual_collect.py collect sweep_out/<model> <model>
python scripts/cross_vendor_sweep.py prep-verify <model>
python scripts/cross_vendor_sweep.py score
```

`collect` reports coverage against the roster, so a run that lost a batch cannot pass as
a finished arm.

## What a result is worth

The portable claim is the inequality — verification precision conditional on recall
against generation recall — not either number alone. Before reading a low recall as a
weak model, check the formula-adherence line `score` prints: a model that cannot return a
parseable SMILES of the requested composition is not being measured on chemistry.
Claude runs 78–95% on that constraint; the first pilot model managed 2%.
