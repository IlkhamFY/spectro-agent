import json, glob
seen=set(); out=open("data/benchmark_v3/predictions2.jsonl","w"); n=0
for f in sorted(glob.glob("data/benchmark_v3/raw/b*.json")):
    arr=json.load(open(f))
    for o in arr:
        if o["qid"] in seen: continue
        seen.add(o["qid"])
        out.write(json.dumps({"qid":o["qid"],"candidates":o.get("candidates",[])[:3]})+"\n"); n+=1
out.close()
print(f"assembled {n} predictions from {len(glob.glob('data/benchmark_v3/raw/b*.json'))} batches")
