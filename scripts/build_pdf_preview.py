#!/usr/bin/env python3
"""Render docs/PAPER_preview.md (= PAPER.md + proposed §5.6) to docs/paper_preview.pdf
for Ilkham & Rodrigo's preliminary reading. Reuses build_pdf.py's header/figure machinery;
appends the generator-probe figure as Fig. 6. Does NOT touch PAPER.md / paper.pdf.
Run from repo root:  python3 scripts/build_pdf_preview.py   (first: python3 scripts/make_preview.py)
"""
import os, sys, tempfile, pypandoc
sys.path.insert(0, "scripts")
import build_pdf as bp

SRC = "docs/PAPER_preview.md"
OUT = "docs/paper_preview.pdf"

# main-text figures + the proposed §5.6 figure (Fig. 6)
FIGS = bp.FIGS + [
    ("fig_generator.png",
     "\\emph{Proposed §5.6 (author review).} A trained generator breaks the recall wall and "
     "its candidates convert. \\textbf{(A)} Truth in the candidate set rises 33.5\\%$\\to$41.8\\% "
     "(scaffold enumeration)$\\to$54.1\\% (trained generator), n=194. \\textbf{(B)} HOSE top-1 on "
     "the same pools: enumeration's near-degenerate isomers crater the verifier (28.4$\\to$16.0\\%) "
     "while the generator's formula-correct, separable candidates improve it (28.4$\\to$35.1\\%; "
     "McNemar p=0.015). The strong LLM forward-verifier lifts the generator pool to 41\\% top-1 "
     "(60-compound set; recall 56\\%, precision 73\\% vs generate-wide's 30\\%/41\\%/72\\%)."),
]

def main():
    md = open(SRC).read()
    md += "\n\n\\clearpage\n\n# Figure plates\n\n"
    for fn, cap in FIGS:
        path = f"docs/figures/{fn}"
        if os.path.exists(path):
            md += f"![{cap}]({path}){{width=82%}}\n\n"
    if any(os.path.exists(f"docs/figures/{fn}") for fn, _ in bp.SI_FIGS):
        md += ("\n\n\\clearpage\n\n```{=latex}\n"
               "\\renewcommand{\\thefigure}{S\\arabic{figure}}\\setcounter{figure}{0}\n```\n\n"
               "# Supporting Information figures\n\n")
        for fn, cap in bp.SI_FIGS:
            path = f"docs/figures/{fn}"
            if os.path.exists(path):
                md += f"![{cap}]({path}){{width=82%}}\n\n"

    # pandoc 3.9 won't close an inline-math $ that's immediately followed by a digit
    # ("$\to$41.8" leaks math mode). Their header maps the unicode arrow to \rightarrow,
    # so swap $\to$ -> → for identical output without the digit-adjacency bug.
    md = md.replace("$\\to$", "→")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as mf:
        mf.write(md); md_path = mf.name
    with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as hf:
        hf.write(bp.header() + "\n\\newunicodechar{§}{\\S}\n"); h_path = hf.name
    args = [f"--pdf-engine={bp.TECTONIC}", "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
            "-V", "linkcolor=blue", "-V", "urlcolor=blue", "-V", "colorlinks=true",
            "-V", "subparagraph", "-H", h_path]
    pypandoc.convert_file(md_path, "pdf", format="markdown", outputfile=OUT, extra_args=args)
    os.unlink(md_path); os.unlink(h_path)
    print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB)")

if __name__ == "__main__":
    main()
