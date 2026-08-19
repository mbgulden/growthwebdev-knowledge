---
type: Reference
title: Google OAuth Extended Scopes (GSC + GA4)
description: OAuth scope extension procedure for accessing Google Search Console + GA4 alongside existing Drive/Gmail/Sheets/Docs scopes. Re-auth required to add webmasters.readonly + analytics.readonly.
tags: [oauth, gsc, ga4, google-api, integration, reference]
timestamp: 2026-06-19T13:50:00Z
linear_issue: null
git_path: okf/integrations/google-oauth-extended.md
status: current
resource: okf/hubs/active-oahu/seo/integrations/google-oauth-extended.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Google OAuth Extended Scopes (GSC + GA4)

## Context

Michael's `mbgulden@gmail.com` Google account has OAuth tokens saved at
`/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json`. The
current scope set is:

- ✅ `drive.file` — read/write files in Drive
- ✅ `drive.readonly` — read all Drive files (for searches)
- ✅ `gmail.readonly` — search/read Gmail
- ✅ `documents` — Google Docs API (read/write Google Docs)
- ✅ `spreadsheets` — Google Sheets API (read/write Sheets)
- ❌ `webmasters.readonly` — Google Search Console (NOT granted)
- ❌ `analytics.readonly` — Google Analytics 4 (NOT granted)

For the AOT SEO initiative, we need **GSC + GA4** access. Both APIs
return `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` with the current token.

## Re-auth procedure

To add the missing scopes WITHOUT losing the existing ones, use
`include_granted_scopes=true` in the auth URL. This keeps existing
grants and adds the new ones in the same consent flow.

### Step 1 — Generate fresh auth URL

```python
import base64, hashlib, os, urllib.parse

verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode()

with open('/tmp/google_pkce_verifier', 'w') as f:
    f.write(verifier)

params = {
    "response_type": "code",
    "client_id": "977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com",
    "redirect_uri": "http://localhost",
    "scope": "openid email profile " +
             "https://www.googleapis.com/auth/drive.file " +
             "https://www.googleapis.com/auth/drive.readonly " +
             "https://www.googleapis.com/auth/documents " +
             "https://www.googleapis.com/auth/spreadsheets " +
             "https://www.googleapis.com/auth/gmail.readonly " +
             "https://www.googleapis.com/auth/webmasters.readonly " +
             "https://www.googleapis.com/auth/analytics.readonly",
    "code_challenge": challenge,
    "code_challenge_method": "S256",
    "access_type": "offline",
    "prompt": "consent",
    "login_hint": "mbgulden@gmail.com",
    "include_granted_scopes": "true",
}

url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
print(url)
```

### Step 2 — Michael authorizes

Michael opens the URL on phone, signs in as mbgulden@gmail.com,
sees the consent screen listing ALL the scopes (existing + new
webmasters.readonly + analytics.readonly). Approves. Google redirects
to `http://localhost/?code=XXXX&scope=...`.

### Step 3 — Exchange code for tokens

```bash
CODE="<from callback URL>"
VERIFIER=$(cat /tmp/google_pkce_verifier)

curl -s -X POST "https://oauth2.googleapis.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com" \
  --data-urlencode "code_verifier=$VERIFIER" \
  --data-urlencode "redirect_uri=http://localhost" \
  -o /tmp/google_token_response.json
```

### Step 4 — Save token

```python
import json
d = json.load(open('/tmp/google_token_response.json'))
with open('/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json', 'w') as f:
    json.dump(d, f, indent=2)
print("Token scopes:", d.get('scope'))
print("Expires in:", d.get('expires_in'), 'seconds')
```

The new scope string should include both old scopes AND
`...webmasters.readonly...analytics.readonly`.

## What the new token unlocks

With webmasters.readonly + analytics.readonly, we can:

1. **List GSC sites** for `activeoahutours.com`
2. **Query GSC Search Analytics** — top queries, pages, countries, devices for last 90+ days
3. **Query GA4 Data API** — sessions, conversions, user flow for activeoahutours.com
4. **Query GA4 Realtime** — live user counts (useful for monitoring)
5. **Set up GA4 custom reports** — funnel analysis for booking flow

Combined with the existing Ubersuggest MCP, this gives us a complete
organic + on-site data picture.

## Re-auth frequency

- Google OAuth refresh tokens: ~7 days for some clients (per skill docs), but typically don't expire unless revoked
- Ubersuggest MCP token: 2 days (we refresh proactively)
- This script should auto-detect 401 responses and trigger re-auth

## Token refresh automation (future)

Build a script `okf/automation/scripts/google_token_refresh.py` that:
1. Checks if current token has webmasters.readonly scope
2. If not, alerts Kai and pauses GSC/GA4 reporting
3. Otherwise, refreshes access token using refresh_token if access_token expires in <1 hour

## Existing partial work

The pre-built pull script for GSC + GA4 already exists at:
`okf/audits/baseline-2026-06-19/pull-ga4-gsc.js`

Once the OAuth scope is extended, this script will execute all 12 sections:
- GA4 top pages, entry pages, conversion events, device/source breakdown, funnel
- GSC top queries, top pages, device/country breakdown, search appearance

Output target: `okf/audits/baseline-2026-06-19/ga4-gsc-baseline.md`
