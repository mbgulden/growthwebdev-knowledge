# AOT booking accessibility + third-party Best Practices sprint (2026-07-09)

## Context

Golden Path Booking & Mobile Conversion follow-up after booking instrumentation and Lighthouse passes:

- GRO-3666: booking-page accessibility misses.
- GRO-3718: remaining Lighthouse Best Practices blockers after safe CSP/font fixes.

## Booking-page accessibility remediation pattern

Target pages:

- `/kayak-rentals/`
- `/multi-activity-adventure-packages/`
- `/rentals/snorkel-gear-rentals/`

High-impact recurring fixes that moved production Lighthouse Accessibility above the AOT threshold:

1. Darken low-contrast orange feature/CTA treatments.
   - Existing orange on white and white-on-orange CTA combinations failed Lighthouse contrast.
   - Apply overrides in CSS loaded by every target page. Some pages load only `style.css`; others also load `nav-fix.css`, so shared/critical overrides may need both.
2. Add visible affordance for in-text/breadcrumb links.
   - Use underlines and darker link colors for paragraph/breadcrumb links instead of relying only on blue-vs-body-color contrast.
3. Label hidden Mailchimp honeypot inputs.
   - Add `aria-label="Leave this field blank"` and avoid malformed self-closing insertion (`/ aria-label=...`).
4. Label photo-gallery thumbnail anchors.
   - Gallery anchors wrapping only images can be flagged as unnamed if image text is not exposed as expected; add `aria-label="View Active Oahu photo gallery"`.
5. Fix visible-label / accessible-name mismatch on footer phone links.
   - If visible text is `(808)498-1894`, the `aria-label` should include that visible text, e.g. `Call (808)498-1894`, not a different spaced form only.
6. Normalize heading levels on target pages.
   - Avoid skipping down to `<h5>` for section/package headings; replace with appropriate `<h2>`/`<h4>` and verify no mismatched `h4`/`h5` closing tags.
7. Remove invalid ARIA roles from visual flex-table pricing markup unless the full required role tree is implemented.
   - A visual flex row with `role="cell"` but no valid `row` parent triggers `aria-required-parent` / `aria-required-children`. Removing invalid roles is safer than partially emulating a table.

## Verification pattern for A11y fixes

Use both structural ad-hoc verification and rendered Lighthouse:

1. Create `/tmp/hermes-verify-*` script that asserts:
   - CSS override markers exist in loaded CSS.
   - Target pages load site CSS.
   - Honeypot inputs are labelled.
   - Gallery thumbnail anchors are labelled.
   - No broken self-closing aria insertion exists.
   - No target `<h5>` remnants or mismatched `<h4>...</h5>` tags remain.
   - Invalid flex-table ARIA roles are removed where applicable.
   - `git diff --check` passes.
2. Run a local static server from `site/` and Lighthouse Accessibility for desktop + mobile target pages.
3. After merge, verify Cloudflare Pages production deployment by commit hash, purge exact URLs or everything when stale, then rerun production Lighthouse with cache-busting query params.
4. Report scores as focused Lighthouse verification, not a full canonical suite.

Observed successful production scores after GRO-3666:

| Page | Desktop A11y | Mobile A11y |
|---|---:|---:|
| `/kayak-rentals/` | 91 | 92 |
| `/multi-activity-adventure-packages/` | 90 | 90 |
| `/rentals/snorkel-gear-rentals/` | 91 | 91 |

## Best Practices blocker classification pattern

After safe CSP/font fixes, remaining Best Practices failures may be third-party/edge tradeoffs rather than broken AOT code.

For GRO-3718, remaining blockers were:

- Third-party cookies from FareHarbor, Google Ads/DoubleClick, Stripe, and TripAdvisor.
- Cloudflare challenge-platform deprecation warnings from `/cdn-cgi/challenge-platform/scripts/jsd/main.js`.
- Page-level Lighthouse `TypeError: Line: 2, column: 1, Syntax error` with weak source location.
- Inspector issues mostly tied to cookie/third-party behavior.

Decision pattern:

- Do **not** remove/defer FareHarbor in a routine sprint; it is core booking infrastructure and directly tied to conversion.
- Do **not** disable Cloudflare challenge/bot/security behavior purely to improve Lighthouse; that is an edge/security policy decision.
- TripAdvisor deferral can be tested, but if a variant does not materially move Best Practices, document rather than ship churn.
- Further score lift should become an explicit consent/third-party deferral/CRO project with booking-flow verification.

## Variant testing notes

Useful isolation variants:

- Disable TripAdvisor widget script and add GA privacy flags to see whether `TypeError` / cookies clear.
- Attempt no-FareHarbor variant only as a local diagnostic; if it causes no-FCP or invalidates booking behavior, mark inconclusive and avoid shipping.
- Browser console may show FareHarbor GA4 warnings while Lighthouse reports a generic page-level TypeError; do not over-attribute unless the source is isolated.

## Documentation verification guard

When a system verification prompt targets generated report/PR-body Markdown rather than code:

- Still create a fresh `/tmp/hermes-verify-*` script.
- Assert the files exist, are non-empty, have no NUL bytes, contain key decision/evidence tokens, and reference evidence directories that exist with files.
- Assert wording does not overclaim full/canonical suite coverage.
- Make token checks case-insensitive when verifying human prose to avoid brittle false negatives like `Third-party` vs `third-party`.
