---
type: Operations
title: AOT Site Gap Fix Plan — 2026-07-26
description: **Owner:** Kai, Orchestrator of Tourism **Date:** 2026-07-26 **Status:** Planned **Team:** GrowthWebDev (Linear workspace) **Labels:** `type:task`, `agent:kai`, `revenue`
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/ops/aot-site-gap-fix-plan-2026-07-26.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# AOT Site Gap Fix Plan — 2026-07-26

**Owner:** Kai, Orchestrator of Tourism  
**Date:** 2026-07-26  
**Status:** Planned  
**Team:** GrowthWebDev (Linear workspace)  
**Labels:** `type:task`, `agent:kai`, `revenue`

---

## Background

A comprehensive gap analysis of activeoahutours.com was conducted on 2026-07-26, combining browser audits, sitemap analysis, and page-level inspection. This plan captures the prioritized fix roadmap derived from that analysis.

**Scope exclusions (per Michael):**
- Items 1 & 2 from the original audit were dismissed — all tour cards have detail pages with "More Info" links, and mobile omission is intentional
- Item 1 (booking calendar fix) was deferred as Critical #2 since it affects revenue

---

## Task Map

| Linear | OkF Ref | Title | Priority | Agent | Notes |
|--------|---------|-------|----------|-------|-------|
| (create) | CRIT-01 | Fix broken booking calendar on /rentals/ | Critical | kai | FareHarbor embed code issue |
| (create) | CRIT-02 | Add booking CTA to guide pages | Critical | kai | Guide pages don't convert |
| (create) | CRIT-03 | Fix heading hierarchy (H1→H3→H4→H2) | Critical | kai | Accessibility + SEO |
| (create) | HIGH-01 | Add Organization + LocalBusiness schema | High | kai | Rich Results loss |
| (create) | HIGH-02 | Fix image alt text on tour cards | High | kai | Accessibility + SEO |
| (create) | HIGH-03 | Add trust signals near booking CTAs | High | kai | Conversion opportunity |
| (create) | HIGH-04 | Fix /adventure-guide/ 404 | High | kai | Dead nav destination |
| (create) | HIGH-05 | Add meta keywords to key pages | High | kai | SEO targeting gap |
| (create) | HIGH-06 | Fix Japanese hreflang (x-default + broken links) | High | kai | International SEO |
| (create) | MED-01 | Add x-default hreflang declaration | Medium | kai | Hreflang completeness |
| (create) | MED-02 | Fix broken links on Japanese tour pages | Medium | kai | Japanese UX |

---

## Critical Tasks

### CRIT-01: Fix broken booking calendar on /rentals/ page
**Problem:** "Load booking calendar" button spins forever — no booking possible for rentals visitors.  
**Evidence:** `/rentals/` — button never resolves  
**Fix:** Verify FareHarbor embed calendar ID against dashboard; check for JS errors blocking load  
**Verification:** Load `/rentals/` in browser → calendar renders without spinner  
**Repo:** `active-oahu-tours-mirror`  
**Files:** Likely `rentals/index.html`  

### CRIT-02: Add booking CTA to guide pages
**Problem:** Guide pages (Chinaman's Hat, Mokulua Islands, etc.) are excellent SEO content but convert at near-zero. One italic text line is the only booking nudge.  
**Evidence:** `/activities/chinamans-hat-kayak-complete-self-guided-tour-guide/` — single italic "Book your Chinaman's Hat kayak rental from our Kailua storefront" at bottom  
**Fix:** Add prominent "Book This Tour" button near top of each guide page. Consider sticky booking bar.  
**Scope:** All guide pages — Chinaman's Hat, Mokulua Islands, Kaneohe Sandbar, Kahana River  
**Verification:** Each guide page has visible booking CTA above the fold  
**Repo:** `active-oahu-tours-mirror`  

### CRIT-03: Fix heading hierarchy
**Problem:** H1→H3→H4→H2 pattern throughout — breaks WCAG accessibility and confuses search engines  
**Evidence:** Homepage deal banner is H4, tour cards jump around  
**Fix:** Enforce H1→H2→H3 cascade. Move "Deal: 15% Off Groups of 4+" to appropriate level (H2 or H3)  
**Scope:** Homepage, activities page, tour cards, key landing pages  
**Verification:** Lighthouse Accessibility score ≥ 85, heading audit passes  
**Repo:** `active-oahu-tours-mirror`  

---

## High Priority Tasks

### HIGH-01: Add Organization + LocalBusiness structured data
**Problem:** Zero structured data — losing Rich Results for business info, hours, ratings  
**Fix:** Add Organization schema + LocalBusiness schema with: name, url, logo, address (134B Hamakua Dr, Kailua HI 96734), phone ((808) 498-1894), hours, geo coordinates  
**Repo:** `active-oahu-tours-mirror` — likely `header.php` or equivalent template  

### HIGH-02: Fix image alt text on tour cards
**Problem:** `alt="kailua-lanikai-kayak-rental-mokes-oahu"` instead of descriptive text  
**Fix:** Replace filename alt text with 1-2 sentence descriptions of the activity shown  
**Scope:** All tour card images on `/activities/`  
**Repo:** `active-oahu-tours-mirror`  

### HIGH-03: Add trust signals near booking CTAs
**Problem:** No social proof at conversion points — reviews/ratings only on contact page  
**Fix:** Add TripAdvisor/Yelp rating badge near "Book Online" button in header. Add review counts to homepage hero area.  
**Repo:** `active-oahu-tours-mirror`  

### HIGH-04: Fix /adventure-guide/ 404
**Problem:** Nav item "Adventure Guide" → `/adventure-guide/` → 404  
**Fix:** Either create the page (content hub) or redirect to `/activities/`  
**Decision:** Recommend creating a lightweight hub page or redirecting to `/activities/`  
**Repo:** `active-oahu-tours-mirror`  

### HIGH-05: Add meta keywords to key pages
**Problem:** No meta keywords on any page — Bing and keyword targeting signal absent  
**Fix:** Add targeted commercial keywords per page: "Oahu kayak rental", "Kailua kayak tour", "Mokulua Islands", "Chinaman's Hat", "Kaneohe Bay"  
**Scope:** Tour pages, rentals page, homepage  
**Repo:** `active-oahu-tours-mirror`  

### HIGH-06: Fix Japanese hreflang
**Problem:** 94 Japanese locale pages — missing `x-default`, broken internal links on Japanese tour pages  
**Fix:** Add `x-default="https://activeoahutours.com/"` to all hreflang blocks. Audit and fix broken /ja/ internal links.  
**Scope:** All `/ja/` pages with hreflang  
**Repo:** `active-oahu-tours-mirror`  

---

## Medium Priority Tasks

### MED-01: Add x-default hreflang declaration
**Problem:** All locale pages missing `x-default` attribute in hreflang  
**Fix:** Add `x-default` for the default (English) version of each page  
**Repo:** `active-oahu-tours-mirror`  

### MED-02: Fix broken links on Japanese tour pages
**Problem:** Japanese Mokulua Islands page has a broken internal link  
**Fix:** Audit all `/ja/activity/` pages for broken internal links; fix or remove  
**Repo:** `active-oahu-tours-mirror`  

---

## Execution Notes

- **Repo target:** `mbgulden/active-oahu-tours-mirror` (public deploy mirror)
- **Staging:** Test on `staging.activeoahutours.com` before production deploy
- **Lighthouse targets:** Performance ≥ 70, Accessibility ≥ 85, Best Practices ≥ 80, SEO ≥ 90
- **Content (Ella):** Ella writes any new copy; Kai handles CSS/HTML/implementation
- **Review gate:** All PRs require browser verification on preview URL before merge

---

## Out of Scope

- FareHarbor checkout flow modifications (handled by FareHarbor directly)
- New tour page creation (existing structure sufficient)
- Japanese content translation (out for bid)
- Price changes (business decision, not implementation)
