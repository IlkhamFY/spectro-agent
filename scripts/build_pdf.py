#!/usr/bin/env python3
"""Render docs/PAPER.md to a submission-quality PDF (pandoc + tectonic/XeTeX).

Keeps PAPER.md clean: figure plates are appended to a temporary copy, and unicode
glyphs (super/subscripts, math relations) are mapped for XeTeX via newunicodechar.
Run from the repo root:  python3 scripts/build_pdf.py
"""
import sys, os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
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
     "training-free protocol). (A) Conditional-on-recall top-1 over the whole benchmark "
     "(n=65) across four verifiers: a GNN trained on the same nmrshiftdb2 data as the "
     "HOSE lookup reaches the LLM verifier's level (91\\% against 89\\%) where the "
     "lookup (85\\%) does not move off the solver's own ranking. (B) Held-out $^{13}$C "
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
    naturally read in chunks by -- / -- but only inside inline code spans, so
    ordinary prose is untouched. UNI maps the character to \allowbreak, which permits
    a break without printing a hyphen (a hyphen would read as part of the path).
    """
    def fix(m):
        inner = m.group(1)
        if "/" not in inner and "_" not in inner:
            return m.group(0)
        # Not after a *trailing* separator: `data/audit/` would then be allowed to break
        # at its own end, stranding the following comma at the head of the next line.
        # Only after "/". A break at "_" splits a single identifier -- MODALITY_ABLATION.md
        # printed as "MODALITY_" / "ABLATION.md", which reads as two names -- while "/" is
        # where a reader already segments a path.
        return "`" + re.sub(r"(/)(?=.)", r"\1" + ZWSP, inner) + "`"
    return re.sub(r"`([^`\n]+)`", fix, md)

SEP_RE = re.compile(r'^\|(?:\s*:?-{2,}:?\s*\|)+$')
TABLE_MEASURE = 96          # target separator-row width, comfortably over pandoc's 72
MIN_COL = 4                 # characters; below this a numeric column pinches its digits


# Latin Modern Mono sets every character on a 0.6em body; Latin Modern Roman's lowercase
# averages nearer 0.45em. A run of code is therefore about a third wider than the same
# number of letters in prose, and counting characters flat under-measures it -- which is
# how `benchmark_v2_ctrl/` came to overprint the column beside it.
MONO_WIDTH = 1.3


def _measure(text):
    """Approximate typeset width of a cell, in units of one prose character."""
    text = text.strip().replace(ZWSP, "")
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)     # [text](link) -> text
    width = 0.0
    for i, part in enumerate(text.split("`")):                  # odd parts are code spans
        width += len(re.sub(r'\*\*|\*|~~', '', part)) * (MONO_WIDTH if i % 2 else 1.0)
    return width


def _cell_len(cell):
    """Rendered width of a markdown cell, ignoring markup that prints nothing.

    Zero-width spaces count here too, and they must not: breakable_paths() runs first, so a
    path cell arrives carrying one per separator and measures several characters wider than
    it prints. The column then wins width it does not need and its neighbours lose it --
    which is what wrapped "Claude Opus 4.8" onto three lines in the ESI's first table.
    """
    return int(round(_measure(cell)))


def _cell_len_tokens(cell):
    """The unbreakable runs in a cell, for the floor on a column's width.

    A column can be narrower than its widest cell -- the text wraps -- but never narrower
    than its longest single token, which has nowhere to break.
    """
    text = cell.strip().replace(ZWSP, " ")
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    out = []
    for i, part in enumerate(text.split("`")):
        scale = MONO_WIDTH if i % 2 else 1.0
        for tok in re.sub(r'\*\*|\*|~~', '', part).split():
            out.append("x" * int(round(len(tok) * scale)))
    return out


def proportional_tables(md):
    """Size each table column to the content it holds.

    A pipe table tells pandoc its column widths through the *length* of the separator
    row's dash runs -- but only when that row is longer than pandoc's --columns setting
    (72 by default). Every table here was written in the compact `|---|--:|--:|` form,
    which is shorter than that, so pandoc emitted no widths at all and the LaTeX writer
    fell back to dividing the page equally. Table 2 then wrapped "scaffold-level (best
    Tanimoto >= 0.45)" across two lines inside a quarter-page column while three columns
    of short percentages sat half empty.

    Rewriting the separator row -- proportional to the widest cell in each column, padded
    past 72 characters -- makes pandoc emit the widths the content actually needs. The
    compact source form stays readable; only what pandoc sees is rebuilt. Alignment
    markers are carried across unchanged, so a right-aligned numeric column stays right-
    aligned.
    """
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        if i + 1 < len(lines) and lines[i].startswith("|") and SEP_RE.match(lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [[c for c in r.strip().strip("|").split("|")] for r in lines[i:j]]
            aligns = [(c.strip().startswith(":"), c.strip().endswith(":"))
                      for c in rows[1]]
            n = len(aligns)
            body = [r for r in rows[:1] + rows[2:] if len(r) == n]   # ragged rows: not measured
            cols = [[_cell_len(r[k]) for r in body] for k in range(n)]
            # Sizing on the widest cell over-serves a column of prose. Prose wraps happily
            # and its long cells are long because they are sentences; a column of short
            # noun phrases does not wrap happily, and one 88-character neighbour was
            # squeezing "Claude Opus 4.8" onto three lines in the ESI's first table.
            #
            # Size on the *mean* instead, which is a fairer proxy for how much room a
            # column will actually use, and bound it: never below the longest unbreakable
            # token in the column (or it cannot be set at all), never above the widest cell
            # (or the column is given room it can never fill).
            longest_token = [
                max((max((len(t) for t in _cell_len_tokens(r[k])), default=0)
                     for r in body), default=0)
                for k in range(n)
            ]
            widths = []
            for k in range(n):
                col = cols[k] or [MIN_COL]
                mean = sum(col) / len(col)
                widths.append(max(MIN_COL, longest_token[k],
                                  min(max(col), round(mean))))
            # A character count is only a proxy for a typeset width, and digits and
            # capitals run wider than the lowercase it is calibrated on. Two characters
            # of slack per column keeps a header that just fits from wrapping anyway.
            widths = [w + 2 for w in widths]
            total = sum(widths)
            scaled = [max(MIN_COL, round(w * TABLE_MEASURE / total)) for w in widths]
            # Scaling can push a column back under the floor it was given, and then the
            # longest token in it has nowhere to go but into the next column -- which is
            # how a row of companion-document paths came to print 44pt past the margin.
            # Restore each floor, and pay for it out of the widest columns.
            floors = [min(t, TABLE_MEASURE // max(n, 1) * 2) for t in longest_token]
            for _ in range(n):
                deficit = sum(max(0, floors[k] - scaled[k]) for k in range(n))
                if not deficit:
                    break
                donors = sorted(range(n), key=lambda k: scaled[k] - floors[k], reverse=True)
                for k in range(n):
                    if scaled[k] < floors[k]:
                        scaled[k] = floors[k]
                for k in donors:
                    if deficit <= 0:
                        break
                    give = min(deficit, max(0, scaled[k] - max(floors[k], MIN_COL)))
                    scaled[k] -= give
                    deficit -= give
            cells = []
            for (left, right), w in zip(aligns, scaled):
                if left and right:
                    cells.append(":" + "-" * (w - 2) + ":")
                elif right:
                    cells.append("-" * (w - 1) + ":")
                elif left:
                    cells.append(":" + "-" * (w - 1))
                else:
                    cells.append("-" * w)
            lines[i + 1] = "|" + "|".join(cells) + "|"
            # Keep the caption with the table it names. pandoc renders the caption as an
            # ordinary paragraph followed by a longtable, and LaTeX will happily break
            # between them: Table 2's caption sat at the foot of p9 with its table
            # overleaf. Reserve caption + header + body before letting the caption set.
            # The caption is a paragraph, and it may wrap: Table 6's runs to a second line
            # ("Recall and precision have / different denominators..."), so testing only
            # the line immediately above the table missed it and its caption sat alone at
            # the foot of p12. Walk back to the start of the paragraph and test that.
            if out and out[-1] == "" and len(out) > 1:
                k = len(out) - 1
                while k > 0 and out[k - 1].strip():
                    k -= 1
                if out[k].startswith("**Table "):
                    need = min(len(rows) + 4, 16)
                    out[k:k] = ["```{=latex}", f"\\needspace{{{need}\\baselineskip}}",
                                "```", ""]
            out.extend(lines[i:j])
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


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


INLINE_TEX = (
    (r"\*\*(.+?)\*\*", r"\\textbf{\1}"),
    (r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\textit{\1}"),
    (r"\^([A-Za-z0-9,]+)\^", r"\\textsuperscript{\1}"),
)


def _inline(md):
    """The handful of markdown constructs the title block actually uses.

    Small on purpose. The front matter is three lines under our own control, so a
    general converter would be more machinery than the job needs -- and pandoc is not
    available here, because the whole point is to hand LaTeX a title block rather than
    let the default template lay one out."""
    for pat, rep in INLINE_TEX:
        md = re.sub(pat, rep, md)
    return md.replace("&", r"\&").replace("~", r"\textasciitilde{}")


TITLE_RE = re.compile(
    r"\A#\s+(?P<title>.+?)\n+"          # H1
    r"(?P<authors>\*\*.+?)\n\n"         # author line (starts bold)
    r"(?P<affil>\*\^a\^.+?)\n",         # affiliation line
    re.S)


def title_block(md):
    """Lay out the title, authors and abstract the way a journal sets them.

    Pandoc's default template renders the H1 as \section and the author line as an
    ordinary bold paragraph, so the first page reads as the start of a report rather
    than the head of an article: no centring, no size contrast, and the abstract sitting
    under a numbered-looking heading among the body sections.

    The substitution happens here rather than in PAPER.md so the source stays plain
    markdown -- readable on GitHub, and still checkable by the gates, which look for the
    `## Abstract` heading this function removes.
    """
    m = TITLE_RE.search(md)
    if not m:
        return md
    title, affil = (_inline(m.group(k).strip()) for k in ("title", "affil"))
    # The corresponding-author note sits inline in the markdown, which is the readable
    # place for it on GitHub and the wrong place in print: it doubles the length of the
    # author line, so the last author breaks across two centred lines with a surname
    # stranded on its own. Journals set it as a separate note under the affiliation.
    authors = m.group("authors").strip()
    corr = re.search(r"\s*\*\(corresponding author:\s*([^)]*)\)\*,?", authors)
    email = corr.group(1).strip() if corr else ""
    if corr:
        authors = (authors[:corr.start()] + ", " + authors[corr.end():]).replace(
            ", ,", ",").rstrip(", ")
    authors = _inline(authors)
    note = (r"\vspace{0.25em}" "\n"
            r"{\small\textit{E-mail: }\texttt{" + email.replace("_", r"\_") + r"}\par}"
            "\n") if email else ""
    head = ("```{=latex}\n"
            r"\begin{center}" "\n"
            r"{\LARGE\bfseries\setlength{\baselineskip}{1.15\baselineskip}" "\n"
            f"{title}\\par}}\n"
            r"\vspace{1.1em}" "\n"
            r"{\large " f"{authors}" r"\par}" "\n"
            r"\vspace{0.5em}" "\n"
            # A full Canadian address is a little too long for the measure and breaks with
            # "Canada." alone on the second line. Set it in a narrower centred box so the
            # break falls inside the address instead of after it.
            r"{\small\begin{minipage}{0.82\linewidth}\centering " f"{affil}"
            r"\end{minipage}\par}" "\n"
            f"{note}"
            r"\end{center}" "\n"
            r"\vspace{0.6em}" "\n"
            "```\n\n")
    md = md[:m.start()] + head + md[m.end():]

    # The abstract is set narrower and smaller, with rules above and below, and loses its
    # heading -- an abstract needs no label where it sits. Kept as markdown between two
    # raw blocks so its citations and cross-references still resolve.
    # re.sub's replacement string eats backslashes, and every one of these is LaTeX;
    # pass a lambda so the text goes through untouched.
    # The rules must span the *narrowed* measure, not \linewidth: inside a group with
    # \leftskip and \rightskip at 2em each, a \linewidth rule hangs 4em past the right
    # margin -- an overfull \hbox of exactly 40pt, and visible on the page.
    rule = r"\rule{\dimexpr\linewidth-4em\relax}{0.4pt}"
    open_abs = ("```{=latex}\n"
                r"\begingroup\small\setlength{\leftskip}{2em}"
                r"\setlength{\rightskip}{2em}" "\n"
                r"\noindent" + rule + r"\vspace{-0.4em}" "\n"
                "```\n\n")
    close_abs = ("```{=latex}\n"
                 r"\vspace{-0.4em}\noindent" + rule + r"\endgroup" "\n"
                 "```\n")
    md = re.sub(r"^---\n+## Abstract\n", lambda _: open_abs, md, count=1, flags=re.M)
    md = re.sub(r"^---\n(?=\n*## 1\.)", lambda _: close_abs, md, count=1, flags=re.M)
    return md


def header():
    lines = [r"\usepackage{newunicodechar}", r"\usepackage{graphicx}",
             r"\renewcommand{\figurename}{Fig.}",
             # TeX's default extra space after a period assumes the period ends a
             # sentence. This text is dense with abbreviations that it does not --
             # "Fig. 5", "e.g.", "i.e.", "vs.", and every abbreviated journal name in the
             # bibliography ("Nat. Mach. Intell.") -- each of which acquires a visible
             # double gap. French spacing is the standard remedy and matches how RSC
             # sets its own PDFs.
             r"\frenchspacing",
             r"\usepackage{needspace}",   # keep each table caption with its table
             # A code block that overruns the measure does not wrap -- it runs off the
             # page and its text is simply absent from the PDF. The ESI quotes verbatim
             # prompts, and one lost the rest of a sentence that way. pandoc emits plain
             # `verbatim` for an unlabelled block, so redefine that as a fancyvrb
             # environment which can break.
             r"\usepackage{fvextra}",
             r"\DefineVerbatimEnvironment{verbatim}{Verbatim}"
             r"{breaklines=true,breakanywhere=true,fontsize=\small,"
             r"breaksymbolleft={},breakautoindent=false}",
             # A caption package, for one reason: figures were labelled "Fig. 1:" while
             # tables -- which are written as markdown paragraphs, not LaTeX captions --
             # read "**Table 1.**". Two conventions on facing pages. This makes the figure
             # label match the table one.
             r"\usepackage{caption}",
             r"\captionsetup{labelsep=period,labelfont=bf,font=small}",
             # Single lines stranded across a page break. TeX's defaults tolerate them;
             # a journal page should not.
             # A paragraph listing five monospaced paths in a row overran the measure by
             # 43pt: TeX had breakpoints between the items but the resulting line would
             # have been loose, and at the default tolerance of 200 it prefers to overrun.
             # 1500 lets it take the loose line instead, which is the right trade in a
             # document this full of unbreakable identifiers; \hbadness keeps the resulting
             # underfull reports out of the log so a real one still stands out.
             r"\tolerance=1500", r"\hbadness=1500",
             r"\clubpenalty=10000", r"\widowpenalty=10000",
             r"\displaywidowpenalty=10000",
             # ... and a heading with one line under it at the foot of a page is the same
             # defect one level up. Reserve enough for the heading plus a few lines.
             r"\pretocmd{\section}{\needspace{4\baselineskip}}{}{}",
             r"\pretocmd{\subsection}{\needspace{3.5\baselineskip}}{}{}",
             r"\pretocmd{\subsubsection}{\needspace{3\baselineskip}}{}{}",
             # Hyphenations TeX gets wrong in this vocabulary, each seen broken in the
             # built PDF: "regioi-somers", "McNe-mar", "Y-randomisation", "IR-exp".
             r"\hyphenation{regio-isomer regio-isomers regio-isomeric McNemar"
             r" InChI-Key IRexp rand-om-isa-tion nitro-phenyl HOSE Che-mo-tion}",
             # Long unbreakable DOIs in the reference list cannot hyphenate, so a
             # justified paragraph stretches interword space towards one word per line.
             # Set the generated bibliography ragged-right instead.
             #
             # The \raggedright has to go *inside* \CSLRightInline's \parbox. Setting it
             # on the environment looks right and does nothing: \parbox begins with
             # \@parboxrestore, which resets \rightskip to zero and so restores full
             # justification for every entry. \sloppy survives that reset (it only
             # touches \tolerance and \emergencystretch) and is still wanted, to keep an
             # over-long DOI from running into the margin.
             #
             # Guarded, because this same preamble builds the ESI, which cites nothing
             # and so never gets pandoc's citeproc block or \CSLRightInline with it.
             r"\usepackage{etoolbox}",
             r"\ifcsdef{CSLRightInline}{"
             # link-bibliography wraps whole entries in \href, so with colorlinks on, some
             # references printed entirely blue and others black with only the DOI blue.
             # RSC prints its reference list black. Keep the links live, drop the colour.
             r"\AtBeginEnvironment{CSLReferences}"
             r"{\sloppy\hypersetup{linkcolor=black,urlcolor=black,citecolor=black}}"
             r"\renewcommand{\CSLRightInline}[1]"
             r"{\parbox[t]{\linewidth - \csllabelwidth}{\raggedright #1}\break}"
             r"}{}"]
    # Continuous line numbers, which RSC asks for on a manuscript under review. Off for
    # a reading copy: LINENOS=0.
    #
    # lineno predates longtable and cannot number inside it -- left alone it aborts the
    # run with an \prevdepth error on the first pipe table, of which this manuscript has
    # nine. Suspending numbering around longtable and around floats is the standard
    # remedy and costs nothing: a reviewer cites a table by its number, not by a line.
    if os.environ.get("LINENOS", "1") != "0":
        # Numbering resumes *after* the environment, not at its end. \AtEndEnvironment
        # injects its code inside the environment, and switching \linenumbers back on
        # there costs a row of vertical space: every table in the document carried its
        # bottom rule 17.8pt below the last row, against 4.1pt under the header rule.
        # \AfterEndEnvironment puts the switch outside, where it belongs -- 17.8pt -> 4.3pt,
        # and numbering still resumes.
        lines += [r"\usepackage{lineno}", r"\linenumbers",
                  r"\AtBeginEnvironment{longtable}{\nolinenumbers}",
                  r"\AfterEndEnvironment{longtable}{\linenumbers}",
                  r"\AtBeginEnvironment{figure}{\nolinenumbers}",
                  r"\AfterEndEnvironment{figure}{\linenumbers}"]
    for ch, cmd in UNI.items():
        lines.append(f"\\newunicodechar{{{ch}}}{{{cmd}}}")
    return "\n".join(lines)

ESI_OUT = "docs/paper_esi.pdf"


def build_esi(h_path, bib):
    """Build the Electronic Supplementary Information as its own document.

    RSC requires the ESI as a separate file, not appended to the article PDF. Figures are
    numbered S1, S2, ... and the ESI carries its own title block so it stands alone.
    """
    # Title set as a display block, the way the article's is -- not as an H1, which
    # rendered the ESI's own title at section weight and made the first page read as a
    # continuation of something rather than the head of a document. Raw LaTeX rather than
    # pandoc metadata: a long subtitle in the %-block renders as a non-wrapping author
    # line and runs off the page.
    md = ("```{=latex}\n"
          r"\begin{center}" "\n"
          r"{\Large\bfseries Electronic Supplementary Information\par}" "\n"
          r"\vspace{0.7em}" "\n"
          r"{\large\bfseries\setlength{\baselineskip}{1.15\baselineskip}" "\n"
          "Recall, not verification, is the bottleneck when frontier LLMs\\\\\n"
          "elucidate molecular structures from real spectra\\par}\n"
          r"\vspace{0.7em}" "\n"
          "Ilkham Yabbarov, Rudra Sondhi, Rodrigo A. Vargas-Hern\u00e1ndez\\par\n"
          r"\vspace{0.3em}" "\n"
          r"{\small\begin{minipage}{0.82\linewidth}\centering\itshape "
          "Department of Chemistry and Chemical Biology, McMaster University, Hamilton, "
          r"Ontario L8S 4L8, Canada.\end{minipage}\par}" "\n"
          r"\end{center}" "\n"
          r"\vspace{0.4em}\noindent\rule{\linewidth}{0.4pt}" "\n"
          "```\n\n"
          "Data, predictions, and the code that regenerates every figure and every number "
          "below are released with the manuscript; see *Data availability* in the main "
          "text.\n\n"
          "```{=latex}\n\\renewcommand{\\thefigure}{S\\arabic{figure}}"
          "\\setcounter{figure}{0}"
          "\n```\n\n")
    # Prose sections, if any: detail displaced from the main text during the cut lives in
    # docs/ESI.md, which is ordinary markdown and carries the same citations. Figures are
    # appended after it, so a reader meets the methods before the plates.
    body = "docs/ESI.md"
    if os.path.exists(body):
        esi_src = open(body).read()
        # The ESI is numbered independently but shares the label namespace with the main
        # text, so [@sec:...] pointing back into the article still resolves.
        import crossref
        esi_src, _ = crossref.resolve(
            esi_src, external=crossref.audit(open("docs/PAPER.md").read())["labels"],
            prefix="S")
        # The same two helpers the article gets. Without them the ESI's tables fell back to
        # pandoc's equal-column division, so script paths in Tables S1, S2 and S4 overprinted
        # the neighbouring column, and Table S5's caption stranded a page above its table --
        # the \needspace guard that prevents that lives inside proportional_tables().
        esi_src = breakable_paths(esi_src)
        esi_src = proportional_tables(esi_src)
        # Figures inside the ESI prose need their widths computed too; the plates appended
        # below already get theirs.
        esi_src = re.sub(r"!\[(.*?)\]\((docs/figures/[^)]+)\)(?!\{)",
                         lambda m: (f"![{m.group(1)}]({m.group(2)})"
                                    f"{{width={fig_width(m.group(2))}}}"
                                    if os.path.exists(m.group(2)) else m.group(0)),
                         esi_src, flags=re.S)
        md += esi_src.rstrip() + "\n\n"
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
    # Section, figure and table numbers are derived from position, never typed. See
    # scripts/crossref.py -- the manuscript carried 202 hand-typed numbers, one of which
    # (Table 9 sitting physically before Tables 6-8) was already wrong in the merged text.
    import crossref
    md, _labels = crossref.resolve(md)
    md = title_block(md)
    md = breakable_paths(md)
    md = proportional_tables(md)
    # RSC requires a table-of-contents (graphical abstract) entry: one image plus a
    # <=250-character text summary. Appended as its own page so the submission bundle
    # carries it; journals lift it out of the PDF.
    toc = "docs/figures/graphical_abstract.png"
    if os.path.exists(toc):
        md += ("\n\n\\clearpage\n\n# Table of contents entry\n\n"
               f"![]({toc}){{width={fig_width(toc)}}}\n\n"
               # RSC caps the table-of-contents text at 250 characters. The earlier
               # wording also invited an arithmetic a reader will actually do: 34% x 89%
               # is 30%, not the 28% it opened with, because 28% is the solver alone and
               # 30% is the solver with forward verification. Say both.
               "Recall, not verification, is the wall. On real, blind IR + "
               "\u00b9H + \u00b9\u00b3C literature spectra a frontier LLM proposes the true "
               "structure for 34% of 194 compounds and, once proposed, selects it 89% of "
               "the time \u2014 lifting top-1 from 28% to 30%.\n\n")
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
