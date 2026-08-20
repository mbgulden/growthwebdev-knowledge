# AOT Booking Conversion Sprint Notes — 2026-07-09

Use this as a pattern after Clean Board and Clean Site Foundation are complete and the Golden Thread moves into Booking & Mobile Conversion.

## Sequence that worked

1. **Start with the open instrumentation PR**
   - Review the PR live with:
     - `gh pr view <n> --repo mbgulden/active-oahu-tours-mirror --json number,title,state,isDraft,mergeable,mergeStateStatus,statusCheckRollup,files,commits,comments,reviews,url,headRefName,baseRefName`
   - Confirm it is not draft, `MERGEABLE`, `CLEAN`, and all checks are `SUCCESS` before merging.
   - Inspect changed files, especially any bulk HTML injection script and shared JS assets.

2. **Verify booking instrumentation before merge**
   - Create a focused `/tmp/hermes-verify-*` script.
   - Verify the instrumentation JS includes the durable browser-side signals:
     - `booking_click`
     - `booking_complete`
     - `window.gtag`
     - `window.FH.open`
     - `fareharbor_item`
     - `cta_source`
     - `__aotBookingAnalyticsInit`
   - Count booking-surface pages: pages with `fareharbor.com/embeds/book` or `FH.open`.
   - Confirm every booking-surface page has at least one tracking path:
     - loader marker / `/assets/js/aot-booking-analytics.js`, or
     - existing inline `booking_click` tracking.
   - Run `python3 -m py_compile scripts/inject_booking_analytics.py`.
   - Re-run `scripts/inject_booking_analytics.py` and assert idempotency: it should inject `0` more pages and leave `git status --short` clean.
   - Do not require every representative page to have the new loader if it already has inline `booking_click`; treat loader OR inline tracking as covered.

3. **Merge and verify production**
   - Merge only after green PR checks and ad-hoc verification.
   - Verify Cloudflare Pages production deployment by commit hash and `latest_stage.status == success`.
   - Purge exact representative page URLs and the JS asset if production appears stale.
   - Re-fetch production and mirror with cache-busting query params.
   - Confirm representative booking pages return HTTP 200 and include the loader/marker where expected.
   - Confirm `/assets/js/aot-booking-analytics.js` returns HTTP 200 on production and mirror and contains `booking_click` + `window.FH.open`.

## Focused Lighthouse pass after instrumentation

After booking instrumentation lands, run a focused Lighthouse pass against:

- Homepage: `/`
- Commercial booking path: `/kayak-rentals/`
- Rental booking path: `/rentals/snorkel-gear-rentals/`
- Package booking path: `/multi-activity-adventure-packages/`

Run both:

- desktop preset
- mobile 390x844 emulation

Save artifacts under a durable report directory, e.g.:

```text
reports/golden-thread/gro-3646-lighthouse-YYYYMMDDTHHMMSSZ/
```

Include `summary.md` plus raw Lighthouse JSON/HTML artifacts.

Compare against AOT thresholds:

- Performance ≥ 70
- Accessibility ≥ 85
- Best Practices ≥ 80
- SEO ≥ 90

Close the Lighthouse-run task when the audit is complete, even if thresholds miss, **provided** follow-up remediation tasks are created with the exact evidence. Do not pretend a failed threshold passed.

## Follow-up task pattern from the 2026-07-09 run

When Lighthouse showed recurring misses, the right move was to create child tasks under the same Booking & Mobile Conversion parent:

1. **Best Practices / CSP-console remediation**
   - Best Practices was `50–54` across checked pages.
   - Primary causes were CSP-blocked Google Ads / Analytics endpoints, Chrome DevTools issues, Cloudflare challenge deprecation warnings, and FareHarbor third-party cookies.
   - Important nuance: repo `site/_headers` did not appear to be the source of the live CSP, so investigate Cloudflare/header config before patching repo headers.

2. **Booking-page accessibility remediation**
   - Accessibility misses included color contrast, link distinguishability, form labels, heading order, link names, and ARIA role structure.

3. **Mobile homepage performance remediation**
   - Mobile homepage performance was just under threshold; booking pages passed performance.
   - Likely opportunities: cache lifetime, image delivery, font display, LCP discovery, render-blocking requests, unused JS/CSS.

## Pitfalls

- Do not verify only that the injection script exists; verify coverage across all booking-surface pages.
- Do not fail a page merely because it lacks the new loader if it already has inline `booking_click` instrumentation.
- Do not merge instrumentation without an idempotency check; bulk injection scripts must be safe to rerun.
- Do not close a Lighthouse remediation task as “green” if thresholds miss. Close the run/audit task and create remediation tasks.
- Do not assume `site/_headers` controls the live CSP. Confirm the live header source through Cloudflare/site config before changing CSP.