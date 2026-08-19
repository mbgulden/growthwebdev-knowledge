---
type: Operations
title: ActiveOahuTours.com Gameplan — Consolidated Strategy
description: **Date:** 2026-07-08 **Owner:** Kai, Orchestrator of Tourism **Scope:** activeoahutours.com, Active Oahu Tours public site, private business OKF, SEO/GSC/Ubersuggest data, current operational reports. **Data snapshot:** 
resource: okf/hubs/active-oahu/business/reports/strategy/2026-07-08-active-oahu-tours-gameplan.md
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T15:05:43Z
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
status: current
---

# ActiveOahuTours.com Gameplan — Consolidated Strategy

**Date:** 2026-07-08  
**Owner:** Kai, Orchestrator of Tourism  
**Scope:** activeoahutours.com, Active Oahu Tours public site, private business OKF, SEO/GSC/Ubersuggest data, current operational reports.  
**Data snapshot:** `okf/reports/strategy/data/2026-07-08-aot-gameplan-data.json`

## Direct answer

We did not have one single, clean gameplan file. We had a lot of strong pieces scattered across repos: SEO reports, GSC pulls, KBA counter-content research, mobile CTA audits, FareHarbor friction audits, site inventory, media indexing, and deployment/governance notes.

This document is the consolidated gameplan.

## North star

Turn ActiveOahuTours.com into the most useful, most bookable, most locally credible Oahu adventure site for:

1. **Kailua / Lanikai / Mokulua kayak + beach-day intent**
2. **North Shore / Sharks Cove snorkel and beach gear intent**
3. **Chinaman’s Hat / Mokoliʻi + Kaneohe / Kahana adventure intent**
4. **Japanese visitor research and booking intent**

The site should not feel like an SEO farm. It should feel like an experienced local outfitter quietly handing a visitor the exact plan they need for a great day on Oʻahu.

## Current verified state

### Site / repo state

- Production apex responds with HTTP 200 through Cloudflare.
- `www.activeoahutours.com` redirects to apex and then returns 200.
- Cloudflare Pages mirror responds with HTTP 200.
- Public mirror currently has no open GitHub PRs.
- Private business repo has one open PR: KBA Kailua/Lanikai counter-content research.

### Search Console source-of-truth snapshot

GSC property: `sc-domain:activeoahutours.com`  
Window: **2026-04-06 → 2026-07-05**  
Rows pulled: **8,812**  
Total clicks: **1,576**  
Total impressions: **161,905**

Top high-impression queries show the core opportunity: AOT is visible, often on page 1 or page 2, but CTR is thin.

| Query | Clicks | Impr. | CTR | Avg pos | Strategic meaning |
|---|---:|---:|---:|---:|---|
| electric beach | 36 | 6,736 | 0.5% | 6.6 | High visibility, weak CTR; content/CRO gap. |
| sharks cove | 18 | 4,837 | 0.4% | 5.9 | Strong snorkel opportunity under-monetized. |
| sharks cove oahu | 54 | 4,618 | 1.2% | 4.5 | Already close; improve snippet + conversion path. |
| boogie board | 0 | 3,412 | 0.0% | 17.5 | Product/rental intent gap. |
| kayaking oahu | 24 | 3,134 | 0.8% | 7.6 | Broad commercial query; needs better hub + internal links. |
| electric beach oahu | 5 | 2,835 | 0.2% | 8.7 | Snorkel guide needs stronger booking bridge. |
| kailua beach park | 8 | 2,618 | 0.3% | 10.0 | Main KBA counter-content target. |
| active oahu | 165 | 2,578 | 6.4% | 2.4 | Brand is strong but not fully position 1. |
| kailua beach | 4 | 2,548 | 0.2% | 7.5 | Major informational opportunity. |
| active oahu tours | 176 | 2,465 | 7.1% | 2.1 | Brand SERP needs tightening. |
| chinamans hat | 7 | 2,404 | 0.3% | 5.8 | Strong adventure route; CTR/conversion weak. |
| kayak | 2 | 2,391 | 0.1% | 7.1 | Broad query visibility but intent mismatch likely. |
| lanikai beach | 2 | 1,855 | 0.1% | 5.2 | KBA is attacking; AOT can improve fast. |
| kayak oahu | 7 | 1,615 | 0.4% | 14.6 | Commercial page-2 opportunity. |
| oahu kayaking | 8 | 1,607 | 0.5% | 13.6 | Commercial page-2 opportunity. |
| kayak rental oahu | 12 | 1,392 | 0.9% | 18.6 | Commercial page-2 opportunity. |

### Ubersuggest competitor snapshot

Ubersuggest is not trusted for AOT traffic truth, but it is useful for competitor intel.

| Domain | Est. organic | DA | Backlinks | Ref domains | Readout |
|---|---:|---:|---:|---:|---|
| activeoahutours.com | 1,231 | 26 | 1,352 | 454 | Real local authority; needs internal architecture + CTR/CRO lift. |
| kailuabeachadventures.com | 2,130 | 32 | 2,242 | 693 | Main Kailua/Lanikai competitor; stronger link profile and destination guide pages. |
| hawaiibeachtime.com | 547 | 24 | 1,507 | 534 | Beach gear competitor; North Shore gear/snorkel overlap. |
| twogoodkayaks.com | 0 | 29 | 912 | 183 | Link authority exists, but low visible organic in this pull. |
| andyoucreations.com | 4,766 | 31 | 16,821 | 896 | Broader tourism/content player, useful for content patterns, not direct local outfitter match. |

KBA’s strongest pages:

| KBA page | Ubersuggest traffic | Backlinks | Ref domains | Strategic concern |
|---|---:|---:|---:|---|
| `/best-beach-lanikai-oahu` | 112,991 | 19 | 7 | They are winning huge destination-guide terms. |
| `/kailua-beach-park` | 28,707 | 100 | 72 | Their Kailua Beach Park guide is the clearest immediate threat. |
| `/` | 4,258 | 352 | 221 | Strong homepage/link profile. |
| `/surfboard-rentals` | 2,232 | 8 | 8 | Rental intent expansion. |
| `/waimanalo-oahu-beach-guide` | 2,051 | 0 | 0 | Guide pages can win without many links. |
| `/complete-guide-the-mokes-mokuluas` | 567 | 18 | 11 | Direct Mokulua/Mokes overlap. |

### Existing site audit / technical state

From the site audit:

- Total HTML pages: **288**
- Japanese pages: **119**
- Activity pages: **37**
- Adventure/info pages: **28**
- Rental pages: **19**
- Orphan pages: **85**
- Pages with schema: **285**
- Pages missing schema: **3**

Operational audit notes:

- Broken links report found **903 broken entries** in the earlier audit set.
- FareHarbor CTA audit identified high-priority booking friction:
  - Header `Book Online` bypasses `FH.open`.
  - No sticky mobile CTA on activity pages.
  - Missing booking analytics events around `FH.open`.
  - FareHarbor API script loading and calendar embed performance need attention.
- Mobile CTA audit found:
  - No sticky mobile CTA means users lose booking access while scrolling.
  - Some booking/tap targets fail or are borderline against 44px mobile target expectations.
  - Trust signals need to move closer to decision points.
- Media index found **5,473 website-ready candidate images**, including **3,435 hero-quality** items, but factual location use requires verification because upstream GPS is absent.

### Analytics caveat

Google Search Console access is working. Ubersuggest access is working. GA4 API access is **not currently usable from this agent session** because the available Google ADC token lacks Analytics API scopes. The GA Admin API returned `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` for analytics read scope. So the plan below uses GSC as the search source-of-truth, Ubersuggest for competitor intel, and existing repo audits for conversion/technical issues. GA4 should be re-authenticated or exported before we finalize conversion-rate benchmarks.

## Strategy

The gameplan has five lanes. They should run in order, but not one at a time. Stability and conversion fixes protect every SEO/content win.

| Lane | Goal | Why it matters | First success metric |
|---|---|---|---|
| 1. Measurement + booking instrumentation | Know which pages and CTAs produce bookings. | Without this, we optimize traffic blind. | Booking CTA events visible in GA4/GTM or an equivalent event log. |
| 2. Conversion + mobile booking | Make existing visitors book more often. | GSC shows visibility already; CTA friction wastes it. | Mobile CTA available on key activity/rental pages without FareHarbor conflicts. |
| 3. SEO architecture + internal links | Turn 288 pages into a coherent route map. | 85 orphan pages and weak internal paths dilute authority. | Priority commercial pages receive internal links from guide pages. |
| 4. Counter-content clusters | Beat competitors where AOT has real operator credibility. | KBA is gaining Kailua/Lanikai territory; AOT has local authority and existing impressions. | GSC CTR and average position improve on target clusters. |
| 5. Trust, imagery, and local proof | Make the site feel like the real outfitter, not a generic reseller. | Tourism users buy confidence. | Hero images, reviews, safety notes, and local detail appear near CTAs. |

## 30 / 60 / 90 day roadmap

### First 30 days — Stop leaking existing demand

#### 1. Lock measurement and booking attribution

**Why:** The site already gets search demand. Before pouring more traffic in, we need booking-event visibility.

Actions:

- Add/verify analytics events around every `FH.open` path:
  - `booking_open`
  - `booking_product_click`
  - `booking_call_click`
  - `mobile_cta_book_click`
  - `mobile_cta_call_click`
- Ensure header `Book Online` uses the same booking path and event instrumentation as activity/rental CTAs.
- Confirm GA4 property/API access or define an alternate export path if agent access remains blocked.
- Build a lightweight weekly KPI sheet/report:
  - GSC clicks/impressions/CTR/position by cluster
  - top pages by clicks
  - top opportunities by impressions and weak CTR
  - booking CTA events if GA4 is available

Acceptance criteria:

- A test click on a booking CTA produces an event we can verify.
- Header, mobile CTA, and body CTAs have distinguishable event names/labels.
- Weekly KPI report can run without manual data stitching.

#### 2. Mobile booking bar + tap-target cleanup

**Why:** Mobile visitors researching beach/kayak trips need persistent booking/call access. The audit shows persistent CTA access is missing.

Actions:

- Implement a mobile-only sticky bottom CTA bar with:
  - `Call`
  - `Book Now`
- Add body bottom padding to prevent content overlap.
- Suppress or adjust bar when FareHarbor modal/overlay is visible.
- Fix activity listing booking buttons that fail mobile tap target/layout expectations.
- Move one trust signal near first booking decision point on priority pages.

Acceptance criteria:

- Rendered mobile check at ~390×844 confirms CTA visibility, no overlap, and correct button behavior.
- Desktop layout remains unchanged.
- FareHarbor modal remains usable.

#### 3. Internal link triage for the money pages

**Why:** 85 orphan pages and scattered generated pages are wasting internal equity.

Priority pages to strengthen first:

- `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/`
- `/activities/sharks-cove-self-guided-snorkel/`
- `/oahu-kayaking-and-beach-adventures/ultimate-guide-for-kailua-beach-park-experience-windward-oahus-safest-and-most-adventurous-beach/`
- `/oahu-kayaking-and-beach-adventures/ultimate-guide-to-lanikai-beach/`
- `/activities/chinamans-hat-oahu-kayak-tours/` and related Mokoliʻi/Chinaman’s Hat pages
- `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/`
- `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/`

Actions:

- Generate a current internal link graph.
- Fix orphan status on active commercial pages first.
- Add contextual guide → rental/activity links, not footer-only links.
- Add “best next adventure” modules to guides.

Acceptance criteria:

- No priority commercial page remains orphaned.
- Every top guide page links to the relevant booking page above the final third of the article.

### Days 31–60 — Build the beachhead clusters

#### Cluster A: Kailua / Lanikai / Mokulua defensive counter-move

This is the immediate KBA battle.

Priority content work:

1. Refresh Kailua Beach Park guide.
2. Refresh Lanikai Beach guide.
3. Strengthen Kailua kayak rental page.
4. Refresh Lanikai snorkel / e-bike snorkel pages.
5. Refresh Mokulua / Mokes content with stronger route, safety, and permitting clarity.

Target query evidence:

| Query | GSC issue | Page direction |
|---|---|---|
| `kailua beach park` | 2,618 impressions, 0.3% CTR, pos 10.0 | Rewrite snippet/title and add better guide structure. |
| `kailua beach` | 2,548 impressions, 0.2% CTR, pos 7.5 | Improve CTR and answer beach-day intent. |
| `lanikai beach` | 1,855 impressions, 0.1% CTR, pos 5.2 | AOT is visible; snippet/content must earn click. |
| `kailua kayak rental` | 598 impressions, pos 14.8 | Strengthen rental page and internal links. |
| `kayak rentals kailua` | 456 impressions, pos 16.5 | Commercial page-2 opportunity. |
| `lanikai beach snorkeling` | 504 impressions, pos 10.4 | Update snorkel page and guide support. |

Content standard:

- Use practical local operator voice.
- Add neighborhood-respect notes for Lanikai.
- Include route/time/wind/current/safety details.
- Include clear “which trip should I book?” blocks.
- Add FAQPage and HowTo where appropriate.
- Link directly to relevant rentals/tours.

#### Cluster B: Sharks Cove / Electric Beach / snorkel gear conversion

This is the highest-impression snorkel opportunity.

Target query evidence:

| Query | GSC issue | Page direction |
|---|---|---|
| `electric beach` | 6,736 impressions, 0.5% CTR, pos 6.6 | Strong informational guide; needs booking bridge and snippet lift. |
| `sharks cove` | 4,837 impressions, 0.4% CTR, pos 5.9 | High visibility, weak click capture. |
| `sharks cove oahu` | 4,618 impressions, 1.2% CTR, pos 4.5 | Close to strong performance; improve trust/CTA. |
| `sharks cove snorkeling` | 2,666 impressions, 3.3% CTR, pos 6.3 | Existing page works; optimize for conversions. |

Actions:

- Rewrite Sharks Cove page intro around the real value proposition: full-day gear, scenic drive, flexible return, North Shore sunset option.
- Improve title/meta for CTR.
- Add “How this rental day works from Kailua” section.
- Add comparison links: Sharks Cove vs Lanikai, Electric Beach, Hanauma Bay where relevant.
- Put snorkel gear booking CTA near the logistics section.

Important CRO rule:

Do not treat the Kailua pickup → North Shore use case as a broken business model. The model is fine; the copy must explain the value.

#### Cluster C: Chinaman’s Hat / Mokoliʻi / Kaneohe / Kahana

AOT has real product fit here. GSC shows high impressions and good average position but weak CTR.

Target query evidence:

| Query | GSC issue | Direction |
|---|---|---|
| `chinamans hat` | 2,404 impressions, 0.3% CTR, pos 5.8 | Improve title/snippet and clarify kayak/hike plan. |
| `chinaman hat` | 987 impressions, 0.0% CTR, pos 6.9 | Variant coverage and CTR. |
| `chinaman's hat` | 879 impressions, weak CTR | Variant coverage and schema. |
| `kaneohe sandbar` | 1,039 impressions, 0.6% CTR, pos 15.9 | Decide if AOT wants to pursue or qualify this intent. |

Actions:

- Consolidate/clarify Chinaman’s Hat/Mokoliʻi page family to avoid cannibalization.
- Add tide/safety/current sections with clear “when not to go” language.
- Link kayak rental pages directly from guide pages.
- Decide whether Kaneohe Sandbar is an informational play, a rental play, or a “not our exact product” qualifier.

### Days 61–90 — Scale authority and international intent

#### Japanese market cleanup

The site has **119 Japanese pages**. That is a major asset if quality and intent are aligned.

Actions:

- Audit top Japanese pages in GSC by query/page.
- Fix missing schema on Japanese pages identified in the site audit.
- Confirm hreflang/canonical behavior for Japanese pages.
- Prioritize Japanese versions of pages already proving English demand:
  - Kailua kayak rental
  - Lanikai guide/snorkel
  - Sharks Cove snorkel
  - Chinaman’s Hat/Mokoliʻi
  - Mokulua/Mokes

Acceptance criteria:

- Japanese pages are not just translated; they answer Japanese traveler logistics: driving, pickup, timing, what to bring, family suitability, payment/booking confidence.

#### Media / trust upgrade

AOT has a large image library ready to become a competitive advantage, but use must be verified.

Actions:

- Select hero images for top 20 commercial and guide pages.
- Copy selected files into the working repo; never edit or direct-link NAS originals.
- Verify location/activity using folder path, filename, shoot group, visual landmarks, or Michael confirmation.
- Add image alt text that is descriptive and not keyword-stuffed.
- Put real customer/social proof near CTAs.

Acceptance criteria:

- Every priority page has a verified, locally credible hero image or section image.
- No image claims a specific place/activity without verification evidence.

#### Authority / backlink development

AOT has decent authority, but KBA has a stronger local link profile. We need links that match real-world relationships, not spam.

Actions:

- Partner/outreach page cleanup.
- Build linkable assets:
  - Kailua Beach Park conditions/planning guide
  - Lanikai respectful access guide
  - Mokoliʻi / Chinaman’s Hat safety/tide guide
  - Sharks Cove snorkel planning guide
- Outreach targets:
  - local accommodations
  - activity roundups
  - wedding/family trip planners
  - Japanese Oʻahu travel blogs
  - local conservation/safety resources where appropriate

Acceptance criteria:

- At least 10 qualified outreach targets per cluster.
- Track links earned and referral traffic.

## Priority backlog

### P0 — Must do before scaling content

| Priority | Work | Why | Evidence |
|---|---|---|---|
| P0 | Booking analytics events | Cannot prove content → booking path without it. | FareHarbor audit found zero booking analytics events. |
| P0 | Mobile sticky CTA + tap targets | Existing traffic leaks on mobile. | Mobile CTA audit found no persistent CTA and tap target failures. |
| P0 | Internal links to money pages | 85 orphan pages indicate architecture leakage. | Site audit. |
| P0 | Merge/save KBA counter-content research | Immediate competitor movement. | KBA `/kailua-beach-park` and `/lanikai` signals. |

### P1 — Highest SEO/CRO upside

| Priority | Work | Why | Target pages |
|---|---|---|---|
| P1 | Kailua Beach Park refresh | 2,618 impressions, 0.3% CTR; KBA strong. | Kailua Beach Park guide |
| P1 | Lanikai guide refresh | 1,855 impressions, 0.1% CTR; KBA strong. | Lanikai guide + snorkel pages |
| P1 | Sharks Cove copy/CRO refresh | Thousands of impressions at page-one positions. | Sharks Cove snorkel page |
| P1 | Electric Beach booking bridge | Highest impression query in GSC snapshot. | Electric Beach snorkel guide |
| P1 | Kailua kayak rental strengthening | Commercial page-2 query set. | Kailua kayak rental page |

### P2 — Growth and moat

| Priority | Work | Why |
|---|---|---|
| P2 | Japanese page intent audit | 119 Japanese pages are a big asset if quality is high. |
| P2 | Verified media refresh | AOT has 5,473 candidate images; local visuals can differentiate. |
| P2 | Backlink/outreach assets | KBA’s link profile is stronger; AOT needs real-world local links. |
| P2 | Content cluster expansion | Waimānalo, turtle/sea-life, family beach day, rainy/windy day alternatives. |

## KPI framework

### Weekly dashboard

| KPI | Source | Target |
|---|---|---|
| Organic clicks | GSC | +15–25% over 90 days on refreshed clusters |
| Organic impressions | GSC | Stable/increasing, but not at expense of CTR |
| CTR on target queries | GSC | Double weak CTR queries below 1% where avg position is top 10 |
| Avg position on target queries | GSC | Move page-2 commercial queries into top 10 |
| Booking CTA clicks | GA4/GTM/FareHarbor wrapper | Establish baseline first, then improve |
| Call CTA clicks | GA4/GTM | Establish baseline first, then improve |
| Mobile CTA visibility / no overlap | Rendered QA | Pass on priority templates |
| Orphan priority pages | Internal crawl | 0 priority commercial pages orphaned |
| Broken internal links | Internal crawl | Downward trend; no broken links on priority funnels |

### Cluster scorecard

Track each cluster separately:

- Kailua / Lanikai / Mokulua
- Sharks Cove / Electric Beach / snorkel gear
- Chinaman’s Hat / Mokoliʻi / Kaneohe / Kahana
- Japanese market
- Brand / homepage

Each cluster should have:

- owner
- target pages
- target queries
- current GSC baseline
- content status
- internal-link status
- CTA/event status
- next action

## Governance / workflow rules

1. **Private strategy stays private.** Competitive intelligence, GSC, Ubersuggest, GA4 notes, and vendor/account details belong in `active-oahu-business`.
2. **Deployable site code stays public-safe.** HTML/CSS/JS/site assets belong in `active-oahu-tours-mirror`.
3. **Use clean worktrees from `origin/main` for PRs.** Do not branch from staging or mixed local branches.
4. **Do not edit generated output only.** Template/CSS/source changes must survive rebuilds.
5. **Every content task needs evidence.** GSC query/page data, competitor evidence, target URL, acceptance criteria.
6. **Every page refresh needs verification.** Static checks plus rendered mobile QA when UI/CTA is touched.
7. **No Hawaiian culture shortcuts.** Use correct diacritics where known, avoid generic/corporate phrasing, include respectful access/safety context.

## Immediate next 10 tasks

1. Merge or preserve PR #4 in `active-oahu-business`: KBA Kailua/Lanikai counter-content research.
2. Create implementation tasks from the KBA Linear-ready draft:
   - Kailua Beach Park guide refresh
   - Lanikai guide/snorkel refresh
   - Kailua kayak rental strengthening
3. Build/verify booking analytics wrapper around `FH.open`.
4. Implement mobile sticky CTA bar with FareHarbor overlay suppression.
5. Generate a fresh internal link graph and identify priority orphan fixes.
6. Refresh Sharks Cove page copy around the actual value proposition.
7. Refresh Electric Beach guide with booking bridge and CTR-focused meta.
8. Audit Japanese pages by GSC query/page and fix missing schema/hreflang issues.
9. Select and verify hero images for top 10 priority pages.
10. Re-auth or export GA4 so booking/event/conversion data can join GSC and Ubersuggest in the weekly dashboard.

## What not to do

- Do not create broad “write more blog posts” tasks.
- Do not use Ubersuggest estimates as truth for AOT performance; use GSC for AOT.
- Do not chase every high-volume tourism keyword if AOT has no booking path for it.
- Do not publish unverified image/location claims.
- Do not optimize for traffic alone. A page that gets clicks but does not explain how to book or what trip fits is unfinished.

## Bottom line

The next paddle stroke is not “more content.” It is:

1. **Instrument booking actions.**
2. **Fix mobile booking access.**
3. **Strengthen internal links to money pages.**
4. **Refresh the Kailua/Lanikai and Sharks Cove clusters using GSC + competitor evidence.**
5. **Use AOT’s real local expertise and verified imagery to make those pages convert.**

That gives us a site that ranks, earns trust, and actually turns searchers into booked tours/rentals.
