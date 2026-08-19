---
type: Operations
title: Active Oahu Business — Decisions & Strategy Log
description: This log documents durable decisions regarding Active Oahu Tours business strategy, hosting vendors, Cloudflare configuration, analytics integration, and FareHarbor bookings setup.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/decisions/decision-log.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Business — Decisions & Strategy Log

This log documents durable decisions regarding Active Oahu Tours business strategy, hosting vendors, Cloudflare configuration, analytics integration, and FareHarbor bookings setup.

---

## 1. Strategy Decisions

### weekly Operating Cadence (Golden Path Transition)
- **Date:** 2026-07-09  
- **Decision:** Transition from floating task queues to a structured weekly operating cadence tying Pull Requests, Linear tickets, Google Search Console, Ubersuggest competitor metrics, Lighthouse audits, and deployment smoke tests.
- **Rationale:** Floating task assignments created priority drift and missed opportunities. Aligning these elements weekly ensures incremental improvements compound over time.
- **Action Plan:** Implement GSC query watchlists and competitor monitoring fallbacks, running Lighthouse thresholds on every pull request.

---

## 2. Vendor & Infrastructure Decisions

### Cloudflare Pages Hosting Migration
- **Date:** 2026-07-03  
- **Decision:** Migrate production website hosting from legacy WordPress hosting (Flywheel staging/mirror) to Cloudflare Pages serving a compiled static mirror.
- **Rationale:** Compiling the site to static HTML pages delivers a 10x improvement in load speed, guarantees 100% uptime, and eliminates WordPress maintenance overhead and security vulnerabilities.
- **Implementation:** Serves content from the `/site` directory of the repository via Cloudflare edge CDN.

### DNS Transition to Cloudflare Pages
- **Date:** 2026-07-07  
- **Decision:** Update primary domain `activeoahutours.com` DNS records to point directly to Cloudflare Pages edge endpoints.
- **Rationale:** Legacy staging redirects and caching issues caused inconsistencies between staging and production. Pointing DNS directly to the Cloudflare Pages repo boundary resolves these conflicts and enables staging previews on pull requests.
- **Action Item:** Tracked in Linear task `GRO-3413`.

---

## 3. Analytics Integration Decisions

### Google Analytics 4 (GA4) Tracking
- **Date:** 2026-06-28  
- **Decision:** Implement custom gtag.js tracking to log click events on booking CTAs and funnel conversions to GA4.
- **Rationale:** Basic page-view tracking failed to capture booking friction. Logging CTA button clicks separates landing page engagement from third-party checkout exits.
- **Privacy Compliance:** Anonymize IP addresses and restrict PII sharing.

---

## 4. FareHarbor Integration Decisions

### Replacement of Inline Text Booking Links
- **Date:** 2026-06-13  
- **Decision:** Systematically replace weak inline text booking links within guide articles with styled, high-visibility CTA buttons linked to FareHarbor booking widgets.
- **Rationale:** Inline text links like "Book your kayak rental here" had a CTR below 0.5% and was visually indistinguishable from background content. Re-styling these as buttons (background: `#006699`, border-radius: `4px`) improves visual hierarchy and conversion rate.
- **Verification:** Audited under `GRO-1539` and validated with 8 high-priority targets.
