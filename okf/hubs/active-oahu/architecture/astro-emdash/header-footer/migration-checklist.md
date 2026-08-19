---
type: Standards
title: Header/footer Astro migration checklist
description: Migrated AOT doc from architecture/astro-emdash/header-footer/migration-checklist.md.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/architecture/astro-emdash/header-footer/migration-checklist.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Header/footer Astro migration checklist

## User-first checks

- [ ] Header logo links home.
- [ ] Phone number is visible and tappable.
- [ ] Book Online remains visible in the utility bar.
- [ ] Primary nav is keyboard accessible.
- [ ] Mobile nav opens once, closes once, and does not overlap submenus.
- [ ] Third-level Rentals → Kayak Rentals children are visible and readable.

## Search-engine checks

- [ ] Header uses `header`/`nav` landmarks.
- [ ] Footer uses `footer`/contentinfo landmark.
- [ ] Main content sits in one `main` landmark between header and footer.
- [ ] All nav/footer links are normal crawlable anchors.
- [ ] LocalBusiness NAP appears visibly and in JSON-LD.
- [ ] Breadcrumbs remain page-specific, not shell-global.

## AI/navigation checks

- [ ] `navTree` is the single source for rendered nav, SiteNavigationElement schema, and `/llms.txt` navigation summary.
- [ ] Every nav group has an intent and `aiSummary`.
- [ ] Footer support/legal/contact links are tagged separately from revenue links.

## Booking checks

- [ ] FareHarbor shortname remains `activeoahutours`.
- [ ] Current embed URL is preserved until a dedicated booking migration.
- [ ] `booking_click` instrumentation survives shell replacement.
- [ ] No shell component blocks FareHarbor modal launch.
