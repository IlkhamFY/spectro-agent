#!/usr/bin/env python3
"""Render docs/PAPER.md to a submission-quality PDF (pandoc + tectonic/XeTeX).

Keeps PAPER.md clean: figure plates are appended to a temporary copy, and unicode
glyphs (super/subscripts, math relations) are mapped for XeTeX via newunicodechar.
Run from the repo root:  python3 scripts/build_pdf.py
"""
import os, subprocess, tempfile, pypandoc

# PDF engine: tectonic by default; override with PDF_ENGINE=xelatex for a texlive host.
TECTONIC = os.environ.get("PDF_ENGINE", "/tmp/tectonic")
OUT = "docs/paper.pdf"

# Main-text figures (numbered Fig. 1-5)
FIGS = [
    ("fig_wall.png", "The diagnosis as a single part-to-whole bar of the 60 "
     "forward-verify compounds. The true structure is verified top-1 for 16 (green), "
     "recalled but mis-ranked for 3 (vermilion), and never proposed for 41 (grey) --- "
     "\\emph{the wall}, 68\\% of the bar. Forward-verification recovers 16/60 = 26\\% "
     "exact top-1 end-to-end: the model proposes the true structure for only 19/60 = "
     "31\\% of compounds and, of those, verifies 84\\%. Recall, not verification, is "
     "the wall."),
    ("fig1_difficulty.png", "Top-1 and recovered accuracy on IRSpectra-Bench by "
     "difficulty (all / simple / complex, n=194) with bootstrap 95\\% CIs."),
    ("fig5_models.png", "Four-model comparison on a 24-compound subset: Fable 5 45\\% "
     "$>$ Opus 25\\% $>$ Sonnet 20\\% $>$ Haiku 0\\% top-1 (strictly nested; "
     "underpowered to separate adjacent models at n=24)."),
    ("fig_mechanism.png", "Forward-verification on a real benchmark regioisomer pair "
     "(picolinamide vs nicotinamide): forward-predicted $^{13}$C matches the true "
     "isomer (chamfer 0.42 vs 1.30 ppm) --- an analog of NMR-crystallography."),
    ("fig3_method.png", "Forward-verification inference ladder on the same 60 "
     "compounds: solver self-ranking → + forward-verify → + generate-wide "
     "(23\\%/26\\%/30\\% top-1)."),
]

# Supporting-Information figures (numbered Fig. S1-S4)
SI_FIGS = [
    ("fig0_overview.png", "Study design: open multimodal data (IRexp) → blind, "
     "complexity-stratified benchmark → decoupled blind solving → "
     "forward-verification re-ranking; training-free core pipeline."),
    ("fig4_dataset.png", "IRexp composition: IR records, NMR-paired, structure-linked, "
     "and full IR+$^1$H+$^{13}$C+structure quadruples."),
    ("fig2_size.png", "Accuracy versus molecular size; the monotonic 60\\%→7\\% "
     "top-1 gradient with heavy-atom count."),
    ("fig6_electrolyte.png", "IRSpectra-Bench-Electrolyte by battery-electrolyte class "
     "(n=46): sp$^3$-C--F easiest (50\\%), sulfonyl and nitrile hardest (12\\%)."),
    ("fig_generator_probe.png", "Trained-generator probe (\\S5.6; a complement, not part "
     "of the training-free protocol). Candidate recall and deterministic-HOSE top-1 on "
     "the 194-compound benchmark for Claude / + scaffold enumeration / + trained "
     "generator: enumeration's near-degenerate isomers collapse the verifier "
     "(28.4→16.0\\%) while the generator's formula-correct candidates convert "
     "(28.4→35.1\\%)."),
    ("fig_verifier.png", "Learned-verifier probe (\\S5.7; a complement, not part of the "
     "training-free protocol). (A) Conditional-on-recall top-1 (n=19) across four "
     "verifiers: a GNN trained on the same nmrshiftdb2 data as the HOSE lookup recovers "
     "the LLM verifier's 84\\% that the lookup (73\\%) could not. (B) Held-out $^{13}$C "
     "MAE --- the learned model is roughly 2$\\times$ sharper (1.70 vs 3.23 ppm)."),
]

UNI = {
    "±": r"\ensuremath{\pm}", "×": r"\ensuremath{\times}", "−": r"\ensuremath{-}",
    "→": r"\ensuremath{\rightarrow}", "≈": r"\ensuremath{\approx}",
    "≤": r"\ensuremath{\leq}", "≥": r"\ensuremath{\geq}", "≫": r"\ensuremath{\gg}",
    "⊂": r"\ensuremath{\subset}", "∩": r"\ensuremath{\cap}",
    "∼": r"\ensuremath{\sim}",
    # Greek — Latin Modern roman lacks these glyphs, so route through math mode
    "χ": r"\ensuremath{\chi}", "μ": r"\ensuremath{\mu}", "σ": r"\ensuremath{\sigma}",
    "Δ": r"\ensuremath{\Delta}", "α": r"\ensuremath{\alpha}", "β": r"\ensuremath{\beta}",
    "λ": r"\ensuremath{\lambda}", "ν": r"\ensuremath{\nu}",
    "¹": r"\textsuperscript{1}", "²": r"\textsuperscript{2}", "³": r"\textsuperscript{3}",
    "⁴": r"\textsuperscript{4}", "⁵": r"\textsuperscript{5}", "⁶": r"\textsuperscript{6}",
    "⁷": r"\textsuperscript{7}", "⁸": r"\textsuperscript{8}", "⁹": r"\textsuperscript{9}",
    "⁰": r"\textsuperscript{0}", "⁻": r"\textsuperscript{$-$}",
    "₀": r"\textsubscript{0}", "₁": r"\textsubscript{1}", "₂": r"\textsubscript{2}",
    "₃": r"\textsubscript{3}", "₄": r"\textsubscript{4}", "₅": r"\textsubscript{5}",
    "₆": r"\textsubscript{6}", "₇": r"\textsubscript{7}", "₈": r"\textsubscript{8}",
    "₉": r"\textsubscript{9}",
}

TEXTWIDTH_IN = 6.3   # \textwidth at 1-inch margins on US-letter

def fig_width(path):
    """Render each figure at its native design size (px / dpi), capped at the text
    width — never upscaled. Upscaling a small figure is what makes lines and type look
    chunky; journals place figures at 1:1."""
    from PIL import Image
    im = Image.open(path)
    dpi = (im.info.get("dpi") or (600, 600))[0] or 600
    w_in = im.size[0] / dpi
    return f"{min(w_in, TEXTWIDTH_IN):.2f}in"

PREPRINT_SERVERS = {"arxiv", "chemrxiv", "biorxiv", "medrxiv"}


def bibliography(tmpdir):
    """docs/references.bib -> CSL JSON, retyping preprints so they render correctly.

    pandoc's BibTeX reader cannot emit CSL type "article", which is the branch the RSC
    style uses for preprints ("arXiv, 2024, preprint, arXiv:2408.08284, DOI: ..."); every
    BibTeX type maps to article-journal/report/webpage instead, which drops the year and
    the preprint label. So we convert to CSL JSON and retype entries whose container is a
    preprint server. references.bib stays the human-editable source of truth.
    """
    import json
    raw = subprocess.run(["pandoc", "docs/references.bib", "-f", "biblatex",
                          "-t", "csljson"], capture_output=True, text=True, check=True)
    entries = json.loads(raw.stdout)
    for e in entries:
        server = (e.get("container-title") or "").strip()
        if server.lower() in PREPRINT_SERVERS:
            e["type"] = "article"                 # -> the CSL preprint branch
            e["publisher"] = server
            if e.get("eprint"):
                e["number"] = e.pop("eprint")
            e.pop("container-title", None)
    out = os.path.join(tmpdir, "references.json")
    with open(out, "w") as f:
        json.dump(entries, f)
    return out


def header():
    lines = [r"\usepackage{newunicodechar}", r"\usepackage{graphicx}",
             r"\renewcommand{\figurename}{Fig.}",
             # Long unbreakable DOIs in the reference list cannot hyphenate, so a
             # justified paragraph stretches interword space to one-word-per-line.
             # Set the generated bibliography ragged-right instead.
             r"\usepackage{etoolbox}",
             r"\AtBeginEnvironment{CSLReferences}{\raggedright\sloppy}"]
    for ch, cmd in UNI.items():
        lines.append(f"\\newunicodechar{{{ch}}}{{{cmd}}}")
    return "\n".join(lines)

def main():
    md = open("docs/PAPER.md").read()
    # RSC requires a table-of-contents (graphical abstract) entry: one image plus a
    # <=250-character text summary. Appended as its own page so the submission bundle
    # carries it; journals lift it out of the PDF.
    toc = "docs/figures/graphical_abstract.png"
    if os.path.exists(toc):
        md += ("\n\n\\clearpage\n\n# Table of contents entry\n\n"
               f"![]({toc}){{width={fig_width(toc)}}}\n\n"
               "A frontier LLM recovers the correct molecular constitution from real, "
               "blind IR + \u00b9H + \u00b9\u00b3C literature spectra for 28% of 194 compounds. "
               "The bottleneck is candidate *recall*, not verification: forward-predicting "
               "\u00b9\u00b3C and re-ranking selects the true structure 84% of the time it is "
               "proposed \u2014 but it is proposed only 31% of the time.\n\n")
    md += "\n\n\\clearpage\n\n# Figure plates\n\n"
    for fn, cap in FIGS:
        path = f"docs/figures/{fn}"
        if os.path.exists(path):
            md += f"![{cap}]({path}){{width={fig_width(path)}}}\n\n"
    # Supporting-Information figures, renumbered Fig. S1, S2, ...
    if any(os.path.exists(f"docs/figures/{fn}") for fn, _ in SI_FIGS):
        md += ("\n\n\\clearpage\n\n"
               "```{=latex}\n\\renewcommand{\\thefigure}{S\\arabic{figure}}"
               "\\setcounter{figure}{0}\n```\n\n# Supporting Information figures\n\n")
        for fn, cap in SI_FIGS:
            path = f"docs/figures/{fn}"
            if os.path.exists(path):
                md += f"![{cap}]({path}){{width={fig_width(path)}}}\n\n"

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as mf:
        mf.write(md); md_path = mf.name
    with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as hf:
        hf.write(header()); h_path = hf.name
    bibdir = tempfile.mkdtemp()
    bib = bibliography(bibdir)

    args = [
        f"--pdf-engine={TECTONIC}",
        # Citations: [@key] in PAPER.md -> numbered RSC-style list, built from the
        # bibliography. Numbering is never hand-maintained.
        "--citeproc",
        f"--bibliography={bib}",
        "--csl=docs/rsc.csl",
        "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
        "-V", "linkcolor=blue", "-V", "urlcolor=blue", "-V", "colorlinks=true",
        "-V", "subparagraph",
        "-H", h_path,
    ]
    pypandoc.convert_file(md_path, "pdf", format="markdown", outputfile=OUT,
                          extra_args=args)
    # also emit a standalone, Overleaf-portable .tex (compile with XeLaTeX)
    pypandoc.convert_file(md_path, "latex", format="markdown",
                          outputfile="docs/paper.tex",
                          extra_args=["-s", "-H", h_path,
                                      "--citeproc",
                                      f"--bibliography={bib}",
                                      "--csl=docs/rsc.csl",
                                      "-V", "geometry:margin=1in",
                                      "-V", "fontsize=11pt"])
    os.unlink(md_path); os.unlink(h_path)
    sz = os.path.getsize(OUT)
    print(f"wrote {OUT} ({sz//1024} KB) and docs/paper.tex")

if __name__ == "__main__":
    main()
