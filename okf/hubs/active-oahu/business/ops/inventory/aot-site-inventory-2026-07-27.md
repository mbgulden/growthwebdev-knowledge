---
type: Operations
title: Active Oahu Tours — Site-Wide Content & SEO Inventory
description: **Generated:** 2026-07-27 | **Scope:** 306 HTML files (EN + JA)
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/ops/inventory/aot-site-inventory-2026-07-27.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Tours — Site-Wide Content & SEO Inventory
**Generated:** 2026-07-27 | **Scope:** 306 HTML files (EN + JA)

---

## Executive Summary

| Metric | Total | Notes |
|--------|-------|-------|
| Total pages | 306 | EN + JA |
| Pages scanned | 306 | 100% |
| CRIT-01: Booking iframe | ✅ Done | rentals/index.html |
| CRIT-02: target=_blank removed | ✅ Done | 267 links |
| CRIT-03: H5→H3 hierarchy | ✅ Done | 0 H5s remaining |
| HIGH-01: Schema `openingHours` | ✅ Done | |
| HIGH-02: Alt text (filename-style) | ✅ Done | 88 files |
| HIGH-03: TripAdvisor badge | ✅ Done | 162 pages |
| HIGH-04: /adventure-guide/ redirect | ✅ Done | 301→/activities/ |
| HIGH-05: Meta keywords | ✅ Done | 38 pages |
| HIGH-06: Japanese hreflang | ✅ Done | 9 pages |

---

## Priority Issues Found

### 🔴 HIGH: Meta Descriptions Missing (7 pages)
These pages have NO meta description at all:

| Page | Type | Size | Action |
|------|------|------|--------|
| `about-active-oahu-tours/awards/.../index.html` | awards | 81KB | Needs description |
| `ja/404.html` | JA | 65KB | Needs description |
| `adventure-guide/index.html` | other | 438B | Redirect page — low priority |
| `chinamans-hat-kayak-tour/index.html` | other | 1.4KB | Redirect target |
| `kaneohe-bay-sandbar-kayak/index.html` | other | 1.4KB | Redirect target |
| `stand-up-paddleboard-rental/index.html` | other | 2.3KB | Redirect target |
| `wp-content/themes/.../kayakers.html` | template | 36KB | Not user-facing |

**Action:** Add meta descriptions to top 4–5 real pages.

---

### 🟡 MEDIUM: Short Meta Descriptions (128 pages)
Pages with descriptions under ~120 chars. Breakdown by type:
- JA pages: 57 (mostly Japanese content — requires translation)
- Rentals pages: 34 (inventory-style pages)
- Activity pages: 17 (some may be intentionally brief)
- Other: 16
- Guide pages: 4

---

### 🟡 MEDIUM: Meta Keywords Missing (268 pages)
Meta keywords are NOT a Google ranking factor but help with internal search and disambiguation.

| Type | Count | HIGH-05 Coverage |
|------|-------|-----------------|
| Activity pages | 2 | Need to check which 2 |
| Guide pages | 14 | Not covered |
| Other | 94 | Not covered |
| JA pages | 91 | Not covered (would need JA keywords) |
| Rentals | 67 | Not covered |

**Action:** Add meta keywords to guide + remaining activity pages.

---

### 🟡 MEDIUM: 9 Activity Pages Without hreflang (NO JA counterpart)
These pages have no Japanese version — adding hreflang would be invalid:

| Page |
|------|
| `activities/couples-romantic-kayak-tour/index.html` |
| `activities/family-kayak-picnic-combo/index.html` |
| `activities/guided-efoil-experience/index.html` |
| `activities/guided-kayak-fishing/index.html` |
| `activities/guided-scubajet-experience/index.html` |
| `activities/kayak-snorkel-hike-adventure/index.html` |
| `activities/oahu-sunset-kayak-tour/index.html` |
| `activities/rainforest-oahu-kayak-tour.html` |
| `activities/turtle-watching-kayak-tour/index.html` |

**Action:** Create JA counterparts OR use `hreflang="x-default"` — requires business decision.

---

### 🟡 MEDIUM: Activity Page Without FareHarbor (1 page)
| Page | Issue |
|------|-------|
| `activities/oahu-snorkel-tour/index.html` | No booking link — verify if intentional |

---

### ✅ VERIFIED GOOD
- Heading hierarchy: 0 H5s remaining, all headings clean
- Trust badges: 162 pages have TripAdvisor badge
- FareHarbor: All activity/rentals pages except 1 have booking links
- Canonical URLs: Present on all major pages
- Schema types: Organization, TravelAgency, WebSite present on homepage

---

## Page Type Breakdown

| Type | Count |
|------|-------|
| Other | 95 |
| JA (Japanese) | 91 |
| Activity pages (EN) | 38 |
| Rentals pages | 68 |
| Guide pages (EN) | 14 |

---

## Recommendations (Prioritized)

1. **[HIGH]** Fix 7 pages missing meta descriptions (especially awards page)
2. **[HIGH]** Investigate `oahu-snorkel-tour` missing FareHarbor link
3. **[MEDIUM]** Expand meta keywords to guide pages + remaining 2 activity pages
4. **[MEDIUM]** Address 9 hreflang gaps (business decision: create JA or use x-default)
5. **[LOW]** Expand meta keywords to other/utility pages
6. **[LOW]** Review short meta descriptions on rentals pages (34 pages)

---

*Inventory generated from: `/home/ubuntu/work/active-oahu-tours-mirror/site/`*
*Full CSV: `/tmp/aot_inventory/inventory.csv`*
*Full JSON: `/tmp/aot_inventory/full_inventory.json`*
