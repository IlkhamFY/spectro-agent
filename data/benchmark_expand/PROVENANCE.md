# Solver provenance — expansion draw

Which model actually produced each deposited batch. Recorded from the agent transcripts
at run time, because the runtime can fall back to a different model than the one
requested; the two arms are only meaningful if each was served by the model its
pre-registration names. Fallbacks were observed only on agents that died on a rate limit
before producing anything, so no deposited batch below was served by a substitute.

| arm | deposit | batch | compounds | model that produced every assistant turn |
|---|---|---|---|---|
| expansion round | `raw/` | 06 | R31–R36 | `claude-opus-5` |
| expansion round | `raw/` | 15 | R85–R90 | `claude-opus-5` |
| expansion round | `raw/` | 18 | R103–R106 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | 02 | R07–R12 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 04 | R19–R24 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 06 | R31–R36 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 07 | R37–R42 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 08 | R43–R48 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 15 | R85–R90 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | 18 | R103–R106 | `claude-fable-5-1` |

Every deposited reply equals the agent's final message exactly. Agents used only the Read
tool on their own batch file and Bash for RDKit formula checks; no transcript mentions the
key vault, an answers file, or any path under the repository.
