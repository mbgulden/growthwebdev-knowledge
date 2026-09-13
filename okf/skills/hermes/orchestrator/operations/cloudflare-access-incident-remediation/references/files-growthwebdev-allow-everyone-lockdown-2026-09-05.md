# Worked Example — files.growthwebdev.com Allow-Everyone Lock-Down (2026-09-05)

Full remediation of an OKF Doc Publisher app that was exposing the entire
artifact-publisher tree to the public. Captures the concrete moves a future
session can copy.

## Discovery / exposure sizing

- Account: `196c1798da487413b0281ccc570f05a1` (GrowthWeb). Credentials:
  `CLOUDFLARE_GROWTHWEB_EMAIL` + `CLOUDFLARE_GROWTHWEB_API_KEY` (API-key pair) and
  `CLOUDFLARE_PAGES_API_TOKEN` (bearer) both see this account.
- App: `files.growthwebdev.com`, type `self_hosted`, Access app id
  `cf2750cb-7318-48c2-a90b-5f3249fabb25`. Its ONLY policy was
  `Allow Everyone` (`decision: allow`, `include: {everyone: {}}`, precedence 1),
  created 2026-06-23, never updated.
- Tunnel `cloudflared-growthweb.service` routes the hostname to
  `http://127.0.0.1:9120` = `hermes-artifact-publisher` (uvicorn).
- **Origin probe** (`curl 127.0.0.1:9120`, bypasses Access) showed the public
  surface under `Allow Everyone`:
  - `/` → service name, version, workspace list, endpoint map.
  - `/workspaces` → **full local file paths** on the host + which dirs exist.
  - `/tree/{workspace}` → recursive listing (filenames, sizes, mtime, content-type).
  - `/download/...` → actual file bytes.
  - Four workspaces mounted: `published` (absent at the time), `hermes-research-reports`,
    `prismatic-engine` (whole repo + scratch), `agentic-swarm-ops`.
- Read: **not intentional** — mounted the raw `prismatic-engine` repo, not a curated
  OKF output; created in the same afternoon as the other Access apps (copy-paste
  "make it reachable" spike). No top-level `.env` in the repo, but not a deep secret sweep.

## The fix (dual-identity)

Replaced the single `Allow Everyone` policy with a two-policy precedence set and PUT the
whole app back:

```
PUT /accounts/196c1798da487413b0281ccc570f05a1/access/apps/cf2750cb-7318-48c2-a90b-5f3249fabb25
policies:
  [1] Bypass Fred Server IP   decision=bypass  include={ip:{ip:"65.129.148.239/32"}}
  [2] Allow mbgulden@gmail.com (PIN)  decision=allow  include={email:{email:"mbgulden@gmail.com"}}
```

- Server egress IP captured with `curl https://api.ipify.org` (65.129.148.239). It is a
  snapshot — if the host's public IP changes, re-issue policy [1].
- PUT succeeded with the full app object; stripped `app_launcher` /
  `public_key_certificate` / `service_token_key_id` from the payload.

## Verification (all three)

- Anonymous (non-listed IP) `/` → now `302` to
  `growthwebdev.cloudflareaccess.com/cdn-cgi/access/login/files.growthwebdev.com`
  (was `200` before). Cannot spoof a foreign src IP, so the authoritative "anonymous
  locked" check = account-level re-read confirms **no** `include: {everyone}` remains.
- From the server IP (65.129.148.239) → still `200`; `/workspaces` works (bypass intact).
- `GET /.well-known/cloudflare-access-protected-resource/` → `"protected": true`.
- `GET /accounts/{acc}/access/apps/{app}` re-read → policies exactly the two intended.

## Notes / adjacent

- The 4 workspace mounts were left unchanged (nothing the user was using breaks); only
  visibility to the public was removed. Optional follow-up: trim mounts to just
  `published/` so even the owner sees only curated output.
- The app was one of 11 in the account; the same enumeration (`GET /accounts/{acc}/access/apps`)
  surfaced the other `Bypass Everyone` apps (HDE demo signup, checkout/report paths) which
  are **intentional** public paths — do not reflexively lock those (see
  `cf-access-expected-public-bypass-classification.md`).
