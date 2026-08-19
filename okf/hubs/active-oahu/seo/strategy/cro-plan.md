---
type: Standard
title: AOT Conversion-Rate Optimization Plan (CRO)
description: Strategy for converting more organic + paid traffic into bookings. Per-page conversion hypotheses, A/B testing framework, booking funnel analysis, and seasonal optimization tactics.
tags: [cro, conversion, aot, strategy, booking-funnel, ab-testing]
timestamp: 2026-06-19T14:00:00Z
linear_issue: null
git_path: okf/strategy/cro-plan.md
status: current
resource: okf/hubs/active-oahu/seo/strategy/cro-plan.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# AOT Conversion-Rate Optimization Plan (CRO)

## Goal

Convert a higher percentage of AOT website visitors into confirmed bookings on FareHarbor.

**Baseline assumption:** Current organic traffic is 1,345/mo. Booking conversion rate unknown (need GA4 data). Even at 2% conversion, that's ~27 bookings/mo from organic alone.

**Target:** 3-4% conversion rate = 40-54 bookings/mo from organic, doubling current baseline.

---

## Booking Funnel Analysis (to validate with GA4 once OAuth extended)

The current funnel:
```
Landing Page Visit
    ↓ (~70% bounce on bad pages)
"Book Online" CTA Click
    ↓
FareHarbor widget opens (FH.open())
    ↓
Widget interaction
    ↓
Date/time/party-size selection
    ↓
Customer info entry
    ↓
Payment
    ↓
Booking confirmed
```

**Known drop-off points** (from previous FareHarbor CTA friction audit GRO-1711):
- Mobile sticky CTA collision with FH widget loading
- Inline text CTAs that should be buttons (GRO-1539)
- "Book Online" button needs to call `FH.open()` not direct link (GRO-1750)
- Date picker UX issues on small screens

**Improvements already shipped:**
- ✅ GRO-1750 — header Book Online CTA now calls FH.open()
- ✅ GRO-1749 — defer FH embed script across all pages
- ✅ GRO-1748 — replace FH calendar document.write() with lazy-loaded iframes

---

## Per-Page CRO Hypotheses (top 5 revenue pages)

### Page 1: `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/`
**Current traffic:** 845 visits/mo (highest AOT page)

**Hypotheses:**
1. **H1 above-the-fold** — Currently generic. Try: "SUP Rental Kailua Bay — From $X/hr, Walk-in Daily"
2. **Hero image** — Currently lifestyle photo. Try: SUP rider in action with pricing overlay
3. **CTA button text** — Currently "Book Online". Try: "Reserve Your SUP →" (action + arrow)
4. **Pricing transparency** — Hide pricing behind "View Rates". Try: Inline pricing table visible above fold
5. **Trust signals** — Currently has reviews widget. Try: Add "As Featured In" press logos + cancellation policy near CTA

**Test priority:** P1 (high traffic, high potential impact)

### Page 2: `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/`
**Current SERP:** Position #2 for `kailua kayak rental` (46 clicks/mo)
**Conversion hypothesis:** Visitors ranking #2 are comparing to KBA. Need to differentiate on:
- Convenience (storefront location, 134B Hamakua Dr.)
- Pricing (match or beat)
- Trust (reviews, experience)
- Equipment quality photos

**Action:** Add an "Why Choose Us" section above fold with 3-4 bullet differentiators. Use the storefront photos from the photo library.

### Page 3: `/activities/sharks-cove-self-guided-snorkel/`
**Current SERP:** Position #3 for `sharks cove snorkeling` (124 clicks/mo)
**Conversion hypothesis:** The "self-guided" framing may be hurting vs. competitors offering "guided tours". Need to emphasize:
- Cost savings (no guide fee)
- Flexibility (go at your own pace)
- Gear quality (top brands)
- Safety (e.g., reef-safe sunscreen provided)

**Action:** Rewrite the value-prop section. Show side-by-side comparison "Guided tour ($150) vs. self-guided with us ($50 + gear)".

### Page 4: `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/`
**Current SERP:** Position #1 (best-performing AOT page)
**Conversion hypothesis:** Already winning. Don't break it. Focus on:
- Cross-sell (add "Add e-bike for $X" upsell)
- Repeat-customer incentives (return-visit discount)
- Photo gallery updates (fresh imagery from Synology library)

### Page 5: `/tours/` (guided tours landing)
**Current traffic:** estimated 100-200 visits/mo
**Conversion hypothesis:** Page is weak — needs stronger hero + e-bike adventure focus. E-bike rental is a high-margin product.

**Action:** Major refresh using new e-bike photography from Kailua Photos and Videos folder.

---

## A/B Testing Framework

### Tools available
- **Native HTML A/B testing** — manually duplicate pages, swap variants, measure with GA4
- **Cloudflare Workers** — if we want to add edge-side A/B testing later (more setup)

### Test cadence
- **1 test per week** during the first 3 months (rapid learning)
- **2 tests per month** once we have statistical power
- **Each test runs 2-4 weeks** for significance

### Test catalog template

For each test, document:
```yaml
test_id: CRO-001
name: "SUP page H1: generic vs pricing-included"
hypothesis: "Including specific pricing in H1 will increase conversion by 15%"
variant_a: "SUP Rentals in Kailua, Oahu" (control)
variant_b: "SUP Rental Kailua Bay — From $X/hr, Walk-in Daily"
primary_metric: Bookings / unique visitor
secondary_metrics: 
  - Bounce rate
  - Time on page
  - FH widget opens
minimum_sample_size: 500 unique visitors per variant
expected_lift: 15%
test_duration_days: 14
decision_criteria: 
  - Promote B if lift ≥10% with p<0.05
  - Continue test if <10% but trend positive
  - Kill test if any degradation
```

---

## Booking Funnel Optimization

### Stage 1: Click → Widget Open (current: ~80% of clicks successfully open widget)
**Issues:**
- FH widget loading delay
- Mobile scroll-jacking when widget opens
- Cookie consent blockers interfering

**Fixes (Kai-CSS):**
- Preload FH widget JS on hover (not click)
- Lazy-init widget only after consent given
- A/B test "sticky bottom bar" vs "inline CTA" for mobile

### Stage 2: Widget Open → Date/Time Selection (current: ~60%)
**Issues:**
- Calendar UI unfamiliar to first-time users
- Time slots not visible without scrolling
- "Today" / "Tomorrow" buttons missing

**Fixes (A/B test):**
- Add guided tour prompt: "First time? Click here for our most popular times"
- Show recommended time slots based on weather/season
- Highlight "Available now" if same-day slots open

### Stage 3: Date Selection → Customer Info (current: ~70%)
**Issues:**
- Form too long (12+ fields)
- Required phone + email before showing price
- No guest count optimization

**Fixes:**
- Reduce to 4 essential fields initially (date, party, name, email)
- Show price upfront based on date + party size
- Add "Continue as Guest" option (no account creation)

### Stage 4: Customer Info → Payment (current: ~50%)
**Issues:**
- Address form too long
- No payment method selector visible
- Cancellation policy unclear

**Fixes:**
- Add Apple Pay / Google Pay buttons (already in FH but need to highlight)
- Move cancellation policy to top of payment page
- Add trust badges (SSL, "10,000+ happy customers")

---

## Seasonal CRO Tactics

### Summer (Jun-Aug): peak season
- Increase ad spend on top-converting pages
- Add "Summer Special" banner to top 5 revenue pages
- Promote longer-duration tours (half-day, full-day)

### Fall (Sep-Nov): shoulder season
- Focus on local Hawaiian market (less tourist traffic)
- Promote "off-season" pricing
- Highlight cooler-weather activities (rainforest river kayaking)

### Winter (Dec-Feb): whale watching + holiday
- Add whale watching content
- Holiday gift certificates
- "Winter escape" packages

### Spring (Mar-May): recovery + spring break
- Promote beginner-friendly tours (intro to kayaking)
- Spring break family packages
- Easter/Passover promotions

---

## Phone Call Tracking

For visitors who don't book online but call instead, set up:
- Dynamic Number Insertion (DNI) — show different phone number per source
- CallRail or Invoca integration (~$50/mo)
- Track which organic keywords drive phone calls vs. online bookings

This gives a fuller picture of conversion attribution.

---

## Email Capture + Remarketing

For visitors who don't book on first visit:
- **Exit-intent popup** offering 10% off first booking
- **Sticky bar** at bottom of page with email signup for "Oahu adventure guide" PDF
- **Remarketing pixels** — Facebook, Google, TikTok for display ads

Build the email list to ~5,000 subscribers in Year 1 (estimated 1-2% conversion of organic traffic over time).

---

## Tracking & Attribution

### GA4 events to set up (once OAuth extended)
- `view_item` — page view on revenue pages
- `select_content` — CTA button click
- `begin_checkout` — FH widget open
- `add_payment_info` — payment step
- `purchase` — booking confirmed
- `generate_lead` — email signup

### Custom dimensions
- `device_category` — desktop/mobile/tablet
- `traffic_source` — organic/paid/direct/referral
- `landing_page_type` — homepage/tour-page/rental-page/guide-page

### Conversion attribution windows
- Last-click attribution: 30-day window
- First-click attribution: 30-day window
- Linear: 30-day window

Compare all three — they tell different stories about which keywords drive bookings.

---

## A/B Test Backlog (priority order)

| # | Test | Page | Hypothesis | Status |
|---|---|---|---|---|
| CRO-001 | H1 with pricing | SUP rental | Pricing in H1 → +15% conversion | Queued |
| CRO-002 | CTA button copy | Kailua kayak | "Reserve Now →" vs "Book Online" | Queued |
| CRO-003 | Hero image variant | Sharks Cove | Action shot vs landscape | Queued |
| CRO-004 | Pricing table visibility | SUP rental | Inline vs behind CTA | Queued |
| CRO-005 | Trust badges placement | All revenue pages | Below CTA vs in sidebar | Queued |
| CRO-006 | Exit-intent popup | All pages | 10% off offer → 5% email capture rate | Queued |
| CRO-007 | Sticky CTA bar | Mobile only | Bottom bar → +20% mobile conversions | Queued |
| CRO-008 | FAQ schema position | Top 10 pages | Above fold vs at bottom | Queued |
| CRO-009 | Video hero | Top 5 pages | Auto-play video → +10% engagement | Queued |
| CRO-010 | Personalization | Returning visitors | "Welcome back" banner → +25% repeat | Queued |

---

## Success criteria

**At end of 6 months (Dec 31, 2026):**
- Conversion rate: 3-4% (from unknown baseline)
- Bookings from organic: 40-55/mo (vs unknown baseline, likely ~15-25/mo)
- Email list: 5,000 subscribers (from unknown baseline)
- Average booking value: stable or +10% (via upsells)
- Phone calls tracked: 30% of bookings attributed (need DNI setup)

---

## Monthly CRO cadence

- **Week 1:** Run 2 A/B tests concurrently
- **Week 2:** Analyze results, kill/extend/promote
- **Week 3:** Launch 2 new tests
- **Week 4:** Monthly CRO report → Michael via Telegram

Reports at `okf/reports/cro-monthly-YYYY-MM.md`.
