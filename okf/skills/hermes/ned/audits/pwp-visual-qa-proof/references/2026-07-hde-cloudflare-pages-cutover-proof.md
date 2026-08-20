# HDE cutover route/API proof lessons — 2026-07-16

## Trigger
Use this reference when validating HDE staging/family-test readiness, Cloudflare Pages route behavior, or production cutover blockers.

## Lessons

- `https://staging.humandesignengine.com` is the canonical family-test surface. Production route fallback blocks **public production cutover**, not controlled staging proof.
- Before saying Cloudflare is unavailable, check the actual token shape. Wrangler expects `CLOUDFLARE_API_TOKEN`, but Ned's profile loads a Pages-capable token as `CLOUDFLARE_PAGES_API_TOKEN` from `/home/ubuntu/.hermes/profiles/ned/.env`; run Wrangler as `CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" npx wrangler ...`. Never print the token value; only report the variable/location.
- Use `npx wrangler pages project list` to verify access. For HDE, the Cloudflare Pages project is `hd-platform` and its domains include `hd-platform.pages.dev` and `humandesignengine.com`.
- Safe non-production proof path: deploy a Cloudflare Pages preview branch, e.g. `npx wrangler pages deploy dist --project-name hd-platform --branch ned-hde-cutover-proof`, then verify the `*.hd-platform.pages.dev` alias before touching custom-domain production traffic.
- Cloudflare Pages can expose redirect loops that local `http-server dist` hides. Specifically, if `_redirects` contains both `/success /success/ 301` and `/success/ /success.html 301` while `/success.html` redirects back to `/success/`, Cloudflare follows a loop.
- The route-complete fix is to avoid generating extensionless/trailing-slash redirects for first-class Astro directory routes and to sync `.html` aliases (`success.html`, `privacy.html`, `terms.html`, `buy-report.html`) to the canonical `route/index.html` content when needed.
- Verification should include both canonical build (`npm run build`) and Cloudflare preview smoke for route title/body, not only HTTP status.

## Good proof commands

```bash
cd /home/ubuntu/work/hd-platform
npm run build
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" npx wrangler pages project list
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" npx wrangler pages deploy dist --project-name hd-platform --branch ned-hde-cutover-proof
for path in /deconditioning/ /privacy/ /terms/ /success/ /success.html; do
  curl -sSL "https://ned-hde-cutover-proof.hd-platform.pages.dev$path" | python3 -c 'import re,sys; s=sys.stdin.read(); m=re.search(r"<title[^>]*>(.*?)</title>",s,re.I|re.S); print(m.group(1).strip() if m else "NO TITLE")'
done
```

## Reporting stance

Use `[FAMILY TEST] PROCEED TO FAMILY TEST ONLY` when staging is proven but production custom-domain routing/API Access/human Telegram proof remain unresolved. Do not call this full production readiness.
