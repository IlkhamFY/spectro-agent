# Models and versions

All experiments used Anthropic Claude models accessed via the Claude consumer
subscription (claude.ai), invoked as independent sub-agents — no API, no
fine-tuning. For reproducibility, record the exact model snapshot identifiers and the
access window here before submission. **[TODO: authors fill in the bracketed values —
do not guess.]**

| role in paper | model (display name) | snapshot identifier | notes |
|---|---|---|---|
| headline benchmark (§4.1), forward-verification (§5) | Claude Opus | `claude-opus-[TODO]` | the frontier solver/verifier |
| cross-model comparison (§4.4) | Claude Fable 5 | `claude-fable-5-[TODO]` | strongest in §4.4 |
| cross-model comparison (§4.4) | Claude Opus | `claude-opus-[TODO]` | |
| cross-model comparison (§4.4) | Claude Sonnet | `claude-sonnet-[TODO]` | |
| cross-model comparison (§4.4) | Claude Haiku | `claude-haiku-[TODO]` | weakest (0% top-1) |

- **Access window:** [TODO: START–END, e.g. February–May 2026].
- **Harness:** consumer-subscription sub-agents (decoupled per-compound contexts; closed-book).
- Replace the bracketed identifiers with the exact snapshot strings actually used so the
  benchmark can be re-run against the same checkpoints. These are not stated in the
  manuscript or build scripts and must be supplied by the authors.
