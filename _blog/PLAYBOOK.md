# REB00T blog: publishing playbook

This is the runbook for the scheduled "REB00T blog post" task (Mon/Wed/Fri). One run publishes one
SEO post on https://reb00t.app/blog/ that funnels readers to the App Store listing:
**https://apps.apple.com/us/app/quit-reboot-lust-blocker/id6761043425**

The repo is `rewiredrising/reb00t-legal`, checked out at
`/Users/ascend/Documents/Projects/Rewire & Rise/Products/REB00T App/reb00t-website`.
GitHub Pages deploys `main` to reb00t.app automatically. Jekyll skips `_blog/`, so nothing in this
folder is public.

## Files
- `_blog/posts/<slug>.html`: post sources (a JSON meta header plus body HTML). See the docstring in `build.py`.
- `_blog/build.py`: renders the posts, blog index, RSS feed, sitemap, robots.txt and OG images. `--check` fails on SEO warnings.
- `_blog/publish.sh "msg" <slug>`: build --check, commit, push, wait until live, ping IndexNow.
- `_blog/content-calendar.md`: the topic queue. `_blog/keyword-research.md`: data plus fact-check rules.
- `_blog/posts/how-to-survive-no-nut-november.html`: the reference post. Match its quality, voice and structure.

## Steps for each run

1. **Sync:** `git pull -q origin main` in the repo. Read `content-calendar.md`,
   `keyword-research.md` (especially the fact-check rules) and the reference post.
2. **Validate the keyword.** Take the first `queued` row, then gather fresh evidence that people
   search for it:
   - Bing + DuckDuckGo autocomplete for the primary keyword with a–z suffixes (see keyword-research.md).
   - Google Trends for the term and 2–3 variants (12-month, US), plus its Related queries
     (rising/top). Use the built-in browser, where the user is logged in to Google.
   - Applyra, if the term isn't a suppressed porn term: traffic/difficulty via the fetch recipe.
   - One WebSearch SERP check: who ranks in the top 8? Small sites or forums = winnable.

   Pick the exact primary keyword (the phrasing with the most evidence) and 5–10 secondary
   phrasings taken verbatim from autocomplete or related queries. If the data says the queued topic
   is weak and another unpublished calendar topic is stronger or more timely, swap them and note why.
3. **Write the post** to `_blog/posts/<slug>.html`:
   - 1,800–2,800 words. A helpful, specific, shame-free voice, like a friend who's been there.
     Short paragraphs. Do not pad.
   - Meta: `title` (the H1; includes the primary keyword), `seo_title` (≤ 60 chars, keyword near
     the front), `description` (120–160 chars, includes the keyword), `dek`, `date` (today,
     YYYY-MM-DD), `category`, `primary_keyword`, `keywords`, `og_title` (short), `og_screen`
     (1–8), and `faq` (5–8 real questions taken from autocomplete or People Also Ask).
   - The primary keyword appears in the first 100 words, in at least one H2, and naturally 3–6
     times overall. Use secondary phrasings as H2/H3 headings where they read naturally.
   - At least 5 `<h2>` sections. Use `<table>`, numbered steps and `<div class="callout">` where they help.
   - **Conversion:** one `<!--cta:Heading|Text-->` mid-article where the app solves the problem
     being discussed, plus one natural in-text link to the App Store URL. The template adds the
     end CTA, sticky mobile bar and Smart App Banner. Add 1–3 `<!--screen:N|caption-->` images
     (1 reps/camera, 2 urge protocol, 3 streak, 4 blocker, 5 community, 6 pattern scan,
     7 trigger map, 8 course). Use plain `&` in placeholders, not `&amp;`.
   - **Internal links:** link to 2–4 existing posts (`/blog/<slug>/`). Then edit 1–3 older
     related posts to add a contextual link to the new post. That counts as an update: set
     their `"updated"` to today.
   - **Sources:** end the body with `<h2 data-toc="no">Sources</h2>` and an `<ol class="sources">` of
     every study or official page cited (links get `rel="nofollow"`). See the reference post.
   - **Accuracy:** follow every fact-check rule. Cite studies by author, journal and year in the
     text. Never invent statistics, quotes, testimonials, user counts or ratings. Describe app
     features only as they actually work: blocker across Safari/Chrome/Firefox plus app shielding;
     5-step urge protocol (Lock In, Breathe, Move with camera-verified reps, Declare, Status Check);
     16-question pattern scan (Escape / Numb / Stimulate); trigger map and risk windows;
     10-module course; streaks; anonymous moderated community. Say "free to download", never "free trial".
   - **Brand safety:** educational, never graphic. No site names of adult platforms. No slurs or
     meme crudeness beyond the term "No Nut November" itself. Don't use "NoFap" as a brand name
     (lowercase "nofap" as a search phrase is fine in meta keywords and an occasional heading).
   - Avoid AI tells: no "delve", "in today's fast-paced world", "it's important to note",
     "game-changer", "unlock", "navigate the journey", rule-of-three padding, or em-dash
     chains. Read it back once as a skeptical 24-year-old and cut anything preachy or generic.
4. **Build and check:** `python3 _blog/build.py --check`. Fix every warning. Then render and look at
   it: run `python3 -m http.server 8765` in the repo (in the background), and screenshot with headless
   Chrome at desktop (1280 wide) and in a 390px iframe for mobile. Look at the OG image
   `blog/<slug>/og.jpg`.
5. **Publish:** `_blog/publish.sh "Blog: <title>" <slug> [<updated-slug> ...]`. It fails unless every
   page returns 200.
6. **Record it:** mark the calendar row `published YYYY-MM-DD` (and add rows if fewer than 9 are
   queued). Add a dated line to the Run log in `keyword-research.md` with the evidence that picked
   the keyword. Commit and push those notes: `git add -A && git commit -m "Blog notes" && git push`.
7. **Report** in 3–6 lines: live URL, primary keyword plus the evidence, word count, internal links
   added, anything that needs the user.

## Guardrails
- **Never link to the blog from `index.html`, `privacy.html`, `terms.html` or `support.html`** unless
  the user says so. App Review reaches those pages from the App Store listing, and the site was
  rejected under Guideline 1.1 for content wording on them (2026-07-27).
- Never edit those four pages, `CNAME`, or the IndexNow key file.
- Blog wording stays on the blog. Never copy blog text into App Store Connect metadata: that copy has
  to avoid naming the content category, which the blog doesn't.
- If the build, push or live check fails, stop, report the error and leave the post source in place.
  Never force-push.
- One post per run. Don't publish a post dated in the future (build.py skips those anyway).
