# n=500 expansion round — status

Pre-registration (frozen above the deviations line):
`docs/EXPANSION_PREREGISTRATION_500.md`.

**Opus deposits: 65/230.** Questions committed. Answer key withheld. No
`predictions2.jsonl`. **Do not score a partial. Do not write a top-1 / recall
number for this round into the ICLR paper.** Headline stays **n=295** until
this round is 100% deposited, validated (already snapshotted), and scored.

This branch is an independent pre-registered expansion, not a silent
replacement of n=194 or n=295. Pooling via `scripts/score_pooled.py --expand
--expand-500` is licensed by the pre-registration only after 230/230 Opus
responses exist.

## Draw (fixed before it ran)

| parameter | value |
|---|---|
| directory | `data/benchmark_expand_500/` |
| sampler | `scripts/benchmark_v2.py sample2` (unchanged) |
| n | 230 |
| seed | 2026500 |
| strata as drawn | 115 simple / 115 complex |
| exclusion set | 375 unique prior InChIKey-14s (all `data/benchmark*/answers*.jsonl`, including a local restore of the withheld +106 key) |
| InChIKey-14 collisions with any prior round | **0** |
| (formula, IR, ¹³C) collisions with any prior `questions*.jsonl` | **0** |
| J in every committed ¹H | yes |

`answers2.jsonl` is **not** in the tree. The +106 expansion key was restored
locally for the exclusion pass, then deleted from the working tree again.

## Ground-truth audit (before any prediction)

`python scripts/validate_benchmark.py` was run on this round **before** any
solver was invoked, so 13C-overread flags cannot depend on whether a compound
was solved.

| | count |
|---|---:|
| drawn | 230 |
| spectrally clean | **224** |
| flagged 13C-overread | **6** |

Flagged qids (still **must be solved**; excluded only from a later headline
pool): **R26, R31, R102, R105, R107, R138**. Snapshot: `clean_qids.json`.

Clean strata: 110 simple / 114 complex. If 224/224 of those later have Opus
responses, 295 + 224 = **519** (above 500). Do not treat 519 as a result; it
is the arithmetic of the draw + this audit, not a score.

## Collected

| arm | solver | compounds with a blind response | of 230 |
|---|---|---:|---:|
| expansion toward 500 | `claude-opus-5` | **65** | 28.3% |

**165** Opus qids outstanding: `outstanding_opus.txt`.

Banked (single-compound Cursor Task, `claude-opus-5-thinking-high`; three
candidates each; RDKit formula check in-solver):

| qid | agent |
|---|---|
| R01 | [Solve expand500 R01](bc-495ba284-1c56-58fc-b282-82f8002aa376) |
| R04 | [Solve expand500 R04](bc-da61804c-7d09-5f4f-9f05-4ed9ee78b904) |
| R05 | [Solve expand500 R05](bc-b1cba293-8512-5db3-bafe-491f476c7015) |
| R07 | [Solve expand500 R07](bc-75763310-4365-51d7-a62e-19c1e1627bbc) |
| R08 | [Solve expand500 R08](bc-c5ea5c74-2ef5-5121-835f-13a98ef270a2) |
| R11 | [Solve expand500 R11](bc-2493c41e-114f-5c3a-93a5-8b29f9d0567f) |
| R13 | [Solve expand500 R13](bc-d1ec949d-3ec1-5d2d-bee0-a0beafd07052) |
| R15 | [Solve expand500 R15](bc-b9890aa4-9049-5b42-94b6-0599a667f1c3) |
| R18 | [Solve expand500 R18](bc-71634e6c-e70b-5991-ad92-92078004449d) |
| R14 | [Solve expand500 R14](bc-af952c84-6a46-5ecf-b1e6-7c3876a8b4a9) |
| R19 | [Solve expand500 R19](bc-64e48a76-94fc-5aae-a0ed-4e850469e50e) |
| R10 | [Solve expand500 R10](bc-757d7b0e-7552-5f2e-a93f-0a7b587c1381) |
| R21 | [Solve expand500 R21](bc-88f5d900-2395-5dc1-9e23-7e0c60136684) |
| R20 | [Solve expand500 R20](bc-68862244-79e5-5a59-9310-f396bdaad8a8) |
| R22 | [Solve expand500 R22](bc-1857d3cd-3597-5327-8263-f286f12ae237) |
| R23 | [Solve expand500 R23](bc-3489b324-4198-5a50-885c-a45fb21ef78f) |
| R02 | [Solve expand500 R02 retry](bc-a049c52a-5d89-56b2-9eca-9c4f90a56ff1) |
| R26 | [Solve expand500 R26](bc-9f9b6b9a-1a47-5dc7-9c35-e43aebda5abf) |
| R28 | [Solve expand500 R28](bc-cd2e7aad-262b-5d7f-a24c-0ae690ec535e) |
| R29 | [Solve expand500 R29](bc-384aece2-b38c-53c4-a0f7-043547780456) |
| R27 | [Solve expand500 R27](bc-31b0c22f-5a19-5eb1-8cf5-06fdf743f83b) |
| R12 | [Solve expand500 R12 retry 2](bc-58d64272-b30a-5e42-af14-820dbc290efd) |
| R31 | [Solve expand500 R31](bc-4d322017-b0cf-5289-bce4-b6e249bd5f1d) |
| R32 | [Solve expand500 R32](bc-a96ac73b-09ae-54f8-949e-c503bcbed0fb) |
| R33 | [Solve expand500 R33](bc-7ed1119f-009b-512e-9c94-1cd528392f30) |
| R34 | [Solve expand500 R34](bc-ea19af6d-aa29-545a-b7d2-09f2f2309334) |
| R36 | [Solve expand500 R36](bc-de38bebc-c871-59a5-8950-83ff193f845d) |
| R24 | [Solve expand500 R24 retry](bc-bac6e539-40b1-5a49-a975-88e844cce172) |
| R35 | [Solve expand500 R35](bc-64c6ecb1-b99c-5aa2-ae86-5ac5d207c8f7) |
| R37 | [Solve expand500 R37](bc-fe25005f-9feb-5be3-9dc8-8486e75b298e) |
| R38 | [Solve expand500 R38](bc-4ab1821e-ff04-5ed3-9ff0-669e0602e542) |
| R41 | [Solve expand500 R41](bc-0ec1a852-6ca3-5e63-8b35-f86fffbc6a12) |
| R40 | [Solve expand500 R40](bc-d1347a06-c0fb-5ef7-9509-aafecd169d99) |
| R17 | [Solve expand500 R17 retry 3](bc-0e8b10c4-95e9-5e39-b1b5-f098d923d922) |
| R39 | [Solve expand500 R39](bc-605fa5ff-2868-5874-994a-5cc5a0da93ae) |
| R42 | [Solve expand500 R42](bc-64784252-af04-51a2-9821-ce6266b5059e) |
| R43 | [Solve expand500 R43](bc-dd5d4b60-9ba9-58e1-9563-04182f7e500b) |
| R45 | [Solve expand500 R45](bc-1b2102bd-af4b-5075-9324-0cb7f339da8c) |
| R47 | [Solve expand500 R47](bc-123817ee-d875-5b63-a472-dcf75e670f68) |
| R49 | [Solve expand500 R49](bc-fdb6db72-f15f-56a1-99f2-4f3287180deb) |
| R48 | [Solve expand500 R48](bc-e899bd10-4deb-5b67-b989-7dd71ca5f6d3) |
| R50 | [Solve expand500 R50](bc-9ac8a15d-bea8-5776-8236-cdd4c40661dc) |
| R52 | [Solve expand500 R52](bc-bedc8aad-616a-5163-b24a-30fb6a151a81) |
| R46 | [Solve expand500 R46](bc-9946176f-67e5-5fc8-9d82-d6ce57bd5c8d) |
| R53 | [Solve expand500 R53](bc-6181ea1d-ebe9-5806-981e-dfefbfc4f10b) |
| R51 | [Solve expand500 R51](bc-e3ac2769-48a3-59a3-b9c1-9e8568d0743b) |
| R56 | [Solve expand500 R56](bc-e82b8de1-0090-5a9e-ace4-7414864d8fce) |
| R57 | [Solve expand500 R57](bc-eeb007dd-46b5-578c-881e-4daef3b28a65) |
| R58 | [Solve expand500 R58](bc-9be4b527-7ba6-579a-9cb4-9668848399e8) |
| R54 | [Solve expand500 R54](bc-35b95323-5362-5810-981b-869be8ba74ae) |
| R59 | [Solve expand500 R59](bc-da9e8650-e819-55bb-95d4-ce53c6d22cd9) |
| R61 | [Solve expand500 R61](bc-d33d0356-6dbb-5559-b863-556e9b9f769c) |
| R62 | [Solve expand500 R62](bc-f9e803fb-b2cc-53d0-8d0b-bf938d94ce16) |
| R63 | [Solve expand500 R63](bc-59552f8f-fb74-5e6f-bcf6-d42318495f2f) |
| R60 | [Solve expand500 R60](bc-e1e1eade-b7c4-5cc5-873a-306151fc160b) |
| R09 | [Solve expand500 R09 resume](https://cursor.com/agents/bc-d762859b-94de-55f5-8b7e-b3d148747657) — Ultra resume 2026-09-19 |
| R03 | deposited via PR #48 — Ultra resume 2026-09-19 |
| R44 | deposited via PR #49 — Ultra resume 2026-09-19 |
| R30 | deposited via PR #51 — Ultra resume 2026-09-19 |
| R16 | deposited via PR #52 — Ultra resume 2026-09-19 |
| R67 | deposited via PR #53 — Ultra resume 2026-09-19 |
| R64 | deposited via PR #54 — Ultra resume 2026-09-19 |
| R25 | deposited via PR #55 — Ultra resume 2026-09-19 |
| R66 | deposited via PR #56 — Ultra resume 2026-09-19 |
| R70 | deposited via PR #58 — Ultra resume 2026-09-19 |

Still in flight:

none. Every previously launched single has either deposited or died.

**Opus usage cap.** Cursor Pro+ hit the monthly Opus limit (resets **2026-10-09**,
or sooner if a spend limit is set). These in-flight singles died with that
error and empty transcripts. **Not banked. Not retried with another model**
— this round's headline arm is Opus-only.

| qid | last agent | why not banked |
|---|---|---|
| R06 | [Solve expand500 R06 retry 6](bc-e18f59ba-3766-561a-a873-1959c27b5078) | Opus usage limit, empty |
| R55 | [Solve expand500 R55 retry](bc-3cc12a26-04b3-5414-bb68-90ea47be4194) | Opus usage limit, empty |
| R65 | [Solve expand500 R65](bc-4cc3c29b-ab0c-5962-90a5-3091828d627f) | Opus usage limit, empty |

Do **not** fill those slots with Grok, Composer, or Fable. Follow-up Cursor
runs should resume Opus singles from `outstanding_opus.txt` only after the
limit resets or a spend limit is added.

Next after Opus is available again: **R06, R55,
R65, then R68–R230**. Bank with `collect_round.py --partial`.
No scores on the 65/230 subset.

R12 first launch ([Solve expand500 R12](bc-7d6926d3-93dd-503d-85c9-dac2ea9e1b5a))
died with an empty reply. Not banked. First retry
([Solve expand500 R12 retry](bc-6c73b001-b1ce-5775-ae98-7f9a1944d3f5)) died
activity-task timeout with no candidates. Not banked. Second retry later
deposited.

R06 first launch ([Solve expand500 R06](bc-ddb8fee2-a02d-596e-acee-3c2743aae19f))
died with an activity-task timeout and no candidates. Not banked. First retry
([Solve expand500 R06 retry](bc-36007791-710e-5dab-8ff7-df7b62b755d9)) also
timed out. Second retry
([Solve expand500 R06 retry 2](bc-7bbd758b-69ac-5bb6-b0bc-a01e38efc558)) died
ERROR with an empty transcript. Not banked. Fourth retry
([Solve expand500 R06 retry 4](bc-bc31be3f-2abe-58d6-9086-ab1362180f0b))
timed out with no candidates. Not banked. Retry 5
([Solve expand500 R06 retry 5](bc-16d2284f-095c-521f-b221-84a6c278fcc4))
timed out with an empty transcript. Not banked. Retried again as a single.
R06 remains outstanding.

R02, R03, and R09 first launches also died on activity-task timeout with no
candidates ([Solve expand500 R02](bc-625e9cda-d75a-5253-a3a4-cf508face9e2),
[Solve expand500 R03](bc-b4a52e6e-c60e-5a0b-ac22-004a38ee4c0e),
[Solve expand500 R09](bc-fdd407c3-345e-554a-9cf8-9749d8402603)). Not banked.
R02's retry later deposited. R03 first retry
([Solve expand500 R03 retry](bc-c77a8696-bad2-55c4-8d2f-a220f54784a1)) died
ERROR with an empty transcript. R09 first retry
([Solve expand500 R09 retry](bc-63afd52f-7a89-5fbd-9c79-4b7c6f1de075)) timed
out with no candidates. Both retried again as singles. R03 retry 3
([Solve expand500 R03 retry 3](bc-a1702eae-0ffb-5f47-8940-835cc5faff01)) died
ERROR with an empty transcript. R09 retry 3
([Solve expand500 R09 retry 3](bc-f2123edc-8a83-52ef-b40b-ce76262b65d8))
timed out with no candidates. Neither banked. Both retried again as singles.
R03 retry 4
([Solve expand500 R03 retry 4](bc-71783912-e22b-51f0-9d48-82404ec7d76d))
and R09 retry 4
([Solve expand500 R09 retry 4](bc-0af73435-1a46-5644-9790-1ab25ad7627f))
timed out with empty transcripts (`{"messages": []}`). Neither banked. Both
retried again as singles. R03 later deposited three candidates on 2026-09-19
(PR #48). **Banked** (Ultra resume). R09 retry 5
([Solve expand500 R09 retry 5](bc-f994f196-d0ab-5685-9868-b5461eddfef7))
returned IDLE with thinking but an empty final message (no JSON). Not banked.
Resumed the same agent
([Solve expand500 R09 resume](https://cursor.com/agents/bc-d762859b-94de-55f5-8b7e-b3d148747657)),
which emitted three candidates on 2026-09-19. **Banked** (Ultra resume).

R16 first launch ([Solve expand500 R16](bc-eeb4d9cf-2c1d-5402-8ab1-0ff2a3234cf6))
died ERROR with an empty transcript (`{"messages": []}`). Not banked. First
retry ([Solve expand500 R16 retry](bc-0c63eb31-d1a2-5979-858c-6ed6af8a180d))
also died ERROR empty. Not banked. Retry 3
([Solve expand500 R16 retry 3](bc-a1ab7e90-1bdf-545d-bb80-dda2920ae5ca))
timed out with no candidates. Not banked. Retry 4
([Solve expand500 R16 retry 4](bc-13896659-c874-5291-963b-3734725f22a7))
timed out with an empty transcript. Not banked. Retried again as a single.
R16 later deposited three candidates on 2026-09-19 (PR #52). **Banked**
(Ultra resume).

R17 first launch ([Solve expand500 R17](bc-3a69da2c-4a4c-51a7-8bc2-3526ac6f3598))
died ERROR with an empty transcript (`{"messages": []}`). Not banked. First
retry ([Solve expand500 R17 retry](bc-6ca82f3d-9ce9-5ee9-8a4d-092b33a2d05c))
timed out with no candidates. Not banked. Third retry later deposited.

R24 first launch ([Solve expand500 R24](bc-fc0d4643-afa8-5471-864c-9bf179e07c41))
died with an activity-task timeout and no candidates. Not banked. Retry later
deposited.

R25 first launch ([Solve expand500 R25](bc-a04586aa-5c41-57ea-b7f3-df1b9d585810))
died with an activity-task timeout and no candidates. Not banked. Retry 2
([Solve expand500 R25 retry 2](bc-571f2499-225e-5855-bcf2-4b47bda807a8))
timed out with no candidates. Not banked. Retry 3
([Solve expand500 R25 retry 3](bc-97af48f9-93db-5155-9b28-db762619e34a))
timed out with an empty transcript. Not banked. Retried again as a single.
R25 later deposited three candidates on 2026-09-19 (PR #55). **Banked**
(Ultra resume).

R30 first launch ([Solve expand500 R30](bc-927de401-0b66-5b0e-a538-3876c223ada0))
died with an activity-task timeout and no candidates. Not banked. Retry 2
([Solve expand500 R30 retry 2](bc-eefd3bac-879e-523f-aaa8-a28f00159fa6))
timed out with no candidates. Not banked. Retry 3
([Solve expand500 R30 retry 3](bc-01f62bec-e70e-5d65-84a5-2bd5214dafdc))
timed out with an empty transcript. Not banked. Retried again as a single.
R30 later deposited three candidates on 2026-09-19 (PR #51). **Banked**
(Ultra resume).

R44 first launch ([Solve expand500 R44](bc-cc570487-c438-5b5c-bdb7-7c43bee03d7f))
died with an activity-task timeout and no candidates. Not banked. First retry
([Solve expand500 R44 retry](bc-885b85b5-ce1c-5192-ba33-f9a71fcf39b9)) timed
out with an empty transcript. Not banked. Retried again as a single. R44
later deposited three candidates on 2026-09-19 (PR #49). **Banked**
(Ultra resume).

R55 first launch ([Solve expand500 R55](bc-6d350f14-6cf4-5202-a99f-423c12c5bbe0))
died with an activity-task timeout and an empty transcript
(`{"messages": []}`). Not banked. Retried as a single. R55 remains
outstanding.

No Fable (or any other) arm is registered on this draw.

## Scoring (not done; do not invent)

| item | status |
|---|---|
| Opus deposits | **65/230** |
| `predictions2.jsonl` | not written (`collect_round.py` writes it only at 100%) |
| `score2` / top-1 / recall | **not run** — partial subsets are not scored |
| `scripts/score_main.py` n=194 | **untouched** |
| paper headline | **n=295** until 100% deposited + scored |
| `scripts/score_pooled.py --expand-500` | **illegal** until 230/230 |
| Fable | not part of this round |
| `forward_verify_main.py` | not run; no verification-precision number exists |

## Key handling

After the draw and the validate snapshot, `answers2.jsonl` was moved to
`/tmp/blind/_key/benchmark_expand_500.answers2.jsonl.withheld` and deleted
from the working tree. Restore for a **complete-round** scoring pass with:

```
python scripts/export_round.py --restore data/benchmark_expand_500 /tmp/blind
```

Confirm before any merge:

```
git ls-files data/benchmark_expand_500/answers2.jsonl   # must be empty
git ls-files data/benchmark_expand/answers2.jsonl       # must be empty
```

## How to deposit (follow-up Cursor runs)

1. Solver sees only the exported prompt under `/tmp/blind/benchmark_expand_500/`
   (or the same text inlined). RDKit formula/parse check only. Model:
   `claude-opus-5-thinking-high`. One compound per agent.
2. Write the reply as `/tmp/blind/replies_500/single_<qid>.json`, shape
   `{"R01": ["SMILES", "...", "..."]}` or `[{"qid":"R01","candidates":[...]}]`.
3. Bank without scoring:

```
python scripts/collect_round.py data/benchmark_expand_500 /tmp/blind/replies_500 --partial
```

4. Append a provenance row. Commit `raw/` + STATUS + outstanding list. Do
   **not** add `answers2.jsonl`. Do **not** run `score2` until 230/230.
5. After each bank, rewrite `outstanding_opus.txt` as the qids in
   `questions2.jsonl` that are not yet in `raw/`.

## How to pool (only at 100%)

```
python scripts/export_round.py --restore data/benchmark_expand_500 /tmp/blind
python scripts/validate_benchmark.py          # should match the committed clean snapshot
python scripts/benchmark_v2.py score2 --outdir data/benchmark_expand_500
python scripts/score_pooled.py --expand --expand-500
```

`score_pooled.py` refuses a missing `predictions2.jsonl` or a withheld key.
It does not rewrite `score_main.py`. Re-withhold the key after the score.

## Overnight / follow-up handoff

**Draw committed. Key withheld. 65/230 Opus deposited. BLOCKED on Cursor
Opus monthly usage (reset 2026-10-09 or spend limit). Do not substitute
another model. Zero in flight. Outstanding: 165 qids in
`outstanding_opus.txt`. No scores. Do not merge. Paper stays n=295.**
