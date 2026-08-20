# AOT Japanese locale nav cleanup + heading font guard — 2026-07-11

## When this applies
Use this pattern after a broken-reference triage leaves a `japanese_locale_nav` bucket, or whenever Michael says AOT headings must use the historical Open Sans Condensed Bold font.

## Key learning
Michael considers `Open Sans Condensed` bold / 700 the established heading face for **all** `h1`-`h6`. Do not leave `--font-headings` pointing at Aleo or rely on page-by-page incidental styles. Enforce the heading face at the theme level and cover standalone static pages that do not load the theme CSS.

## Workflow
1. Start from clean `origin/main` worktree on a Kai/content branch.
2. Re-run the current broken-reference scanner; do not trust stale counts.
3. For `japanese_locale_nav`, patch only verified-safe route fixes:
   - Missing `/ja/rentals/` route should map to `/ja/oahu-equipment-rentals/`.
   - Missing `/ja/rentals/index.html` should map to `/ja/oahu-equipment-rentals/index.html`.
   - Missing `/ja/activities.html` should map to `/ja/activities/`.
   - Bad smart-quote storefront URL `/ja/%E2%80%9C` should map to `/ja/kailua-oahu-storefront/`.
   - Malformed activity hrefs ending in `/ /` should be normalized only if the clean target exists.
   - If an English page advertises a missing translated slug and no local JA page exists, remove the dead JA alternate and/or point the language-switch anchor to `/ja/` rather than a 404.
4. Enforce heading fonts in both theme CSS files:
   - Set `--font-headings: "Open Sans Condensed", sans-serif;`.
   - Add a clear `h1, h2, h3, h4, h5, h6, .h1...` guard with `font-family: "Open Sans Condensed", "Arial Narrow", Arial, sans-serif !important; font-weight: 700 !important; font-style: normal !important;`.
5. Crawl static HTML for heading-bearing pages that do **not** load `wp-content/themes/activeoahu/css/style.css`; add an inline `aot-heading-font-guard` plus the existing Google Fonts Open Sans Condensed 700 stylesheet to those standalone pages.
6. Cache-bust theme CSS references where practical so production does not keep a stale heading stylesheet.
7. Verify with a fresh `/tmp/hermes-verify-*` script:
   - broken-reference scan shows `japanese_locale_nav = 0`;
   - every heading-bearing HTML page either loads theme `style.css` or has inline `aot-heading-font-guard`;
   - rendered Playwright crawl checks representative or all non-redirect pages and asserts every visible `h1`-`h6` computed `fontFamily` includes `Open Sans Condensed` and `fontWeight >= 700`.
8. After merge, purge exact CSS/page URLs and run production marker + rendered heading checks before reporting done.

## Pitfalls
- Do not bulk-create or fake Japanese pages just to satisfy a scanner row; route only to verified existing targets.
- Do not chase Cloudflare `/cdn-cgi` rows as part of Japanese nav cleanup.
- Meta-refresh redirect pages may navigate before Playwright can inspect headings; use static guard checks for those and skip them in rendered heading crawls.
- If production HTML is fresh but the CSS asset body is stale, purge exact `style.css` and `brand-overrides.css` URLs as well as representative pages.
