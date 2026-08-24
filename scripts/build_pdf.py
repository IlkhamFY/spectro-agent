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

# Supporting-Information figures. Numbered S1, S2, ... by their order in this list --
# scripts/crossref.si_labels() reads that order back out of here, so a caption may be
# reworded but the filenames and their order may not be reshuffled casually.
# Section pointers are written as [@sec:...] and resolved in build_esi(), for the same
# reason the manuscript stopped typing them: "\\S5.6" is right on the day it is typed
# and silently wrong the moment a section moves.
SI_FIGS = [
    ("fig0_overview.png", "Study design: open multimodal data (IRexp) → blind, "
     "complexity-stratified benchmark → decoupled blind solving → "
     "forward-verification re-ranking; training-free core pipeline."),
    ("fig4_dataset.png", "IRexp composition: IR records, NMR-paired, structure-linked, "
     "and full IR+$^1$H+$^{13}$C+structure quadruples."),
    ("fig2_size.png", "Accuracy versus molecular size; top-1 falls monotonically as "
     "heavy-atom count increases."),
    ("fig6_electrolyte.png", "IRSpectra-Bench-Electrolyte by battery-electrolyte class "
     "(n=46)."),
    ("fig_generator_probe.png",
     "Trained-generator probe ([@sec:recall-wall-task-intrinsic]; a complement, not "
     "part of the training-free protocol). Candidate recall and deterministic-HOSE "
     "top-1 for Claude-only, + scaffold enumeration, and + trained generator on the "
     "194-compound benchmark."),
    ("fig_verifier.png",
     "Learned-verifier probe ([@sec:non-llm-verifiers-deterministic]; a complement, not "
     "part of the training-free protocol). (**a**) Conditional-on-recall top-1 over the "
     "whole benchmark (n=65) across four verifiers. (**b**) Held-out $^{13}$C MAE "
     "(lower is better)."),
]

UNI = {
    # Zero-width space -> a legal line break with no hyphen inserted. Used to make
    # long file paths in \texttt breakable; see breakable_paths() below.
    "\u200b": r"\allowbreak{}",
    "±": r"\ensuremath{\pm}", "×": r"\ensuremath{\times}", "−": r"\ensuremath{-}",
    "≈": r"\ensuremath{\approx}",
    # Relations and bounds set their own spacing; see \relspaced and \atmost in header().
    # A bare \ensuremath{\leq} is a single atom with no neighbours, so TeX contributes
    # nothing and the printed gap is whatever the author happened to type around it.
    "→": r"\relspaced{\rightarrow}", "≫": r"\relspaced{\gg}",
    "⊂": r"\relspaced{\subset}", "∩": r"\relspaced{\cap}",
    "≤": r"\atmost{\leq}", "≥": r"\atmost{\geq}",
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

# Cap on figure width. \textwidth at 1-inch margins on US-letter is 6.5in; the cap
# sits at the 6.3in the wide plates are drawn at, so it currently never binds -- it
# is a guard against a future figure exported wider than the measure, not a
# statement of what the measure is. (The 0.2in it leaves means a full-width plate
# does not line up with the text block; closing that is a change to the figure
# scripts, since fig_width() must never upscale.)
TEXTWIDTH_IN = 6.30
# ChemRxiv / RSC-article two-column page (A4). No journal class: branding lives in
# the running header as "ChemRxiv preprint" only.
GEO_ARTICLE = ("a4paper,top=1.65cm,bottom=1.75cm,left=1.5cm,right=1.5cm,"
               "columnsep=0.6cm,headheight=14pt")

def fig_size(path):
    """Native width and height in inches (from PNG dpi), capped at TEXTWIDTH_IN — never upscaled."""
    from PIL import Image
    png = path if path.lower().endswith(".png") else (path[:-4] + ".png"
          if path.lower().endswith(".pdf") else path)
    measure = png if os.path.exists(png) else path
    if measure.lower().endswith(".pdf"):
        return f"{TEXTWIDTH_IN:.2f}in", f"{TEXTWIDTH_IN * 0.55:.2f}in"
    im = Image.open(measure)
    dpi = (im.info.get("dpi") or (600, 600))[0] or 600
    w_in = im.size[0] / dpi
    h_in = im.size[1] / dpi
    if w_in > TEXTWIDTH_IN:
        scale = TEXTWIDTH_IN / w_in
        w_in *= scale
        h_in *= scale
    return f"{w_in:.2f}in", f"{h_in:.2f}in"


def fig_width(path):
    """Render each figure at its native design size (px / dpi), capped at the text
    width — never upscaled. Upscaling a small figure is what makes lines and type look
    chunky; journals place figures at 1:1.

    Prefer a sibling .pdf when present (vector twin from figstyle.save): LaTeX embeds
    it crisply. Width still comes from the PNG's dpi metadata when available.
    """
    return fig_size(path)[0]


def prefer_vector(path):
    """Swap docs/figures/foo.png -> foo.pdf when the vector twin exists."""
    if path.lower().endswith(".png"):
        pdf = path[:-4] + ".pdf"
        if os.path.exists(pdf):
            return pdf
    return path


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
    def fix(m, in_table):
        inner = m.group(1)
        if "/" not in inner and "_" not in inner:
            return m.group(0)
        # Not after a *trailing* separator: `data/audit/` would then be allowed to break
        # at its own end, stranding the following comma at the head of the next line.
        #
        # In prose, only after "/". A break at "_" splits a single identifier --
        # MODALITY_ABLATION.md printed as "MODALITY_" / "ABLATION.md", which reads as two
        # names -- while "/" is where a reader already segments a path.
        #
        # Inside a table cell the trade reverses, but only when the cell cannot otherwise
        # fit. A column is narrow by construction and a reader expects wrapping there,
        # whereas an unbreakable filename sets the column's minimum width and takes that
        # room from its neighbours. So allow the underscore break in a table -- but only
        # for a token long enough that refusing would squeeze the column: a 20-character
        # threshold leaves `score_main.py` and `clean_qids.json` whole and gives
        # `verifier_table_results.txt` somewhere to go.
        def sub(mm):
            tok = mm.group(0)
            return re.sub(r"([/_])(?=.)", r"\1" + ZWSP, tok) if (
                in_table and len(tok) >= 20) else re.sub(r"(/)(?=.)", r"\1" + ZWSP, tok)
        return "`" + re.sub(r"\S+", sub, inner) + "`"

    return "\n".join(
        re.sub(r"`([^`\n]+)`", lambda m: fix(m, line.lstrip().startswith("|")), line)
        for line in md.split("\n"))

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
                    # A table that fits on a page should not be broken; a table that
                    # cannot fit should not have a page reserved for it, because the
                    # attempt abandons the page -- the ESI's first page once ended 330pt
                    # short that way. So reserve the whole table when the whole table
                    # plausibly fits, and only the caption, head and two rows when it
                    # cannot. Without this Table 1 split with a single row stranded on the
                    # next page under no header.
                    whole = len(rows) + 4
                    # 12, not 8: a reserve that fits the caption and the head
                    # but no body rows leaves the head at the foot of a page
                    # and repeats it overleaf, which reads as two headers with
                    # nothing between them.
                    need = whole if whole <= 28 else 12
                    # ... and set it at caption size. \captionsetup{font=small} in the
                    # preamble reaches figures only, because a figure caption is a real
                    # \caption and a table caption here is an ordinary markdown
                    # paragraph. So figure captions printed at 9.96pt and table captions
                    # at 10.91pt -- body size -- on facing pages, the same mismatch of
                    # convention the caption package was brought in to end. \small has to
                    # close *after* the paragraph, so the closing \par is set with the
                    # small \baselineskip too.
                    out[k:k] = ["```{=latex}", f"\\needspace{{{need}\\baselineskip}}",
                                r"\begingroup\small", "```", ""]
                    out += ["```{=latex}", r"\endgroup", "```", ""]
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
    (r"\^([A-Za-z0-9,*]+)\^", r"\\textsuperscript{\1}"),
)


def _inline(md):
    """The handful of markdown constructs the title block actually uses.

    Small on purpose. The front matter is three lines under our own control, so a
    general converter would be more machinery than the job needs -- and pandoc is not
    available here, because the whole point is to hand LaTeX a title block rather than
    let the default template lay one out."""
    for pat, rep in INLINE_TEX:
        md = re.sub(pat, rep, md)
    return md.replace("&", r"\&").replace("~", r"\textasciitilde{}").replace("%", r"\%")


TITLE_RE = re.compile(
    r"\A#\s+(?P<title>.+?)\n+"          # H1
    r"(?P<authors>\*\*.+?)\n\n"         # author line (starts bold)
    r"(?P<affil>\*\^a\^.+?)\n",         # affiliation line
    re.S)


KEYWORDS = (
    "structure elucidation; NMR spectroscopy; infrared spectroscopy; "
    "large language models; chemical information; benchmark"
)

ABS_RE = re.compile(
    r"^---\n+## Abstract\n+(?P<abstract>.*?)\n+---\s*\n",
    re.M | re.S)


def title_block(md):
    r"""Lay out title, authors and abstract as a ChemRxiv / RSC-article banner.

    Two-column body (Digital Discovery / RSC article measure) with the banner
    spanning both columns. No journal name, logo, or copyright line -- ChemRxiv
    must not look already published. The `## Abstract` heading is removed here so
    PAPER.md stays checkable on GitHub.
    """
    m = TITLE_RE.search(md)
    if not m:
        return md
    title, affil = (_inline(m.group(k).strip()) for k in ("title", "affil"))
    authors = m.group("authors").strip()
    corr = re.search(r"\s*\*\(corresponding author:\s*([^)]*)\)\*,?", authors)
    email = corr.group(1).strip() if corr else ""
    if corr:
        authors = (authors[:corr.start()] + "^*^," + authors[corr.end():]).replace(
            ", ,", ",").rstrip(", ")
    authors = _inline(authors)
    note = (r"{\small\textsuperscript{*}\textit{E-mail: }"
            + email.replace("_", r"\_") + r"\par}" "\n") if email else ""
    am = ABS_RE.search(md)
    abstract = _inline(am.group("abstract").strip()) if am else ""
    # \twocolumn[{...}] is how article.cls sets a full-width title on a two-column
    # paper. Do NOT also pass classoption=twocolumn -- that path errors on a second
    # \twocolumn call.
    head = ("```{=latex}\n"
            r"\twocolumn[{" "\n"
            r"\centering" "\n"
            r"{\small\color{preprintink}\textit{ChemRxiv preprint"
            r" --- this version has not been peer reviewed.}\par}" "\n"
            r"\vspace{0.85em}" "\n"
            r"{\LARGE\bfseries\setlength{\baselineskip}{1.15\baselineskip}" "\n"
            f"{title}\\par}}\n"
            r"\vspace{0.85em}" "\n"
            r"{\large " f"{authors}" r"\par}" "\n"
            r"\vspace{0.4em}" "\n"
            r"{\small " f"{affil}" r"\par}" "\n"
            f"{note}"
            r"\vspace{0.85em}" "\n"
            r"\begin{minipage}{\textwidth}" "\n"
            r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.35em}" "\n"
            r"\small\noindent\textbf{Abstract.}\enspace " f"{abstract}" r"\par" "\n"
            r"\vspace{0.35em}" "\n"
            r"{\small\noindent\textbf{Keywords.}\enspace " f"{KEYWORDS}" r"\par}" "\n"
            r"\end{minipage}" "\n"
            r"\vspace{0.7em}" "\n"
            r"}]" "\n"
            "```\n\n")
    md = md[:m.start()] + head + md[m.end():]
    md = ABS_RE.sub("", md, count=1)
    # The H1 was consumed by the banner, so remaining ## must become \section, not
    # \subsection 0.1. Crossref already writes "1. Introduction" into the heading;
    # secnumdepth is 0 so LaTeX does not number it a second time.
    md = re.sub(r"^(#{2,4})(\s)", lambda m: "#" * (len(m.group(1)) - 1) + m.group(2),
                md, flags=re.M)
    return md


def header():
    lines = [r"\usepackage{newunicodechar}", r"\usepackage{graphicx}",
             # etoolbox supplies \pretocmd, \ifcsdef, \AtBeginEnvironment and
             # \AfterEndEnvironment, all used below. pandoc's own template happens to load
             # it first, and so does fvextra, which is why the load used to sit *after*
             # its first use and still work. Declare the dependency where it is needed.
             r"\usepackage{etoolbox}",
             r"\graphicspath{{./}{../}{figures/}{docs/figures/}}",
             r"\setcounter{secnumdepth}{0}",
             # TeX's default extra space after a period assumes the period ends a
             # sentence. This text is dense with abbreviations that it does not --
             # "Fig. 5", "e.g.", "i.e.", "vs.", and every abbreviated journal name in the
             # bibliography ("Nat. Mach. Intell.") -- each of which acquires a visible
             # double gap. French spacing is the standard remedy and matches how RSC
             # sets its own PDFs.
             r"\frenchspacing",
             r"\usepackage{needspace}",   # keep each table caption with its table
             r"\emergencystretch=2em",    # minor overfull lines in justified prose
             # RSC / Digital Discovery article measure: Times, indented paragraphs,
             # running ChemRxiv ident -- never a journal logo or "accepted manuscript".
             r"\definecolor{preprintink}{HTML}{5c636a}",
             r"\setlength{\parindent}{12pt}",
             r"\setlength{\parskip}{0pt plus 1pt}",
             r"\usepackage{fancyhdr}",
             r"\usepackage{dblfloatfix}",
             r"\pagestyle{fancy}",
             r"\fancyhf{}",
             r"\renewcommand{\headrulewidth}{0.35pt}",
             r"\renewcommand{\footrulewidth}{0pt}",
             r"\fancyhead[L]{\small\color{preprintink} ChemRxiv preprint}",
             r"\fancyhead[R]{\small\color{preprintink}\itshape IRSpectra-Bench}",
             r"\fancyfoot[C]{\small\thepage}",
             r"\fancypagestyle{plain}{\fancyhf{}"
             r"\renewcommand{\headrulewidth}{0.35pt}"
             r"\fancyhead[L]{\small\color{preprintink} ChemRxiv preprint}"
             r"\fancyhead[R]{\small\color{preprintink}\itshape IRSpectra-Bench}"
             r"\fancyfoot[C]{\small\thepage}}",
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
             r"\renewcommand{\figurename}{Fig.}",
             # Single lines stranded across a page break. TeX's defaults tolerate them;
             # a journal page should not.
             # A paragraph listing five monospaced paths in a row overran the measure by
             # 43pt: TeX had breakpoints between the items but the resulting line would
             # have been loose, and at the default tolerance of 200 it prefers to overrun.
             # 1500 lets it take the loose line instead, which is the right trade in a
             # document this full of unbreakable identifiers; \hbadness keeps the resulting
             # underfull reports out of the log so a real one still stands out.
             r"\tolerance=1500", r"\hbadness=1500",
             # pandoc emits a bare \begin{figure}, whose default placement is [tbp] --
             # "here" is not among the options, so a figure that would sit happily in the
             # column gets deferred to the top of a page and can end up alone on one.
             # Fig. 6 held a page with four lines of text on it. Allow "here".
             r"\makeatletter\renewcommand{\fps@figure}{htbp}\makeatother",
             # (\displaywidowpenalty sat here too and did nothing: it only fires at a page
             # break inside displayed maths, and neither document sets a display -- no
             # equation, align, gather or \[ in either .tex.)
             r"\clubpenalty=10000", r"\widowpenalty=10000",
             # ... and a heading with one line under it at the foot of a page is the same
             # defect one level up. Reserve enough for the heading plus a few lines.
             r"\pretocmd{\section}{\needspace{4\baselineskip}}{}{}",
             r"\pretocmd{\subsection}{\needspace{3.5\baselineskip}}{}{}",
             r"\pretocmd{\subsubsection}{\needspace{3\baselineskip}}{}{}",
             # Hyphenations TeX gets wrong in this vocabulary, each seen broken in the
             # built PDF: "regioi-somers", "McNe-mar", "IR-exp".
             #
             # "regioisomeric" and "randomisation" were listed here too and neither can
             # ever be reached: the first appears in no document, and the second only
             # ever appears as "Y-randomisation", where the explicit hyphen ends the word
             # as far as TeX's pattern matching is concerned, so the exception is never
             # consulted. The break that was actually seen is the one at that hyphen.
             r"\hyphenation{regio-isomer regio-isomers McNemar"
             r" InChI-Key IRexp nitro-phenyl HOSE Che-mo-tion}",
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
             r"\ifcsdef{CSLRightInline}{"
             # link-bibliography wraps whole entries in \href, so with colorlinks on, some
             # references printed entirely blue and others black with only the DOI blue.
             # RSC prints its reference list black. Keep the links live, drop the colour.
             r"\AtBeginEnvironment{CSLReferences}"
             r"{\sloppy\hypersetup{linkcolor=black,urlcolor=black,citecolor=black}}"
             r"\renewcommand{\CSLRightInline}[1]"
             r"{\parbox[t]{\linewidth - \csllabelwidth}{\raggedright #1}\break}"
             r"}{}"]
        # Continuous line numbers, which many journals ask for on a manuscript *under
    # review*. They are NOT part of a submission-ready reading copy and they are not
    # how the paper will print. Default OFF; set LINENOS=1 for a referee PDF.
    #
    # lineno predates longtable and cannot number inside it -- left alone it aborts the
    # run with an \prevdepth error on the first pipe table, of which this manuscript has
    # nine. Suspending numbering around longtable and around floats is the standard
    # remedy and costs nothing: a reviewer cites a table by its number, not by a line.
    if os.environ.get("LINENOS", "0") == "1":
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
    # Spacing for the relation glyphs, fixed here rather than left to the source.    #
    # \ensuremath{\leq} is one atom with nothing beside it, so TeX's own relation spacing
    # never fires and the printed gap is exactly the spaces the author typed: the same
    # glyph read "≥ 0.45" on one page and "≤15" on another, "1/20 → 3/20" against
    # "19/60→25/60". Both definitions swallow the neighbouring spaces (\unskip behind,
    # \ignorespaces ahead) and lay down their own, so the source can go on being written
    # whichever way reads best in markdown.
    #
    #   \relspaced  a genuine binary relation between two operands (→, ⊂, ∩, ≫): a thin
    #               space on both sides. The one behind is a kern and the one ahead is
    #               glue, which is how TeX treats a relation in math -- a line may break
    #               after it, never before, so "A →" cannot be stranded at a line end.
    #   \atmost     ≤ and ≥ never relate two operands in this manuscript; every one of
    #               them reads "at most 15", "at least 0.45" -- a prefix on the quantity
    #               that follows. So: an ordinary atom, not a relation, bound tight to
    #               its number with no space and no breakpoint between the two. The space
    #               to its left is a word boundary rather than relation spacing, and is
    #               left to the source, which varies it correctly ("Tanimoto ≥0.45" but
    #               "p≥0.25").
    lines += [
        r"\newcommand{\relspaced}[1]{\leavevmode\unskip\,\ensuremath{#1}"
        r"\hskip0.16667em\relax\ignorespaces}",
        r"\newcommand{\atmost}[1]{\ensuremath{\mathord{#1}}\ignorespaces}",
    ]
    for ch, cmd in UNI.items():
        lines.append(f"\\newunicodechar{{{ch}}}{{{cmd}}}")
    return "\n".join(lines)


def convert_longtables(tex):
    """longtable is illegal in two-column mode; emit table* + tabular instead."""
    needle = r"\begin{longtable}[]{"
    out, i = [], 0
    while True:
        j = tex.find(needle, i)
        if j < 0:
            out.append(tex[i:])
            break
        out.append(tex[i:j])
        brace = j + len(needle) - 1
        depth, p = 0, brace
        while p < len(tex):
            if tex[p] == "{":
                depth += 1
            elif tex[p] == "}":
                depth -= 1
                if depth == 0:
                    break
            p += 1
        cols = (tex[brace + 1:p]
                .replace(r"\columnwidth", r"\textwidth")
                .replace(r"\linewidth", r"\textwidth"))
        end = tex.find(r"\end{longtable}", p)
        body = tex[p + 1:end]
        for tag in (r"\endfirsthead", r"\endhead", r"\endfoot", r"\endlastfoot",
                    r"\noalign{}"):
            body = body.replace(tag, "")
        out.append("\\begin{table*}[htbp]\n\\centering\\small\n"
                   f"\\begin{{tabular}}{{{cols}}}{body}\\end{{tabular}}\n"
                   "\\end{table*}\n")
        i = end + len(r"\end{longtable}")
    return "".join(out)


def star_wide_figures(tex):
    """Plates authored wider than one column ride in figure* (full measure)."""
    def repl(m):
        inner = m.group(1)
        wm = re.search(r"width=([\d.]+)in", inner)
        if wm and float(wm.group(1)) >= 4.0:
            return r"\begin{figure*}" + inner + r"\end{figure*}"
        return m.group(0)
    return re.sub(r"\\begin\{figure\}(.*?)\\end\{figure\}", repl, tex, flags=re.S)


def attach_table_captions(tex):
    """Hoist the markdown table title into \\caption* so it travels with table*."""
    out, i = [], 0
    key = r"\textbf{Table "
    while True:
        j = tex.find(key, i)
        if j < 0:
            out.append(tex[i:])
            break
        # only rewrite the needspace/begingroup sandwich immediately before
        pre = tex[max(0, j - 80):j]
        if r"\begingroup\small" not in pre:
            out.append(tex[i:j + len(key)])
            i = j + len(key)
            continue
        # brace-match the \textbf{...}
        b = tex.find("{", j)
        depth, p = 0, b
        while p < len(tex):
            if tex[p] == "{":
                depth += 1
            elif tex[p] == "}":
                depth -= 1
                if depth == 0:
                    break
            p += 1
        cap = tex[b + 1:p]
        rest = tex[p + 1:]
        m = re.match(r"\s*\\endgroup\s*\\begin\{table\*\}\[htbp\]\s*\\centering\\small\s*", rest)
        if not m:
            out.append(tex[i:j + len(key)])
            i = j + len(key)
            continue
        ns = tex.rfind(r"\needspace", i, j)
        if ns < 0:
            out.append(tex[i:j + len(key)])
            i = j + len(key)
            continue
        out.append(tex[i:ns])
        out.append("\\begin{table*}[htbp]\n\\centering\\small\n"
                   f"\\caption*{{{cap}}}\n")
        i = p + 1 + m.end()
    return "".join(out)


def postprocess_tex(tex):
    """RSC-article two-column float conventions, no journal class required."""
    tex = tex.replace("{docs/figures/", "{figures/")
    tex = convert_longtables(tex)
    tex = attach_table_captions(tex)
    tex = star_wide_figures(tex)
    return tex

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
          "IRSpectra-Bench and IRexp: candidate recall, not verification,\\\\\n"
          "limits LLM elucidation from real experimental IR and NMR\\par}\n"
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
    # The ESI is numbered independently but shares the label namespace with the main
    # text, so [@sec:...] pointing back into the article still resolves.
    import crossref
    article = crossref.audit(open("docs/PAPER.md").read())["labels"]
    # Prose sections, if any: detail displaced from the main text during the cut lives in
    # docs/ESI.md, which is ordinary markdown and carries the same citations. Figures are
    # appended after it, so a reader meets the methods before the plates.
    body = "docs/ESI.md"
    if os.path.exists(body):
        esi_src = open(body).read()
        esi_src, _ = crossref.resolve(esi_src, external=article, prefix="S")
        # The same two helpers the article gets. Without them the ESI's tables fell back to
        # pandoc's equal-column division, so script paths in Tables S1, S2 and S4 overprinted
        # the neighbouring column, and Table S5's caption stranded a page above its table --
        # the \needspace guard that prevents that lives inside proportional_tables().
        esi_src = breakable_paths(esi_src)
        esi_src = proportional_tables(esi_src)
        # Figures inside the ESI prose need their widths computed too; the plates appended
        # below already get theirs.
        esi_src = re.sub(r"!\[(.*?)\]\((docs/figures/[^)]+)\)(?!\{)",
                         lambda m: (lambda p: (
                                    (lambda wh: f"![{m.group(1)}]({p}){{width={wh[0]} height={wh[1]}}}")
                                    (fig_size(p)) if os.path.exists(p) else m.group(0)))(prefer_vector(m.group(2))),
                         esi_src, flags=re.S)
        md += esi_src.rstrip() + "\n\n"
    n = 0
    for fn, cap in SI_FIGS:
        path = prefer_vector(f"docs/figures/{fn}")
        if os.path.exists(path):
            # The plate captions are a second caption source, and they pointed at the
            # article by typed number ("\\S5.6"). crossref exists so no number is typed;
            # run them through it as well, and an undefined label now stops the build
            # instead of printing a stale pointer.
            cap, _ = crossref.resolve(cap, external=article, prefix="S")
            w, h = fig_size(path)
            md += f"![{cap}]({path}){{width={w} height={h}}}\n\n"
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
    toc = prefer_vector("docs/figures/graphical_abstract.png")
    if os.path.exists(toc):
        md += ("\n\n\\clearpage\n\n```{=latex}\n\\section*{Table of contents entry}\n```\n\n"
               f"![]({toc}){{width={fig_size(toc)[0]} height={fig_size(toc)[1]}}}\n\n"
               # RSC caps the table-of-contents text at 250 characters. The earlier
               # wording also invited an arithmetic a reader will actually do: 34% x 89%
               # is 30%, not the 28% it opened with, because 28% is the solver alone and
               # 30% is the solver with forward verification. Say both.
               "IRSpectra-Bench and IRexp on real literature IR + \u00b9H + \u00b9\u00b3C: "
               "candidate recall, not verification, limits LLM elucidation \u2014 the true "
               "structure is proposed for 34% of 194 compounds and, once proposed, selected "
               "89% of the time, lifting top-1 from 28% to 30%.\n\n")
    # Main-text figures are inline in PAPER.md, placed at first discussion as a journal
    # requires. Their captions live there too -- one source of truth, so a caption cannot
    # drift from the text the way the old duplicate list did. Widths are computed here
    # because markdown cannot: each figure renders at native size, never upscaled.
    def _size(m):
        path = prefer_vector(m.group(2))
        if not os.path.exists(path):
            return m.group(0)
        w, h = fig_size(path)
        # Explicit height stops pandoc from injecting height=\textheight, which once
        # forced tall plates into a full-page box and blew the page (Fig. 6 + Table 7).
        return f"![{m.group(1)}]({path}){{width={w} height={h}}}"
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

    tex_args = [
        "-s", "-H", h_path,
        "--citeproc",
        f"--bibliography={bib}",
        "--csl=docs/rsc.csl",
        "-M", "link-citations=true",
        "-M", "link-bibliography=true",
        "-V", f"geometry:{GEO_ARTICLE}",
        "-V", "fontsize=10pt",
        "-V", "mainfont=Liberation Serif",
        "-V", "sansfont=Liberation Sans",
        "-V", "linkcolor=blue", "-V", "urlcolor=blue", "-V", "colorlinks=true",
    ]
    pypandoc.convert_file(md_path, "latex", format="markdown",
                          outputfile="docs/paper.tex", extra_args=tex_args)
    with open("docs/paper.tex") as fh:
        tex = fh.read()
    with open("docs/paper.tex", "w") as fh:
        fh.write(postprocess_tex(tex))
    run = subprocess.run([TECTONIC, "-o", "docs", "docs/paper.tex"],
                         capture_output=True, text=True)
    if run.returncode:
        sys.stderr.write(run.stderr or run.stdout)
        raise SystemExit(run.returncode)
    sz = os.path.getsize(OUT)
    n_esi = build_esi(h_path, bib)          # needs h_path, so clean up after
    os.unlink(md_path); os.unlink(h_path)
    print(f"wrote {OUT} ({sz//1024} KB) and docs/paper.tex")
    if n_esi:
        esz = os.path.getsize(ESI_OUT)
        print(f"wrote {ESI_OUT} ({esz//1024} KB, {n_esi} SI figures)")

if __name__ == "__main__":
    main()
