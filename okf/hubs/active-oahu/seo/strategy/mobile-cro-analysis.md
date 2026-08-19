---
type: Analysis
title: Mobile CRO Analysis — 63% of AOT Traffic is Mobile
description: Mobile-first conversion analysis. GSC shows mobile=63% of AOT traffic but CTR is only 0.5% (vs desktop 0.4%). Identifying mobile-specific UX gaps + CRO opportunities.
tags: [mobile, cro, conversion, aot, ux, cta, performance]
timestamp: 2026-06-19T16:00:00Z
linear_issue: null
git_path: okf/strategy/mobile-cro-analysis.md
status: current
resource: okf/hubs/active-oahu/seo/strategy/mobile-cro-analysis.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Mobile CRO Analysis — 63% of AOT Traffic is Mobile

## GSC mobile data (last 90 days)

| Device | Clicks | Impr | CTR |
|---|---:|---:|---:|
| Mobile | 47 | 10,031 | 0.5% |
| Desktop | 25 | 5,772 | 0.4% |
| Tablet | 2 | 119 | 1.7% |

**Insight:** Mobile drives 63% of clicks. CTR is similar to desktop but absolute volume is much higher. **Mobile experience is the #1 conversion lever.**

## Current mobile issues (from existing GRO tickets + audits)

### Booking widget (FareHarbor) on mobile

Known issues:
- Widget loading delay (mitigated via GRO-1749: defer FH embed script)
- Mobile scroll-jacking when widget opens (partially mitigated)
- Cookie consent blockers interfering (work in progress)
- Date picker UX poor on small screens (known)

### Call-to-action

Known issues:
- Inline text CTAs that should be buttons (GRO-1539)
- "Book Online" button sometimes links directly instead of calling FH.open() (GRO-1750)
- Calendar document.write() replaced with lazy-loaded iframes (GRO-1748) ✅

### Page speed

- Cloudflare Pages auto-deploys but no measurement yet
- Image optimization likely needed (14,490 photos are mostly 4K+)

## Mobile UX audit checklist (per page)

For each top 20 revenue page:

- [ ] **Above the fold:** Hero image loads in <2s on 4G
- [ ] **CTA above fold:** "Book Online" button visible without scroll
- [ ] **CTA prominent:** Sticky bottom bar on mobile only
- [ ] **Tap targets:** All buttons ≥48x48px
- [ ] **Font size:** Body ≥16px, headings ≥20px
- [ ] **Form fields:** Single-column on mobile, autofill enabled
- [ ] **Date picker:** Native iOS/Android picker, not custom HTML
- [ ] **Map embed:** Lazy-loaded, tap-to-expand (no iframe in viewport)
- [ ] **Reviews widget:** Skeleton screens, not blank
- [ ] **Photo gallery:** Swipe gestures, not tiny arrows

## A/B test backlog (mobile-specific)

| Test | Hypothesis | Priority |
|---|---|---|
| **Sticky bottom CTA bar** | Bottom bar = +20% mobile conversion | P0 |
| **Hero text overlay with price** | Pricing in hero = +15% mobile CTR | P0 |
| **Phone number in header** | Tap-to-call = +10% mobile bookings | P0 |
| **One-page checkout** | Reduce steps = +25% completion | P1 |
| **Apple Pay / Google Pay** | Native payment = +30% mobile booking | P1 |
| **Tap-to-call tour guide** | Personal touch = +5% conversion | P2 |
| **WhatsApp chat widget** | High CTR in many markets | P2 |

## Page speed improvements (P0)

Actions:
1. Compress all images to WebP (8x smaller than JPEG)
2. Lazy-load below-fold images
3. Inline critical CSS
4. Defer non-critical JavaScript
5. Use Cloudflare's Polish (auto image optimization)

**Target:** PageSpeed Insights mobile score ≥80 for all top 10 revenue pages.

## Mobile-specific schema

```json
{
  "@context": "https://schema.org",
  "@type": "MobileApplication",
  "url": "https://activeoahutours.com",
  "operatingSystem": "WEB"
}
```

(Actually schema doesn't help mobile much, but worth noting.)

## Phone call attribution

Many mobile visitors prefer to call instead of booking online. Set up:
- **Dynamic Number Insertion (DNI)** — show different phone per source
- **CallRail or Invoca** integration (~$50/mo)
- Track which organic keywords drive phone calls

This captures the "tap to call" mobile audience.

## Success metrics

| Metric | Baseline | Target (6 months) |
|---|---:|---:|
| Mobile CTR | 0.5% | 1.0% |
| Mobile bookings (from analytics) | unknown | establish +30% lift |
| PageSpeed mobile score (top 10) | unknown | ≥80 |
| Mobile phone calls tracked | 0 | 30% of bookings |

---

*Analysis authored by Kai on 2026-06-19 based on GSC device data.*
