#!/usr/bin/env python3
"""Static-site localization plumbing (config-driven).

Config: _i18n/config.json
  site      absolute origin, e.g. "https://risereps.app"
  pages     English core pages (root-relative file names) that get localized
  css       root-relative path of the switcher/RTL stylesheet
  locales   [{code, name, og, dir, live}]  -- first entry is the default (English, served at /)

Layout:
  English pages live at the site root (unchanged URLs).
  A translation of <page> for locale <code> lives at /<code>/<page>
  (index.html is served as /<code>/). Add a locale by adding it to config.json,
  creating /<code>/ with translated copies of the pages, then running this script.

Each page carries two managed blocks that this script rewrites (do not hand-edit):
  <!-- i18n:head -->...<!-- /i18n:head -->          hreflang alternates, og:locale, css
  <!-- i18n:switcher -->...<!-- /i18n:switcher -->  language switcher
For translated pages it also sets <html lang/dir>, canonical, og:url, JSON-LD url,
and rewrites relative links so assets resolve from the /<code>/ folder.
sitemap.xml gets a managed <!-- I18N:START -->...<!-- I18N:END --> block.

Translated pages record the hash of the English source they were translated from
(<!-- i18n:source=... -->). `--check` lists missing/stale translations.

Usage: python3 _i18n/i18n.py            apply plumbing to all pages + sitemap
       python3 _i18n/i18n.py --check    also exit 1 if a live locale is missing pages
       python3 _i18n/i18n.py --stamp L  record current English hashes in locale L's pages
Standard library only.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "_i18n" / "config.json").read_text(encoding="utf-8"))
SITE = CFG["site"].rstrip("/")
PAGES = CFG["pages"]
LOCALES = CFG["locales"]
DEFAULT = LOCALES[0]
CSS = "/" + CFG.get("css", "assets/i18n.css").lstrip("/")

BLOCK = lambda name: re.compile(r"<!-- i18n:%s -->.*?<!-- /i18n:%s -->" % (name, name), re.S)
SOURCE_RE = re.compile(r"<!-- i18n:source=([0-9a-f]+) -->\n?")


def page_path(code, page):
    return ROOT / page if code == DEFAULT["code"] else ROOT / code / page


def page_url(code, page, absolute=True):
    tail = "" if page == "index.html" else page
    path = "/" + tail if code == DEFAULT["code"] else f"/{code}/{tail}"
    return SITE + path if absolute else path


def available(page):
    """Live locales that have this page."""
    return [l for l in LOCALES if l.get("live") and page_path(l["code"], page).exists()]


def strip_managed(text):
    text = BLOCK("head").sub("<!-- i18n:head --><!-- /i18n:head -->", text)
    text = BLOCK("switcher").sub("<!-- i18n:switcher --><!-- /i18n:switcher -->", text)
    return SOURCE_RE.sub("", text)


def source_hash(page):
    return hashlib.sha1(strip_managed(page_path(DEFAULT["code"], page).read_text(encoding="utf-8"))
                        .encode()).hexdigest()[:12]


def head_block(loc, page):
    alts = available(page)
    out = ["<!-- i18n:head -->"]
    if len(alts) > 1:
        for a in alts:
            out.append(f'<link rel="alternate" hreflang="{a["code"]}" href="{page_url(a["code"], page)}" />')
        out.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(DEFAULT["code"], page)}" />')
        out.append(f'<meta property="og:locale" content="{loc["og"]}" />')
        for a in alts:
            if a is not loc:
                out.append(f'<meta property="og:locale:alternate" content="{a["og"]}" />')
        out.append(f'<link rel="stylesheet" href="{CSS}" />')
    if not loc.get("live"):
        out.append('<meta name="robots" content="noindex" />')
        out.append(f'<link rel="stylesheet" href="{CSS}" />')
    out.append("<!-- /i18n:head -->")
    return "\n".join(out)


def switcher_block(loc, page):
    alts = available(page)
    if len(alts) < 2:
        return "<!-- i18n:switcher --><!-- /i18n:switcher -->"
    items = []
    for a in alts:
        cur = ' aria-current="true"' if a is loc else ""
        items.append(f'<li><a href="{page_url(a["code"], page, absolute=False)}" hreflang="{a["code"]}" '
                     f'lang="{a["code"]}"{cur}>{html.escape(a["name"])}</a></li>')
    label = html.escape(loc.get("label", "Language"))
    return ("<!-- i18n:switcher -->"
            f'<details class="lang-switch"><summary aria-label="{label}">'
            '<svg viewBox="0 0 24 24" aria-hidden="true" width="16" height="16"><path fill="none" stroke="currentColor" '
            'stroke-width="1.8" d="M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9'
            'M12 3c-2.5 2.7-3.8 5.7-3.8 9s1.3 6.3 3.8 9"/></svg>'
            f'<span>{html.escape(loc["name"])}</span></summary><ul>{"".join(items)}</ul></details>'
            "<!-- /i18n:switcher -->")


SKIP = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|/|#|\.\./|\{)", re.I)


def rewrite_rel(code, text):
    """Make relative URLs in a /<code>/ page resolve: translated pages stay local, rest gets ../"""
    def fix(url):
        if not url or SKIP.match(url):
            return url
        base = url.split("#")[0].split("?")[0]
        if base in PAGES and page_path(code, base).exists():
            return url
        return "../" + url

    def attr(m):
        name, q, val = m.group(1), m.group(2), m.group(3)
        if name.lower() == "srcset":
            val = ", ".join(" ".join([fix(p.split()[0])] + p.split()[1:]) for p in val.split(",") if p.strip())
        else:
            val = fix(val)
        return f"{name}={q}{val}{q}"
    text = re.sub(r"\b(href|src|poster|srcset|action)=([\"'])(.*?)\2", attr, text)
    # url(...) in inline styles
    return re.sub(r"url\((['\"]?)(?!data:|https?:|/|#|\.\./)([^)'\"]+)\1\)", r"url(\1../\2\1)", text)


def set_attr(tag, name, value):
    if re.search(rf'\s{name}="[^"]*"', tag):
        return re.sub(rf'\s{name}="[^"]*"', f' {name}="{value}"', tag)
    return tag[:-1] + f' {name}="{value}">'


def ensure_markers(text, path):
    if "<!-- i18n:head -->" not in text:
        text = text.replace("</head>", "<!-- i18n:head --><!-- /i18n:head -->\n</head>", 1)
    if "<!-- i18n:switcher -->" not in text:
        print(f"WARN {path.relative_to(ROOT)}: no <!-- i18n:switcher --> marker; switcher not shown")
    return text


def process(loc, page):
    path = page_path(loc["code"], page)
    text = ensure_markers(path.read_text(encoding="utf-8"), path)
    text = BLOCK("head").sub(lambda m: head_block(loc, page), text)
    text = BLOCK("switcher").sub(lambda m: switcher_block(loc, page), text)
    if loc is not DEFAULT:
        text = re.sub(r"<html\b[^>]*>", lambda m: set_attr(set_attr(m.group(0), "lang", loc["code"]),
                                                             "dir", loc.get("dir", "ltr")), text, count=1)
        en, here = page_url(DEFAULT["code"], page), page_url(loc["code"], page)
        text = re.sub(r'(<link\s+rel="canonical"\s+href=")[^"]*(")', rf"\g<1>{here}\2", text)
        text = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")', rf"\g<1>{here}\2", text)
        text = re.sub(r'("url"\s*:\s*")' + re.escape(en) + '"', rf'\g<1>{here}"', text)
        text = rewrite_rel(loc["code"], text)
    path.write_text(text, encoding="utf-8")


def sitemap():
    sm = ROOT / "sitemap.xml"
    if not sm.exists():
        return
    rows = []
    for page in PAGES:
        for a in available(page):
            if a is not DEFAULT:
                rows.append(f"  <url><loc>{page_url(a['code'], page)}</loc></url>")
    block = "<!-- I18N:START (managed by _i18n/i18n.py) -->\n" + "\n".join(rows) + ("\n" if rows else "") + "  <!-- I18N:END -->"
    text = sm.read_text(encoding="utf-8")
    if "<!-- I18N:START" in text:
        text = re.sub(r"<!-- I18N:START.*?<!-- I18N:END -->", lambda m: block, text, flags=re.S)
    else:
        text = text.replace("</urlset>", "  " + block + "\n</urlset>")
    sm.write_text(text, encoding="utf-8")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--stamp"]:
        code = args[1]
        for page in PAGES:
            p = page_path(code, page)
            if p.exists():
                t = SOURCE_RE.sub("", p.read_text(encoding="utf-8"))
                t = re.sub(r"(<!DOCTYPE[^>]*>\n?)", rf"\1<!-- i18n:source={source_hash(page)} -->\n", t, count=1, flags=re.I)
                p.write_text(t, encoding="utf-8")
        print(f"stamped {code}")
    problems = []
    for loc in LOCALES:
        for page in PAGES:
            p = page_path(loc["code"], page)
            if not p.exists():
                if loc.get("live"):
                    problems.append(f"missing {loc['code']}/{page}")
                continue
            if loc is not DEFAULT:
                m = SOURCE_RE.search(p.read_text(encoding="utf-8"))
                if not m or m.group(1) != source_hash(page):
                    print(f"STALE {loc['code']}/{page}: English source changed since translation")
            process(loc, page)
    sitemap()
    for pr in problems:
        print("WARN", pr)
    print("i18n: " + ", ".join(f"{l['code']}{'' if l.get('live') else '(off)'}" for l in LOCALES))
    if "--check" in args and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
