---
type: Verification
title: GRO-3718 — Lighthouse Best Practices remediation
description: Resolve the remaining Best Practices blockers that were still visible after the safe CSP/font pass:
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/verification/gro-3718-remediation-20260710.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# GRO-3718 — Lighthouse Best Practices remediation

## Scope

Resolve the remaining Best Practices blockers that were still visible after the safe CSP/font pass:

- third-party cookies from TripAdvisor/FareHarbor/Google/Stripe
- Cloudflare challenge-platform deprecation noise
- page-level `TypeError: Line: 2, column: 1, Syntax error`

## Changes made

1. Removed stale static Cloudflare challenge snippets from the exported site.
   - Before: static files contained `285` references to `/cdn-cgi/challenge-platform/scripts/jsd/main.js` and `window.__CF$cv`.
   - After: `0` references remain in `.html`, `.php`, or `.js` files.

2. Deferred TripAdvisor widgets.
   - Replaced direct `https://www.jscache.com/wejs...` widget scripts with inert `data-aot-lazy-tripadvisor` placeholders.
   - Added `/assets/js/aot-lazy-tripadvisor.js` to load the widget only when the review widget nears the viewport or the visitor scrolls.
   - Booking clicks do not trigger TripAdvisor loading.

3. Removed hidden FareHarbor checkout prewarm.
   - The hidden `fareharbor-prewarm` iframe created third-party booking cookies before a visitor asked to book.
   - FareHarbor API/lightbox remains active for visible booking CTAs.

4. Removed empty `speculationrules` script tags.
   - These were the source of Chromium's `While parsing speculation rules: Line: 2, column: 1, Syntax error` warning and the matching page-level Playwright/Lighthouse TypeError.
   - Non-empty valid speculation rules were preserved.

5. Deferred remaining third-party cookie sources until visitor intent.
   - Replaced eager FareHarbor API loading with `/assets/js/aot-lazy-fareharbor.js`, which loads FareHarbor only after a booking CTA click and preserves item-specific `FH.open` calls.
   - Replaced eager FareHarbor calendar embeds with click-to-load placeholders plus `/assets/js/aot-lazy-fareharbor-calendar.js`.
   - Replaced eager Google Tag Manager / gtag loading with `/assets/js/aot-lazy-marketing.js`, which waits for a pointer/keyboard interaction before loading marketing tags.

## Verification

Focused static verification:

```text
prewarmFH: 0
fareharbor-prewarm: 0
__CF$cv: 0
/cdn-cgi/challenge-platform/scripts/jsd/main.js: 0
lazy TA placeholders: 79
lazy loader includes: 77
```

Syntax / diff hygiene:

```text
git diff --check: pass
python3 -m py_compile scripts/remediate_lighthouse_best_practices.py: pass
node --check site/assets/js/aot-lazy-tripadvisor.js: pass
```

Rendered console trace on `/kayak-rentals/`:

| Run | TripAdvisor initial request | FareHarbor prewarm request | Static CF challenge request | Page errors |
|---|---:|---:|---:|---:|
| Baseline | yes | yes | yes | `TypeError: Line: 2, column: 1, Syntax error` |
| After | no | no | no | none |

Booking CTA smoke test on `/kayak-rentals/` after remediation:

```json
{
  "before": {
    "fhReady": true,
    "tripAdvisorLoaded": 0,
    "prewarmIframes": 0
  },
  "after": {
    "overlays": 4,
    "spinnerPresent": true,
    "tripAdvisorLoaded": 0
  },
  "fareHarborRequestCount": 27
}
```

Focused local Lighthouse Best Practices rerun:

| Page | Baseline BP | After BP | Cookie finding |
|---|---:|---:|---|
| `/kayak-rentals/` | 54 | 54 | reduced from 6 cookies to 2 cookies |
| `/rentals/snorkel-gear-rentals/` | 54 | 54 | unchanged at 5 cookies |

Artifacts:

- `reports/golden-thread/gro-3718-lighthouse-final-20260710T093907Z/`
- `okf/verification/gro-3718-lighthouse-rebase-20260710T204317Z-kayak-rentals.best-practices.json`

## Rebase refresh — 2026-07-10 20:43Z

PR #77 was rebuilt on top of `origin/main` (`fc62696f4`) and the HTMLParser remediation was re-run against the current generated site export.

Refresh verification:

```text
python3 scripts/remediate_lighthouse_best_practices.py
changed_files=287
removed_cloudflare_challenge_snippets=285
deferred_tripadvisor_widgets=78

python3 -m py_compile scripts/remediate_lighthouse_best_practices.py: pass
node --check site/assets/js/aot-lazy-tripadvisor.js: pass
git diff --check: pass

static scan after refresh:
__CF$cv: 0
/cdn-cgi/challenge-platform/scripts/jsd/main.js: 0
prewarmFH: 0
fareharbor-prewarm: 0
empty speculationrules marker: 0
lazy TA placeholders: 79
lazy loader includes: 77

local Lighthouse, http://127.0.0.1:8787/kayak-rentals/:
Best Practices: 54
third-party-cookies: 2 cookies found
errors-in-console: 4 local 404 image requests only
Cloudflare deprecations: pass
```

## Intent-gated third-party refresh — 2026-07-10 21:39Z

Additional refresh after the rebase verification showed FareHarbor/Google cookies were still the only remaining Best Practices blockers on booking pages.

Static scan after the intent-gated loaders:

```text
prewarmFH: 0
fareharbor-prewarm: 0
__CF$cv: 0
/cdn-cgi/challenge-platform/scripts/jsd/main.js: 0
direct TripAdvisor jscache scripts: 0
eager FareHarbor API scripts: 0
eager FareHarbor calendar scripts: 0
eager gtag src scripts: 0
lazy TripAdvisor placeholders: 79
lazy FareHarbor calendar placeholders: 24
```

Rendered Playwright smoke test on `/kayak-rentals/`:

```json
{
  "initial": {
    "lazyTripAdvisorLoader": true,
    "lazyFareHarborLoader": true,
    "lazyMarketingLoader": true,
    "directTA": 0,
    "directFHApi": 0,
    "directGoogle": 0,
    "prewarmIframes": 0
  },
  "firstRequests": [],
  "afterClick": {
    "directFHApi": 1,
    "overlays": 8,
    "directTA": 0
  },
  "pageErrors": []
}
```

Focused local Lighthouse Best Practices rerun:

| Page | Before BP | After BP | Third-party cookies | Deprecations | Inspector cookie issues |
|---|---:|---:|---|---|---|
| `/kayak-rentals/` | 54 | 96 | pass, 0 items | pass | pass |
| `/rentals/snorkel-gear-rentals/` | 54 / 73 intermediate | 96 | pass, 0 items | pass | pass |

Artifacts:

- `okf/verification/gro-3718-lighthouse-lazy-20260710T213304Z-kayak-rentals.best-practices.json`
- `okf/verification/gro-3718-lighthouse-lazy-20260710T213850Z-snorkel.best-practices.json`

## Remaining caveat

The controllable Lighthouse Best Practices blockers are now resolved in focused local runs. The remaining caveat is product-side: marketing tags and FareHarbor calendars now load after visitor intent rather than at first paint, so production rollout should watch analytics pageview continuity and calendar conversion behavior after merge.
