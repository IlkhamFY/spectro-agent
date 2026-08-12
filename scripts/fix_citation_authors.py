#!/usr/bin/env python3
"""
Rewrite each bibliography entry's author list from its authoritative record.

scripts/verify_citations.py found six entries whose family names were all correct and
whose given names were not -- "Chacko, Elizabeth" for a paper by Edwin Chacko, "Praski,
Micha{\\l}" for one by Mateusz Praski. Because RSC style prints initials, several of
those rendered identically to the truth and were invisible in the PDF; the wrong names
sat in the BibTeX that anyone re-using this work would inherit.

Hand-patching invites the same class of error, so the author field is regenerated from
CrossRef (for DOIs) or the arXiv API (for preprints) rather than retyped.

  python scripts/fix_citation_authors.py --dry-run   # show what would change
  python scripts/fix_citation_authors.py             # apply
"""
import json, re, subprocess, sys, time, unicodedata, urllib.parse

BIB = "docs/references.bib"
DRY = "--dry-run" in sys.argv


def get(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sL", "--max-time", "40", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        time.sleep(2 * (i + 1))
    return ""


def latex_escape(name):
    """Non-ASCII given/family names must survive as valid BibTeX."""
    out = []
    for ch in name:
        out.append({
            "á": r"{\'a}", "é": r"{\'e}", "í": r"{\'i}", "ó": r"{\'o}", "ú": r"{\'u}",
            "à": r"{\`a}", "è": r"{\`e}", "ä": r'{\"a}', "ö": r'{\"o}', "ü": r'{\"u}',
            "ñ": r"{\~n}", "ç": r"{\c c}", "ł": r"{\l}", "ż": r"{\.z}", "ś": r"{\'s}",
            "ć": r"{\'c}", "ź": r"{\'z}", "ą": r"{\k a}", "ę": r"{\k e}", "å": r"{\aa}",
            "ø": r"{\o}", "š": r"{\v s}", "č": r"{\v c}", "ř": r"{\v r}", "ž": r"{\v z}",
        }.get(ch, ch))
    return "".join(out)


def fmt(authors):
    """[(family, given)] -> BibTeX 'Family, Given and ...', wrapped at a sane width."""
    parts = [f"{latex_escape(f)}, {latex_escape(g)}" if g else latex_escape(f)
             for f, g in authors]
    line, lines = "", []
    for i, p in enumerate(parts):
        piece = p + (" and " if i < len(parts) - 1 else "")
        if len(line) + len(piece) > 62:
            lines.append(line.rstrip()); line = ""
        line += piece
    if line:
        lines.append(line.rstrip())
    return ("\n" + " " * 13).join(lines)


def authoritative(entry_body):
    doi = re.search(r'doi\s*=\s*\{([^}]*)\}', entry_body)
    eprint = re.search(r'eprint\s*=\s*\{([^}]*)\}', entry_body)
    doi = doi.group(1) if doi else ""
    if eprint or "arxiv" in doi.lower():
        aid = eprint.group(1) if eprint else doi.split("arXiv.")[-1]
        xml = get(f"https://export.arxiv.org/api/query?id_list={aid}&max_results=1")
        names = re.findall(r'<author>\s*<name>(.*?)</name>', xml, re.S)
        out = []
        for n in names:
            w = n.split()
            out.append((w[-1], " ".join(w[:-1])) if len(w) > 1 else (n, ""))
        return out, "arXiv"
    if doi:
        try:
            m = json.loads(get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"))["message"]
        except Exception:
            return None, "unresolved"
        return [(a.get("family", ""), a.get("given", "")) for a in m.get("author", [])], "CrossRef"
    return None, "no identifier"


def main():
    raw = open(BIB, encoding="utf-8").read()
    changed = 0
    for m in list(re.finditer(r'@(\w+)\{([^,]+),(.*?)\n\}', raw, re.S)):
        key, body = m.group(2).strip(), m.group(3)
        cur = re.search(r'(author\s*=\s*\{)(.*?)(\},?\s*\n)', body, re.S)
        if not cur:
            continue
        if "others" in cur.group(2).lower():
            print(f"  --  {key:24} 'and others' — left alone")
            continue
        auth, src = authoritative(body)
        if not auth:
            print(f"  ??  {key:24} {src}")
            continue
        # Never trade a full given name for the registry's initial: CrossRef stores
        # "W." for Wolfgang Bremser, and overwriting would lose information the bib
        # already has right. Keep ours when the source is merely an abbreviation of it.
        old_pairs = []
        # Normalise the whole field first: the author list is wrapped across lines, so
        # splitting on " and " before collapsing whitespace silently merges the pair
        # that straddles a line break and the length check below then skips the merge.
        for a in " ".join(cur.group(2).split()).split(" and "):
            a = " ".join(a.split())
            if "," in a:
                f_, g_ = a.split(",", 1)
            else:
                w = a.split(); f_, g_ = (w[-1], " ".join(w[:-1])) if len(w) > 1 else (a, "")
            old_pairs.append((f_.strip(), g_.strip()))
        if len(old_pairs) == len(auth):
            merged = []
            for (of, og), (nf, ng) in zip(old_pairs, auth):
                on = re.sub(r'[^A-Za-z]', '', og.split()[0]) if og.split() else ""
                nn = re.sub(r'[^A-Za-z]', '', ng.split()[0]) if ng.split() else ""
                # CrossRef stores several names stripped of diacritics and hyphens
                # ("Vargas Hernandez" for Vargas-Hern\'andez, "Alan" for Al\'an).
                # That is a poorer record, not a correction, so keep ours whenever the
                # two agree once accents and hyphens are folded away.
                fold = lambda t: re.sub(r'[^a-z]', '', unicodedata.normalize("NFKD", t.lower())
                                        .encode("ascii", "ignore").decode())
                bib_tex_fold = lambda t: re.sub(r'[^a-z]', '', re.sub(r"\\[a-z']|\{|\}", '', t.lower()))
                same_modulo_accents = (bib_tex_fold(of) == fold(nf) and
                                       bib_tex_fold(og) == fold(ng))
                keep_old = same_modulo_accents or (len(nn) <= 1 and len(on) > 1 and
                                                   on[:1].lower() == nn[:1].lower())
                merged.append((of, og) if keep_old else (nf, ng))
            auth = merged
        new_field = fmt(auth)
        old_field = " ".join(cur.group(2).split())
        if " ".join(new_field.split()) == old_field:
            print(f"  ok  {key:24} {src}")
            continue
        changed += 1
        print(f"  ->  {key:24} {src}")
        print(f"        was: {old_field[:96]}")
        print(f"        now: {' '.join(new_field.split())[:96]}")
        if not DRY:
            new_body = body[:cur.start(2)] + new_field + body[cur.end(2):]
            raw = raw.replace(m.group(0), f"@{m.group(1)}{{{key},{new_body}\n}}")
    if not DRY and changed:
        open(BIB, "w", encoding="utf-8").write(raw)
    print(f"\n{changed} entr{'y' if changed == 1 else 'ies'} "
          f"{'would be' if DRY else ''} rewritten")


if __name__ == "__main__":
    main()
