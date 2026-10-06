#!/usr/bin/env python3
"""Build the reb00t.app blog.

Sources live in _blog/posts/<slug>.html (Jekyll skips underscore folders, so
they are never published). Each source starts with a JSON meta block:

    <!--meta
    { "title": "...", "seo_title": "...", "description": "...", "date": "2026-10-06", ... }
    -->
    <p>Body HTML…</p>

Body placeholders:
    <!--cta-->                      inline App Store call-to-action box
    <!--cta:Heading|Body text-->    same, with custom copy
    <!--screen:N|Caption-->         app screenshot blog/img/app-screen-N.jpg

Outputs: blog/<slug>/index.html, blog/<slug>/og.jpg, blog/index.html,
blog/feed.xml, sitemap.xml, robots.txt. Standard library + Pillow only.

Usage: python3 _blog/build.py            build everything
       python3 _blog/build.py --check    build + exit 1 if any post fails SEO checks
"""

import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_blog" / "posts"
BLOG_DIR = ROOT / "blog"
SITE = "https://reb00t.app"
APP_NAME = "Quit & REBOOT"
APP_ID = "6761043425"
APP_STORE_URL = "https://apps.apple.com/us/app/quit-reboot-lust-blocker/id6761043425"
BRAND = "REB00T"
ORG = "Rewired & Rising"
AUTHOR = "The REB00T Team"

SCREEN_ALTS = {
    1: "Quit & REBOOT app counting jumping jack reps with on-device pose tracking during an urge",
    2: "Quit & REBOOT urge protocol screen: Lock In, Breathe, Move, Declare",
    3: "Quit & REBOOT streak dashboard showing a 50-day streak",
    4: "Quit & REBOOT protection screen blocking adult content across all browsers",
    5: "Quit & REBOOT anonymous community forum",
    6: "Quit & REBOOT pattern scan result showing an escape-driven loop",
    7: "Quit & REBOOT trigger map and risk-time patterns",
    8: "Quit & REBOOT 10-module recovery course",
}

warnings = []


def warn(slug, msg):
    warnings.append(f"[{slug}] {msg}")


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"[\s-]+", "-", s).strip("-")[:60]


def fmt_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d, %Y")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def json_ld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")


# ---------------------------------------------------------------- load posts

def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*(.*)", raw, re.S)
        if not m:
            sys.exit(f"{path.name}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        meta["slug"] = path.stem
        meta["body_src"] = m.group(2)
        meta.setdefault("status", "published")
        meta.setdefault("updated", meta["date"])
        meta.setdefault("category", "Recovery")
        meta.setdefault("faq", [])
        meta.setdefault("keywords", [])
        if meta["status"] != "published":
            continue
        if meta["date"] > date.today().isoformat():
            continue  # scheduled for the future
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


# ---------------------------------------------------------------- body render

def cta_box(heading=None, text=None):
    heading = heading or "Stop fighting urges with willpower alone"
    text = text or (
        f"{APP_NAME} blocks adult content across Safari, Chrome and Firefox, then walks you "
        "through a 5-minute urge protocol the moment a craving hits. Free to download on iPhone."
    )
    return f"""
<aside class="cta-inline">
  <img src="/blog/img/app-icon.png" alt="{esc(APP_NAME)} app icon" width="64" height="64" loading="lazy">
  <div>
    <p class="cta-inline-title">{esc(heading)}</p>
    <p>{esc(text)}</p>
    <a class="btn-store" href="{APP_STORE_URL}">Download {esc(APP_NAME)} on the App Store</a>
  </div>
</aside>"""


def screen_figure(n, caption):
    alt = SCREEN_ALTS.get(n, f"{APP_NAME} app screenshot")
    return f"""
<figure class="screen">
  <a href="{APP_STORE_URL}"><img src="/blog/img/app-screen-{n}.jpg" alt="{esc(alt)}" width="640" height="1387" loading="lazy"></a>
  <figcaption>{esc(caption)}</figcaption>
</figure>"""


def render_body(meta):
    body = meta["body_src"]
    body = re.sub(r"<!--cta-->", lambda m: cta_box(), body)
    body = re.sub(
        r"<!--cta:(.*?)\|(.*?)-->", lambda m: cta_box(m.group(1).strip(), m.group(2).strip()), body
    )
    body = re.sub(
        r"<!--screen:(\d+)\|(.*?)-->", lambda m: screen_figure(int(m.group(1)), m.group(2).strip()), body
    )

    toc = []

    def add_id(m):
        attrs, inner = m.group(1) or "", m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        if not idm:
            attrs = f' id="{hid}"' + attrs
        toc.append((hid, strip_tags(inner)))
        return f"<h2{attrs}>{inner}</h2>"

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", add_id, body, flags=re.S)
    return body, toc


# ---------------------------------------------------------------- page chrome

def head(title, description, canonical, og_image, og_type="website", extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="apple-itunes-app" content="app-id={APP_ID}">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="alternate" type="application/rss+xml" title="{BRAND} Blog" href="{SITE}/blog/feed.xml">
  <link rel="preload" href="/blog/fonts/BebasNeue-Regular.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="stylesheet" href="/blog/blog.css">
{extra}</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a class="logo" href="/blog/">REB<span>00</span>T <em>Blog</em></a>
      <a class="btn-top" href="{APP_STORE_URL}">Get the app</a>
    </div>
  </header>
"""


def footer():
    year = date.today().year
    return f"""
  <a class="sticky-cta" href="{APP_STORE_URL}">
    <img src="/blog/img/app-icon.png" alt="" width="36" height="36">
    <span><strong>{esc(APP_NAME)}</strong> Free on the App Store</span>
    <span class="sticky-get">GET</span>
  </a>
  <footer class="site-footer">
    <p><a href="/blog/">Blog</a> · <a href="/support.html">Support</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="{APP_STORE_URL}">App Store</a></p>
    <p>© {year} {esc(ORG)}. Articles are educational and are not medical advice.</p>
  </footer>
</body>
</html>
"""


# ---------------------------------------------------------------- pages

def render_post(meta, posts):
    slug = meta["slug"]
    url = f"{SITE}/blog/{slug}/"
    og = f"{SITE}/blog/{slug}/og.jpg"
    body, toc = render_body(meta)
    words = len(strip_tags(body).split())
    minutes = max(1, round(words / 230))
    meta["minutes"] = minutes
    seo_title = meta.get("seo_title") or meta["title"]

    graph = [
        {
            "@type": "BlogPosting",
            "@id": url + "#article",
            "headline": meta["title"][:110],
            "description": meta["description"],
            "image": og,
            "datePublished": meta["date"],
            "dateModified": meta["updated"],
            "author": {"@type": "Organization", "name": AUTHOR, "url": SITE + "/blog/"},
            "publisher": {
                "@type": "Organization",
                "name": ORG,
                "logo": {"@type": "ImageObject", "url": SITE + "/apple-touch-icon.png"},
            },
            "mainEntityOfPage": url,
            "keywords": ", ".join(meta["keywords"]),
            "wordCount": words,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": meta["title"], "item": url},
            ],
        },
    ]
    if meta["faq"]:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": strip_tags(f["a"])}}
                for f in meta["faq"]
            ],
        })
    ld = f'  <meta property="article:published_time" content="{meta["date"]}">\n' \
         f'  <meta property="article:modified_time" content="{meta["updated"]}">\n' \
         f'  <script type="application/ld+json">{json_ld({"@context": "https://schema.org", "@graph": graph})}</script>\n'

    toc_html = ""
    if len(toc) >= 3:
        items = "\n".join(f'      <li><a href="#{hid}">{esc(t)}</a></li>' for hid, t in toc)
        toc_html = f"""
    <nav class="toc" aria-label="Table of contents">
      <p class="toc-title">In this guide</p>
      <ol>
{items}
      </ol>
    </nav>"""

    faq_html = ""
    if meta["faq"]:
        qa = "\n".join(
            f'      <div class="faq-item">\n        <h3>{esc(f["q"])}</h3>\n        <p>{f["a"]}</p>\n      </div>'
            for f in meta["faq"]
        )
        faq_html = f"""
    <section class="faq" id="faq">
      <h2>Frequently asked questions</h2>
{qa}
    </section>"""

    related = [p for p in posts if p["slug"] != slug][:3]
    related_html = ""
    if related:
        cards = "\n".join(
            f'      <a class="related-card" href="/blog/{p["slug"]}/"><span>{esc(p["category"])}</span><strong>{esc(p["title"])}</strong></a>'
            for p in related
        )
        related_html = f"""
  <section class="related">
    <h2>Keep reading</h2>
    <div class="related-grid">
{cards}
    </div>
  </section>"""

    updated = ""
    if meta["updated"] != meta["date"]:
        updated = f' · Updated <time datetime="{meta["updated"]}">{fmt_date(meta["updated"])}</time>'

    page = head(seo_title, meta["description"], url, og, "article", ld)
    page += f"""
  <main class="article-shell">
    <article>
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / <span>{esc(meta["category"])}</span></nav>
      <header class="article-header">
        <p class="eyebrow">{esc(meta["category"])}</p>
        <h1>{esc(meta["title"])}</h1>
        <p class="dek">{esc(meta.get("dek", meta["description"]))}</p>
        <p class="byline">By {esc(AUTHOR)} · <time datetime="{meta["date"]}">{fmt_date(meta["date"])}</time>{updated} · {minutes} min read</p>
      </header>
{toc_html}
      <div class="prose">
{body}
      </div>
{faq_html}
{cta_box("Ready to make this the time it sticks?", f"Download {APP_NAME} free on iPhone. Block adult sites on every browser, beat urges in 5 minutes with the guided protocol, and track your streak privately on your device.")}
      <p class="disclaimer">This article is for education and general support. It is not medical or psychological advice. If compulsive sexual behavior is affecting your health, relationships or work, consider talking to a licensed therapist, ideally one experienced with compulsive sexual behavior.</p>
    </article>
  </main>
{related_html}
"""
    page += footer()
    out = BLOG_DIR / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    make_og(meta, BLOG_DIR / slug / "og.jpg")
    check_post(meta, body, words)


def render_index(posts):
    url = f"{SITE}/blog/"
    title = "REB00T Blog: Quit Porn, Beat Urges & Rewire Your Brain"
    desc = ("Practical, shame-free guides for men who want to quit porn: urge control, "
            "blocking adult content on iPhone, NNN, streaks and relapse prevention.")
    cards = []
    for p in posts:
        cards.append(f"""
      <a class="post-card" href="/blog/{p["slug"]}/">
        <img src="/blog/{p["slug"]}/og.jpg" alt="" width="1200" height="630" loading="lazy">
        <div class="post-card-body">
          <span class="post-card-cat">{esc(p["category"])} · {fmt_date(p["date"])}</span>
          <h2>{esc(p["title"])}</h2>
          <p>{esc(p["description"])}</p>
        </div>
      </a>""")
    graph = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": f"{BRAND} Blog",
        "url": url,
        "publisher": {"@type": "Organization", "name": ORG},
        "blogPost": [
            {"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/",
             "datePublished": p["date"]} for p in posts
        ],
    }
    page = head(title, desc, url, f"{SITE}/blog/img/og-blog.jpg", "website",
                f'  <script type="application/ld+json">{json_ld(graph)}</script>\n')
    page += f"""
  <main class="index-shell">
    <header class="index-hero">
      <p class="eyebrow">The {BRAND} Blog</p>
      <h1>Quit porn. Keep your streak. Rewire your brain.</h1>
      <p class="dek">No shame, no fluff. Practical guides on beating urges, blocking adult content on iPhone and building a streak that holds, from the team behind {esc(APP_NAME)}.</p>
      <a class="btn-store" href="{APP_STORE_URL}">Download {esc(APP_NAME)} on the App Store</a>
    </header>
    <section class="post-grid">{"".join(cards)}
    </section>
  </main>
"""
    page += footer()
    (BLOG_DIR / "index.html").write_text(page, encoding="utf-8")
    make_og({"title": "Quit porn. Keep your streak. Rewire your brain.", "slug": "_index"},
            BLOG_DIR / "img" / "og-blog.jpg")


def render_feed(posts):
    items = []
    for p in posts[:30]:
        pub = datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 08:00:00 +0000")
        link = f"{SITE}/blog/{p['slug']}/"
        items.append(f"""  <item>
    <title>{esc(p["title"])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{pub}</pubDate>
    <description>{esc(p["description"])}</description>
  </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{BRAND} Blog</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Guides for men quitting porn: urges, blockers, streaks and relapse prevention.</description>
  <language>en-us</language>
{chr(10).join(items)}
</channel>
</rss>
"""
    (BLOG_DIR / "feed.xml").write_text(feed, encoding="utf-8")


def render_sitemap(posts):
    newest = posts[0]["updated"] if posts else date.today().isoformat()
    urls = [(f"{SITE}/", None), (f"{SITE}/blog/", newest)]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["updated"]) for p in posts]
    urls += [(f"{SITE}/{page}", None) for page in ("support.html", "privacy.html", "terms.html")]
    rows = []
    for loc, lastmod in urls:
        lm = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        rows.append(f"  <url><loc>{loc}</loc>{lm}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
                                     encoding="utf-8")


# ---------------------------------------------------------------- OG images

def _font(names, size):
    from PIL import ImageFont
    dirs = [Path.home() / "Library/Fonts", Path("/Library/Fonts"),
            Path("/System/Library/Fonts/Supplemental"), Path("/System/Library/Fonts")]
    for n in names:
        for d in dirs:
            for candidate in [d / n, *d.glob(f"*/{n}")]:
                if candidate.exists():
                    return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def make_og(meta, out):
    """1200x630 share card: brand eyebrow, title, app screenshot on the right."""
    if out.exists() and not meta.get("regen_og"):
        return
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError:
        warn(meta["slug"], "Pillow missing; og.jpg not generated")
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (6, 8, 11))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-250, -300, 450, 350), fill=(16, 70, 70))
    gd.ellipse((700, 300, 1400, 900), fill=(70, 50, 12))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(140)), 0.9)
    d = ImageDraw.Draw(img)

    shot_n = meta.get("og_screen", 2)
    shot_path = BLOG_DIR / "img" / f"app-screen-{shot_n}.jpg"
    text_w = 700
    if shot_path.exists():
        shot = Image.open(shot_path).convert("RGB")
        # crop the phone area (skip the marketing headline at the top)
        sw, sh = shot.size
        shot = shot.crop((0, int(sh * 0.27), sw, sh))
        scale = 600 / shot.size[1]
        shot = shot.resize((int(shot.size[0] * scale), 600))
        mask = Image.new("L", shot.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *shot.size), 28, fill=255)
        img.paste(shot, (W - shot.size[0] - 40, 30), mask)
        text_w = W - shot.size[0] - 140

    gold, white, muted = (240, 180, 60), (245, 245, 245), (170, 176, 184)
    d.text((64, 58), "REB00T  ·  BLOG", font=_font(["BarlowCondensed-Bold.ttf", "DIN Condensed Bold.ttf"], 34), fill=gold)

    title = (meta.get("og_title") or meta["title"]).upper()
    size = 132
    while size > 44:
        f = _font(["BebasNeue-Regular.ttf", "Impact.ttf"], size)
        lines, line = [], ""
        for word in title.split():
            trial = f"{line} {word}".strip()
            if d.textlength(trial, font=f) <= text_w:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
        if len(lines) * size <= 380:
            break
        size -= 4
    y = 120 + (380 - len(lines) * size) // 2
    for i, ln in enumerate(lines):
        d.text((64, y), ln, font=f, fill=white if i < len(lines) - 1 or len(lines) == 1 else gold)
        y += int(size * 1.0)
    d.text((64, H - 84), "reb00t.app  ·  Quit & REBOOT on the App Store",
           font=_font(["BarlowCondensed-SemiBold.ttf", "Avenir Next Condensed.ttc"], 30), fill=muted)
    img.save(out, "JPEG", quality=86, optimize=True)


# ---------------------------------------------------------------- SEO checks

def check_post(meta, body, words):
    slug = meta["slug"]
    seo_title = meta.get("seo_title") or meta["title"]
    kw = meta.get("primary_keyword", "").lower()
    if not kw:
        warn(slug, "no primary_keyword")
    if len(seo_title) > 62:
        warn(slug, f"seo_title is {len(seo_title)} chars (aim ≤ 60)")
    if not 120 <= len(meta["description"]) <= 160:
        warn(slug, f"description is {len(meta['description'])} chars (aim 120–160)")
    if words < 1200:
        warn(slug, f"only {words} words (aim 1,500+)")
    if kw:
        first = " ".join(strip_tags(body).lower().split()[:120])
        for where, text in [("seo_title", seo_title), ("description", meta["description"]),
                            ("first 120 words", first)]:
            if kw not in text.lower():
                warn(slug, f"primary keyword '{kw}' missing from {where}")
        if not set(kw.split()) & set(slug.split("-")):
            warn(slug, "slug shares no words with primary keyword")
    if body.count("<h2") < 4:
        warn(slug, "fewer than 4 H2 sections")
    if APP_STORE_URL not in body:
        warn(slug, "no inline App Store CTA in body (add <!--cta-->)")
    if "/blog/" not in meta["body_src"] and len(load_posts()) > 1:
        warn(slug, "no internal links to other blog posts")
    for img in re.findall(r"<img[^>]*>", body):
        if 'alt="' not in img:
            warn(slug, f"image missing alt: {img[:80]}")


# ---------------------------------------------------------------- main

def main():
    posts = load_posts()
    BLOG_DIR.mkdir(exist_ok=True)
    for p in posts:
        render_post(p, posts)
    render_index(posts)
    render_feed(posts)
    render_sitemap(posts)
    print(f"Built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))
    for w in warnings:
        print("WARN", w)
    if "--check" in sys.argv and warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
