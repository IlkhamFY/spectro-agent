#!/usr/bin/env python3
"""
Dump the 4-config ensemble's candidate SMILES per benchmark qid, keyed in the
closing_the_gap.py convention (main: 'R01'; controlled: 'data/benchmark_v3:R01'),
so the paper's HOSE/forward verifier can rerank Claude+generator pools.
Output: data/experimental/gen_candidates.jsonl  {qid_key: [canonical SMILES, ...]}
"""
import os, sys, glob, json
import numpy as np, torch
import selfies as sf
from omegaconf import OmegaConf
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from spectro_v2.train.core.system.selfies_generation_system import SELFIESGenerationSystem

EXP = "/home/rudra/spectro_v2/data/experimental"
CFGS = ["wave2_aug_light", "wave1_smiles_transfer", "wave1_smiles_adapter", "wave2_aug_mod"]
BEAMS = 10

def ck(run):
    d = sorted(glob.glob(f"/home/rudra/spectro_v2/logs/{run}/*/"))[-1]
    return sorted(glob.glob(d+"model-epoch=*val_loss*.ckpt"),
                  key=lambda x: float(x.split("val_loss=")[1].replace(".ckpt","")))[0]

def canon(s):
    m = Chem.MolFromSmiles(s) if s else None
    return Chem.MolToSmiles(m) if m else None

def key_of(coh, qid):
    return qid if coh == "benchmark_main" else f"data/{coh}:{qid}"

man = {json.loads(l)["row_idx"]: json.loads(l) for l in open(f"{EXP}/manifest.jsonl")}
test_idx = [int(i) for i in np.load(f"{EXP}/test_indices.npy")]
meta = [man[i] for i in test_idx]
cand = {key_of(m["cohort"], m["qid"]): set() for m in meta}

for run in CFGS:
    c = ck(run); print(f"gen from {run}: {os.path.basename(c)}")
    blob = torch.load(c, map_location="cpu", weights_only=False)
    cfg = OmegaConf.create(blob["hyper_parameters"]["cfg"])
    cfg.system.model.compile_backend = None; cfg.system.model.init_weights_from = None
    cfg.system.model.pretrained = False
    sysm = SELFIESGenerationSystem(cfg); sysm.load_state_dict(blob["state_dict"], strict=False)
    sysm = sysm.to("cuda:0").eval()
    dm = sysm.get_datamodule(); dm.setup("test"); dm.batch_size = 16
    tok = dm.tokenizer; is_smiles = getattr(dm, "target_type", "selfies") == "smiles"
    from torch.utils.data import DataLoader
    loader = DataLoader(dm.test_dataset, batch_size=16, num_workers=0, shuffle=False)
    gi = 0
    with torch.no_grad():
        for batch in loader:
            batch = {k:(v.to("cuda:0") if torch.is_tensor(v) else v) for k,v in batch.items()}
            mem, mask = sysm.encode(batch)
            bs,_ = sysm.decoder.generate_beam_search(mem, memory_key_padding_mask=mask,
                                                     max_len=sysm.decoder.max_len, num_beams=BEAMS)
            for i in range(bs.size(0)):
                k = key_of(meta[gi]["cohort"], meta[gi]["qid"]); gi += 1
                for b in range(BEAMS):
                    ids = bs[i,b].cpu().tolist()
                    try:
                        smi = tok.decode([ids])[0] if is_smiles else sf.decoder(tok.decode(ids))
                        cc = canon(smi)
                        if cc: cand[k].add(cc)
                    except Exception: pass
    del sysm; torch.cuda.empty_cache()

out = {k: sorted(v) for k, v in cand.items()}
json.dump(out, open(f"{EXP}/gen_candidates.jsonl", "w"))
szs = sorted(len(v) for v in out.values())
print(f"\nwrote {len(out)} qids -> {EXP}/gen_candidates.jsonl")
print(f"candidates/compound: median {szs[len(szs)//2]}, max {szs[-1]}, mean {sum(szs)/len(szs):.1f}")
