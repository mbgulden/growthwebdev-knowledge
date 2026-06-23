---
type: Standard
title: Cloudflare Access — OKF Doc Publisher Lockdown (2026-06-23)
description: How the files.growthwebdev.com Cloudflare Access app is configured, the policies, what to do if your IP changes, and how to add new agents.
---

# Cloudflare Access — OKF Doc Publisher

The OKF Doc Publisher (`https://files.growthwebdev.com/raw/...`) is locked down behind Cloudflare Access as of 2026-06-23 13:50 UTC.

## What was done

Created Cloudflare Access app **`OKF Doc Publisher (files.growthwebdev.com)`** with id `cf2750cb-7318-48c2-a90b-5f3249fabb25` in account `196c1798da487413b0281ccc570f05a1` (GrowthWebDev on Cloudflare).

**Two allow policies, both `decision: allow`:**

| Policy name | ID | Includes |
|---|---|---|
| `Allow mbgulden@gmail.com (PIN)` | `09e90cc4-a390-476b-ba96-5ef650a31249` | `{email: {email: "mbgulden@gmail.com"}}` |
| `Allow Michael IP 65.129.148.239` | `93f41520-ab70-494f-8fdb-1d000d704549` | `{ip: {ip: "65.129.148.239/32"}}` |

**Session duration:** 24h (browser cookie)

**App config:** `self_hosted`, `app_launcher_visible: true`, `skip_interstitial: false`, domain `files.growthwebdev.com`

## What works / doesn't work

- **From allowed IP (65.129.148.239):** direct access, no login required (CF Access sees the IP and allowlists)
- **From mbgulden@gmail.com (any IP):** one-time PIN email login (existing IdP `c75c7ad6-cc78-447b-a2f7-4328792fd7e2`)
- **From anywhere else:** 302 redirect to `https://growthwebdev.cloudflareaccess.com/cdn-cgi/access/login/files.growthwebdev.com?...`

## What to do if Michael's IP changes

Run the curl below and update the policy. This is the check command:

```bash
curl -sS https://api.ipify.org
```

To update the policy:

```bash
# Get current IP
NEW_IP=$(curl -sS https://api.ipify.org)
echo "New IP: $NEW_IP"

# Update the IP policy via CF API
# (script at /home/ubuntu/.hermes/profiles/orchestrator/scripts/update_cf_access_ip.sh)
bash /home/ubuntu/.hermes/profiles/orchestrator/scripts/update_cf_access_ip.sh "$NEW_IP"
```

## How to add new agents (service tokens)

For programmatic access (e.g. a cron job or another agent that needs to fetch OKF docs), create a CF Access Service Token bound to this app. The endpoint should be:

```
POST https://api.cloudflare.com/client/v4/accounts/{acct}/access/service-tokens
```

Then bind it to the app by adding a third policy with `{service_token: {token_id: "..."}}` in the include list.

> **Note:** In my testing, this endpoint returned 404 for this Cloudflare account — possibly a permissions or tier issue. Service tokens may need to be created via the Cloudflare Dashboard UI instead. If you need one, do it manually:
> 1. Go to https://one.dash.cloudflare.com → Access → Service Auth
> 2. Create a new service token
> 3. Add the token to the OKF Doc Publisher app policies
> 4. Save the `CF-Access-Client-Id` + `CF-Access-Client-Secret` to a secret store
> 5. Pass them as headers when curling:
>    ```
>    curl -H "CF-Access-Client-Id: ..." -H "CF-Access-Client-Secret: ..." https://files.growthwebdev.com/raw/...
>    ```

## Why no auth on the local publisher (port 9120)

The local publisher at `http://127.0.0.1:9120/raw/...` does NOT have auth — but it's only bound to localhost. Anything reaching it from outside would have to come through the Cloudflare tunnel, which now enforces Access. So the stack is: CF Access (auth) → Cloudflare tunnel → localhost:9120 (no auth) → workspace files.

## Files

- Linear task: [GRO-2199](https://linear.app/growthwebdev/issue/GRO-2199) (marked Done 2026-06-23)
- CF API used: `CLOUDFLARE_GROWTHWEB_API_KEY` in `/home/ubuntu/.hermes/profiles/orchestrator/.env`
- Account ID: `196c1798da487413b0281ccc570f05a1`
- Zone: `b008d11093f4852e7aae67e28c76c0f5`
- App ID: `cf2750cb-7318-48c2-a90b-5f3249fabb25`