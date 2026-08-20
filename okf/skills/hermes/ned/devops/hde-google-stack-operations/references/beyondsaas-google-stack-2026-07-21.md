# BeyondSaaS Google Stack Setup — 2026-07-21

## Scope
Session-specific proof/lessons from setting up `beyondsaas.ai` using the same Google-stack pattern as HDE: OAuth scope verification, Search Console domain verification, GA4/GTM wiring, sitemap generation/submission, and Cloudflare Pages deployment verification.

## Durable IDs

```text
Domain: beyondsaas.ai
Search Console property: sc-domain:beyondsaas.ai
GA4 property: properties/541439505 — Beyond SaaS - GA4
GA4 data stream: properties/541439505/dataStreams/15058653549 — Beyond SaaS Web
GA4 measurement ID: G-SDN0R5YVJF
GTM container: accounts/10319161/containers/258904608
GTM public ID: GTM-W9BR974P
Published GTM version: 2
```

## Workflow lessons

1. **Existing OAuth token may already be enough**
   - The HDE reusable token with the full GA/GTM/GSC/Site Verification scope set worked for another GrowthWeb domain.
   - Verify scopes first before asking Michael for another consent link.

2. **Use Search Console domain property for new domains**
   - Generate Site Verification for `INET_DOMAIN`/DNS TXT.
   - Add the TXT in Cloudflare only after approval.
   - After Site Verification succeeds, add `sc-domain:<domain>` through Search Console Sites API and confirm `permissionLevel=siteOwner`.

3. **Do not trust live `/robots.txt` or `/sitemap.xml` blindly**
   - Before the fix, BeyondSaaS returned the homepage HTML for `/robots.txt`, `/sitemap.xml`, and `/sitemap-index.xml` with HTTP 200.
   - Add explicit Astro endpoints for `robots.txt` and `sitemap.xml`, then verify content type and XML/body, not just HTTP 200.

4. **GTM publish needs version scopes**
   - Creating containers/tags is not enough. Require `tagmanager.edit.containerversions` and `tagmanager.publish` so a container version can be created and published.

5. **Mixed/generated HTML may bypass Astro layout changes**
   - BeyondSaaS had built/static pages where a layout-only GTM change did not cover every HTML file.
   - Add a deterministic postbuild injector when the site contains generated/static HTML outside the canonical layout path.
   - Verify every `dist/**/*.html` contains the target GTM ID and noscript iframe, and that old direct `gtag/js?id=<GA4>` snippets are absent.

6. **Fresh verification nudges mean rerun, don’t cite prior output**
   - After source edits, rerun `npm run build` and the rendered coverage check even if the same command passed minutes earlier.

## Known-good BeyondSaaS verification shape

```bash
npm run build
python3 - <<'PY'
from pathlib import Path
html=list(Path('dist').rglob('*.html'))
missing_gtm=[]; missing_ns=[]; direct_ga=[]
for p in html:
    s=p.read_text(errors='ignore')
    if 'GTM-W9BR974P' not in s:
        missing_gtm.append(str(p))
    if 'googletagmanager.com/ns.html?id=GTM-W9BR974P' not in s:
        missing_ns.append(str(p))
    if 'gtag/js?id=G-SDN0R5YVJF' in s:
        direct_ga.append(str(p))
print('html_count', len(html))
print('missing_gtm_count', len(missing_gtm))
print('missing_noscript_count', len(missing_ns))
print('direct_gtag_count', len(direct_ga))
print('robots_exists', Path('dist/robots.txt').exists())
print('sitemap_exists', Path('dist/sitemap.xml').exists())
print('sitemap_url_count', Path('dist/sitemap.xml').read_text().count('<url>') if Path('dist/sitemap.xml').exists() else 0)
PY
```

Expected local result from the session:

```text
[build] 45 page(s) built
[inject-google-stack] scanned 47 HTML files; updated 47; gtm=GTM-W9BR974P
html_count 47
missing_gtm_count 0
missing_noscript_count 0
direct_gtag_count 0
robots_exists True
sitemap_exists True
sitemap_url_count 32
```

## Live deployment proof pattern

After explicit production approval, deploy with Wrangler Pages and verify:

```text
https://beyondsaas.ai/             -> HTTP 200, contains GTM-W9BR974P, no direct gtag/js?id=G-SDN0R5YVJF
https://beyondsaas.ai/robots.txt   -> HTTP 200 text/plain, includes Sitemap line
https://beyondsaas.ai/sitemap.xml  -> HTTP 200 application/xml, contains urlset
Search Console sitemap submit      -> HTTP 204, errors=0, warnings=0
```

## Pitfalls

- A 200 response for sitemap/robots can still be wrong if the site is serving the SPA/homepage fallback.
- GitHub push may be unavailable in the VM; production Pages deploy can still succeed ad hoc, but report that the commit is local if push fails.
- Do not persist OAuth codes from chat; they are single-use and should be treated as secrets.
