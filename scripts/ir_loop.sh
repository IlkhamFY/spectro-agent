#!/bin/bash
cd /home/user/spectro-agent
for round in $(seq 1 60); do
  raw=$(wc -l < data/irexp/ir.jsonl 2>/dev/null || echo 0)
  [ "$raw" -ge 330000 ] && { echo "raw target reached: $raw"; break; }
  python3 scripts/s3_ir_harvest.py --target 500000 --out data/irexp --workers 48 >> /tmp/s3_loop.log 2>&1
  gzip -c data/irexp/ir.jsonl > data/irexp/ir_harvest_snapshot.jsonl.gz 2>/dev/null
  gzip -c data/irexp/seen_papers.txt > data/irexp/seen_papers.txt.gz 2>/dev/null
  git add -f data/irexp/ir_harvest_snapshot.jsonl.gz data/irexp/seen_papers.txt.gz >/dev/null 2>&1
  git commit -q -m "IRexp loop round $round: $(wc -l < data/irexp/ir.jsonl) raw IR" >/dev/null 2>&1
  git push -q origin claude/funny-maxwell-u5S31 >/dev/null 2>&1
  echo "round $round done: raw=$(wc -l < data/irexp/ir.jsonl)" 
done
