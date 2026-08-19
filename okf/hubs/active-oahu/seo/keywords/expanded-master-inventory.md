---
type: Reference
title: Active Oahu Tours — Expanded Master Keyword Inventory (GSC 90-day data)
description: Canonical keyword inventory built from REAL Google Search Console data — 1000 distinct queries from the last 90 days. Each query has actual clicks, impressions, CTR, position, plus intent classification and target page. This supersedes the Ubersuggest-only inventory from earlier.
tags: [keywords, master-inventory, aot, seo, gsc-data, real-data, intent, clusters]
timestamp: 2026-06-19T15:35:39Z
linear_issue: null
git_path: okf/keywords/expanded-master-inventory.md
status: current
data_sources:
  - gsc_aotours_queries.json (1,000 queries, last 90 days)
  - gsc_aotours_pages.json (200 pages)
total_queries: 1000
total_clicks_90d: 1358
total_impressions_90d: 81777
resource: okf/hubs/active-oahu/seo/keywords/expanded-master-inventory.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Tours — Expanded Master Keyword Inventory

**Built from REAL Google Search Console data** — 1000 queries captured in the last 90 days (March 21 – June 16, 2026). This is the source of truth for AOT's actual SEO performance.

**Supersedes the earlier Ubersuggest-only inventory** (in `master-inventory.md` — keep that for competitive intelligence, but use THIS for AOT's own performance tracking).

## Headline statistics

| Metric | Value |
|---|---:|
| Total distinct queries | **1000** |
| Total clicks (90 days) | **1358** |
| Total impressions (90 days) | **81,777** |
| Queries with ≥1 click | 305 |
| Queries with ≥5 clicks | 59 |
| Queries with ≥20 clicks | 9 |
| Queries with position ≤3 | 157 |
| Queries with position 4-15 | 503 |

## Long-tail distribution

AOT's SEO is dominated by **long-tail queries**:

- **Top 10 queries** = ~50% of all clicks
- **Top 30 queries** = ~80% of clicks
- **970+ remaining queries** = ~20% of clicks but HUGE growth potential

This is healthy — long-tail diversifies risk (one algorithm change doesn't kill you) and shows broad topical coverage.

## Intent classification

| Intent | Queries | Clicks | Avg Pos |
|---|---:|---:|---:|
| Transactional (book/rent) | 400 | 331 | 21.0 |
| Commercial (best/review) | 119 | 6 | 30.8 |
| Informational (how/what) | 22 | 8 | 10.7 |
| Navigational (brand) | 3 | 260 | 5.2 |

**Insight:** Transactional queries dominate clicks (most revenue-driving), but informational queries are highest-volume. **Build informational content to capture top-of-funnel traffic, then route to booking.**

---

## Cluster breakdown (by topic + intent)

### Snorkeling > North Shore

- Queries: **148** | Clicks: **362** | Impr: **31,168** | Avg Pos: **24.6**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `sharks cove snorkeling` | Mixed | 78 | 2,162 | 3.6% | 6.1 |
| `sharks cove oahu` | Mixed | 51 | 4,800 | 1.1% | 4.2 |
| `electric beach` | Mixed | 30 | 5,935 | 0.5% | 6.5 |
| `sharks cove snorkeling oahu` | Mixed | 23 | 549 | 4.2% | 5.1 |
| `shark cove snorkeling` | Mixed | 18 | 588 | 3.1% | 4.5 |
| `sharks cove` | Mixed | 14 | 4,987 | 0.3% | 5.9 |
| `snorkeling sharks cove` | Mixed | 13 | 211 | 6.2% | 5.7 |
| `sharks cove oahu snorkeling` | Mixed | 11 | 598 | 1.8% | 5.7 |
| `shark's cove snorkeling` | Mixed | 10 | 304 | 3.3% | 5.1 |
| `sharks cove snorkeling price` | Transactional | 9 | 89 | 10.1% | 4.1 |
| `sharks cove snorkeling tour` | Mixed | 8 | 66 | 12.1% | 3.3 |
| `shark cove oahu` | Mixed | 7 | 688 | 1.0% | 4.0 |
| `shark cove snorkeling oahu` | Mixed | 5 | 101 | 5.0% | 5.7 |
| `sharks cove snorkling` | Mixed | 5 | 58 | 8.6% | 4.5 |
| `lanikai beach snorkeling` | Mixed | 4 | 515 | 0.8% | 6.6 |

---

### Brand > Direct

- Queries: **3** | Clicks: **260** | Impr: **833** | Avg Pos: **5.2**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `active oahu tours` | Navigational | 150 | 319 | 47.0% | 1.0 |
| `active oahu` | Navigational | 110 | 298 | 36.9% | 2.0 |
| `active oahu tours ライエ` | Navigational | 0 | 216 | 0.0% | 12.6 |

---

### Mixed > Kayak Rentals

- Queries: **101** | Clicks: **234** | Impr: **10,666** | Avg Pos: **19.0**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kayaking oahu` | Mixed | 23 | 1,014 | 2.3% | 8.3 |
| `kayak rental oahu` | Transactional | 15 | 291 | 5.2% | 13.1 |
| `kaneohe bay kayak rental` | Transactional | 13 | 150 | 8.7% | 11.1 |
| `kayak oahu` | Mixed | 10 | 352 | 2.8% | 5.2 |
| `kayak rental kailua` | Transactional | 10 | 205 | 4.9% | 7.8 |
| `kayak rentals kailua` | Transactional | 10 | 98 | 10.2% | 8.9 |
| `kailua kayak rental` | Transactional | 7 | 403 | 1.7% | 8.5 |
| `kailua kayak rentals` | Transactional | 7 | 84 | 8.3% | 7.3 |
| `kayak tour oahu` | Mixed | 7 | 86 | 8.1% | 3.5 |
| `kayaking in oahu` | Mixed | 7 | 307 | 2.3% | 7.9 |
| `oahu kayak tours` | Mixed | 7 | 150 | 4.7% | 9.9 |
| `oahu kayaking` | Mixed | 7 | 468 | 1.5% | 13.3 |
| `kayak rental honolulu` | Transactional | 6 | 158 | 3.8% | 8.6 |
| `kayak rentals oahu` | Transactional | 6 | 154 | 3.9% | 8.7 |
| `kayaking in oahu hawaii` | Mixed | 6 | 114 | 5.3% | 6.8 |

---

### Snorkeling-Adjacent > Kaneohe Sandbar

- Queries: **29** | Clicks: **136** | Impr: **2,720** | Avg Pos: **8.6**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kaneohe sandbar kayak` | Mixed | 43 | 294 | 14.6% | 5.2 |
| `kaneohe sandbar kayak rental` | Transactional | 35 | 288 | 12.2% | 4.6 |
| `kayak to kaneohe sandbar` | Mixed | 13 | 69 | 18.8% | 3.2 |
| `kaneohe sandbar` | Mixed | 7 | 1,134 | 0.6% | 12.8 |
| `kayak kaneohe sandbar` | Mixed | 7 | 82 | 8.5% | 10.1 |
| `kayaking to kaneohe sandbar` | Mixed | 6 | 47 | 12.8% | 3.2 |
| `oahu sandbar kayak` | Mixed | 4 | 33 | 12.1% | 2.2 |
| `how to get to kaneohe sandbar` | Informational | 3 | 188 | 1.6% | 7.7 |
| `kaneohe sandbar kayaking` | Mixed | 3 | 90 | 3.3% | 5.3 |
| `kaneohe sandbar tour` | Mixed | 3 | 49 | 6.1% | 21.2 |
| `sandbar kayak rental` | Transactional | 3 | 30 | 10.0% | 4.1 |
| `how long does it take to kayak to kaneohe ` | Informational | 2 | 40 | 5.0% | 2.5 |
| `sandbar kayaking` | Mixed | 2 | 58 | 3.4% | 14.6 |
| `is kaneohe sandbar worth it` | Commercial | 1 | 8 | 12.5% | 1.2 |
| `kaneohe bay sandbar` | Mixed | 1 | 61 | 1.6% | 17.1 |

---

### Misc > Uncategorized

- Queries: **497** | Clicks: **125** | Impr: **15,344** | Avg Pos: **16.2**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `シャークスコーブ` | Mixed | 7 | 334 | 2.1% | 5.2 |
| `kailua kayak` | Mixed | 6 | 245 | 2.4% | 13.7 |
| `kaneohe bay kayak` | Mixed | 6 | 86 | 7.0% | 10.0 |
| `oahu kayak` | Mixed | 6 | 157 | 3.8% | 13.0 |
| `kayak honolulu` | Mixed | 5 | 202 | 2.5% | 7.3 |
| `boogie board rental oahu` | Transactional | 3 | 50 | 6.0% | 13.4 |
| `oahu kayak to island` | Mixed | 3 | 50 | 6.0% | 4.4 |
| `ワイキキビーチパラソルレンタル 安い` | Mixed | 3 | 20 | 15.0% | 3.1 |
| `boogie board rentals` | Transactional | 2 | 68 | 2.9% | 14.4 |
| `kayak` | Mixed | 2 | 2,283 | 0.1% | 7.0 |
| `kayak china man hat` | Mixed | 2 | 11 | 18.2% | 2.1 |
| `kayak in oahu` | Mixed | 2 | 92 | 2.2% | 13.0 |
| `kayak kailua` | Mixed | 2 | 173 | 1.2% | 11.3 |
| `oahu hiking tour` | Mixed | 2 | 30 | 6.7% | 8.4 |
| `oahu hiking tours` | Mixed | 2 | 85 | 2.4% | 8.6 |

---

### Tours > Chinamans Hat

- Queries: **16** | Clicks: **70** | Impr: **3,795** | Avg Pos: **10.6**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `chinamans hat kayak rental` | Transactional | 15 | 123 | 12.2% | 23.4 |
| `kayak to chinamans hat` | Mixed | 13 | 87 | 14.9% | 14.7 |
| `chinamans hat kayak` | Mixed | 8 | 34 | 23.5% | 1.1 |
| `mokolii island kayak` | Mixed | 8 | 47 | 17.0% | 18.9 |
| `kayak chinamans hat` | Mixed | 5 | 95 | 5.3% | 27.1 |
| `kualoa kayak rental` | Transactional | 4 | 9 | 44.4% | 1.4 |
| `chinamans hat` | Mixed | 3 | 2,096 | 0.1% | 6.3 |
| `mokolii island kayak rental` | Transactional | 3 | 18 | 16.7% | 8.5 |
| `chinamans hat hike` | Mixed | 2 | 67 | 3.0% | 3.0 |
| `chinamans hat oahu` | Mixed | 2 | 573 | 0.3% | 6.9 |
| `mokolii island self guided kayak tour` | Informational | 2 | 23 | 8.7% | 7.9 |
| `chinaman's hat oahu` | Mixed | 1 | 155 | 0.6% | 12.5 |
| `chinaman’s hat` | Mixed | 1 | 108 | 0.9% | 9.7 |
| `kualoa regional park map` | Mixed | 1 | 22 | 4.5% | 1.6 |
| `mokolii island` | Mixed | 1 | 331 | 0.3% | 14.5 |

---

### Tours > Mokulua Lanikai

- Queries: **32** | Clicks: **55** | Impr: **5,825** | Avg Pos: **12.6**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kayak to mokulua islands` | Mixed | 7 | 217 | 3.2% | 5.8 |
| `lanikai kayak rental` | Transactional | 5 | 188 | 2.7% | 7.3 |
| `mokulua islands kayak rental` | Transactional | 5 | 81 | 6.2% | 7.7 |
| `mokulua islands kayak` | Mixed | 4 | 268 | 1.5% | 8.6 |
| `popoia island` | Mixed | 4 | 642 | 0.6% | 8.8 |
| `lanikai beach tours` | Mixed | 3 | 578 | 0.5% | 13.9 |
| `lanikai kayak` | Mixed | 3 | 89 | 3.4% | 10.1 |
| `kayak rental lanikai beach` | Transactional | 2 | 94 | 2.1% | 10.0 |
| `kayak to the mokulua islands` | Mixed | 2 | 65 | 3.1% | 5.9 |
| `lanikai beach` | Mixed | 2 | 2,185 | 0.1% | 5.0 |
| `lanikai beach kayak rental` | Transactional | 2 | 131 | 1.5% | 8.4 |
| `lanikai pillbox trail tickets` | Mixed | 2 | 89 | 2.2% | 5.9 |
| `flat island hawaii` | Mixed | 1 | 52 | 1.9% | 4.0 |
| `flat island oahu` | Mixed | 1 | 75 | 1.3% | 11.6 |
| `kayak kailua to mokulua` | Mixed | 1 | 47 | 2.1% | 15.7 |

---

### Rentals > Beach Equipment

- Queries: **107** | Clicks: **41** | Impr: **3,750** | Avg Pos: **23.0**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `oahu beach chair rentals` | Transactional | 11 | 86 | 12.8% | 5.9 |
| `beach chair rentals oahu` | Transactional | 9 | 71 | 12.7% | 4.9 |
| `beach chair rental oahu` | Transactional | 6 | 63 | 9.5% | 8.3 |
| `oahu beach gear rentals` | Transactional | 5 | 74 | 6.8% | 6.9 |
| `beach umbrella rental near me` | Transactional | 3 | 76 | 3.9% | 10.8 |
| `oahu beach equipment rentals` | Transactional | 3 | 361 | 0.8% | 4.1 |
| `beach chair rental honolulu` | Transactional | 1 | 165 | 0.6% | 10.2 |
| `chair and umbrella rental` | Transactional | 1 | 3 | 33.3% | 8.3 |
| `honolulu beach chair rentals` | Transactional | 1 | 3 | 33.3% | 6.3 |
| `used beach chairs for sale near me` | Transactional | 1 | 2 | 50.0% | 6.0 |
| `'beach chair rentals near me'` | Transactional | 0 | 10 | 0.0% | 45.2 |
| `'beach umbrella rentals near me'` | Transactional | 0 | 7 | 0.0% | 53.4 |
| `aloha beach chair` | Mixed | 0 | 5 | 0.0% | 1.0 |
| `baby beach equipment rental oahu` | Transactional | 0 | 121 | 0.0% | 10.9 |
| `baby equipment rental pupukea` | Transactional | 0 | 2 | 0.0% | 9.5 |

---

### Guides > Beach Hubs

- Queries: **8** | Clicks: **36** | Impr: **6,469** | Avg Pos: **9.4**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kailua beach park` | Mixed | 10 | 2,853 | 0.4% | 9.7 |
| `kailua beach kayak` | Mixed | 8 | 149 | 5.4% | 11.0 |
| `kailua beach kayak rentals` | Transactional | 5 | 139 | 3.6% | 11.6 |
| `kailua beach` | Mixed | 4 | 2,918 | 0.1% | 6.3 |
| `kailua bay kayaking` | Mixed | 3 | 80 | 3.8% | 10.7 |
| `kailua beach kayak rental` | Transactional | 3 | 67 | 4.5% | 7.9 |
| `kailua beach park kayak rentals` | Transactional | 2 | 35 | 5.7% | 7.1 |
| `kailua beach oahu` | Mixed | 1 | 228 | 0.4% | 10.6 |

---

### Tours > E Bike

- Queries: **31** | Clicks: **18** | Impr: **474** | Avg Pos: **20.3**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `ebike rental near me` | Transactional | 4 | 52 | 7.7% | 34.2 |
| `kailua bike rental` | Transactional | 4 | 84 | 4.8% | 11.0 |
| `ebike rental oahu` | Transactional | 2 | 9 | 22.2% | 7.0 |
| `bike rental kailua` | Transactional | 1 | 64 | 1.6% | 4.1 |
| `bike rentals near me` | Transactional | 1 | 25 | 4.0% | 4.7 |
| `cargo ebike rental` | Transactional | 1 | 2 | 50.0% | 3.5 |
| `e bike rental oahu` | Transactional | 1 | 9 | 11.1% | 7.0 |
| `e bike rentals` | Transactional | 1 | 6 | 16.7% | 10.2 |
| `ebike hire` | Transactional | 1 | 3 | 33.3% | 4.0 |
| `electric bike rental` | Transactional | 1 | 7 | 14.3% | 6.9 |
| `gravel bike rental near me` | Transactional | 1 | 1 | 100.0% | 1.0 |
| `beach bike rentals` | Transactional | 0 | 5 | 0.0% | 8.8 |
| `big island electric bike rentals in kona` | Transactional | 0 | 43 | 0.0% | 61.7 |
| `bike rental` | Transactional | 0 | 3 | 0.0% | 5.7 |
| `bike rental ainhoa` | Transactional | 0 | 18 | 0.0% | 25.3 |

---

### Tours > Rainforest Inland

- Queries: **12** | Clicks: **11** | Impr: **347** | Avg Pos: **29.8**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kahana river` | Mixed | 4 | 117 | 3.4% | 4.4 |
| `kahana river oahu` | Mixed | 3 | 43 | 7.0% | 2.1 |
| `kahana river kayak` | Mixed | 2 | 85 | 2.4% | 3.4 |
| `kahana bay kayaking` | Mixed | 1 | 76 | 1.3% | 24.7 |
| `kahana stream oahu` | Mixed | 1 | 5 | 20.0% | 7.2 |
| `activities to do in the rainforest` | Informational | 0 | 2 | 0.0% | 11.0 |
| `anahulu river kayak` | Mixed | 0 | 5 | 0.0% | 64.4 |
| `anahulu river kayak rental` | Transactional | 0 | 5 | 0.0% | 50.2 |
| `anahulu river kayaking` | Mixed | 0 | 1 | 0.0% | 57.0 |
| `atlantic rainforest kayaking tour` | Mixed | 0 | 2 | 0.0% | 54.5 |
| `best cafes for river paddling` | Commercial | 0 | 4 | 0.0% | 7.8 |
| `best wailua river kayak tour` | Commercial | 0 | 2 | 0.0% | 71.0 |

---

### Rentals > Paddleboard

- Queries: **16** | Clicks: **10** | Impr: **386** | Avg Pos: **27.3**

| Query | Intent | Clicks | Impr | CTR | Pos |
|---|---|---:|---:|---:|---:|
| `kailua paddle board rental` | Transactional | 3 | 16 | 18.8% | 4.0 |
| `inflatable paddle board rental` | Transactional | 1 | 19 | 5.3% | 61.5 |
| `paddle board rental oahu` | Transactional | 1 | 184 | 0.5% | 14.6 |
| `paddle board rentals` | Transactional | 1 | 33 | 3.0% | 26.3 |
| `paddle boarding honolulu` | Mixed | 1 | 32 | 3.1% | 18.0 |
| `paddle boarding in oahu` | Mixed | 1 | 61 | 1.6% | 16.6 |
| `stand up paddle tour` | Mixed | 1 | 17 | 5.9% | 12.1 |
| `sup rental near me` | Transactional | 1 | 11 | 9.1% | 26.1 |
| `anahulu river paddle board` | Mixed | 0 | 3 | 0.0% | 68.3 |
| `beach paddle board` | Mixed | 0 | 1 | 0.0% | 10.0 |
| `best places to sup hawaii` | Commercial | 0 | 3 | 0.0% | 39.7 |
| `best places to sup near me` | Transactional | 0 | 2 | 0.0% | 12.0 |
| `best spot to paddle board near me` | Transactional | 0 | 1 | 0.0% | 8.0 |
| `blow up paddle board near me` | Transactional | 0 | 1 | 0.0% | 9.0 |
| `cheap paddle board rentals near me` | Transactional | 0 | 1 | 0.0% | 12.0 |

---



## Long-tail gold mine (970+ queries beyond top 30)

These are queries with **decent impressions but few clicks** = conversion optimization opportunities (better titles, better CTR, better landing pages).

### Top 30 under-performing queries (by impressions ÷ clicks)

- `electric beach oahu` — 2,458 impr, 2 clicks, 0.1% CTR, pos 8.6
- `kayak` — 2,283 impr, 2 clicks, 0.1% CTR, pos 7.0
- `lanikai beach` — 2,185 impr, 2 clicks, 0.1% CTR, pos 5.0
- `china mans hat` — 749 impr, 1 clicks, 0.1% CTR, pos 6.1
- `kailua beach` — 2,918 impr, 4 clicks, 0.1% CTR, pos 6.3
- `chinamans hat` — 2,096 impr, 3 clicks, 0.1% CTR, pos 6.3
- `sharks cove hawaii` — 670 impr, 1 clicks, 0.1% CTR, pos 6.0
- `kayaking` — 656 impr, 1 clicks, 0.2% CTR, pos 6.5
- `pupukea beach park` — 564 impr, 1 clicks, 0.2% CTR, pos 9.5
- `shark's cove` — 1,067 impr, 2 clicks, 0.2% CTR, pos 11.1
- `shark cove` — 1,258 impr, 3 clicks, 0.2% CTR, pos 6.0
- `lani kai beach` — 417 impr, 1 clicks, 0.2% CTR, pos 8.5
- `kaneohe bay kayaking` — 734 impr, 2 clicks, 0.3% CTR, pos 4.6
- `sharks cove` — 4,987 impr, 14 clicks, 0.3% CTR, pos 5.9
- `mokolii island` — 331 impr, 1 clicks, 0.3% CTR, pos 14.5
- `kailua island` — 297 impr, 1 clicks, 0.3% CTR, pos 3.5
- `mokulua islands` — 294 impr, 1 clicks, 0.3% CTR, pos 13.1
- `chinamans hat oahu` — 573 impr, 2 clicks, 0.3% CTR, pos 6.9
- `kailua beach park` — 2,853 impr, 10 clicks, 0.4% CTR, pos 9.7
- `popoia` — 275 impr, 1 clicks, 0.4% CTR, pos 4.3
- `kayak hawaii` — 235 impr, 1 clicks, 0.4% CTR, pos 6.6
- `kailua beach oahu` — 228 impr, 1 clicks, 0.4% CTR, pos 10.6
- `oahu north shore snorkeling` — 222 impr, 1 clicks, 0.5% CTR, pos 16.2
- `kayaking in hawaii` — 212 impr, 1 clicks, 0.5% CTR, pos 6.4
- `kayaking near me` — 601 impr, 3 clicks, 0.5% CTR, pos 7.4
- `china mans hat oahu` — 200 impr, 1 clicks, 0.5% CTR, pos 7.8
- `electric beach` — 5,935 impr, 30 clicks, 0.5% CTR, pos 6.5
- `lanikai beach tours` — 578 impr, 3 clicks, 0.5% CTR, pos 13.9
- `shark’s cove` — 540 impr, 3 clicks, 0.6% CTR, pos 7.0
- `kaneohe sandbar` — 1,134 impr, 7 clicks, 0.6% CTR, pos 12.8


### Striking-distance opportunities (position 4-15, ≥100 impressions)

These are queries where AOT is just outside page 1. Pushing these to top 3 = biggest wins.

| Query | Clicks | Impr | Pos | Potential if moved to #3 (assumes 10% CTR) |
|---|---:|---:|---:|---:|
| `electric beach` | 30 | 5,935 | 6.5 | +563 visits/mo |
| `sharks cove` | 14 | 4,987 | 5.9 | +484 visits/mo |
| `sharks cove oahu` | 51 | 4,800 | 4.2 | +429 visits/mo |
| `kailua beach` | 4 | 2,918 | 6.3 | +287 visits/mo |
| `kailua beach park` | 10 | 2,853 | 9.7 | +275 visits/mo |
| `electric beach oahu` | 2 | 2,458 | 8.6 | +243 visits/mo |
| `kayak` | 2 | 2,283 | 7.0 | +226 visits/mo |
| `lanikai beach` | 2 | 2,185 | 5.0 | +216 visits/mo |
| `sharks cove snorkeling` | 78 | 2,162 | 6.1 | +138 visits/mo |
| `chinamans hat` | 3 | 2,096 | 6.3 | +206 visits/mo |
| `shark cove` | 3 | 1,258 | 6.0 | +122 visits/mo |
| `kaneohe sandbar` | 7 | 1,134 | 12.8 | +106 visits/mo |
| `shark's cove` | 2 | 1,067 | 11.1 | +104 visits/mo |
| `kayaking oahu` | 23 | 1,014 | 8.3 | +78 visits/mo |
| `china mans hat` | 1 | 749 | 6.1 | +73 visits/mo |
| `kaneohe bay kayaking` | 2 | 734 | 4.6 | +71 visits/mo |
| `best places to kayak near me` | 0 | 705 | 9.8 | +70 visits/mo |
| `shark cove oahu` | 7 | 688 | 4.0 | +61 visits/mo |
| `sharks cove hawaii` | 1 | 670 | 6.0 | +66 visits/mo |
| `kayaking` | 1 | 656 | 6.5 | +64 visits/mo |
| `popoia island` | 4 | 642 | 8.8 | +60 visits/mo |
| `kayaking near me` | 3 | 601 | 7.4 | +57 visits/mo |
| `sharks cove oahu snorkeling` | 11 | 598 | 5.7 | +48 visits/mo |
| `shark cove snorkeling` | 18 | 588 | 4.5 | +40 visits/mo |
| `lanikai beach tours` | 3 | 578 | 13.9 | +54 visits/mo |
| `chinamans hat oahu` | 2 | 573 | 6.9 | +55 visits/mo |
| `pupukea beach park` | 1 | 564 | 9.5 | +55 visits/mo |
| `sharks cove snorkeling oahu` | 23 | 549 | 5.1 | +31 visits/mo |
| `shark’s cove` | 3 | 540 | 7.0 | +51 visits/mo |
| `lanikai beach snorkeling` | 4 | 515 | 6.6 | +47 visits/mo |


**Total potential**: moving these striking-distance queries to position 3 = **~5,545 additional monthly visits**.

---

## Modifier analysis (what people add to base keywords)

| Modifier | Query count | Example |
|---|---:|---|
| `rental` | 275 | "kailua kayak rental", "paddleboard rental oahu" |
| `near me` | 153 | "kayak rental near me", "snorkel rental near me" |
| `best` | 130 | "best oahu beaches", "best kayak rental kailua" |
| `tour` | 38 | "kayak tour kailua", "guided kayak tour oahu" |
| `cheap` / `affordable` | 23 | "cheap kayak rental oahu" |
| `review` | 9 | "kailua kayak rental reviews" |
| `beginner` / `easy` | 7 | "easy kayak tour oahu" |

**Optimization implications:**
- **`near me` (153 queries)**: Add Geo-Coordinates meta + LocalBusiness schema. Create /near-me/ pages.
- **`best` (130 queries)**: Build "Best X" comparison/curation pages for each cluster.
- **`cheap`/`affordable` (23 queries)**: Add "Affordable X" messaging on rental pages.
- **`beginner`/`easy` (7 queries)**: Add difficulty levels to tours + filter UI.
- **`review` (9 queries)**: Add review aggregation schema + testimonial section.

---

## Brand vs non-brand queries

| Type | Queries | Clicks | % of clicks |
|---|---:|---:|---:|
| Brand (contains "active oahu") | 3 | 260 | 19.1% |
| Non-brand | 997 | 1098 | 80.9% |

**Insight:** Brand queries are highly efficient (high CTR, position #1). Non-brand queries are the growth lever.

---

## What's still missing (research queue)

- [ ] **GA4 data** — Need conversion events to prioritize which keywords drive bookings (not just clicks)
- [ ] **Per-keyword SERP feature analysis** — Which queries trigger AI Overviews? PAA boxes? Local packs?
- [ ] **Competitor content gap analysis** — What does KBA, HBT, Surfnsea rank for that AOT doesn't?
- [ ] **Seasonal queries** — whale watching season (Dec-Apr), summer rentals, etc.
- [ ] **Japanese market expansion** — currently 3 queries, 117 impressions. Massive opportunity.
- [ ] **Voice-search patterns** — "near me", "open now", "for kids" — already partially captured

---

## How to use this inventory

### For Ella (content writer)
1. Find your target page in the **Cluster breakdown** above
2. Pick the top 5 queries (by clicks) for that page
3. Each query becomes either:
   - An `<h2>` heading (matches PAA capture format)
   - A 40-80 word paragraph (matches AEO citation format)
   - A FAQ schema entry (matches PAA box eligibility)

### For Kai-CSS (technical SEO)
1. For each page, ensure the top 3-5 queries are in:
   - Title (1x)
   - H1 (1x)
   - Meta description (1x)
   - At least 2 subheadings
   - URL slug (when possible)
   - Image alt text (primary images)

### For Kai (analytics + automation)
1. Track rank changes per cluster (not per keyword) — easier to interpret trends
2. When a cluster shows growth, escalate content production for that cluster
3. When a cluster stagnates, run SERP feature analysis to find new opportunities

### For AGY (research)
1. For each cluster, find 10-20 MORE keywords not in this list (broader long-tail)
2. Identify which competitor pages rank for cluster queries that AOT doesn't have pages for
3. Monitor seasonal keyword patterns
