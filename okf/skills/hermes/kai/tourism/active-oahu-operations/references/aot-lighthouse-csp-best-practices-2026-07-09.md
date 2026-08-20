# AOT Lighthouse Best Practices / CSP remediation notes — 2026-07-09

Use this when Lighthouse Best Practices is low on Active Oahu booking pages and the failures look like CSP/console/third-party issues.

## Durable findings

- The live production CSP for `activeoahutours.com` may come from a **Cloudflare response header transform ruleset**, not from repo `site/_headers`.
- Check Cloudflare rulesets at zone scope and inspect the `http_response_headers_transform` phase before patching repo headers.
- In this session the relevant rule was a response-header transform rule described like `GRO-2207: Enforce Content-Security-Policy and remove Report-Only`.
- Always back up the full Cloudflare ruleset JSON before PUT updates.
- After edge CSP changes, verify the live response header with `curl -D -` against a cache-busted URL before rerunning Lighthouse.

## Safe CSP remediation pattern

1. Capture live headers:
   ```bash
   curl -sS -D - -o /dev/null 'https://activeoahutours.com/?kai_verify_csp=1' | tr -d '\r' | sed -n '1,80p'
   ```
2. Inspect Cloudflare zone rulesets:
   - list zone rulesets
   - fetch the `http_response_headers_transform` ruleset by ID
   - identify the CSP-setting rule
3. Save a timestamped backup under `reports/golden-thread/` before every Cloudflare ruleset update.
4. Add only domains proven by Lighthouse/console evidence; do not blanket wildcard third parties.
5. Remove stale `report-uri` only when verified failing; in this session `activeoahutours.report-uri.com/r/default/csp/reportOnly` returned 400 and itself caused console noise.
6. Recheck live CSP, then rerun focused Lighthouse.

## Common domains observed in Best Practices remediation

From production Lighthouse runs, these domains may be legitimate AOT dependencies when their specific resources are blocked:

- Google/ads/analytics: `analytics.google.com`, `stats.g.doubleclick.net`, `ad.doubleclick.net`, `googleads.g.doubleclick.net`, `www.googleadservices.com`, `www.google.com`
- Cloudflare analytics: `static.cloudflareinsights.com`, `cloudflareinsights.com`
- TripAdvisor widget assets/fonts: `static.tacdn.com`

Map each to the correct directive (`script-src`, `style-src`, `img-src`, `font-src`, `connect-src`) based on the actual console violation.

## Repo-side font URL fix pattern

Lighthouse console errors may show false-looking 404s such as:

```text
https://activeoahutours.com/kayak-rentals/fonts.gstatic.com/s/lato/...
```

This means static HTML has relative `url(fonts.gstatic.com/...)` or `url(../../fonts.gstatic.com/...)` in inline `@font-face` blocks. Fix by converting to absolute:

```text
url(https://fonts.gstatic.com/...)
```

Focused verifier should assert:

- no `url((../)*/?fonts.gstatic.com/...)` remains
- representative pages contain `url(https://fonts.gstatic.com/...)`
- `git diff --check` passes
- temporary `/tmp/hermes-verify-*` verifier is cleaned up

## PR body quoting pitfall

When creating GitHub PRs from shell, do not put Markdown bodies with backticks directly inside a double-quoted `--body` argument. Bash will execute command substitutions inside backticks. Write the PR body to `/tmp/*.md` and use `--body-file`, or update through the GitHub REST API with file content.

## Best Practices may remain below threshold

Do not claim Best Practices is fixed just because CSP blocks are reduced. In this session, after safe CSP and font fixes, Lighthouse still stayed around `50–54` because of:

- third-party cookies from FareHarbor, Google Ads/DoubleClick, Stripe, and TripAdvisor
- Cloudflare challenge-platform deprecated API warnings from `/cdn-cgi/challenge-platform/scripts/jsd/main.js`
- a remaining page-level `TypeError: Line: 2, column: 1, Syntax error`

Close the CSP remediation only when safe fixes are complete and create a follow-up for deeper third-party deferral/CMP/widget isolation if the score remains below target.
