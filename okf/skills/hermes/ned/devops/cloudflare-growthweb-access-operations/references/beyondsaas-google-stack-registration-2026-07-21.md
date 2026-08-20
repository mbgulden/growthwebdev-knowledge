# BeyondSaaS Google Stack Registration — 2026-07-21

Session pattern for registering a Cloudflare Pages marketing site with Google Analytics, Tag Manager, Search Console, and Cloudflare DNS verification.

## Durable pattern

1. Confirm reusable Google OAuth token has these scopes before GA/GTM/GSC work:
   - `analytics.edit`
   - `analytics.readonly`
   - `tagmanager.manage.accounts`
   - `tagmanager.edit.containers`
   - `tagmanager.edit.containerversions`
   - `tagmanager.publish`
   - `tagmanager.readonly`
   - `webmasters`
   - `siteverification`
2. Probe Google APIs separately; valid OAuth scopes are not enough if APIs are disabled on the OAuth client project.
3. For Search Console domain properties, use Google Site Verification API to generate a DNS TXT token, then create the root `TXT` record in Cloudflare. Verify on public resolvers before calling the Google verify endpoint.
4. Use `sc-domain:<domain>` for Search Console domain properties, not only `https://domain/` URL-prefix properties.
5. Create/find the GA4 web stream and record its measurement ID.
6. Create a GTM container under the appropriate Tag Manager account, create a Google tag (`type=googtag`) using the GA4 measurement ID, create a container version, then publish it. `tagmanager.edit.containerversions` and `tagmanager.publish` are required for the last two steps.
7. Update the site to load GTM, not a stale direct `gtag.js` snippet, and verify built HTML includes:
   - GTM container ID
   - `googletagmanager.com/gtm.js`
   - `googletagmanager.com/ns.html`
   - no obsolete direct `gtag/js?id=<measurement>` if GTM owns GA4
8. Add real `robots.txt` and `sitemap.xml` endpoints before submitting the sitemap in Search Console.
9. Submit the live sitemap via Search Console API and verify it lists with `errors=0`, `warnings=0`.

## BeyondSaaS concrete proof values

Non-secret identifiers from the successful run:

```text
domain=beyondsaas.ai
GA4 property=properties/541439505
GA4 stream=properties/541439505/dataStreams/15058653549
GA4 measurementId=G-SDN0R5YVJF
GTM publicId=GTM-W9BR974P
GTM container=accounts/10319161/containers/258904608
Search Console property=sc-domain:beyondsaas.ai
Cloudflare Pages project=beyondsaas
```

## Cloudflare Pages deployment pitfall

Do not deploy Pages from a dirty worktree unless explicitly preserving/checkpointing the dirty state immediately after. A dirty Pages deploy can make production contain source files/assets that are not yet in Git. If this happens:

1. Archive `git status`, branch/worktree state, diffs, and untracked files first.
2. Secret-scan untracked text files.
3. Remove only mechanically safe duplicates/cache.
4. Commit live-ish untracked source/assets that were part of the production deployment, or explicitly roll them back and redeploy from a clean commit.
5. Run `npm run build` and a post-build HTML coverage check before reporting green.

## Verification snippets

Local build coverage shape:

```bash
npm run build
python3 - <<'PY'
from pathlib import Path
html=list(Path('dist').rglob('*.html'))
print('html_count', len(html))
print('missing_gtm_count', sum('GTM-W9BR974P' not in p.read_text(errors='ignore') for p in html))
print('missing_noscript_count', sum('googletagmanager.com/ns.html?id=GTM-W9BR974P' not in p.read_text(errors='ignore') for p in html))
print('direct_gtag_count', sum('gtag/js?id=G-SDN0R5YVJF' in p.read_text(errors='ignore') for p in html))
print('robots_exists', Path('dist/robots.txt').exists())
print('sitemap_exists', Path('dist/sitemap.xml').exists())
PY
```

Live endpoint smoke shape:

```bash
curl -sS -A 'Mozilla/5.0 verification' -D /tmp/headers -o /tmp/home https://beyondsaas.ai/
curl -sS -D /tmp/robots.headers -o /tmp/robots https://beyondsaas.ai/robots.txt
curl -sS -D /tmp/sitemap.headers -o /tmp/sitemap https://beyondsaas.ai/sitemap.xml
```

Expected: homepage 200 with GTM, robots 200 `text/plain`, sitemap 200 `application/xml`.
