# AOT Broken Reference Triage + PWP Visual Audit Notes — 2026-07-11

Use this when a Golden Thread task asks to triage a large broken-link/internal-reference audit without blindly fixing every scanner row, especially when the user also asks for a PWP visual audit on new/recent pages.

## Core lesson

Do **not** chase the raw broken-reference total as if every row is equally risky. A stale audit reported `1,139` broken refs, but a fresh current scan after prior work found a smaller/different set. The durable workflow is:

1. Re-scan current `origin/main` before editing.
2. Classify every row into exactly one bucket.
3. Patch only the smallest safe high-revenue slice when targets are concrete and locally verifiable.
4. Treat Cloudflare `/cdn-cgi` email decoder/protection URLs as scanner noise unless live rendering shows visible email/runtime breakage.
5. Save a compact report artifact and verify with a `/tmp/hermes-verify-*` script.

## Buckets that worked

- `booking_revenue_path` — tour/rental/booking/CTA links, hreflang/canonical refs for commercial pages, FareHarbor-adjacent user paths.
- `japanese_locale_nav` — `/ja/` alternate/nav targets and malformed JA relatives.
- `cloudflare_email_decoder_noise` — `/cdn-cgi/scripts/...email-decode...` and `/cdn-cgi/l/email-protection...` rows.
- `asset_template_path` — `_templates/` relative links, `wp-content` assets, scripts/images/icons and template-only relative path artifacts.
- `orphan_author_path` — legacy `/author/mbgulden` / skip-link targets.
- `other_content_or_route` — real but lower-priority content paths that do not fit the above.

## Safe patch examples

Only patch rows where the new target exists locally or the live path is already canonical:

- Bad alternate: `https://activeoahutours.com/../rainforest-oahu-kayak-tour.html`
  - Fix to canonical current tour URL.
- Bad JA alternate: `https://activeoahutours.com/../../ja/.../index.html`
  - Fix to root absolute `/ja/.../` URL.
- Broken relative fragment: `../../rentals/index#rental-gear`
  - Fix to `/rentals/index.html#rental-gear` when that exported target exists.

Do **not** bulk-edit `_templates/` or all JA paths in the same PR unless the task explicitly scopes that slice. Recommend the next slice separately.

## PWP visual audit pattern

When the user asks for PWP visual consistency/contrast on new pages:

1. Pick new/recent content surfaces plus any pages touched by the patch.
2. Run rendered checks at mobile `390x844` and desktop `1366x900`.
3. Check: HTTP status, H1 presence, horizontal overflow, visible button count, computed contrast for visible page/footer text, and screenshots.
4. Scope contrast to meaningful visible content/footer text; note existing static-export console noise separately (`jQuery is not defined`, `wp is not defined`, local missing resources) instead of treating it as a text-style blocker.
5. Fix low-contrast CTA/pricing/footer text immediately when safe.
6. Attach representative screenshots in the final report and label verification as focused ad-hoc unless a canonical suite ran.

## Contrast fixes from this run

- CTA text may need inline `color:#fff !important` because old AOT anchor rules can override normal button styling.
- Snorkel/pricing microcopy in pricing tables needed stronger selectors on both `p` and `small` text, not only `small`.
- Footer links/emails on blue backgrounds may need explicit white + underline styles, and sometimes an inline style on `mailto:` anchors when inherited link rules win.

## Reporting shape

Report:

- old/stale audit total vs fresh current total;
- bucket counts after patch;
- exact high-revenue rows patched;
- PWP page/viewport matrix with contrast/overflow results;
- PR, merge commit, Cloudflare purge, and production marker verification;
- next recommended slice (usually JA locale/nav before Cloudflare noise).