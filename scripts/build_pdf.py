#!/usr/bin/env python3
"""Render docs/PAPER.md to a submission-quality PDF (pandoc + tectonic/XeTeX).

Keeps PAPER.md clean: figure plates are appended to a temporary copy, and unicode
glyphs (super/subscripts, math relations) are mapped for XeTeX via newunicodechar.
Run from the repo root:  python3 scripts/build_pdf.py
"""
import os, subprocess, tempfile, pypandoc

TECTONIC = "/tmp/tectonic"
OUT = "docs/paper.pdf"

FIGS = [
    ("fig0_overview.png", "Study design: open multimodal data (IRexp) $\\to$ blind, "
     "complexity-stratified benchmark $\\to$ decoupled blind solving $\\to$ "
     "forward-verification re-ranking; training-free throughout."),
    ("fig4_dataset.png", "IRexp composition: IR records, NMR-paired, structure-linked, "
     "and full IR+$^1$H+$^{13}$C+structure quadruples."),
    ("fig1_difficulty.png", "Top-1 and recovered accuracy on IRSpectra-Bench by "
     "difficulty (all / simple / complex, n=194) with bootstrap 95\\% CIs."),
    ("fig2_size.png", "Accuracy versus molecular size; the monotonic 60\\%$\\to$7\\% "
     "top-1 gradient with heavy-atom count."),
    ("fig5_models.png", "Four-model comparison on a 24-compound subset: Fable 5 45\\% "
     "$\\gg$ Opus 25\\% $>$ Sonnet 20\\% $\\gg$ Haiku 0\\% top-1; capability-sensitive "
     "and far from saturated even for the newest model."),
    ("fig6_electrolyte.png", "IRSpectra-Bench-Electrolyte by battery-electrolyte class "
     "(n=46): sp$^3$-C--F easiest (50\\%), sulfonyl and nitrile hardest (12\\%)."),
    ("fig_mechanism.png", "Forward-verification on a real benchmark regioisomer pair "
     "(picolinamide vs nicotinamide): forward-predicted $^{13}$C matches the true "
     "isomer (chamfer 0.42 vs 1.30 ppm) --- the LLM analog of NMR-crystallography."),
    ("fig3_method.png", "Inference-time methodology ladder: single-pass $\\to$ "
     "decoupled agents $\\to$ generate-wide + forward-verify (5\\%/23\\%/30\\%)."),
]

UNI = {
    "±": r"\ensuremath{\pm}", "×": r"\ensuremath{\times}", "−": r"\ensuremath{-}",
    "→": r"\ensuremath{\rightarrow}", "≈": r"\ensuremath{\approx}",
    "≤": r"\ensuremath{\leq}", "≥": r"\ensuremath{\geq}", "≫": r"\ensuremath{\gg}",
    "¹": r"\textsuperscript{1}", "²": r"\textsuperscript{2}", "³": r"\textsuperscript{3}",
    "⁴": r"\textsuperscript{4}", "⁵": r"\textsuperscript{5}", "⁶": r"\textsuperscript{6}",
    "⁷": r"\textsuperscript{7}", "⁸": r"\textsuperscript{8}", "⁹": r"\textsuperscript{9}",
    "⁰": r"\textsuperscript{0}", "⁻": r"\textsuperscript{$-$}",
    "₂": r"\textsubscript{2}", "₃": r"\textsubscript{3}", "₆": r"\textsubscript{6}",
}

def header():
    lines = [r"\usepackage{newunicodechar}", r"\usepackage{graphicx}",
             r"\renewcommand{\figurename}{Fig.}"]
    for ch, cmd in UNI.items():
        lines.append(f"\\newunicodechar{{{ch}}}{{{cmd}}}")
    return "\n".join(lines)

def main():
    md = open("docs/PAPER.md").read()
    md += "\n\n\\clearpage\n\n# Figure plates\n\n"
    for i, (fn, cap) in enumerate(FIGS, 1):
        path = f"docs/figures/{fn}"
        if os.path.exists(path):
            md += f"![{cap}]({path}){{width=82%}}\n\n"

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as mf:
        mf.write(md); md_path = mf.name
    with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as hf:
        hf.write(header()); h_path = hf.name

    args = [
        f"--pdf-engine={TECTONIC}",
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
                                      "-V", "geometry:margin=1in",
                                      "-V", "fontsize=11pt"])
    os.unlink(md_path); os.unlink(h_path)
    sz = os.path.getsize(OUT)
    print(f"wrote {OUT} ({sz//1024} KB) and docs/paper.tex")

if __name__ == "__main__":
    main()
