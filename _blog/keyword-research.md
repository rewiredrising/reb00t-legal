# REB00T blog: keyword research

First pass 2026-10-06. Scheduled runs append new findings to the **Run log** at the bottom.
Audience: men 18–35 trying to quit porn or compulsive sexual habits. Every post funnels to
the App Store listing: https://apps.apple.com/us/app/quit-reboot-lust-blocker/id6761043425

## Sources and how to re-pull them

| Source | What it proves | How |
| --- | --- | --- |
| **Google Trends** (built-in browser, logged in as the user) | Relative US demand, seasonality, and "rising/breakout" related queries (real Google searches) | `https://trends.google.com/trends/explore?date=today%2012-m&geo=US&q=term1,term2` then scroll to the bottom so the Related queries widget loads, and read `.fe-related-queries .item`. Trends returns 429 if hit right after heavy autocomplete scraping, so wait a minute. |
| **Bing + DuckDuckGo autocomplete** | Verbatim queries people type (Google's own autocomplete filters out almost every adult term) | `https://api.bing.com/osjson.aspx?query=…` and `https://duckduckgo.com/ac/?type=list&q=…` with a–z suffixes |
| **Applyra** (applyra.io, built-in browser, Google login) | App Store search demand. Traffic (T) and difficulty (D) 0–100 for the same audience | From an applyra.io tab: `fetch('/dashboard/keywords-inspector?keyword=X&store=ITUNES&country=US&lang=en-US')`, regex `trafficScore":N` / `difficultyScore":N`. Run fetches in parallel with `Promise.all` (sequential calls time out). **T8 D18 = no data** (Apple suppresses porn terms). App id 482208. |
| **WebSearch SERP checks** | Whether small sites, forums or spam rank (a low-difficulty signal) | Search the exact phrase and note who's in the top 8 |

Ahrefs and Similarweb connectors exist but need OAuth. If the user connects Ahrefs, replace the
"no public data" volume cells with real numbers.

## Google Trends: US, past 12 months (to 2026-10-04)

Average interest, all five compared in one query:

| Term | Avg |
| --- | --- |
| porn addiction | **74** |
| semen retention | 27 |
| quit porn | 12 |
| porn blocker | 8 |
| stop watching porn | 5 |

Five-year view: **no nut november** spikes every year in the first week of November (100 in 2021,
31 in Nov 2025) and is near zero the rest of the year. Searches start building in late October.
Semen retention now runs higher than nofap year-round.

**Rising related queries (real Google searches):**
- porn addiction → *compulsive sexual behavior disorder* (+550%), *is porn addiction a real thing* (+350%), *porn addiction recovery timeline* (+300%), *therapist near me* (+500%)
- quit porn → *the easy peasy way to quit porn pdf* (Breakout)
- porn blocker → *blockerx* (+130%), *blockp* (+80%), *adult content blocker* (+60%), *beta blocker* (noise)
- stop watching porn → top: *how to stop watching porn* (100), *how do i stop watching porn* (23), *cant stop watching porn* (17), *how can i stop watching porn* (15), *i cant stop watching porn* (10)
- semen retention → *brahmacharya* (+600%), *semen retention aura* (+600%), *semen retention studies* (+200%), *health benefits of semen retention* (+160%)
- no nut november → breakouts every year: *no nut november [year]*, *no nut november [year] rules*, *no nut november rules reddit*

## Applyra (App Store, US), 2026-10-06

| Keyword | T | D |  | Keyword | T | D |
| --- | --- | --- | --- | --- | --- | --- |
| nnn | 96 | 20 |  | urge | 96 | 58 |
| celibacy | 70 | 16 |  | abstinence | 70 | 47 |
| lust | 63 | 18 |  | nofap | 63 | 36 |
| adult content blocker | 63 | 41 |  | purity | 56 | 55 |
| dopamine | 55 | 49 |  | no nut | 54 | 36 |
| semen retention | 52 | 19 |  | dopamine detox | 52 | 58 |
| website blocker | 50 | 40 |  | retention | 48 | 26 |
| stop lust | 47 | 26 |  | monk mode | 44 | 30 |
| relapse | 41 | 46 |  | quit lust | 37 | 47 |

`porn blocker`, `quit porn`, `porn addiction` and `no nut november` return no data (T8 D18).

## Autocomplete (Bing/DDG): verbatim long tails

**No Nut November:** no nut november rules, no nut november tips, how to survive no nut november,
no nut november benefits, is no nut november bad for you, is no nut november healthy, is no nut
november worth it, does no nut november have benefit, no nut november side effects, what happens
when you fail no nut november, what if you fail no nut november, failing no nut november, no nut
november challenge, no nut november challenge day 1, no nut november free pass, no nut november
and december, no nut november before and after, when is no nut november, what is no nut november,
no nut november rules reddit, do wet dreams count for no nut november, does no nut november apply
to girls.

**Other:** block pornography on iphone, how to block websites on iphone, blocking pornography from
my computer, porn blocker dns, porn addiction recovery timeline, porn addiction signs, porn addiction
side effects, porn addiction and adhd, porn addiction and depression, porn addiction how to stop,
nofap one month benefits, nofap one week benefits, nofap testosterone results, nofap flatline (via
semen retention flatline), semen retention timeline, semen retention stages, semen retention 90 days,
semen retention relapse, what is dopamine detox, does a dopamine detox work.

## Opportunity map (from SERP checks, 2026-10-06)

Brand-new domain = only long tails are realistic for the first 3–6 months. Difficulty is directional.

| Keyword | Difficulty signal | Notes |
| --- | --- | --- |
| how to survive no nut november / nnn tips | **Low** (parasite spam, Substack) | Seasonal; peaks Nov 1–7 |
| no nut november rules / do wet dreams count | **Low** for "does X count" | KnowYourMeme ranks for "rules" |
| how to block porn on chrome iphone | Low–Med | one-sec.app, AirDroid, techlockdown |
| porn addiction recovery timeline | Low–Med | A Beehiiv newsletter ranks #1. Parent "porn addiction recovery" ≈ 14.8k/mo (Keyword Planner via Origins Recovery, Jul 2024) |
| nofap flatline | Low | unanswered.io, Reddit mirrors |
| porn relapse / what to do after relapse | Low–Med | Canopy, Beehiiv |
| how to stop porn urges | Low | spam plus one therapist blog |
| porn brain fog | Low–Med | techlockdown, Canopy |
| quittr alternative | Low | only AlternativeTo ranks |
| how to stop edging | Low | |
| nofap benefits timeline | Low–Med | |
| best porn blocker for iphone | Med | habitdoom.com (small app blog) is #1 |
| how to block porn on iphone | Med | techlockdown, Canopy, AirDroid |
| am I addicted to porn / porn addiction signs | Med (YMYL) | |
| is porn addiction real / CSBD | Med | rising +350% |
| how to stop watching porn / how to quit porn | **High** | Canopy, ChoosingTherapy, Talkspace. Pillar later, once supporting posts exist |
| semen retention benefits | High | Healthline, Ro. Use a debunk angle only |
| porn addiction (head) | High | ≈ 30.7k/mo help-seeking cluster |

Competitor blogs that rank: **canopy.us** (the main one), techlockdown.com, one-sec.app,
habitdoom.com, Begin Again Institute, Ever Accountable. QUITTR, Brainbuddy, Fortify, BlockerX and
Relay were not seen ranking for these terms.

## Fact-check rules (do not break these)

- "Porn addiction" is **not** a DSM-5-TR diagnosis. ICD-11 (WHO) lists **Compulsive Sexual
  Behaviour Disorder, 6C72**, as an impulse-control disorder. Say "compulsive/problematic porn use".
- The "testosterone peaks at day 7 / 145.7%" study (Jiang 2003, 28 men) was **retracted
  2021-12-10** (doi 10.1631/jzus.2003.r236). Never present it as evidence.
- Garas, Levang & Pukall 2025, *J Sex Med* 22(9):1649: NNN participants vs. non-participants
  showed no difference in sexual wellbeing (n=435 → 114).
- Rider et al. 2016, *European Urology*: 21+ ejaculations/month linked to 19–22% lower prostate
  cancer risk (31,925 men).
- Kühn & Gallinat 2014 ("porn shrinks the brain") is correlational. Don't claim causation.
- Flatline, brain fog and 90-day reboot timelines are **community self-reports**, not studied. Say so.
- Semen retention and dopamine detox benefits have no scientific support (Healthline, Ro, MNT).
- iOS Screen Time "Limit Adult Websites" filters Safari **and other supported browsers**
  (Chrome, Firefox). Apple support 105121. Menu paths change every iOS version (iOS 27 is current
  as of Oct 2026), so tell readers to search "adult websites" in Settings rather than giving a rigid path.
- The app's Safari content blocker alone covers only Safari. The cross-browser claim is true
  because the app also applies the Screen Time / ManagedSettings web filter
  (`ContentBlockerService.applyScreenTimeBlocking`).
- Don't claim a free trial (it depends on the RevenueCat offering). Say "free to download".
- NoFap is a registered trademark. Use "nofap" only as a descriptive search term and never imply
  affiliation.

## Run log

- 2026-10-06: initial research (Trends, Applyra, Bing/DDG autocomplete, SERP checks). Published
  `how-to-survive-no-nut-november`.
