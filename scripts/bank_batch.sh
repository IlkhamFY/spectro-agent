#!/usr/bin/env bash
# Bank one solver reply: verify the serving model from the agent transcript, deposit,
# append the provenance row, commit, push. Refuses to deposit a batch served by a
# fallback model.
#   scripts/bank_batch.sh <arm: opus|fable> <batch tag e.g. 04a> <agent-id> <qid range e.g. R19–R21>
set -euo pipefail
arm=$1; tag=$2; aid=$3; qids=$4
T=/tmp/claude-0/-home-user-spectro-agent/bec08aee-f6ac-507c-b903-7ad60c5a4054/tasks
if [ "$arm" = opus ]; then want=claude-opus-5; replies=/tmp/blind/replies; armflag=""; label="expansion round"; dep='`raw/`'
else want=claude-fable-5-1; replies=/tmp/blind/replies_fable; armflag="--arm fable"; label="cross-model arm"; dep='`raw_fable/`'; fi
served=$(python - "$T/$aid.output" <<'PY'
import json, sys, collections
m=collections.Counter()
for ln in open(sys.argv[1]):
    try: d=json.loads(ln)
    except Exception: continue
    msg=d.get("message",{})
    if isinstance(msg,dict) and msg.get("role")=="assistant" and msg.get("model"): m[msg["model"]]+=1
print(",".join(sorted(m)))
PY
)
[ "$served" = "$want" ] || { echo "REFUSING: batch $tag served by '$served', wanted $want"; exit 1; }
python scripts/collect_round.py data/benchmark_expand $replies $armflag --partial | head -1
row="| $label | $dep | $tag | $qids | \`$want\` |"
grep -qF "$row" data/benchmark_expand/PROVENANCE.md || echo "$row" >> data/benchmark_expand/PROVENANCE.md
git add data/benchmark_expand scripts/bank_batch.sh
git commit -q -m "Bank $label batch $tag ($want throughout)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0181o1WwM8sg4LoTvjqNAP6k"
git push -q origin claude/funny-maxwell-u5S31 && echo "banked $tag, pushed"
