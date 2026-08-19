---
type: Standards
title: Phase 6 — First Real Astro Page Cohort Plan
description: **Generated:** 2026-07-28 **Phase:** 6 of 8 **Status:** Planning
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/architecture/astro-emdash/header-footer/phase-6-cohort-plan.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Phase 6 — First Real Astro Page Cohort Plan

**Generated:** 2026-07-28
**Phase:** 6 of 8
**Status:** Planning

## Goal

Document the first 5 pages to adopt the Astro/emdash shell, with pre-build acceptance criteria, rollback paths, and content boundaries. No Astro implementation yet — this is the planning artifact.

---

## Cohort Pages

### 1. Homepage — `/`

| Field | Value |
|-------|-------|
| Source file | `site/index.html` |
| File size | 108,254 bytes / 1,913 lines |
| JSON-LD blocks | 3 |
| Canonical | `https://activeoahutours.com/` |
| FareHarbor refs | 9 |
| H1 | "Oahu Kayak & Gear Rentals Near Laie, Kahana, Kualoa &..." |
| Booking path | FareHarbor overlay + direct links |
| JA variant | `site/ja/index.html` |

**Lighthouse baseline (2026-07-28 verified):**
- Performance: 94 ✅ ← jumped from 73 after jQuery fixes (PR #128/#129/#130)
- Accessibility: 95 ✅
- Best Practices: 81 ✅
- SEO: 100 ✅

**Content boundaries:** Full homepage — hero, deals, activity grid, testimonials, footer. No WordPress widget areas (no dynamic sidebars, no blog excerpts, no recent posts).

**Schema to preserve:** LocalBusiness + Product + FAQPage JSON-LD. OG tags (og:title, og:description, og:image). Twitter card.

**Pre-build acceptance checks:**
- [ ] Lighthouse Perf baseline documented (73)
- [ ] Rollback: one-line DNS change + Cloudflare Pages re-deploy from current `main`
- [ ] All 9 FareHarbor links verified working on live
- [ ] JA variant homepage (`/ja/`) identified for parallel migration

---

### 2. Activity Tour Page — `/activities/chinamans-hat-self-guided-oahu-kayak-tour/`

| Field | Value |
|-------|-------|
| Source file | `site/activities/chinamans-hat-self-guided-oahu-kayak-tour/index.html` |
| File size | 93,769 bytes / 1,835 lines |
| JSON-LD blocks | 2 |
| Canonical | `https://activeoahutours.com/activities/chinamans-hat-self-guided-oahu-kayak-tour/` |
| FareHarbor refs | 11 |
| H1 | "Chinaman's Hat Self-Guided Kayak Tour" |
| Booking path | FareHarbor overlay + inline calendar trigger |

**Lighthouse baseline:**
- Performance: 93 ✅
- Accessibility: 91 ✅
- Best Practices: 54 ⚠️ LOW
- SEO: 92 ✅

**Why this page matters:** Highest-traffic activity page. If it converts well, the Astro shell pattern scales to all 40+ activity pages.

**Pre-build acceptance checks:**
- [ ] Best Practices 54 investigation — what's failing? (likely Cloudflare Rocket Loader + third-party)
- [ ] Lighthouse Perf baseline documented (93)
- [ ] Rollback: revert to static HTML from current `main`
- [ ] Booking overlay (`FH.open(...)`) verified working on live
- [ ] Content boundary: intro → itinerary → includes → location map → booking CTA. Excludes: related tours sidebar, blog excerpts.

**Known issues to fix in Astro migration:**
- BP=54 from Rocket Loader + deprecated APIs (not fixable in WordPress, should improve in Astro)

---

### 3. Rental Page — `/rentals/`

| Field | Value |
|-------|-------|
| Source file | `site/rentals/index.html` |
| File size | 87,968 bytes / 1,758 lines |
| JSON-LD blocks | 1 |
| Canonical | `https://activeoahutours.com/rentals/` |
| FareHarbor refs | 9 (includes direct iframe embeds) |
| H1 | "Oʻahu Beach Gear Rentals & Deliveries" |
| Booking path | Direct iframe calendar + FareHarbor overlay |

**Lighthouse baseline:**
- Performance: 99 ✅
- Accessibility: 94 ✅
- Best Practices: 73 ⚠️
- SEO: 100 ✅

**Why this page matters:** Revenue-critical. Highest Lighthouse performance score (99). If Astro can match P99, it's safe to scale.

**Content boundaries:** Rental categories grid, individual rental product sections, delivery info, FAQ accordion, direct iframe calendar embeds (2). Excludes: blog/news sections, unrelated rentals cross-sells.

**Pre-build acceptance checks:**
- [ ] Lighthouse Perf baseline documented (99)
- [ ] Rollback: static HTML revert from current `main`
- [ ] Direct FareHarbor iframe calendars verified working (2 iframes, `/rentals/`)
- [ ] FareHarbor overlay verified working on booking CTAs
- [ ] jQuery gallery (magnificPopup) verified — currently broken (JS errors), should be fixed by PR #128+#130 before Astro migration

---

### 4. Guide Page — `/guides/ocean-kayaking-beginners-oahu/`

| Field | Value |
|-------|-------|
| Source file | `site/guides/ocean-kayaking-beginners-oahu/index.html` |
| File size | 103,151 bytes / 1,921 lines |
| JSON-LD blocks | 2 |
| Canonical | `https://activeoahutours.com/guides/ocean-kayaking-beginners-oahu/` |
| FareHarbor refs | 7 |
| H1 | "Beginner's Guide to Ocean Kayaking on Oahu" |
| Booking path | CTA links to FareHarbor overlay |

**Lighthouse baseline:**
- Performance: 86 ✅
- Accessibility: 95 ✅
- Best Practices: 81 ✅
- SEO: 92 ✅

**Why this page matters:** Top organic content page. If Astro can preserve P86/A95 on a long-form guide, the platform is suitable for editorial content.

**Content boundaries:** Full guide content — intro, sections, tip boxes, related activity CTAs. Excludes: sidebar related posts, comment sections.

**Pre-build acceptance checks:**
- [ ] Lighthouse baseline documented (P86 A95 BP81 S92)
- [ ] Rollback: static HTML revert from current `main`
- [ ] Internal link count verified (guide has many contextual links to activity pages)
- [ ] Schema: Article/HowTo JSON-LD preserved

---

### 5. Japanese Homepage — `/ja/`

| Field | Value |
|-------|-------|
| Source file | `site/ja/index.html` |
| File size | 104,891 bytes / 1,523 lines |
| JSON-LD blocks | 3 |
| Canonical | None (no `<link rel="canonical">` found) |
| FareHarbor refs | 9 |
| H1 | "Oahu Kayak & Gear Rentals Near Laie, Kahana, Kualoa &..." (from OG) |
| Booking path | Same as English homepage |

**Lighthouse baseline:**
- Performance: 83 ✅
- Accessibility: 94 ✅
- Best Practices: 77 ⚠️
- SEO: 100 ✅

**Why this page matters:** Japanese market is a key audience. The Astro shell must support i18n routing (`/ja/` → `site/ja/`). Weglot language switching (retired per GRO-4139) needs replacement with proper hreflang switching.

**Content boundaries:** JA homepage mirror of EN homepage. JA activity pages in `site/ja/activities/`.

**Pre-build acceptance checks:**
- [ ] Lighthouse baseline documented (P83 A94 BP77 S100)
- [ ] Rollback: static HTML revert from current `main`
- [ ] hreflang tags verified on EN homepage pointing to JA variant
- [ ] Language switcher behavior documented (current mechanism)
- [ ] JA-specific schema ( TouristAttraction or TouristDestination)

**Known gap:** No canonical URL on JA homepage. This should be fixed in Astro migration:
```html
<link rel="canonical" href="https://activeoahutours.com/ja/" />
<link rel="alternate" hreflang="ja" href="https://activeoahutours.com/ja/" />
<link rel="alternate" hreflang="en" href="https://activeoahutours.com/" />
```

---

## Cross-Cutting Pre-Build Checklist

Before building any cohort page in Astro:

- [ ] Phase 5 QA (AGY) complete — sandbox shell passes all 8 checks
- [ ] Canonical shell data (`aot-shell-data.json`, `aot-nav.json`) verified against live header/footer for each cohort page
- [ ] FareHarbor shortname `activeoahutours` preserved in all booking CTAs
- [ ] `data-booking-event="booking_click"` analytics attribute preserved on all booking buttons
- [ ] Google Tag Manager container ID verified (from current committed HTML)
- [ ] WCAG AA color contrast verified on header/footer navigation
- [ ] Mobile nav breakpoint verified (current: 1024px — Astro shell must match)
- [ ] All 5 cohort pages have Lighthouse baseline scores documented above
- [ ] Rollback procedure documented for each page (Cloudflare Pages revert + DNS)

---

## Rollback Procedure

**For each cohort page, rollback is:**
1. Cloudflare Pages: `git revert HEAD` (if merged) or force-push previous commit
2. Cloudflare Pages auto-redeploys from `main` within ~60 seconds
3. Verify page loads with `curl -sSL https://activeoahutours.com/[path] | grep -c "jquery"` to confirm static HTML restored

---

## Open Questions

1. **Weglot removal (GRO-4139):** What's the current language-switching mechanism on `/ja/`? Need to verify hreflang handling before Astro i18n routing.
2. **Direct FareHarbor iframe calendars on `/rentals/`:** These are direct iframe embeds, not lazy-loaded. Astro should preserve these as static iframes or replace with the FareHarbor calendar web component.
3. **Homepage Performance 73:** Is the P73 on homepage due to image bloat, third-party scripts, or WordPress bloat? If image optimization, Astro's image pipeline should help.
4. **Activity page Best Practices 54:** Root cause likely Rocket Loader + Cloudflare challenge scripts. Should improve in Astro since we'll control the script loading.

---

## Next Step

After Phase 5 QA results come back from AGY, create Linear tasks for each cohort page (GRO-43XX series) with pre-build acceptance criteria from this document.
