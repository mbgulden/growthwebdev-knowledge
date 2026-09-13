# Cloudflare API enumeration — working routes (multi-credential)

Condensed from the 2026-09-05 `files.growthwebdev.com` (OKF Doc Publisher) exposure
triage. Use this when you must enumerate Access policies and/or WAF rulesets across
the whole estate before deciding lock-down vs. intentional-public.

## Working read routes (verified)

| Purpose | Endpoint | Scope |
|---|---|---|
| List accounts | `GET /client/v4/accounts` | per credential |
| List zones (one account) | `GET /client/v4/zones?name=<domain>` | per credential |
| **Access apps + all policies** | `GET /client/v4/accounts/{account_id}/access/apps` | **account-level** |
| **WAF rulesets (custom+managed)** | `GET /client/v4/zones/{zone_id}/rulesets` | zone-level |
| One ruleset's rules/expressions | `GET /client/v4/zones/{zone_id}/rulesets/{ruleset_id}` | zone-level |
| Workers scripts (info) | `GET /client/v4/zones/{zone_id}/workers/scripts` | zone-level |

## Routes that 404 (do NOT call — "No route for that URI")

`/zones/{id}/waf`, `/zones/{id}/waf/*`, `/zones/{id}/httpsecurityanalysis`,
`/zones/{id}/firewall`, `/zones/{id}/security`, `/zones/{id}/securityanalytics`,
`/zones/{id}/hostnames`. The dashboard has these tabs; the API does not expose them at
those paths. WAF state lives entirely in `/rulesets`.

## Credential topology (this environment)

Env carries independent credential sets, each bound to one Cloudflare account:
- `CLOUDFLARE_GROWTHWEB_EMAIL` + `CLOUDFLARE_GROWTHWEB_API_KEY` → API-key auth
  (`X-Auth-Email` / `X-Auth-Key`).
- `CLOUDFLARE_PAGES_API_TOKEN` → bearer auth (`Authorization: Bearer`).
- `CLOUDFLARE_AOT_EMAIL` + `CLOUDFLARE_AOT_API_KEY` → separate account for the AOT domain.

The same account id (e.g. `196c17…`) can be reachable via BOTH an API key and a bearer
token — normal. A zone only resolves under its owning account's credential, so to see
every zone you must list zones under **each** credential set. `CLOUDFLARE_PAGES_ACCOUNT_ID`
/ `CLOUDFLARE_AOT_ACCOUNT_ID` name the target account but don't replace auth.

## Recurring shape

- Access app = `{ id, domain, type: self_hosted|app_launcher|warp, policies: [...] }`.
- Policy = `{ decision: allow|bypass|deny, include: [{everyone:{}} | {email:{email}} |
  {ip:{ip:"A.B.C.D/32"}}], precedence, name, created_at, updated_at }`.
- `decision: allow` + `include: everyone` = **fully public** (no challenge at all).
- `decision: bypass` + `include: everyone` = Access layer skipped for that app (public
  checkout/report/webhook paths often do this intentionally — classify before locking).
- A `files.*` "Doc Publisher" app whose only policy is `Allow Everyone` exposing a raw
  repo workspace (not a curated `published/` dir) is the classic unintended-public
  signature: created in a bulk "make it reachable" spike, never locked down.

## Probing the origin to size the exposure

`Allow Everyone`/`Bypass Everyone` means an anonymous internet visitor reaches the
origin. Measure the raw surface by hitting the tunnel origin directly (bypasses Access):
`curl 127.0.0.1:<tunnel_port>` (the local backend the tunnel points at). Read the
`/` or root JSON for the service name, mounted workspace list, and endpoint map; then
hit an enumeration endpoint (e.g. `/workspaces`, `/tree/<ws>`) to see what a stranger
can list/download. That output — not the Access config — is the real blast radius.
