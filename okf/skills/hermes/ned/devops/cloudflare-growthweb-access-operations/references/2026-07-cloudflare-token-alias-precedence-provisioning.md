# Cloudflare Token Aliases — Pages/API/Bearer Precedence for PWP provisioning

Captured from the 2026-07-29 `provision_site` Phase 1 + Phase 2 work.

## The credential landscape

The Ned profile exposes multiple Cloudflare credentials in
`/home/ubuntu/.hermes/profiles/ned/.env`:

| Variable | Type | Prefix | Used for |
|---|---|---|---|
| `CLOUDFLARE_GROWTHWEB_API_KEY` | Global API key | `cfk_` | Older account-wide read/write; uses `X-Auth-Email` + `X-Auth-Key` headers, **not** Bearer |
| `CLOUDFLARE_AOT_API_KEY` | Global API key | `cfk_` | Same as above, scoped to the Active Oahu account |
| `CLOUDFLARE_PAGES_API_TOKEN` | Scoped token | `cfut_` (53 chars) | Bearer-auth; works for Pages:Read, Zone:Read, DNS:Read/Write on `michael@growthwebdev.com` |
| `CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS` | Zone ID | — | Active Oahu zone lookup helper |
| `CLOUDFLARE_AOT_ACCOUNT_ID` | Account ID | — | Active Oahu account lookup |
| `CLOUDFLARE_PAGES_ACCOUNT_ID` | Account ID | — | Pages-account lookup |

`cfut_qck...af71` (53 chars, the actual value of `CLOUDFLARE_PAGES_API_TOKEN`)
proved sufficient for the live PWP provisioner flow against real Cloudflare:

- `GET /zones?per_page=5` returned 11 zones including
  `humandesignengine.com` (zone `5bc0972595ff588618e45fda74a51128`) and
  `ezshare.systems` (zone `e520e620cbdac8ffe505cec74a276a4f`).
- `POST /zones/{id}/dns_records` for TXT creation succeeded.
- `PUT /zones/{id}/dns_records/{record_id}` for TXT update succeeded.
- `DELETE /zones/{id}/dns_records/{record_id}` for TXT cleanup succeeded.

It is **NOT** sufficient for Cloudflare Access app management (that's
`CLOUDFLARE_GROWTHWEB_API_KEY` territory).

## Token-alias precedence for `from_env()`

The PWP plugin should accept **any** of the standard Cloudflare env var
names so deployments don't have to rename their existing secrets.
Precedence order in `CloudflareClient.from_env()`:

```python
NAMES = (
    "CF_API_TOKEN",                # canonical PWP name
    "CLOUDFLARE_API_TOKEN",        # Cloudflare-docs default
    "CLOUDFLARE_PAGES_API_TOKEN",  # Ned-profile alias (Pages-scoped)
)
for name in NAMES:
    value = os.environ.get(name, "").strip()
    if value:
        return cls(token=value, _token_source=name)
raise ValueError(
    "None of " + ", ".join(NAMES) + " are set. "
    "Set one to a Cloudflare API token with Zone:Edit + DNS:Edit + "
    "Zone:Read scopes."
)
```

`_token_source` on the constructed client records which env var won,
useful for debugging "why did this resolve to the Pages token instead of
the canonical one."

## Discovery recipe

When you need to know whether a Cloudflare token is usable for the PWP
flow:

```python
import json, os, urllib.request
from pathlib import Path

# Load .env
for line in Path("/home/ubuntu/.hermes/profiles/ned/.env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ[k] = v

token = os.environ["CLOUDFLARE_PAGES_API_TOKEN"]
print("Token length:", len(token))
print("Token prefix tail:", token[-4:])  # safe-to-display tail only

# Probe 1: zones list
req = urllib.request.Request(
    "https://api.cloudflare.com/client/v4/zones?per_page=5",
    headers={"Authorization": f"Bearer {token}",
             "Content-Type": "application/json"},
)
zones = json.loads(urllib.request.urlopen(req, timeout=10).read())
print("zones:", zones["result_info"]["total_count"])
for z in zones["result"]:
    print("  ", z["name"], "id=" + z["id"][:12] + "...", "status=" + z["status"])

# Probe 2: DNS records on a known zone
if zones["result"]:
    zid = zones["result"][0]["id"]
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/zones/{zid}/dns_records?per_page=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    recs = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print(f"DNS records on {zones['result'][0]['name']}:", recs["result_info"]["total_count"])

# Probe 3: Accounts (proves Pages scope)
req = urllib.request.Request(
    "https://api.cloudflare.com/client/v4/accounts?per_page=5",
    headers={"Authorization": f"Bearer {token}"},
)
accs = json.loads(urllib.request.urlopen(req, timeout=10).read())
for a in accs["result"]:
    print("account:", a["name"], "id=" + a["id"][:12] + "...")
```

`/user/tokens/verify` confirms token validity but does **not** reveal
scopes — you have to probe actual API endpoints.

## Verifier pattern

For a fresh `hermes-verify-*` script that exercises a Cloudflare mutation
end-to-end:

1. Load the env vars with `Path(...).read_text()` line-split (NOT
   `subprocess.run(["bash", "-c", "source ...; env"])` — subshells don't
   propagate back).
2. Mask the token in any stdout display: `print("token:", token[:6] + "..." + token[-4:])`.
3. Always create the resource with a unique tag (e.g. `pwp-verify-...`
   for the challenge TXT, or include `comment: "pwp-verify ..."` on the
   DNS record) so cleanup is unambiguous.
4. Clean up the resource in a `finally` block — the user's Cloudflare
   account should not accumulate test artifacts.
5. Report the resource ID, name, and content (not the API key).

## What the EZShare live test left on Cloudflare

A `_pwp-verify.ezshare.systems` TXT record was created at zone
`e520e620cbdac8ffe505cec74a276a4f` during the 2026-07-29 Phase 2 demo:

```text
record_id: 8025287b8126aae408d9eb56479eb934
content:   pwp-verify-e4578515877c54a6
comment:   PWP provision_site domain verification (ezshare.systems live test)
ttl:       60
```

Plus the GSC placeholder TXT at the apex:

```text
record_id: cc25f603d34395b31e032a0b02081426
content:   pwp-gsc-7b9acc91cbee3162
zone_id:   e520e620cbdac8ffe505cec74a276a4f
```

These should be deleted when the demo is complete; use
`CloudflareClient.dns_delete(zone_id, record_id)`.

For `humandesignengine.com` (zone `5bc0972595ff588618e45fda74a51128`):

- The Phase 1 live-test TXT was already deleted on 2026-07-29
  (record id `a3218e4daeca168cd65daeeec115ba26`).
- No active artifacts left as of the Phase 2 run.