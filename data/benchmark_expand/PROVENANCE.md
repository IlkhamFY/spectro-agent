# Solver provenance — expansion draw

Which model actually produced each deposited batch. Recorded from the agent transcripts
at run time, because the runtime can fall back to a different model than the one
requested; the two arms are only meaningful if each was served by the model its
pre-registration names. Fallbacks were observed only on agents that died on a rate limit
before producing anything, so no deposited batch below was served by a substitute.

| arm | deposit | batch | compounds | model that produced every assistant turn |
|---|---|---|---|---|
| expansion round | `raw/` | 02 | R07–R12 | `claude-opus-5` |
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
| expansion round | `raw/` | 04a | R19–R21 | `claude-opus-5` |
| expansion round | `raw/` | 03a | R13–R15 | `claude-opus-5` |
| expansion round | `raw/` | 03b | R16–R18 | `claude-opus-5` |
| expansion round | `raw/` | 05 | R25–R30 | `claude-opus-5` |
| expansion round | `raw/` | 01a | R01–R03 | `claude-opus-5` |
| expansion round | `raw/` | 07b | R40–R42 | `claude-opus-5` |
| expansion round | `raw/` | 08b | R46–R48 | `claude-opus-5` |
| expansion round | `raw/` | 01b | R04–R06 | `claude-opus-5` |
| expansion round | `raw/` | 10b | R58–R60 | `claude-opus-5` |
| expansion round | `raw/` | 09b | R52–R54 | `claude-opus-5` |
| expansion round | `raw/` | 08a | R43–R45 | `claude-opus-5` |
| expansion round | `raw/` | 11b | R64–R66 | `claude-opus-5` |
| expansion round | `raw/` | 07a1 | R37 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | single_R01 | R01 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R02 | R02 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R04 | R04 | `claude-fable-5-1` |
| expansion round | `raw/` | single_R24 | R24 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | single_R13 | R13 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R14 | R14 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R17 | R17 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R16 | R16 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R25 | R25 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R26 | R26 | `claude-fable-5-1` |
| expansion round | `raw/` | single_R38 | R38 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | single_R15 | R15 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R28 | R28 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R29 | R29 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R06 | R06 | `claude-fable-5-1` |
| expansion round | `raw/` | single_R51 | R51 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | single_R52 | R52 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R55 | R55 | `claude-fable-5-1` |
| cross-model arm | `raw_fable/` | single_R53 | R53 | `claude-fable-5-1` |
| expansion round | `raw/` | single_R23 | R23 | `claude-opus-5` |
| cross-model arm | `raw_fable/` | single_R30 | R30 | `claude-fable-5-1` |
