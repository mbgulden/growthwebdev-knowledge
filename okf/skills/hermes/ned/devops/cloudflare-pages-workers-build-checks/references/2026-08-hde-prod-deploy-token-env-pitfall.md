# 2026-08-19 HDE prod deploy — CF token env pitfall + deploy record

## The pitfall (reusable)
Wrangler authenticates via `CLOUDFLARE_API_TOKEN`. This box exposes the
token under `CLOUDFLARE_PAGES_API_TOKEN` (a `cfut_…` user token). When the
token value is inlined in a terminal command line
(`CLOUDFLARE_API_TOKEN=*** npx wrangler …`), the shell/redaction layer
corrupts the value so wrangler sends a malformed Authorization header:

```
✘ [ERROR] A request to the Cloudflare API (/accounts) failed.
  Invalid request headers [code: 6003]
  - Invalid format for Authorization header [code: 6111]
```

The token itself is fine — a direct `curl`/urllib `GET /accounts` with
`Authorization: Bearer <token>` returns HTTP 200. The corruption is an
artifact of the command-line path, not the credential.

### Diagnosis
```bash
CLOUDFLARE_API_TOKEN=*** node -e \
  "console.log('len:', (process.env.CLOUDFLARE_API_TOKEN||'').length)"
```
If it prints `len: 3`, the value was replaced by the literal `***`
(redaction marker). A healthy 53-char `cfut_…` token would print `len: 53`.

### Fix
Pass the token through a Python subprocess env instead of the shell line:
```python
import os, subprocess
env = dict(os.environ)
env['CLOUDFLARE_API_TOKEN'] = os.environ.get('CLOUDFLARE_PAGES_API_TOKEN', '')
r = subprocess.run(
    ['npx', 'wrangler', 'pages', 'deploy', 'dist',
     '--project-name', 'hd-platform', '--branch', 'main'],
    env=env, capture_output=True, text=True, timeout=240)
```
Redact `cfut_[A-Za-z0-9_-]{16,}` out of logged output before reporting.

## Deploy record (this session)
- Worktree: `/home/ubuntu/work/hd-platform-prod-merge`
- Branch: `ned/hde-prod-deploy-promotion-2026-08-19`
- `npm run build` green (10 Astro pages + postbuild route-complete).
- `wrangler pages deploy dist --project-name hd-platform --branch main`
  → deployment `https://a2b0aadb.hd-platform.pages.dev`.
- Live prod (humandesignengine.com) verified:
  - `POST /api/checkout/create-session` → 200 + real `cs_live_…` Stripe URL
    (previously 405 — the broken payment button).
  - `/sanctuary-demo/` → 200 "14-Day Sanctuary Demo".
  - `/deconditioning/`, `/success/`, `/privacy/`, `/checkout/pay/` → 200.
  - GA4 loader `G-Q6TPL08VM7` present on built pages.
- PR: https://github.com/mbgulden/hd-platform/pull/54

## Follow-ups that stayed open (not part of this skill)
- Prod `hde-api.service` still runs old checkout (branch `feature/gro-3999`)
  so `/api/demo/start` 404s on prod even though the edge proxy is live.
  Needs the prod API checkout promoted to code containing the demo route +
  restart. Staging returns a working demo deep link — use it as reference.
