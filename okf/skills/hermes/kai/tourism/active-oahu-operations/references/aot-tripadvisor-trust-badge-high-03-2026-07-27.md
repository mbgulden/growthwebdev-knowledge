# AOT HIGH-03: TripAdvisor Trust Badge — 2026-07-27

## Task
Add a compact TripAdvisor rating badge directly above every "Book Online" FareHarbor CTA across the AOT site for conversion trust.

## Badge Design
- Inline SVG TripAdvisor stars (5 stars, first 4 filled #34E0A1, 5th white/empty)
- Rating text: "4.8" in bold green
- Review count: "· 356 reviews" in gray
- Links to: `https://www.tripadvisor.com/Attraction_Review-g60659-d5079465-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html`
- Target: `_blank` + `rel="noopener"` (external link)
- CSS scoped to `.tripadvisor-inline-badge` to avoid collisions

## Implementation
`/tmp/fix_trust_signals.py` — Python script that:
1. Injects scoped CSS once per file (guarded by `tripadvisor-inline-badge` check)
2. Finds all `fareharbor.com/embeds/book` links with "Book Online" text
3. Injects badge HTML immediately before each matching `<a>` tag
4. Processes all 180+ EN pages (excludes `/ja/` and `/author/`)

## Results
- 162 badges across 161 pages
- PR #107 — merged to `origin/main`
- Live site: awaiting Cloudflare Pages async cache refresh

## Verification
```bash
# origin/main committed content (immediate)
git show origin/main:site/index.html | grep -c '<div class="tripadvisor-inline-badge">'
# expect: 5 (home page header + hero + other CTAs)

# Live site (may lag CF Pages deploy)
curl -sS https://activeoahutours.com/ | grep -c 'tripadvisor-inline-badge'
# expect: >0 when CF Pages deploy completes
```

## Key Pre-deployment Checks
1. **Verify current TripAdvisor rating** — scrape `https://www.tripadvisor.com/Attraction_Review-g60659-d5079465-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html` or check the reviews page on AOT to confirm the 356 / 4.8 figures are still accurate before hardcoding
2. **CSS collision check** — scope CSS with `.tripadvisor-inline-badge` prefix; verify no existing site styles target this class
3. **No double-injection** — guard with string check before adding CSS; count `<div class="tripadvisor-inline-badge">` (not total occurrences) after run
4. **Idempotence** — running the script twice should not double-inject; the CSS guard prevents this

## Schema Enhancement (HIGH-01 companion)
The TravelAgency schema in `site/index.html` and `site/_templates/head.html` was also updated in HIGH-01 (PR #105) to add `openingHoursSpecification`. These are complementary:
- HIGH-01: structured data / search appearance
- HIGH-03: conversion trust / booking confidence

Both were deployed together in the July 27 sprint.
