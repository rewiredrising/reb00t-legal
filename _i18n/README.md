# Localization (_i18n)

Core pages are translated; the blog stays English-only.

- `config.json` — locales (first entry = English default at `/`), the core pages, and `live` flags.
  Set `"live": false` to hide a locale from the switcher/hreflang/sitemap (its pages get `noindex`).
- Translations live at `/<code>/<page>` (e.g. `/de/index.html` → `https://<site>/de/`).
- `python3 _i18n/i18n.py` re-applies the plumbing after any change: `<html lang/dir>`, canonical,
  og:url/og:locale, hreflang alternates (+ `x-default` = English), the language switcher
  (`<!-- i18n:switcher -->` marker), relative-link fixes for subfolders, and the `I18N` block in `sitemap.xml`.
  It also prints `STALE` for translations whose English source changed since they were stamped.
- Add a locale: add it to `config.json`, copy each core page into `/<code>/`, translate the copy
  (text, title, meta/og/twitter, alt, JSON-LD text; leave markup/URLs alone), then
  `python3 _i18n/i18n.py --stamp <code>` and commit.
- After editing an English core page, update the translations (or accept STALE) and re-run the script.
- Do not hand-edit content between `<!-- i18n:... -->` markers or inside `<!-- I18N:START/END -->` in sitemap.xml.
