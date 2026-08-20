---
name: cloudflare-growthweb-access-operations
description: Use when managing GrowthWeb Cloudflare Access apps, tunnels, or HDE public API bypass paths from Ned.
---

# GrowthWeb Cloudflare Access Operations

## Trigger
Use this when Cloudflare Access is blocking a public GrowthWeb/HDE path, a tunnel route needs inspection, or the API token appears to list accounts but returns `403` for Access apps.

## Credential location
- Usable GrowthWeb Cloudflare global-key API shape is in `/home/ubuntu/cf_setup_staging.py`.
- Use the file for account/zone IDs and the `X-Auth-Email` + `X-Auth-Key` headers.
- Do **not** use the Pages Bearer token for Access apps; it can list Pages/account data but lacks Access-app permissions.
- Do not paste the key in chat or logs.

## Read Access apps
```bash
python3 - <<'PY'
import urllib.request, json
src=open('/home/ubuntu/cf_setup_staging.py').read()
EMAIL='michael@growthwebdev.com'
KEY=src.split('API_KEY = "')[1].split('"')[0]
ACC=src.split('ACCOUNT_ID = "')[1].split('"')[0]
headers={'X-Auth-Email':EMAIL,'X-Auth-Key':KEY,'Content-Type':'application/json'}
url=f'https://api.cloudflare.com/client/v4/accounts/{ACC}/access/apps'
apps=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=headers)))['result']
for a in apps:
    print(a['domain'], a['name'], [p.get('decision') for p in a.get('policies',[])])
PY
```

## HDE public checkout bypass pattern
For public checkout/static paths under the protected `api.humandesignengine.com` Access app, create more-specific self-hosted Access apps with an inline `bypass` policy:

```json
{
  "name": "HDE Public Checkout Create",
  "domain": "api.humandesignengine.com/create-checkout",
  "type": "self_hosted",
  "session_duration": "24h",
  "app_launcher_visible": false,
  "auto_redirect_to_identity": false,
  "policies": [{
    "name": "Bypass Everyone — public checkout/report path",
    "decision": "bypass",
    "include": [{"everyone": {}}],
    "exclude": [],
    "require": [],
    "precedence": 1
  }]
}
```

Known public HDE bypass paths created on 2026-07-18:
- `api.humandesignengine.com/create-checkout`
- `api.humandesignengine.com/create-checkout-session`
- `api.humandesignengine.com/checkout`
- `api.humandesignengine.com/checkout/*`
- `api.humandesignengine.com/static/*`
- `api.humandesignengine.com/api/checkout/create-session`
- `api.humandesignengine.com/api/checkout/session`
- `api.humandesignengine.com/webhook`
- `api.humandesignengine.com/stripe-webhook`
- `api.humandesignengine.com/api/webhooks/stripe`
- `api.humandesignengine.com/api/affiliate-signup`
- `api.humandesignengine.com/api/affiliate-stats`
- `reports.humandesignengine.com/reports/*`

## Cloudflare rate-limit rule quirks
When adding a zone `http_ratelimit` ruleset through the Cloudflare Rulesets API, free/lower entitlement plans may reject common examples. Durable pattern learned on HDE staging demo signup:

- `ratelimit.characteristics` must include `cf.colo.id` as well as `ip.src`; `ip.src` alone can fail because counting happens at colo level.
- Allowed `period` may be constrained to `10` seconds, not `60`.
- Allowed `mitigation_timeout` may also be constrained to `10` seconds.
- A working staging shape for a semi-public POST gate was: host/path expression, `action: block`, `characteristics: ["cf.colo.id", "ip.src"]`, `period: 10`, `requests_per_period: 5`, `mitigation_timeout: 10`.
- Store a redacted local proof artifact with `ruleset_id`, `rule_id`, host, path, threshold, action, and UTC verification time; verify by re-fetching the ruleset and checking the rule exists/enabled. Do not print API keys.

## Verification
Unauthenticated public route checks should return origin status, not Cloudflare Access 302:
```bash
curl -sS -D - -o /tmp/out https://api.humandesignengine.com/static/hd-checkout.js | sed -n '1,14p'
curl -sS -D - -o /tmp/out -X POST https://api.humandesignengine.com/create-checkout \
  -H 'Content-Type: application/json' \
  --data '{"name":"Smoke","email":"smoke@example.test","report":"natal","birthdate":"1989-04-12","birthtime":"17:07","location":"Meridian, ID","timezone":"America/Boise"}' | sed -n '1,14p'
```

Expected: HTTP `200` and Stripe Checkout JSON for checkout paths; no `growthwebdev.cloudflareaccess.com` redirect.

## Local routing notes
- Cloudflared local config: `/home/ubuntu/.cloudflared/config.yml` routes `api.humandesignengine.com` to local nginx `http://localhost:8091`.
- Nginx public API config: `/etc/nginx/sites-enabled/api-humandesignengine`.
- Payment server: `hde-payment.service` on port `8002`.
- The production Pages site `humandesignengine.com` is Cloudflare Pages (`hd-platform` project), not the local nginx root. Use Pages Functions for same-origin `/api/checkout/create-session` or `/create-checkout` proxy routes; deploying staging `dist/` alone can still leave production checkout returning `405`. See `references/hde-cloudflare-pages-checkout-proxies-2026-07-18.md`.
- When using Wrangler in non-interactive sessions, explicitly export a token named `CLOUDFLARE_API_TOKEN` (often from the Pages token) before `wrangler pages deploy`; passing a differently named env var is not enough. However, do not deploy `--branch main` / production unless the current user request explicitly authorizes production or you are performing an emergency rollback of a bad production deployment.using Wrangler in non-interactive sessions, explicitly export a token named `CLOUDFLARE_API_TOKEN` (often from the Pages token) before `wrangler pages deploy`; passing a differently named env var is not enough. However, do not deploy `--branch main` / production unless the current user request explicitly authorizes production or you are performing an emergency rollback of a bad production deployment.

## Pages/API token alias for non-Wrangler clients

The Ned profile's `.env` exposes the Cloudflare Pages/API token as `CLOUDFLARE_PAGES_API_TOKEN` (not `CLOUDFLARE_API_TOKEN`). When wiring a Python client that uses Bearer auth and isn't Wrangler, implement a precedence chain in `from_env()`:

```python
NAMES = ("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_PAGES_API_TOKEN")
for name in NAMES:
    value = os.environ.get(name, "").strip()
    if value:
        return cls(token=value)
```

The `cfut_` prefix (53 chars) is the Pages/API token shape — usable for Zone:Read, DNS:Read, Pages:Read on `michael@growthwebdev.com`. The older `cfk_` Global API Key in `CLOUDFLARE_*_API_KEY` works for read-only ops but cannot do Bearer-auth write ops on most modern accounts. For provisioning flows that need zone create / DNS record create, the Bearer token is the right choice. See `references/2026-07-cloudflare-token-alias-precedence-provisioning.md` for the full discovery recipe, the precedence-chain pattern that landed in `prismatic-pwp-ubersuggest-auth/plugins/pwp/capabilities/provision_site/cloudflare_client.py`, and the live-test artifacts left on Cloudflare during the 2026-07-29 ezshare.systems run.
- Never deploy Cloudflare Pages from a dirty HDE checkout. Build/deploy from the intended clean commit or isolated worktree and verify content markers after deploy.
- Dirty Pages deploys are allowed only with explicit user approval and must be treated as a temporary incident: archive status/diffs/untracked files first, deploy, then immediately checkpoint or roll back the dirty state so production is not ahead of source. This came up on BeyondSaaS after a successful ad-hoc Pages deploy included untracked pages/assets; see `references/beyondsaas-google-stack-registration-2026-07-21.md`.
- After any Pages deployment that changes checkout/demo/API behavior, verify the same-origin Functions too — not just static routes. For HDE demo/checkout, `POST /api/demo/start` with an invalid email should return JSON `400` (not Access HTML/302, `405`, or empty response), and a safe checkout smoke should create a live Stripe Checkout URL without completing payment. Ensure production branches include required `functions/**` source; missing Pages Functions can leave static pages green while APIs fail. See `references/2026-07-hde-pages-demo-production-deploy.md`.
- When a Pages Function proxies to `api.humandesignengine.com`, make sure Cloudflare Access has more-specific bypass apps for new public upstream paths such as `api.humandesignengine.com/api/demo/start`; otherwise the same-origin Function may proxy an Access login page.
- When backing up nginx configs, do **not** leave backup copies in `/etc/nginx/sites-enabled/`. Move them to `/etc/nginx/backups/` or another non-enabled directory before `nginx -t`; enabled backups can create duplicate `server_name` warnings and mask which block is serving traffic.

## Google OAuth / Search Console verification for Cloudflare Pages sites

When Google-stack work is blocked, treat auth as layered: AGY/Kai Google login, `gcloud` ADC scopes, reusable OAuth scopes, Google Cloud API enablement, Search Console ownership, and live deployed crawler endpoints are separate gates. Verify each with live probes before calling the stack green.

- For the HDE 2026-07-20 working pattern — scoped OAuth exchange, API enablement, Cloudflare DNS TXT verification, `siteOwner` promotion, and sitemap submission — see `references/hde-google-oauth-gsc-verification-2026-07-20.md`.
- For the BeyondSaaS 2026-07-21 pattern — GA4 web stream, GTM container creation/version/publish, Search Console `sc-domain:` property, Cloudflare DNS verification, real `robots.txt`/`sitemap.xml`, dirty Pages deploy cleanup, and HTML coverage checks — see `references/beyondsaas-google-stack-registration-2026-07-21.md`.

Key pitfalls:
- `AUTH_OK` / AGY login is not proof of GA4/GTM/GSC API readiness.
- A token with valid scopes can still fail until `analyticsadmin`, `tagmanager`, `searchconsole`, and `siteverification` APIs are enabled on the OAuth client project.
- Search Console `siteUnverifiedUser` is not enough for sitemap reads/submits; require `siteOwner`.
- Adding the Google verification TXT record in Cloudflare is an infrastructure change; get explicit approval first.

## GrowthWeb Google Site Verification DNS TXT

When Google Search Console/Site Verification needs a DNS TXT record for a GrowthWeb-owned Cloudflare zone, use `hde-google-stack-operations` for the Google-side flow and this skill for the Cloudflare mutation pattern. Ask Michael before creating or changing DNS records. Use the global-key Cloudflare API shape from `/home/ubuntu/cf_setup_staging.py`, never print the key, create the root `TXT` record on the target zone, verify via Cloudflare API plus public resolvers (`1.1.1.1`, `8.8.8.8`), then return to the Google Site Verification API. See `hde-google-stack-operations/references/hde-google-stack-2026-07-20.md` for HDE proof and `hde-google-stack-operations/references/beyondsaas-google-stack-2026-07-21.md` for BeyondSaaS proof.

Pitfall: do not infer success from HTTP 200 on `/robots.txt` or `/sitemap.xml`; Cloudflare Pages/static fallbacks can return homepage HTML. Verify content type/body after deployment.

## HDE Cloudflare Pages security headers

When adding or changing Pages security headers for `hd-platform`:

- Put the policy in `public/_headers`; Astro copies it into `dist/_headers` during `npm run build`. Do not hand-edit `dist/_headers` as source.
- Keep CSP checkout-safe unless a separate hardening task explicitly removes inline/script allowances: Stripe (`https://checkout.stripe.com`, `https://js.stripe.com`, `https://hooks.stripe.com`, `https://api.stripe.com`), GA/GTM (`https://www.googletagmanager.com`, `https://www.google-analytics.com`, `https://region1.google-analytics.com`, `https://stats.g.doubleclick.net`), and Google Fonts (`https://fonts.googleapis.com`, `https://fonts.gstatic.com`).
- Commit the source/doc change before long verification, then run `npm run build` and assert `dist/_headers` contains HSTS, CSP, Permissions-Policy, `frame-ancestors`, and the required third-party allowances.
- For post-finalization Hermes verification nudges, rerun `npm run build` fresh and use a temporary `/tmp/hermes-verify-*` wrapper that also checks the local RESULT artifact for the same evidence markers, then delete the verifier before reporting.
- Keep the Linear issue **In Review**, not Done, until live Cloudflare Pages proof confirms the headers are actually served on `humandesignengine.com` and checkout still passes after deploy.

## HDE Workers Build check diagnostics

When a PR shows Cloudflare Pages success but the GitHub check `Workers Builds: hd-platform` fails, inspect the commit check-runs directly with `gh api repos/mbgulden/hd-platform/commits/<sha>/check-runs`; `gh pr view --json statusCheckRollup` can fail on deprecated Projects fields in this repo. Capture both the GitHub check run id and the Cloudflare Workers build id from the check output. If GitHub exposes no annotations/log text and Cloudflare read-only build/log endpoints return only `204` or service metadata, do not silently call it green. Default posture is to keep the Linear issue in **In Review** and report the remote proof as not green; if the same commit has a successful Cloudflare Pages check and the Pages preview route(s) are live with expected markers, you may document an explicit waiver for the noisy Workers integration before proceeding with review/approval. See `references/hde-workers-build-check-diagnostics-2026-07-18.md` and `references/2026-07-hde-workers-build-waiver-pattern.md`.

## Related skills
- Use `stripe-payment-live-operations` when checkout routing works but Stripe still shows Sandbox or when switching HDE payments from test to live mode.
