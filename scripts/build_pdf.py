#!/usr/bin/env python3
"""Render docs/PAPER.md to a submission-quality PDF (pandoc + tectonic/XeTeX).

Keeps PAPER.md clean: figure plates are appended to a temporary copy, and unicode
glyphs (super/subscripts, math relations) are mapped for XeTeX via newunicodechar.
Run from the repo root:  python3 scripts/build_pdf.py
"""
import os, re, subprocess, tempfile, pypandoc

# PDF engine: tectonic by default; override with PDF_ENGINE=xelatex for a texlive host.
TECTONIC = os.environ.get("PDF_ENGINE", "/tmp/tectonic")
OUT = "docs/paper.pdf"

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
    ("fig_verifier.png", "Learned-verifier probe (\\S5.4; a complement, not part of the "
     "training-free protocol). (A) Conditional-on-recall top-1 (n=19) across four "
     "verifiers: a GNN trained on the same nmrshiftdb2 data as the HOSE lookup recovers "
     "the LLM verifier's 84\\% that the lookup (73\\%) could not. (B) Held-out $^{13}$C "
     "MAE --- the learned model is roughly 2$\\times$ sharper (1.70 vs 3.23 ppm)."),
]

UNI = {
    # Zero-width space -> a legal line break with no hyphen inserted. Used to make
    # long file paths in \texttt breakable; see breakable_paths() below.
    "\u200b": r"\allowbreak{}",
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


ZWSP = "\u200b"


def breakable_paths(md):
    """Give LaTeX somewhere to break a long file path.

    Paths set in \texttt cannot hyphenate, so `scripts/forward_verify_main.py` in
    running prose overflows the measure and, inside a narrow table cell, spills into
    the neighbouring column. Insert a zero-width space after the separators a path is
    naturally read in chunks by -- / and _ -- but only inside inline code spans, so
    ordinary prose is untouched. UNI maps the character to \allowbreak, which permits
    a break without printing a hyphen (a hyphen would read as part of the path).
    """
    def fix(m):
        inner = m.group(1)
        if "/" not in inner and "_" not in inner:
            return m.group(0)
        return "`" + re.sub(r"([/_])", r"\1" + ZWSP, inner) + "`"
    return re.sub(r"`([^`\n]+)`", fix, md)

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

ESI_OUT = "docs/paper_esi.pdf"


def build_esi(h_path, bib):
    """Build the Electronic Supplementary Information as its own document.

    RSC requires the ESI as a separate file, not appended to the article PDF. Figures are
    numbered S1, S2, ... and the ESI carries its own title block so it stands alone.
    """
    # Title in the body, not pandoc metadata: a long subtitle in the %-block renders as a
    # non-wrapping author line and runs off the page.
    md = ("# Electronic Supplementary Information\n\n"
          "**Recall, not verification, is the bottleneck when frontier LLMs elucidate "
          "molecular structures from real spectra**\n\n"
          "Ilkham Yabbarov, Rudra Sondhi, Rodrigo A. Vargas-Hern\u00e1ndez\n\n"
          "This document contains the Supporting Information figures referenced in the "
          "main article. Data, predictions, and the code that regenerates every figure "
          "are released with the manuscript; see *Data and code availability* in the "
          "main text.\n\n"
          "```{=latex}\n\\renewcommand{\\thefigure}{S\\arabic{figure}}"
          "\\setcounter{figure}{0}\n```\n\n")
    n = 0
    for fn, cap in SI_FIGS:
        path = f"docs/figures/{fn}"
        if os.path.exists(path):
            md += f"![{cap}]({path}){{width={fig_width(path)}}}\n\n"
            n += 1
    if not n:
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as mf:
        mf.write(md); esi_md = mf.name
    pypandoc.convert_file(esi_md, "pdf", format="markdown", outputfile=ESI_OUT,
                          extra_args=[f"--pdf-engine={TECTONIC}", "--citeproc",
                                      f"--bibliography={bib}", "--csl=docs/rsc.csl",
                                      "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
                                      "-H", h_path])
    os.unlink(esi_md)
    return n


def main():
    md = open("docs/PAPER.md").read()
    md = breakable_paths(md)
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
               "\u00b9\u00b3C and re-ranking selects the true structure 89% of the time it is "
               "proposed \u2014 but it is proposed only 34% of the time.\n\n")
    # Main-text figures are inline in PAPER.md, placed at first discussion as a journal
    # requires. Their captions live there too -- one source of truth, so a caption cannot
    # drift from the text the way the old duplicate list did. Widths are computed here
    # because markdown cannot: each figure renders at native size, never upscaled.
    def _size(m):
        path = m.group(2)
        return f"![{m.group(1)}]({path}){{width={fig_width(path)}}}" if os.path.exists(path) else m.group(0)
    # (?!\{) so an image that already carries an attribute block -- the graphical
    # abstract appended above -- is not stamped a second time and left rendering its
    # own width as literal body text.
    md, n_inline = re.subn(r"!\[(.*?)\]\((docs/figures/[^)]+)\)(?!\{)", _size, md,
                           flags=re.S)

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
        # Make the superscript citation numbers jump to their reference entry, and the
        # entries carry their DOI as a link. Without link-citations the in-text markers
        # render as inert text and a reader has to scroll to the list by hand.
        "-M", "link-citations=true",
        "-M", "link-bibliography=true",
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
    sz = os.path.getsize(OUT)
    n_esi = build_esi(h_path, bib)          # needs h_path, so clean up after
    os.unlink(md_path); os.unlink(h_path)
    print(f"wrote {OUT} ({sz//1024} KB) and docs/paper.tex")
    if n_esi:
        esz = os.path.getsize(ESI_OUT)
        print(f"wrote {ESI_OUT} ({esz//1024} KB, {n_esi} SI figures)")

if __name__ == "__main__":
    main()
