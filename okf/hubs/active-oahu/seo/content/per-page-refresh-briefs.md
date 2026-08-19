---
type: Reference
title: Per-Page Refresh Briefs (GSC-Priority)
description: Per-page refresh briefs prioritized by REAL Google Search Console data (not Ubersuggest estimates). Each brief specifies the page, current GSC stats, target keyword cluster, schema requirements, and CTA.
tags: [content-briefs, gsc-data, refresh, priority, aot, seo]
timestamp: 2026-06-19T15:43:33Z
linear_issue: null
git_path: okf/content/per-page-refresh-briefs.md
status: current
resource: okf/hubs/active-oahu/seo/content/per-page-refresh-briefs.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Per-Page Refresh Briefs (GSC-Priority)

Per-page briefs for refreshing existing AOT pages. Priority ordered by **real GSC traffic data** (not Ubersuggest estimates).

**Total briefs:** 20 top-page refreshes + 6 new pillar pages (separate file: `brief-registry.md`).

## How priority is calculated

For each page, priority = `current_clicks × (position_gap_to_top3 × 0.2)`.

A page in position 6 with 500 clicks has higher priority than a page in position 4 with 50 clicks.

---

## Tier 1 — IMMEDIATE REFRESH (do in Week 1-2)

These pages have the highest clicks AND the closest path to top 3. Refreshing them = biggest immediate ROI.

### REFRESH-001: `/activities/sharks-cove-self-guided-snorkel/`

**GSC stats (90 days):**
- Clicks: **589** (AOT's #1 traffic page!)
- Impressions: 48,974
- CTR: 1.2%
- Position: 8.0

**Striking-distance queries this page ranks for:**
- `sharks cove snorkeling` (2,162 impr, pos 6.1)
- `sharks cove oahu` (4,800 impr, pos 4.2) ← CLOSEST TO TOP 3
- `sharks cove` (4,987 impr, pos 5.9)
- `shark cove snorkeling` (588 impr, pos 4.5)
- `shark's cove snorkeling` (304 impr, pos 5.1)
- `sharks cove snorkeling oahu` (549 impr, pos 5.1)
- `sharks cove snorkeling tour` (66 impr, pos 3.3) ← ALMOST THERE
- `snorkeling sharks cove` (211 impr, pos 5.7)

**Total potential at position 3:** ~1,000+ additional clicks/mo

**Refresh actions:**
1. Add FAQ schema with 6 Q&As (drives PAA + AI Overview capture)
2. Add AEO block (40-80 word direct answer at top)
3. Add HowTo schema with steps
4. Refresh photos (Sharks Cove has dedicated subfolder in Synology)
5. Update title tag to include "sharks cove oahu"
6. Update meta description for higher CTR
7. Add customer reviews with photos
8. Internal links to /guides/best-snorkeling-on-oahu/ + /faq/

**Success criteria:** Move from pos 8 → pos 3 within 4 weeks

### REFRESH-002: `/oahu-equipment-rentals/chinamans-hat-kayak-rentals/`

**GSC stats:**
- Clicks: 469
- Impressions: 6,571
- CTR: 7.1%
- Position: 12.0

**Refresh actions:**
1. Push from pos 12 → top 3 (huge CTR win, currently 7.1% which is GREAT for pos 12)
2. Title tag optimization (currently probably too generic)
3. FAQ schema
4. Photo refresh

### REFRESH-003: `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/`

**GSC stats:**
- Clicks: 387
- Impressions: 10,162
- CTR: 3.8%
- Position: 14.0

**Striking-distance queries:**
- `kaneohe sandbar kayak` (294 impr, pos 5.2)
- `kayak to kaneohe sandbar` (69 impr, pos 3.2)
- `kaneohe sandbar kayak rental` (288 impr, pos 4.6)
- `kaneohe bay kayak rental` (150 impr, pos 11.1)

**Refresh actions:**
1. Push from pos 14 → top 3 (big jump possible)
2. Kanohe-specific FAQ schema
3. HowTo schema for the kayak route
4. AEO block with operator voice

### REFRESH-004: `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/`

**GSC stats:**
- Clicks: 155
- Impressions: 9,648
- CTR: 1.6%
- Position: 11.1

**Striking-distance queries:**
- `kayak rental oahu` (291 impr, pos 13.1)
- `kailua beach kayak` (149 impr, pos 11.0)
- `kayak rental kailua` (205 impr, pos 7.8)
- `kayak rentals kailua` (98 impr, pos 8.9)

**Refresh actions:**
1. Push from pos 11 → top 3
2. Add competitor comparison (vs KBA)
3. 134B Hamakua Dr. storefront callout
4. FAQ schema

### REFRESH-005: `/rentals/oahu-beach-chair-rentals/`

**GSC stats:**
- Clicks: 142
- Impressions: 6,311
- CTR: 2.3%
- Position: 14.1

**Refresh actions:**
1. Push from pos 14 → top 5
2. Add product schema with all chair variants
3. Comparison table (beach chair vs umbrella vs tent)
4. LocalBusiness schema

### REFRESH-006: `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-self-guided-kayak-tour/`

**GSC stats:**
- Clicks: 115
- Impressions: 7,348
- CTR: 1.6%
- Position: 7.6

**Note:** TWO Kanohe Sandbar pages exist. Consider consolidating to one canonical URL.

### REFRESH-007: `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/`

**GSC stats:**
- Clicks: 96
- Impressions: 5,943
- CTR: 1.6%
- Position: 21.2

**Striking-distance queries:**
- (Very few — this page is NOT striking distance for many queries)

**Refresh actions:**
1. Massive content refresh needed (pos 21 is way off)
2. Add SUP-specific FAQ
3. SUP technique content (beginner-friendly)
4. AEO block

### REFRESH-008: `/rentals/kailua-beach-bike-rentals/`

**GSC stats:**
- Clicks: 90
- Impressions: 2,746
- CTR: 3.3%
- Position: 13.6

**Refresh actions:**
1. E-bike emphasis (this is e-bike, not regular bike)
2. Push from pos 13 → top 5
3. Comparison with pedal bikes

### REFRESH-009: `/activities/kahana-rainforest-river-oahu-kayak-tour/`

**GSC stats:**
- Clicks: 84
- Impressions: 3,949
- CTR: 2.1%
- Position: 15.5

**Refresh actions:**
1. River-specific FAQ
2. Wildlife content (Kahana Valley has native flora/fauna)
3. AEO block

### REFRESH-010: `/rentals/oahu-life-vest-rentals/`

**GSC stats:**
- Clicks: 80
- Impressions: 1,869
- CTR: 4.3%
- Position: 7.0

**Refresh actions:**
1. Push from pos 7 → top 3
2. Safety-focused content
3. Bundle with other rental pages

### REFRESH-011: `/oahu-kayaking-and-beach-adventures/discover-oahus-best-snorkel-spot-at-electric-beach/`

**GSC stats:**
- Clicks: 71
- Impressions: 14,267
- CTR: 0.5%
- Position: 7.2

**Striking-distance queries:**
- `electric beach` (5,935 impr, pos 6.5) ← HUGE volume, push to top 3

**Refresh actions:**
1. CRITICAL: Page is at pos 7 with 14,267 impressions! Push to top 3 = +200-300 clicks/mo
2. AEO block (why Electric Beach is special)
3. FAQ schema
4. New photos

### REFRESH-012: `/rentals/cruiser-oahu-beach-equipment-rental-package/`

**GSC stats:**
- Clicks: 65
- Impressions: 4,275
- CTR: 1.5%
- Position: 11.5

**Refresh actions:**
1. Bundle package details
2. Push from pos 11 → top 5
3. Photo gallery of full setup

### REFRESH-013: `/rentals/oahu-beach-umbrella-rentals/`

**GSC stats:**
- Clicks: 65
- Impressions: 3,533
- CTR: 1.8%
- Position: 17.3

**Refresh actions:**
1. Push from pos 17 → top 5
2. UV protection content
3. Family/group bundle

### REFRESH-014: `/activities/chinamans-hat-oahu-kayak-tours/`

**GSC stats:**
- Clicks: 57
- Impressions: 2,287
- CTR: 2.5%
- Position: 13.1

**Striking-distance queries:**
- `chinamans hat kayak rental` (123 impr, pos 23.4) — push to top 5
- `kayak to chinamans hat` (87 impr, pos 14.7)
- `chinamans hat kayak` (34 impr, pos 1.1) ← DEFEND

**Refresh actions:**
1. Critical: AOT is #1 for `chinamans hat kayak` (defend it)
2. Push `chinamans hat kayak rental` from pos 23 → top 5
3. FAQ schema

### REFRESH-015: `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/`

**GSC stats:**
- Clicks: 53
- Impressions: 3,955
- CTR: 1.3%
- Position: 16.3

**Striking-distance queries:**
- `mokolii island kayak` (47 impr, pos 18.9) — push to top 5

**Refresh actions:**
1. Push from pos 16 → top 5
2. Mokulua-specific FAQ
3. Wildlife content

### REFRESH-016: `/rentals/oahu-snorkel-mask-and-fin-rentals/`

**GSC stats:**
- Clicks: 49
- Impressions: 4,914
- CTR: 1.0%
- Position: 13.3

**Refresh actions:**
1. Push from pos 13 → top 5
2. Gear comparison (mask-only vs full set)
3. AEO block

### REFRESH-017: `/ja/activities/sharks-cove-self-guided-snorkel/`

**GSC stats:**
- Clicks: 48
- Impressions: 1,290
- CTR: 3.7%
- Position: 6.0

**Refresh actions:**
1. Japanese FAQ schema
2. Push to top 3 (already strong in Japan)
3. See japanese-market-deep-dive.md for full plan

### REFRESH-018: `/oahu-kayaking-and-beach-adventures/ultimate-guide-to-lanikai-beach/`

**GSC stats:**
- Clicks: 48
- Impressions: 9,491
- CTR: 0.5%
- Position: 8.3

**Striking-distance queries:**
- `lanikai beach kayak rental` (probably significant)
- `lanikai beach oahu` (high volume)

**Refresh actions:**
1. Push from pos 8 → top 3
2. **Consider replacing with full Lanikai Pillar** (4,000 words)
3. AEO block with Lanikai visitor info

### REFRESH-019: `/` (homepage)

**GSC stats:**
- Clicks: 402
- Impressions: 22,460
- CTR: 1.8%
- Position: 9.7

**Refresh actions:**
1. Critical: Homepage at pos 9.7 for `activeoahutours.com` queries — should be #1!
2. Improve title + meta
3. Add LocalBusiness schema
4. Verify brand SERP features

### REFRESH-020: `/` (root www variant)

**GSC stats:**
- Clicks: 495
- Impressions: 9,508
- CTR: 5.2%
- Position: 4.8

**Refresh actions:**
1. Should be #1 for brand queries (verify redirect)
2. Verify canonical URL
3. Submit to Search Console as preferred domain

---

## Per-query striking-distance list (top 30)

These queries are NOT yet assigned to pages. Need brief-by-query analysis to determine target.

| Query | Impr | Pos | Likely target page |
|---|---:|---:|---|
| `electric beach` | 5,935 | 6.5 | `/guides/best-snorkeling-on-oahu/` |
| `sharks cove` | 4,987 | 5.9 | `/activities/sharks-cove-self-guided-snorkel/` |
| `sharks cove oahu` | 4,800 | 4.2 | `/activities/sharks-cove-self-guided-snorkel/` |
| `kailua beach` | 2,918 | 6.3 | `/guides/best-snorkeling-on-oahu/` |
| `kailua beach park` | 2,853 | 9.7 | `/guides/best-snorkeling-on-oahu/` |
| `electric beach oahu` | 2,458 | 8.6 | `/guides/best-snorkeling-on-oahu/` |
| `kayak` | 2,283 | 7.0 | `TBD` |
| `lanikai beach` | 2,185 | 5.0 | `/guides/best-snorkeling-on-oahu/` |
| `sharks cove snorkeling` | 2,162 | 6.1 | `/activities/sharks-cove-self-guided-snorkel/` |
| `chinamans hat` | 2,096 | 6.3 | `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` |
| `shark cove` | 1,258 | 6.0 | `/activities/sharks-cove-self-guided-snorkel/` |
| `kaneohe sandbar` | 1,134 | 12.8 | `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` |
| `shark's cove` | 1,067 | 11.1 | `/activities/sharks-cove-self-guided-snorkel/` |
| `kayaking oahu` | 1,014 | 8.3 | `TBD` |
| `china mans hat` | 749 | 6.1 | `TBD` |
| `kaneohe bay kayaking` | 734 | 4.6 | `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` |
| `best places to kayak near me` | 705 | 9.8 | `TBD` |
| `shark cove oahu` | 688 | 4.0 | `/activities/sharks-cove-self-guided-snorkel/` |
| `sharks cove hawaii` | 670 | 6.0 | `/activities/sharks-cove-self-guided-snorkel/` |
| `kayaking` | 656 | 6.5 | `TBD` |
| `popoia island` | 642 | 8.8 | `TBD` |
| `kayaking near me` | 601 | 7.4 | `TBD` |
| `sharks cove oahu snorkeling` | 598 | 5.7 | `/activities/sharks-cove-self-guided-snorkel/` |
| `shark cove snorkeling` | 588 | 4.5 | `/activities/sharks-cove-self-guided-snorkel/` |
| `lanikai beach tours` | 578 | 13.9 | `/guides/best-snorkeling-on-oahu/` |
| `chinamans hat oahu` | 573 | 6.9 | `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` |
| `pupukea beach park` | 564 | 9.5 | `/guides/best-snorkeling-on-oahu/` |
| `sharks cove snorkeling oahu` | 549 | 5.1 | `/activities/sharks-cove-self-guided-snorkel/` |
| `shark’s cove` | 540 | 7.0 | `/activities/sharks-cove-self-guided-snorkel/` |
| `lanikai beach snorkeling` | 515 | 6.6 | `/guides/best-snorkeling-on-oahu/` |


---

## Per-page refresh checklist

For each Tier 1 refresh:

- [ ] Review current page content (Kai)
- [ ] Check schema validity (Kai-CSS)
- [ ] Identify top 3 striking-distance queries for that page
- [ ] Refresh content per brief (Ella)
- [ ] Add FAQPage schema with page-relevant Q&As (Kai-CSS)
- [ ] Add AEO block (40-80 word direct answer) (Ella)
- [ ] Add internal links to/from 3-5 related pages (Kai-CSS)
- [ ] Deploy to Cloudflare Pages (Kai-CSS)
- [ ] Verify schema validates (Kai)
- [ ] Re-pull GSC for that page in 7 days (Kai)
- [ ] Report position change in weekly digest (Kai)
