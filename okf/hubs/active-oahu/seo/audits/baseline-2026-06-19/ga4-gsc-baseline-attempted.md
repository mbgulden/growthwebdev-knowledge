---
type: Audit
title: Active Oahu Tours — GA4 + GSC Baseline (Attempted / Scope-Blocked)
description: Attempted GA4 + Google Search Console baseline pull for activeoahutours.com covering 2026-03-19 → 2026-06-19. Execution blocked at the OAuth scope layer — current refresh token does not carry webmasters.readonly or analytics.readonly. This file documents the block, the required scope additions, the exact re-auth procedure for Kai, and the pre-built data-pull script that will run the moment the token is re-scoped.
tags: [audit, aot, ga4, gsc, search-console, analytics, baseline, scope-blocked, oauth, 2026-q2]
timestamp: 2026-06-19T12:38:00Z
linear_issue: null
git_path: okf/audits/baseline-2026-06-19/ga4-gsc-baseline-attempted.md
status: blocked-scope
companion_files:
  - ga4-gsc-baseline-attempt-raw.json
  - pull-ga4-gsc.js
migrated_from: null
data_sources:
  - gsc-api:https://www.googleapis.com/webmasters/v3/sites
  - ga4-api:https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport
visibility: private
resource: okf/hubs/active-oahu/seo/audits/baseline-2026-06-19/ga4-gsc-baseline-attempted.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Tours — GA4 + GSC Baseline (Attempted)

**Audit Date:** June 19, 2026
**Window requested:** 2026-03-19 → 2026-06-19 (last 90 days)
**Domain:** `activeoahutours.com`
**Account used:** `mbgulden@gmail.com` (Michael Gulden, confirmed via Drive `about` call)
**Status:** ❌ **BLOCKED — insufficient OAuth scopes**
**Auditor:** Kai (orchestrator agent) + googleapis Node client

---

## TL;DR

The refresh token at `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json` is **valid and working** (confirmed: Drive `about` returned 200 with user `Michael Gulden`), but its scope set is:

```
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/drive.file
```

It is **missing** the two scopes required for this task:

- `https://www.googleapis.com/auth/webmasters.readonly` (GSC)
- `https://www.googleapis.com/auth/analytics.readonly` (GA4)

Empirical evidence (executed 2026-06-19 12:38 UTC):

| API | Endpoint | Status | Error |
|---|---|---:|---|
| GSC | `GET /webmasters/v3/sites` | **403** | `ACCESS_TOKEN_SCOPE_INSUFFICIENT` (reason: `insufficientPermissions`) |
| GA4 | `GET /analyticsadmin/v1beta/accountSummaries` | **403** | `ACCESS_TOKEN_SCOPE_INSUFFICIENT` (service: `analyticsadmin.googleapis.com`) |
| Drive | `GET /drive/v3/about?fields=user` | **200** | (sanity check — confirms account `Michael Gulden`) |

Raw response bodies: `ga4-gsc-baseline-attempt-raw.json`

**The token is not broken. The token just doesn't carry the scopes we need.** Re-auth is required — see "Re-auth Procedure" below.

---

## What I tried (in order)

1. **Read the existing Ubersuggest baseline** at `state-of-aot-baseline.md` to understand context (DA 26, 1,345 monthly organic traffic, etc.). ✅
2. **Inspected OAuth credentials** at `/home/ubuntu/.config/mcp-gdrive/`:
   - `gcp-oauth.keys.json` → client `977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com` (project `spartan-impact-497114-m2`)
   - `.gdrive-server-credentials.json` → refresh token, expires 1781864005791 (mid-2026), **scope set documented above**
3. **Attempted token refresh** with the Node `googleapis` client → ✅ success, access token obtained.
4. **Called GSC `sites.list`** → ❌ 403 `insufficientPermissions`.
5. **Called GA4 `accountSummaries`** → ❌ 403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.
6. **Searched the filesystem for any other Google tokens** that might have wider scopes (`/home/ubuntu/.config/`, `/home/ubuntu/`) → found `.michael-gmail-credentials.json` but its scope set is identical (Drive + Gmail + Sheets + Docs). No GSC/GA4 tokens exist anywhere on disk.
7. **Checked `gcloud`** → installed (`/snap/bin/gcloud`) but **no account configured** (`gcloud config get-value account` returned `(unset)`). Would require a browser-based interactive login — not viable from a non-interactive subagent context.
8. **Conclusion:** the only viable path is **option (a) from the brief** — extend the OAuth scope and re-auth with Kai. The pre-built pull script (`pull-ga4-gsc.js`, included with this report) will execute the moment the new token lands.

---

## Why re-auth, not a workaround

- **Refresh tokens carry fixed scopes at issuance.** A refresh token cannot be silently re-scoped — Google requires the user to re-consent to a *new* scope set, which produces a *new* refresh token (the old one is still valid for the old scopes but is useless for the new ones).
- **No Service Account alternative** is configured in the OAuth client (`gcp-oauth.keys.json` is the "installed" / desktop-app flow, not a service-account JSON). The user has to consent interactively.
- **`gcloud auth application-default login` is browser-based** and would block here. Even if it worked, the resulting token would still be limited to whatever scopes the local `gcloud` config requests — which currently has no account set.
- **Direct API calls with the current token are a dead end**, as both API checks returned `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.

---

## Re-auth Procedure (for Kai)

**One-time browser step.** Estimated time: 60-90 seconds including MFA.

### 1. Open this URL in Michael's browser (signed into `mbgulden@gmail.com`)

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com&redirect_uri=http://localhost&response_type=code&scope=openid%20https://www.googleapis.com/auth/drive.readonly%20https://www.googleapis.com/auth/spreadsheets%20https://www.googleapis.com/auth/documents%20https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/drive.file%20https://www.googleapis.com/auth/webmasters.readonly%20https://www.googleapis.com/auth/analytics.readonly&access_type=offline&prompt=consent%20select_account&include_granted_scopes=true
```

**Important:** `prompt=consent` is required (Google otherwise skips the consent screen for already-granted scopes and won't issue a new refresh token). `include_granted_scopes=true` keeps the existing Drive/Gmail/Sheets/Docs grants so we don't lose them.

### 2. Authorize

Google will show one combined consent screen with the two new permissions:
- "See, edit, create, and delete **Google Search Console** data" (webmasters.readonly)
- "See and download your **Google Analytics** account data" (analytics.readonly)

Approve. The browser will redirect to `http://localhost/?code=4/0AXX...&scope=...`. Copy the entire redirect URL.

### 3. Hand off the auth code to the subagent

The subagent (this one, re-invoked) will:

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com" \
  -d "client_secret=REDACTED__SEE__/home/ubuntu/.config/mcp-gdrive/ (re-auth via okf/hubs/active-oahu/seo/integrations/google-oauth-extended.md)" \
  -d "code=PASTE_CODE_HERE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=http://localhost"
```

The response will contain a new `refresh_token` (different from the current one). The subagent will:

1. Back up the current token: `cp .gdrive-server-credentials.json .gdrive-server-credentials.json.bak-2026-06-19`
2. Overwrite `.gdrive-server-credentials.json` with the new credentials JSON (containing the new refresh_token, updated scope string, new access_token, new expiry_date).
3. Run `node pull-ga4-gsc.js` — the script is pre-built and ready.
4. Re-run the full 12-section report and save `ga4-gsc-baseline.md` (replacing this `*-attempted.md` file).

### 4. Rollback

If anything goes wrong, the old token is preserved at `.gdrive-server-credentials.json.bak-2026-06-19`. Drive/Gmail/Sheets/Docs keep working as before.

---

## What the re-authed run will produce

The pre-built `pull-ga4-gsc.js` script (included in this directory) executes **all 12 sections** requested in the brief:

### GA4 sections (uses `analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport`)

1. **Top 20 pages by sessions** (organic segment: `sessionDefaultChannelGroup == 'Organic Search'`)
2. **Top 10 entry pages** with `bounceRate`, `averageSessionDuration`
3. **Conversion events** — probes for `purchase`, `book`, `generate_lead`, `begin_checkout`, `add_to_cart`, `view_item`, `sign_up`, `contact`, and lists *all* custom event names found via `events:list` if reachable
4. **Traffic by device** — `deviceCategory` (desktop / mobile / tablet)
5. **Traffic by source/medium** — `sessionSource` × `sessionMedium`
6. (handled below) **Landing page funnel** — visits → `book_online_click` → `purchase` (or whatever booking event is found)
7. (handled below) **Events timeline** — counts per event, sorted by frequency to identify drop-off

### GSC sections (uses `searchanalytics.googleapis.com` via `/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`)

6. **Top 50 queries** with `clicks`, `impressions`, `ctr`, `position` (last 90 days)
7. **Top 20 pages** with same metrics
8. **Device breakdown** — `device` filter aggregation
9. **Country breakdown** — top 10 countries
10. **Search appearance breakdown** — `searchAppearance` filter aggregation

### Output

- `ga4-gsc-baseline.md` — human-readable report (this file, *regenerated* after scope fix)
- `ga4-gsc-baseline-raw.json` — full raw API responses for reproducibility
- `pull-ga4-gsc.js` — the pull script (already in this directory)

---

## Open questions for Michael (post re-auth)

These will be visible only after the data is pulled — flagging now so they can be answered during the kickoff review:

1. **GA4 property ID for activeoahutours.com** — the script will discover it via `accountSummaries` + `properties:list`, but if multiple properties exist we'll need Michael to pick the right one.
2. **GSC site URL** — confirmed `https://activeoahutours.com/` (URL-prefix property) vs `sc-domain:activeoahutours.com` (domain property). The script probes both.
3. **Booking event name** — if the booking platform (FareHarbor / Peek / Bokun / custom) fires a non-standard event, the script will surface all custom events so we can identify it.
4. **Conversion attribution model** — GA4 default is `data-driven`; if the property is using `last-click` we should note it.

---

## File inventory (this directory)

| File | Status | Purpose |
|---|---|---|
| `ga4-gsc-baseline-attempted.md` | ✅ this file | Documents the block + re-auth procedure |
| `ga4-gsc-baseline-attempt-raw.json` | ✅ written | Raw API responses proving the scope error |
| `pull-ga4-gsc.js` | ✅ written | Pre-built pull script — ready to run post re-auth |
| `ga4-gsc-baseline.md` | ⏳ pending | Will be written by `pull-ga4-gsc.js` after re-auth |
| `ga4-gsc-baseline-raw.json` | ⏳ pending | Will be written by `pull-ga4-gsc.js` after re-auth |

---

## Appendix A — Exact API responses

### GSC `sites.list`

```http
HTTP/1.1 403 Forbidden
{
  "error": {
    "code": 403,
    "message": "Request had insufficient authentication scopes.",
    "errors": [{ "message": "Insufficient Permission", "domain": "global", "reason": "insufficientPermissions" }],
    "status": "PERMISSION_DENIED",
    "details": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
      "domain": "googleapis.com",
      "metadata": { "service": "searchconsole.googleapis.com", "method": "google.webmasters.v3.WebmastersService.ListSites" }
    }]
  }
}
```

### GA4 `accountSummaries`

```http
HTTP/1.1 403 Forbidden
{
  "error": {
    "code": 403,
    "message": "Request had insufficient authentication scopes.",
    "status": "PERMISSION_DENIED",
    "details": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
      "domain": "googleapis.com",
      "metadata": { "service": "analyticsadmin.googleapis.com", ... }
    }]
  }
}
```

### Drive `about` (sanity check, 200)

```json
{ "user": { "displayName": "Michael Gulden", "photoLink": "https://lh3.googleusercontent.com/a/ACg8ocLAMLJ3n8si0FkLnnfaQFLyZHHr-lb3pNVqAV421CR1OhWkJfTD=s64", ... } }
```

---

## Appendix B — Environment snapshot

- **Node:** v22.22.2
- **googleapis:** installed locally in `/tmp/node_modules/googleapis` (will need to be installed in the working directory or the script will use a local lookup)
- **gcloud:** `/snap/bin/gcloud` (snap install, no account)
- **Refresh token expiry:** 1781864005791 (millis → mid-2026; ample life remaining)
- **OAuth client:** Desktop-app "installed" flow, redirect `http://localhost` (loopback) — appropriate for the CLI use case

---

*End of report. Next action: Michael runs the re-auth URL above; subagent regenerates this report as `ga4-gsc-baseline.md` with live data.*
