# Create & push the two clean repos (human one-time)

`gh repo create` failed from the agent token (no `createRepository` permission).
Run these locally while logged in as **IlkhamFY**:

```bash
# --- IRexp (Scientific Data) ---
cd /path/to/exports/IRexp   # or unpack artifacts/IRexp-git.tar.gz
gh repo create IlkhamFY/IRexp --public \
  --description "IRexp: Scientific Data Data Descriptor (experimental IR band lists)" \
  --source . --remote origin --push

# --- IRSpectra-Bench (ICLR) ---
cd /path/to/exports/IRSpectra-Bench
gh repo create IlkhamFY/IRSpectra-Bench --public \
  --description "IRSpectra-Bench: ICLR manuscript (recall/verification diagnosis)" \
  --source . --remote origin --push
```

Or without `gh`:

```bash
# create empty repos on github.com/new as IlkhamFY/IRexp and IlkhamFY/IRSpectra-Bench
cd IRexp
git remote add origin git@github.com:IlkhamFY/IRexp.git
git push -u origin main

cd ../IRSpectra-Bench
git remote add origin git@github.com:IlkhamFY/IRSpectra-Bench.git
git push -u origin main
```

## Overleaf after push

1. New Project → Import from GitHub → each repo
2. Main document: `scientific_data.tex` / `iclr_paper.tex`
3. Compiler: pdfLaTeX

Commit author used in these packs: **Ilkham Yabbarov \<ilkhamfy@gmail.com\>**
