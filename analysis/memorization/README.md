# Memorization check (locked n=500)

Public-proxy check for the locked IRSpectra-Bench headline set (n=500, generation top-1 227/500, top-3 249/500). The script does not write into `data/` and does not change locked scores.

```bash
pip install rdkit numpy matplotlib
python analysis/memorization/run.py
```

First run downloads ChEMBL chemreps (latest public file pinned in the script), builds Morgan fingerprints, and queries PubChem and Europe PMC. Those files stay in `analysis/memorization/cache/` and are not committed. Later runs reuse the cache.

Inputs for the +106 and +200 rounds are read from git commit `48fcd30153df5e331fab43cfa514763db8ee3891` (branch `cursor/expand-bench-500-b78b`). The n=194 files are read from the working tree. Reconstructed structures stay in the cache because the expansion answer key is withheld from the tree.
