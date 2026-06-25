#!/usr/bin/env python3
"""
ABLATION: does IRexp finetuning create the recall, or does the simulated pretraining
alone already solve the experimental test? Evaluates the ORIGINAL sim SELFIES checkpoint
(NO experimental finetune) on the experimental 248 test, beam IK-14 recall@10.

Sim model: encoder sim-vocab (136/10) — matches the experimental_simvocab NMR cache;
decoder sim SELFIES (55 vocab) — decode with the SIM tokenizer (not the exp 143 one).
Compares to the IRexp-finetuned numbers (transfer 24.6%, aug champion 25.8%).
"""
import os, sys, glob
import torch
import selfies as sf
from omegaconf import OmegaConf
from rdkit import Chem
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
sys.path.insert(0, "/home/rudra/spectro_v2/preprocessing/tokenizers")
from selfies_tokenizer import SELFIESTokenizer
from spectro_v2.train.core.system.selfies_generation_system import SELFIESGenerationSystem

SIM_CKPT = sorted(glob.glob("/home/rudra/spectro_v2/logs/spectro_v2/selfies/hnmr_cnmr/"
                            "pretrained_false/03-13-17-43-08/model-epoch=*.ckpt"))[-1]
SIM_VOCAB = "/home/rudra/spectro_v2/data/simulated_data/tokenized_selfies/vocab.json"
DEV = "cuda:0"

def ik14(smi):
    m = Chem.MolFromSmiles(smi) if smi else None
    try: return Chem.MolToInchiKey(m)[:14] if m else None
    except Exception: return None

blob = torch.load(SIM_CKPT, map_location="cpu", weights_only=False)
cfg = OmegaConf.create(blob["hyper_parameters"]["cfg"])
OmegaConf.set_struct(cfg, False)
cfg.system.model.compile_backend = None
cfg.system.model.pretrained = False
cfg.system.model.init_weights_from = None
# swap datamodule to the EXPERIMENTAL sim-vocab cache (sim encoder vocab matches)
_dcfg = sys.argv[1] if len(sys.argv) > 1 else "exp_selfies_simvocab"
exp_data = OmegaConf.load(f"/home/rudra/spectro_v2/configs/data/{_dcfg}.yaml")
cfg.data = exp_data
print(f"input cache: {_dcfg}")
print(f"sim ckpt: {os.path.basename(SIM_CKPT)}  decoder_vocab={cfg.system.model.decoder_arch.vocab_size}")

sysm = SELFIESGenerationSystem(cfg)
sysm.load_state_dict(blob["state_dict"], strict=False)
sysm = sysm.to(DEV).eval()
dm = sysm.get_datamodule(); dm.setup("test"); dm.batch_size = 16
sim_tok = SELFIESTokenizer(vocab_path=SIM_VOCAB)        # 55-vocab, for decoding sim outputs
print(f"sim decode vocab: {sim_tok.vocab_size}")

from torch.utils.data import DataLoader
loader = DataLoader(dm.test_dataset, batch_size=16, num_workers=0, shuffle=False)
gt = dm.test_smiles
top1 = recall = valid = total = 0; gi = 0; K = 10
with torch.no_grad():
    for batch in loader:
        batch = {k:(v.to(DEV) if torch.is_tensor(v) else v) for k,v in batch.items()}
        mem, mask = sysm.encode(batch)
        bs,_ = sysm.decoder.generate_beam_search(mem, memory_key_padding_mask=mask,
                                                 max_len=sysm.decoder.max_len, num_beams=K)
        for i in range(bs.size(0)):
            g = ik14(gt[gi]); gi += 1; total += 1
            preds = []
            for b in range(K):
                try:
                    smi = sf.decoder(sim_tok.decode(bs[i,b].cpu().tolist()))
                    preds.append(ik14(smi))
                except Exception: preds.append(None)
            if preds[0]: valid += 1
            if g and preds[0] == g: top1 += 1
            if g and g in preds: recall += 1
pc = lambda x: f"{x}/{total} ({100*x/total:.1f}%)"
print(f"\n=== SIM zero-shot (NO IRexp finetune) on experimental 248 ===")
print(f"  top-1                : {pc(top1)}")
print(f"  recall@10            : {pc(recall)}")
print(f"  valid (beam-1)       : {pc(valid)}")
print(f"  vs IRexp-finetuned: transfer recall@10 24.6%, aug champion 25.8%")
