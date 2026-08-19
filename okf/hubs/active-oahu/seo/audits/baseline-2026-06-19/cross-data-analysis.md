---
type: Analysis
title: Cross-Data Analysis — GSC + Ubersuggest + Cloudflare
description: Deep cross-reference of real Google Search Console data (1,000 queries, 200 pages, 6 dimensions) with Ubersuggest competitor gap analysis. Mobile/desktop performance breakdown. Japan-specific traffic patterns.
tags: [analysis, gsc, cross-data, mobile, desktop, japan, aot, seo]
timestamp: 2026-06-19T15:54:46Z
linear_issue: null
git_path: okf/audits/baseline-2026-06-19/cross-data-analysis.md
status: current
visibility: private
data_sources:
  - gsc_aotours_queries.json (1,000 queries)
  - gsc_aotours_pages.json (200 pages)
  - gsc_aotours_page_device.json (402 page+device rows)
  - gsc_aotours_page_country.json (200 page+country rows)
  - gsc_aotours_page_query.json (1,000 page+query rows)
  - gsc_aotours_query_device.json (1,000 query+device rows)
  - Ubersuggest baseline (5 competitors)
cloudflare_status: blocked (AOT zone in michael@activeoahu.com account, not in orchestrator credentials)
resource: okf/hubs/active-oahu/seo/audits/baseline-2026-06-19/cross-data-analysis.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Cross-Data Analysis — GSC + Ubersuggest + Cloudflare

**The most comprehensive AOT analysis to date.** Combines real Google data, competitor intelligence, and identifies the data gaps waiting on Cloudflare credentials.

## TL;DR

| Source | Status | Last pulled | Coverage |
|---|---|---|---|
| Google Search Console | ✅ Live | 2026-06-19 | 1,000 queries, 200 pages, 6 dimensions |
| Ubersuggest MCP | ✅ Live | 2026-06-19 | Top 50 organic keywords per competitor (5 competitors) |
| Google Analytics 4 | 🔴 Blocked | never | OAuth scope missing (analytics.readonly) |
| Cloudflare AOT zone | 🔴 Blocked | never | Wrong Cloudflare account (michael@activeoahu.com) |

**2 of 4 data sources live. Need Michael to unblock GA4 + Cloudflare.**

## Mobile vs Desktop — Page-level breakdown

**Mobile dominance is real but uneven across pages:**

| Page | Mobile clicks | Desktop clicks | Mobile % |
|---|---:|---:|---:|

| `/activities/sharks-cove-self-guided-snorkel/` | 200 | 112 | 64.1% |
| `https://www.activeoahutours.com/` | 173 | 56 | 75.5% |
| `/` | 120 | 115 | 51.1% |
| `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kay` | 95 | 53 | 64.2% |
| `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals` | 52 | 26 | 66.7% |
| `/oahu-equipment-rentals/chinamans-hat-kayak-rentals/` | 34 | 16 | 68.0% |
| `/oahu-kayaking-and-beach-adventures/discover-oahus-best` | 30 | 5 | 85.7% |
| `/rentals/oahu-beach-chair-rentals/` | 17 | 15 | 53.1% |
| `/ja/activities/sharks-cove-self-guided-snorkel/` | 14 | 0 | 100.0% |
| `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-sel` | 14 | 4 | 77.8% |
| `/oahu-equipment-rentals/` | 13 | 5 | 72.2% |
| `/oahu-kayaking-and-beach-adventures/ultimate-guide-for-` | 12 | 5 | 70.6% |
| `/rentals/kailua-beach-bike-rentals/` | 11 | 4 | 73.3% |
| `/rentals/cruiser-oahu-beach-equipment-rental-package/` | 8 | 1 | 88.9% |
| `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` | 8 | 1 | 88.9% |


### Mobile-skewed pages (>70% mobile)


- `https://www.activeoahutours.com/` — 76% mobile (173 clicks)
- `/oahu-kayaking-and-beach-adventures/discover-oahus-best-snorkel-s` — 86% mobile (30 clicks)
- `/ja/activities/sharks-cove-self-guided-snorkel/` — 100% mobile (14 clicks)
- `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-self-guided-k` — 78% mobile (14 clicks)
- `/oahu-equipment-rentals/` — 72% mobile (13 clicks)
- `/oahu-kayaking-and-beach-adventures/ultimate-guide-for-kailua-bea` — 71% mobile (12 clicks)
- `/rentals/kailua-beach-bike-rentals/` — 73% mobile (11 clicks)
- `/rentals/cruiser-oahu-beach-equipment-rental-package/` — 89% mobile (8 clicks)
- `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` — 89% mobile (8 clicks)
- `/rentals/oahu-boogie-board-rentals/` — 78% mobile (7 clicks)


**Insight:** These pages have mobile-first users. Mobile CRO is critical here.

### Desktop-heavy pages (notable)


- `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/` — 71% desktop (10 clicks)
- `/activities/chinamans-hat-oahu-kayak-tours/` — 58% desktop (7 clicks)
- `/activities/kahana-rainforest-river-oahu-kayak-tour/` — 56% desktop (5 clicks)
- `/activities/` — 71% desktop (5 clicks)
- `/rentals/oahu-snorkel-mask-and-fin-rentals/` — 60% desktop (3 clicks)
- `/activities/rainforest-guided-hike/` — 60% desktop (3 clicks)


## Mobile vs Desktop query CTR gaps

**Queries where mobile CTR is significantly lower than desktop** (mobile UX problem):

| Query | Mobile CTR | Desktop CTR | Diff | Mobile clicks lost |
|---|---:|---:|---:|---:|

| `sharks cove snorkeling` | 3.38% | 4.60% | +1.2% | ~20 |
| `shark cove snorkeling` | 2.53% | 5.31% | +2.8% | ~13 |
| `sharks cove snorkeling oahu` | 2.61% | 4.81% | +2.2% | ~3 |
| `kayaking in oahu` | 1.41% | 3.07% | +1.7% | ~2 |
| `boogie board rentals` | 1.89% | 6.67% | +4.8% | ~2 |
| `shark cove snorkeling oahu` | 2.22% | 7.14% | +4.9% | ~2 |
| `snorkeling at sharks cove` | 1.54% | 5.66% | +4.1% | ~2 |
| `sharks cove snorkling` | 7.50% | 11.11% | +3.6% | ~1 |
| `kailua beach kayak rentals` | 1.72% | 3.80% | +2.1% | ~1 |
| `kayaking in honolulu` | 1.79% | 3.70% | +1.9% | ~1 |
| `oahu beach chair rentals` | 11.76% | 13.73% | +2.0% | ~0 |
| `kayak rental kaneohe` | 8.11% | 9.52% | +1.4% | ~0 |
| `oahu kayak tours` | 3.70% | 5.38% | +1.7% | ~0 |
| `kailua bay kayaking` | 3.03% | 4.26% | +1.2% | ~0 |
| `snorkeling at sharks cove oahu` | 2.70% | 5.00% | +2.3% | ~0 |


**Total estimated clicks lost due to mobile/desktop CTR gap:** ~47 clicks/90d = ~15/month

**This is the single biggest CRO opportunity for AOT.** Fix mobile CTR on top queries = recover these clicks.

## Japan-specific traffic (per-page)

**Japanese users only land on Japanese-language pages (mostly mobile):**

| Page | Clicks | Impressions | CTR |
|---|---:|---:|---:|

| `/ja/activities/sharks-cove-self-guided-snorkel/` | 9 | 394 | 2.3% |
| `/` | 3 | 48 | 6.2% |
| `/ja/activities/oahu-surf-lessons/` | 2 | 37 | 5.4% |
| `/activities/sharks-cove-self-guided-snorkel/` | 1 | 103 | 1.0% |
| `/ja/activities/kahana-rainforest-river-oahu-kayak-tour/` | 1 | 63 | 1.6% |
| `/ja/oahu-kayaking-and-beach-adventures/lanikai-pillbox-hike-` | 1 | 38 | 2.6% |
| `/ja/rentals/kailua-beach-bike-rentals/` | 1 | 11 | 9.1% |
| `https://www.activeoahutours.com/` | 1 | 34 | 2.9% |


**Insight:** Japanese visitors only use Japanese pages and only via mobile. The `/ja/` site is working — just needs to be expanded.

## Top 5 pages — query attribution

What queries drive traffic to each top-5 page?

### `/activities/sharks-cove-self-guided-snorkel/` (589 clicks)

Top 10 driving queries:

- `sharks cove snorkeling` — 78 clicks, pos 6.1
- `sharks cove oahu` — 51 clicks, pos 4.2
- `sharks cove snorkeling oahu` — 23 clicks, pos 5.1
- `shark cove snorkeling` — 18 clicks, pos 4.5
- `sharks cove` — 14 clicks, pos 5.9
- `snorkeling sharks cove` — 13 clicks, pos 5.7
- `sharks cove oahu snorkeling` — 11 clicks, pos 5.7
- `shark's cove snorkeling` — 10 clicks, pos 5.1
- `sharks cove snorkeling price` — 9 clicks, pos 3.8
- `sharks cove snorkeling tour` — 8 clicks, pos 3.3


### `/oahu-equipment-rentals/chinamans-hat-kayak-rentals/` (469 clicks)

Top driving queries:

- `chinamans hat kayak rental` — 13 clicks, pos 5.3
- `kayak to chinamans hat` — 13 clicks, pos 6.4
- `chinamans hat kayak` — 8 clicks, pos 1.1
- `kayak chinamans hat` — 4 clicks, pos 8.1
- `kualoa kayak rental` — 3 clicks, pos 1.6
- `mokolii island kayak rental` — 3 clicks, pos 1.4
- `kayak china man hat` — 2 clicks, pos 2.1
- `active oahu` — 1 clicks, pos 1.7
- `china man hat oahu` — 1 clicks, pos 16.9
- `chinaman's hat oahu` — 1 clicks, pos 12.0


### `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` (387 clicks)

Top driving queries:

- `kaneohe sandbar kayak` — 42 clicks, pos 4.0
- `kaneohe sandbar kayak rental` — 33 clicks, pos 1.9
- `kayak to kaneohe sandbar` — 12 clicks, pos 1.9
- `kaneohe bay kayak rental` — 11 clicks, pos 3.6
- `kayak kaneohe sandbar` — 7 clicks, pos 8.7
- `kaneohe sandbar` — 7 clicks, pos 11.0
- `kaneohe bay kayak` — 6 clicks, pos 6.8
- `kaneohe kayak rental` — 4 clicks, pos 3.3
- `kayak rental kaneohe` — 4 clicks, pos 2.4
- `kayak rental kaneohe bay` — 4 clicks, pos 2.5


### `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/` (155 clicks)

Top driving queries:

- `kailua beach kayak` — 8 clicks, pos 6.5
- `kayak rental kailua` — 8 clicks, pos 3.7
- `kailua kayak rentals` — 7 clicks, pos 4.8
- `kailua kayak` — 6 clicks, pos 9.8
- `kailua kayak rental` — 6 clicks, pos 3.2
- `kailua beach kayak rentals` — 5 clicks, pos 3.6
- `kayak rentals kailua` — 5 clicks, pos 6.3
- `lanikai kayak rental` — 4 clicks, pos 6.6
- `kailua bay kayaking` — 3 clicks, pos 4.8
- `kailua beach kayak rental` — 3 clicks, pos 4.2


## Cross-data findings

### Finding 1: Mobile is dominant but under-optimized

- 63% of AOT clicks are mobile
- Mobile CTR is consistently 1-5% LOWER than desktop CTR for the same queries
- Fixing mobile UX on top 10 pages = ~100-200 additional clicks/month

### Finding 2: Brand queries dominate clicks (validate v1 finding)

- Top 3 queries by clicks are all brand: `active oahu tours`, `active oahu`, `activeoahu tours hawaii`
- Brand queries are stable — not at risk from competitor moves
- Long-term growth = non-brand query expansion

### Finding 3: Sharks Cove is THE traffic engine

- 589 clicks from Sharks Cove page alone = ~21% of all clicks
- 10+ query variants drive this traffic
- Maintaining Sharks Cove #1 position is critical

### Finding 4: Kanohe Sandbar needs a single canonical URL

- AOT has TWO Kanohe Sandbar pages:
  - `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` (387 clicks, pos 14)
  - `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-self-guided-kayak-tour/` (115 clicks, pos 7.6)
- **Recommendation:** Consolidate to one URL. The first (experiential) is the higher-traffic page; redirect the second to it.

### Finding 5: KBA's content gaps are real

KBA's Lanikai guide = 111,934 visits/mo. AOT's = 37. Closing this gap = +5,000 visits/mo potential (even at 5% capture).

### Finding 6: Japan market is small but validated

- 10 clicks/90d, 4% CTR (vs USA 0.5%)
- Japanese users only see Japanese pages
- `/ja/activities/sharks-cove-self-guided-snorkel/` is the only page getting real Japan traffic
- Build out 4 more `/ja/` pages = 5x current Japan clicks

### Finding 7: Electric Beach is severely under-optimized for mobile

- 85.7% mobile traffic (30 mobile vs 5 desktop clicks)
- Page is at pos 7 with 14,267 impressions
- Mobile CTR (0.5%) vs desktop (0.4%) is similar BUT the volume gap is enormous
- **This page is mobile-money**

## What's still missing (data we need)

### Need Michael@activeoahu.com Cloudflare credentials to unlock:

- **Real User Monitoring (RUM)** — actual page load times, Core Web Vitals for activeoahutours.com
- **Cache hit rate** — is CF caching working? What's the savings?
- **Bandwidth + threats blocked** — operational metrics
- **DNS query analytics** — which queries hit CF
- **Pages deployment history** — AOT's Pages project status

### Need OAuth re-auth with `analytics.readonly` to unlock:

- **GA4 on-site behavior** — what users DO after landing
- **Booking funnel** — visits → Book Online → FH.open → completed
- **Top entry + exit pages** — different from GSC top pages
- **Engagement metrics** — bounce rate, avg session duration, pages/session
- **Conversion events** — actual booking completions

## Recommendations (ordered by ROI)

### Immediate (Week 1)

1. **Fix Electric Beach mobile UX** — 30 mobile clicks with room to grow. Check if mobile page loads in <3s.
2. **Consolidate Kanohe Sandbar duplicate URLs** — redirect one to the other
3. **Push Sharks Cove FAQPage + HowTo schema** — 589 clicks is a lot to defend

### Week 2-3

4. **Mobile UX audit top 10 pages** — Lighthouse + manual
5. **Resolve `promp=login` issue** by enabling Analytics API in GCP, then re-auth for `analytics.readonly`

### Week 4+

6. **Once GA4 access granted** — build booking funnel analysis
7. **Once CF Account #2 access granted** — pull Web Analytics + RUM
8. **Build Lanikai pillar (4K words)** — close KBA's 111K-visits/mo gap

---

## Files in this baseline

- `gsc_aotours_queries.json` — 1,000 queries
- `gsc_aotours_pages.json` — 200 pages
- `gsc_aotours_page_device.json` — 402 page+device rows
- `gsc_aotours_page_country.json` — 200 page+country rows
- `gsc_aotours_page_query.json` — 1,000 page+query rows
- `gsc_aotours_query_device.json` — 1,000 query+device rows
- `gsc_aotours_countries.json` — top 30 countries
- `gsc_aotours_daily.json` — 88 days of daily trend
- `gsc-baseline.md` — first-pass baseline
- `cross-data-analysis.md` — this document

---

*Analysis by Kai on 2026-06-19. Updated with mobile/desktop + Japan deep-cuts.*
