#!/usr/bin/env python3
"""Publication figures for the benchmark paper."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json, random
from score_main import load, metrics, boot  # noqa
random.seed(0)
R=metrics(load())
def rate(rs,k): return 100*sum(r[k] for r in rs)/len(rs) if rs else 0
plt.rcParams.update({"font.size":11,"axes.spomednable" if False else "axes.grid":True,"grid.alpha":0.3})

# Fig 1: by difficulty, top-1 & recall with bootstrap CI
groups=[("All",R),("Simple",[r for r in R if r['diff']=='simple']),("Complex",[r for r in R if r['diff']=='complex'])]
fig,ax=plt.subplots(figsize=(5.2,3.6))
import numpy as np
x=np.arange(len(groups)); w=0.38
for i,(key,col,lab) in enumerate([("top1","#2a6f97","exact top-1"),("rec","#89c2d9","recovered (top-3)")]):
    pts=[];los=[];his=[]
    for _,sub in groups:
        p,lo,hi=boot(sub, lambda s: rate(s,key)); pts.append(p);los.append(p-lo);his.append(hi-p)
    ax.bar(x+(i-0.5)*w, pts, w, yerr=[los,his], capsize=4, color=col, label=lab)
ax.set_xticks(x); ax.set_xticklabels([f"{g[0]}\n(n={len(g[1])})" for g in groups])
ax.set_ylabel("accuracy (%)"); ax.set_ylim(0,80); ax.legend(frameon=False,fontsize=9)
ax.set_title("LLM structure elucidation on real spectra")
plt.tight_layout(); plt.savefig("docs/figures/fig1_difficulty.png",dpi=150); plt.close()

# Fig 2: by molecule size
buckets=["<=15","16-25",">25"]
fig,ax=plt.subplots(figsize=(5,3.4))
sub=lambda b:[r for r in R if r['hac']==b]
ax.plot(buckets,[rate(sub(b),'top1') for b in buckets],"o-",color="#2a6f97",label="exact top-1")
ax.plot(buckets,[rate(sub(b),'rec') for b in buckets],"s--",color="#89c2d9",label="recovered")
for b in buckets: ax.annotate(f"n={len(sub(b))}",(b,2),ha="center",fontsize=8,color="gray")
ax.set_xlabel("heavy atoms"); ax.set_ylabel("accuracy (%)"); ax.set_ylim(0,80); ax.legend(frameon=False)
ax.set_title("Accuracy falls with molecular size")
plt.tight_layout(); plt.savefig("docs/figures/fig2_size.png",dpi=150); plt.close()

# Fig 3: method ladder (from frozen prior results)
labels=["single-pass\n(no tools)","decoupled\nagents","generate-wide\n+ forward-verify"]
vals=[5,23,30]
fig,ax=plt.subplots(figsize=(4.6,3.4))
ax.bar(labels,vals,color=["#bbb","#89c2d9","#2a6f97"])
for i,v in enumerate(vals): ax.text(i,v+1,f"{v}%",ha="center")
ax.set_ylabel("exact top-1 (%)"); ax.set_ylim(0,40); ax.set_title("Inference-time methodology, no training")
plt.tight_layout(); plt.savefig("docs/figures/fig3_method.png",dpi=150); plt.close()

# Fig 4: IRexp dataset composition
import gzip
tot=121233; nmr=87075; struct=42842; trip=40491
fig,ax=plt.subplots(figsize=(4.8,3.2))
cats=["IR records","+ NMR","+ structure","full quad"]; v=[tot,nmr,struct,trip]
ax.bar(cats,v,color=["#013a63","#2a6f97","#468faf","#89c2d9"])
for i,val in enumerate(v): ax.text(i,val+2000,f"{val//1000}k",ha="center",fontsize=9)
ax.set_ylabel("records"); ax.set_title("IRexp: largest open experimental-IR dataset")
plt.xticks(rotation=15); plt.tight_layout(); plt.savefig("docs/figures/fig4_dataset.png",dpi=150); plt.close()
print("wrote 4 figures to docs/figures/")
