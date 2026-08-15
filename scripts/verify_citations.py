#!/usr/bin/env python3
"""
Check every bibliography entry against an authoritative source.

A wrong citation is worse than a missing one: it sends a reader to the wrong paper and
it is the first thing a referee spot-checks. This resolves each entry independently --
CrossRef for DOIs, the arXiv API for preprints -- and compares the year, the first
author's family name, the title, and (for journal articles) volume and pages against
what references.bib claims.

  python scripts/verify_citations.py           # report
  python scripts/verify_citations.py --strict  # exit non-zero on any disagreement

Network access required. Entries with neither a DOI nor an arXiv id (databases, web
resources, a company white paper) are listed as unverifiable rather than silently passed.
"""
import json, re, subprocess, sys, time, urllib.parse

BIB = "docs/references.bib"
STRICT = "--strict" in sys.argv


def get(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sL", "--max-time", "40", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        time.sleep(2 * (i + 1))
    return ""


def entries():
    raw = open(BIB, encoding="utf-8").read()
    for m in re.finditer(r'@(\w+)\{([^,]+),(.*?)\n\}', raw, re.S):
        body = m.group(3)
        f = lambda k: (re.search(rf'{k}\s*=\s*\{{(.*?)\}},?\s*\n', body, re.S) or
                       re.search(rf'{k}\s*=\s*\{{(.*?)\}}\s*$', body, re.S))
        get_f = lambda k: " ".join(f(k).group(1).split()) if f(k) else None
        yield {"key": m.group(2).strip(), "type": m.group(1),
               "title": get_f("title"), "author": get_f("author"),
               "year": get_f("year"), "doi": get_f("doi"),
               "journal": get_f("journal"), "volume": get_f("volume"),
               "pages": get_f("pages"), "eprint": get_f("eprint")}


import unicodedata


def norm(s):
    """Lower-case, strip LaTeX accent commands and fold Unicode accents.

    Without the fold, a bibliography spelling H{\\"a}se and CrossRef's "Häse" compare
    unequal and every accented name reports as a mismatch, burying the real ones.
    """
    s = (s or "")
    s = re.sub(r'\\[\'`"^~=.]\{?([a-zA-Z])\}?', r'\1', s)   # \"a -> a
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r'[{}$^_]', '', s)       # math/markup vanish; replacing them with a
    s = re.sub(r'\\[a-z]+', ' ', s)      # space would split Schl{\\"o}rer, and would turn
                                        # {$^{13}$}C into "13 c" against CrossRef's "13c"
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return " ".join(s.split())


def first_family(author):
    """BibTeX 'Family, Given and Family2, Given2' -> family of the first author."""
    if not author:
        return ""
    a = author.split(" and ")[0]
    fam = a.split(",")[0] if "," in a else a.split()[-1]
    return norm(fam)



def _split(a):
    """BibTeX 'Family, Given' or 'Given Family' -> (family, given)."""
    if "," in a:
        fam, giv = a.split(",", 1)
    else:
        parts = a.split()
        fam, giv = (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else (a, "")
    return norm(fam), norm(giv)


def compare_authors(bib_author, source_names, src):
    """Compare the full author list: family names AND given names.

    Family names alone are not enough. references.bib carried "Chacko, Elizabeth" and
    "Praveen, Aravind" for a paper actually written by Edwin Chacko and Arnav Praveen;
    every family name matched, and because RSC style prints initials only, even the
    rendered citation looked right. The wrong names sat in the deposited BibTeX, where
    anyone re-using it would inherit them.
    """
    if "others" in (bib_author or "").lower():
        return []
    bib = [_split(a) for a in bib_author.split(" and ")]
    got = [_split(n) for n in source_names if n.strip()]
    if not bib or not got:
        return []
    if len(bib) != len(got):
        return [f"author count: bib {len(bib)} vs {src} {len(got)}"]
    bad = []
    for i, ((bf, bg), (gf, gg)) in enumerate(zip(bib, got), 1):
        # compound surnames tokenize differently across registries (CrossRef stores
        # "Vargas Hernandez" for Vargas-Hernandez); accept either containing the other
        if bf != gf and bf not in gf and gf not in bf:
            bad.append(f"#{i} family: bib '{bf}' vs {src} '{gf}'")
            continue
        if bg and gg:
            b1 = [w for w in bg.split() if w]
            g1 = [w for w in gg.split() if w]
            if b1 and g1:
                # a full given name that differs beyond the initial is a real error
                if b1[0] != g1[0] and not (len(b1[0]) == 1 or len(g1[0]) == 1):
                    bad.append(f"#{i} given: bib '{bg}' vs {src} '{gg}' (family {gf})")
    if bad:
        return [f"author list differs: " + "; ".join(bad[:5])]
    return []


def check_crossref(e):
    data = get(f"https://api.crossref.org/works/{urllib.parse.quote(e['doi'])}")
    try:
        m = json.loads(data)["message"]
    except Exception:
        # NIST (10.18434) and RADAR4Chem (10.22000) register with DataCite, not
        # CrossRef. Absence there is not evidence the DOI is wrong; resolve it instead.
        code = subprocess.run(
            ["curl", "-sIL", "--max-time", "40", "-o", "/dev/null",
             "-w", "%{http_code}", f"https://doi.org/{e['doi']}"],
            capture_output=True, text=True).stdout.strip()
        if code.endswith(("200", "302", "303")):
            return []
        return [f"DOI not in CrossRef and does not resolve (HTTP {code or 'no reply'})"]
    bad = []
    ttl = norm((m.get("title") or [""])[0])
    if ttl and norm(e["title"]) and ttl[:45] != norm(e["title"])[:45]:
        bad.append(f"title\n        bib:      {norm(e['title'])[:88]}\n        crossref: {ttl[:88]}")
    yr = None
    for k in ("published-print", "published-online", "issued", "created"):
        if m.get(k, {}).get("date-parts", [[None]])[0][0]:
            yr = m[k]["date-parts"][0][0]; break
    if yr and e["year"] and str(yr) != e["year"]:
        bad.append(f"year: bib {e['year']} vs crossref {yr}")
    auths = m.get("author") or []
    if auths and e["author"]:
        bad += compare_authors(e["author"],
                               [f"{a.get('given','')} {a.get('family','')}" for a in auths],
                               "crossref")
    if e["volume"] and m.get("volume") and str(m["volume"]) != e["volume"]:
        bad.append(f"volume: bib {e['volume']} vs crossref {m['volume']}")
    if e["pages"] and m.get("page"):
        if norm(m["page"]).replace(" ", "") not in norm(e["pages"]).replace(" ", "").replace("--", "-"):
            bad.append(f"pages: bib {e['pages']} vs crossref {m['page']}")
    return bad


def check_arxiv(e):
    aid = e["eprint"] or (e["doi"] or "").split("arXiv.")[-1]
    xml = get(f"http://export.arxiv.org/api/query?id_list={aid}&max_results=1")
    t = re.search(r'<entry>.*?<title>(.*?)</title>', xml, re.S)
    if not t:
        return [f"arXiv id {aid} returned no record"]
    bad = []
    got = norm(t.group(1))
    if norm(e["title"])[:45] != got[:45]:
        bad.append(f"title\n        bib:   {norm(e['title'])[:88]}\n        arXiv: {got[:88]}")
    names = re.findall(r'<author>\s*<name>(.*?)</name>', xml, re.S)
    if names and e["author"]:
        bad += compare_authors(e["author"], names, "arXiv")
    pub = re.search(r'<published>(\d{4})', xml)
    if pub and e["year"] and pub.group(1) != e["year"]:
        bad.append(f"year: bib {e['year']} vs arXiv v1 {pub.group(1)}")
    return bad


def main():
    ok = unver = 0
    problems = []
    for e in entries():
        doi = e["doi"] or ""
        if "arxiv" in doi.lower() or e["eprint"]:
            bad = check_arxiv(e); src = "arXiv"
        elif doi:
            bad = check_crossref(e); src = "CrossRef"
        else:
            print(f"  ??  {e['key']:24} no DOI/eprint — verify by hand ({e['type']})")
            unver += 1
            continue
        if bad:
            problems.append((e["key"], src, bad))
            print(f"  !!  {e['key']:24} {src}")
            for b in bad:
                print(f"        {b}")
        else:
            ok += 1
            print(f"  ok  {e['key']:24} {src}")
    print(f"\nverified {ok}, disagreements {len(problems)}, unverifiable {unver}")
    if problems and STRICT:
        sys.exit(1)


if __name__ == "__main__":
    main()
