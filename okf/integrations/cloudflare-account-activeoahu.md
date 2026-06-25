---
type: Integration
title: Cloudflare Accounts — Active Oahu Tours (michael@activeoahu.com)
description: Canonical reference for the Cloudflare account that owns activeoahutours.com. Separate from GrowthWebDev (michael@growthwebdev.com). Covers auth method, env-var locations, zone IDs, and known failure modes.
resource: okf/integrations/cloudflare-account-activeoahu.md
tags: [integration, cloudflare, active-oahu, dns, tunnel, prismatic-engine]
timestamp: 2026-06-23T14:30:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/cloudflare-account-activeoahu.md
last_verified: 2026-06-25
verified_by: ned
status: current
---

# Cloudflare Account — Active Oahu Tours (`michael@activeoahu.com`)

This is the **second** Cloudflare account we operate, distinct from GrowthWebDev. Future agents must not confuse the two — they have different account IDs, different zones, different auth credentials.

## TL;DR

- **Account email:** `michael@activeoahu.com`
- **Account name (per API):** `Michael@activeoahu.com's Account`
- **Account ID:** `3e13f120ec7532f0bc8ac0bc9bfc7108`
- **Auth method:** Global API Key (`cfk_` prefix) — uses `X-Auth-Email` + `X-Auth-Key` headers
- **Role:** Super Administrator — All Privileges (full access)
- **Zones:** `activeoahutours.com` — zone ID `a8dc4f7db7ab9cea93c04ba315a7a7f7`, on the **Cloudflare Pro** plan tier. Subscription ID `e32a212902e042828f62f75c1ec9d70e`. Pro features: 20 page rules, custom WAF rules, advanced DDoS, prioritized support. NOT Free, NOT Business, NOT Enterprise.

## Plan Tier & Limits (verified 2026-06-23)

The AOT zone is on the **Cloudflare Pro** plan tier (also called "Pro Website" in the `/zones` API response and "Cloudflare Pro Plan" in `/subscription` — same thing). This unlocks features Free zones can't use:

| Feature | Free limit | Pro limit (activeoahutours.com) | Currently used |
|---|---|---|---|
| Page rules | 5 | **20** | unknown (audit: `curl /zones/$ZONE/pagerules`) |
| Custom WAF rules | ❌ no | ✅ yes (WAF setting currently `off` — see warning below) | `off` |
| Rate limiting rules | 1 | 10 | unknown |
| Advanced DDoS | basic | ✅ advanced | enabled (default for Pro) |
| Priority support | ❌ | ✅ | n/a |
| Min TLS version (lowest allowed) | 1.0 | 1.0 (Pro doesn't enforce TLS 1.3) | **1.0** (set 2022, never upgraded) |
| Security Level | n/a (challenge-passive only) | configurable | **essentially_off** (set 2022-08-22, never changed) |

**⚠️ Warning:** The zone's WAF is `off` and security level is `essentially_off` since 2022-08-22 — that's almost 4 years of effectively no Cloudflare-managed bot/abuse protection at the edge. If you make changes here, consider whether to tighten `security_level` to `medium` and turn WAF `on`. But: any change to security posture may break legitimate traffic patterns, so coordinate with Michael before flipping these.

**Verifying the plan tier via API:**
```bash
source ~/.hermes/profiles/orchestrator/.env
ZONE=$CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS

# Plan name from /zones
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  | python3 -c "import sys,json; r=json.load(sys.stdin)['result']; print(f\"zone plan: {r['plan']['name']} (id={r['plan']['id']})\")"

# Rate plan + entitlements from /subscription
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE/subscription" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  | python3 -c "import sys,json; r=json.load(sys.stdin)['result']; print(f\"rate plan: {r['rate_plan']['public_name']} (id={r['rate_plan']['id']})\")"
```

## How it differs from GrowthWebDev

| Property | GrowthWebDev (michael@growthwebdev.com) | Active Oahu Tours (michael@activeoahu.com) |
|---|---|---|
| **Account ID** | `196c1798da487413b0281ccc570f05a1` | `3e13f120ec7532f0bc8ac0bc9bfc7108` |
| **Zones** | 9 (humandesignengine, prismaticengine, growthwebdev, beyondsaas, ezshare, ideaforgenexus, prizeofthedamned, whatanadventure, assetforge3d) | 1 (activeoahutours) |
| **Zone plan tier** | All 9 zones on **Free Website** | **Pro** (`/zones` says "Pro Website"; `/subscription` says "Cloudflare Pro Plan") — see Plan Tier & Limits below |
| Auth method | `cfk_b7…9397` Global Key + `cfut_q…af71` Bearer | `cfk_dj…10f8` Global Key (Super Admin) |
| Primary use | SaaS products, Knowledge, AI consulting | Active Oahu Tours website (tours/rentals) |
| Env var prefix | `CLOUDFLARE_GROWTHWEB_*` | `CLOUDFLARE_AOT_*` |
| This account is referenced by | `kai.activeoahutours.com/signals` route in Prismatic Engine configs (but the zone is NOT here — see Known Failure Modes) | n/a |

**Critical:** Even though Prismatic Engine configs reference `kai.activeoahutours.com`, the `activeoahutours.com` zone IS on this AOT account (confirmed via API 2026-06-23). The Cloudflare Pages/Workers side (`kai.activeoahutours.com`) is in the GrowthWebDev account.

## Environment Variables

```bash
# In /home/ubuntu/.hermes/profiles/{fred,ned,kai,orchestrator}/.env

# AOT account (this account)
CLOUDFLARE_AOT_EMAIL=michael@activeoahu.com
CLOUDFLARE_AOT_API_KEY=cfk_dj...10f8           # Global API Key, Super Admin
CLOUDFLARE_AOT_ACCOUNT_ID=3e13f120ec7532f0bc8ac0bc9bfc7108
CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS=a8dc4f7db7ab9cea93c04ba315a7a7f7
```

These four variables are in **all four agent profiles** (`fred`, `ned`, `kai`, `orchestrator`) as of 2026-06-23. AGY inherits them through the orchestrator's `HOME` when launched by Fred/Ned.

## How to use

### Verify the account is reachable

```bash
source /home/ubuntu/.hermes/profiles/orchestrator/.env

# Verify auth (returns account details, "Super Administrator - All Privileges")
curl -s "https://api.cloudflare.com/client/v4/user" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['email'], '|', d['result']['organizations'][0]['name'])"

# List zones on this account
curl -s "https://api.cloudflare.com/client/v4/zones" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  | python3 -c "import sys,json; [print(f\"{z['name']} ({z['id']})\") for z in json.load(sys.stdin)['result']]"
```

### Read/modify DNS records

```bash
ZONE_ID=$CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS

# List DNS records
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY"

# Create or update a record (PUT replaces; POST creates)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"subdomain","content":"target.example.com","ttl":1,"proxied":true}'
```

### Update Cloudflare Tunnel ingress (if a tunnel is attached)

```bash
TUNNEL_ID=<discover via: curl -s "$URL/cfd_tunnel" with auth>
curl -s "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_AOT_ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/configurations" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY"
# Edit the config object, then PUT back as {config: <full object>}
```

For the full tunnel-fix workflow (502/1033, https→http, etc.), see the `cf-tunnel-api-config` skill — that skill already covers the AOT account as of 2026-06-23.

## Known Failure Modes

### `cfk_dj…10f8` is a Global API Key, not a Bearer token

The first attempt to test this credential failed with HTTP 401 "Invalid API Token" because the test was using `Authorization: Bearer …`. **Always use `X-Auth-Email` + `X-Auth-Key` headers with this credential.** The June 8 session log shows prior attempts used a `cfat_` Bearer token; that token was apparently rotated/expired, and the working replacement is this `cfk_` Global Key (verified Super Admin on 2026-06-23).

### The `activeoahu.com` apex domain is NOT on this account

The zone `activeoahu.com` (apex, distinct from `activeoahutours.com`) is registered to Michael but **not** in this Cloudflare account — it appears to be on Flywheel hosting (per `~/.hermes/profiles/active-oahu/memories/MEMORY.md`). Only `activeoahutours.com` is on CF.

### The `kai.activeoahutours.com` Pages site is on GrowthWebDev, not here

Prismatic Engine configs reference `kai.activeoahutours.com/signals` as a signal-ingestion endpoint, but the zone `activeoahutours.com` doesn't own a Pages deployment. The Cloudflare Pages project lives in the GrowthWebDev account. If you need to deploy to that hostname, you need BOTH the GrowthWebDev Pages creds AND a CNAME record on the AOT account pointing `kai` → the GrowthWebDev Pages URL.

### Tunnel token default

The variable `CLOUDFLARED_TUNNEL_TOKEN_GROWTH_WEB` is the GrowthWebDev tunnel token. The AOT account does not currently have a tunnel token in any `.env` file (as of 2026-06-23). If you need to spin up a tunnel for AOT, generate one in the dashboard and add it as `CLOUDFLARED_TUNNEL_TOKEN_AOT` to the four profile `.env` files.

## Re-auth procedure (if the key is revoked)

1. Log into `https://dash.cloudflare.com/?to=/:account/3e13f120ec7532f0bc8ac0bc9bfc7108/api-tokens`
2. Either:
   - **Re-use the existing Global API Key:** My Profile → API Tokens → Global API Key → "View" (it shows the value; "Roll" regenerates)
   - **Create a scoped token:** Create Token → "Edit zone DNS" template → scope to zone `activeoahutours.com` (more secure, but limits what you can do)
3. Update `/home/ubuntu/.hermes/profiles/{fred,ned,kai,orchestrator}/.env` with the new `CLOUDFLARE_AOT_API_KEY`
4. Verify: `source ~/.hermes/profiles/orchestrator/.env && curl -s "https://api.cloudflare.com/client/v4/user" -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY"`
5. If a leaked key triggered rotation, audit any transcripts / logs for the old key and scrub it (per `secret-rotation protocol` in `api-key-locations.md`)

## References

- `cf-tunnel-api-config` skill — the generic tunnel-fix workflow, now accounts-aware
- `okf/integrations/api-key-locations.md` — the master API-key registry (this file should be kept in sync)
- `okf/integrations/cloudflare-tunnel-webhooks.md` — GrowthWebDev tunnel routing
- `~/.hermes/profiles/active-oahu/memories/MEMORY.md` — domain assignments (activeoahutours.com=CF, activeoahu.com=Flywheel, yourhawaiiguide.com=Flywheel)

## History

- **2026-06-23**: AOT credentials discovered missing from all `.env` files after a profile migration (May 23 migration log shows no record of the creds being intentionally removed). User provided the working `cfk_dj…10f8` Global API Key. Verified Super Admin via API. Documented here to prevent re-discovery churn.
- **2026-06-08** (per session search): Prior session used a `cfat_…` Bearer token, which was rotated/expired by 2026-06-23.
