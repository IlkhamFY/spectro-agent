# Solver provenance — n=500 expansion draw

Which model actually produced each deposited batch. Recorded at deposit time,
because a runtime can fall back to a different model than the one requested.
This round's headline arm is **only** `claude-opus-5` (Cursor serving slug
`claude-opus-5-thinking-high`). A deposit served by any other model is refused.

Pre-registration: `docs/EXPANSION_PREREGISTRATION_500.md` (seed 2026500, n=230,
single-compound batches).

| arm | deposit | batch | compounds | model that produced every assistant turn |
|---|---|---|---|---|
| expansion toward 500 | `raw/` | single_R04 | R04 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R05 | R05 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R08 | R08 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R11 | R11 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R01 | R01 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R13 | R13 | `claude-opus-5` |
| expansion toward 500 | `raw/` | single_R07 | R07 | `claude-opus-5` |
