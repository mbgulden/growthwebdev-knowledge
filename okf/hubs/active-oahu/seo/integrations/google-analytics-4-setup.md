---
type: Reference
title: Google Analytics 4 (GA4) Setup Procedure for AOT
description: Step-by-step procedure for granting Kai access to Google Analytics 4 data for activeoahutours.com. Requires OAuth scope extension OR GCP project config to enable Analytics API.
tags: [ga4, google-analytics, oauth, integration, on-site-analytics]
timestamp: 2026-06-19T15:55:24Z
linear_issue: null
git_path: okf/integrations/google-analytics-4-setup.md
status: current
resource: okf/hubs/active-oahu/seo/integrations/google-analytics-4-setup.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Google Analytics 4 (GA4) Setup Procedure for AOT

## Why GA4 matters for AOT SEO

GA4 gives us **on-site behavior data** that GSC cannot:
- What users DO after landing (clicks, scrolls, form fills)
- Booking funnel (visits → "Book Online" → FH.open → completed booking)
- Conversion attribution (which organic keywords drive bookings, not just clicks)
- Engagement metrics (bounce rate, time on page, pages per session)
- Traffic by hour of day (when users are most engaged)
- New vs returning users

## Discovered configuration

**GA4 Property ID:** `G-PRRRLMBR8Z` (confirmed in HTML gtag config across multiple AOT pages on 2026-06-19)

```
gtag("config", "G-PRRRLMBR8Z");
```

This is the property to query once access is granted.

## Current state

- **OAuth scope:** `analytics.readonly` is NOT in current token
- **GCS Analytics API:** NOT enabled in GCP project (matches what happened with previous scope extension attempt)
- **Cloudflare Account #2:** AOT zone is in michael@activeoahu.com account, NOT accessible from orchestrator env
- **Workaround needed:** Enable Analytics API in GCP project, then re-auth

## Step 1: Enable Analytics Data API in GCP project

1. Find the GCP project that hosts the OAuth client:
   - Client ID: `977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com`
   - Project ID: discoverable via OAuth client credentials page in GCP console

2. Open the API Library for this project:
   ```
   https://console.cloud.google.com/apis/library/analytics.googleapis.com?project=<PROJECT_ID>
   ```

3. Click **ENABLE**

4. Wait ~1 minute for the API to provision

## Step 2: Generate auth URL with analytics.readonly

Kai will generate a fresh auth URL including `analytics.readonly` scope:

```
https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost&scope=openid+email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.file+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdocuments+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fwebmasters.readonly+https%3A%2F%2Fwww.googleapis.com%2Fanalytics.readonly&code_challenge=<PKCE_VERIFIER>&code_challenge_method=S256&access_type=offline&prompt=consent&login_hint=mbgulden%40gmail.com&include_granted_scopes=true
```

The PKCE verifier is fresh and saved at `/tmp/google_pkce_verifier_analytics`.

## Step 3: Michael authorizes

Michael:
1. Opens the URL on phone
2. Logs in as mbgulden@gmail.com
3. Sees consent screen listing all existing scopes + analytics.readonly
4. Approves
5. Browser redirects to `http://localhost/?code=XXXX`
6. Sends the full URL to Kai

## Step 4: Kai exchanges code for tokens

```bash
curl -s -X POST "https://oauth2.googleapis.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com" \
  --data-urlencode "client_secret=REDACTED__SEE__/home/ubuntu/.config/mcp-gdrive/ (re-auth via okf/hubs/active-oahu/seo/integrations/google-oauth-extended.md)" \
  --data-urlencode "code_verifier=$(cat /tmp/google_pkce_verifier_analytics)" \
  --data-urlencode "redirect_uri=http://localhost" \
  -o /tmp/google_token_response_ga4.json
```

Token response saved to existing `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json`.

## Step 5: Discover GA4 Property ID

Once token has analytics.readonly:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://analyticsadmin.googleapis.com/v1beta/accountSummaries"
```

Returns list of accounts and their GA4 properties. Look for the one matching `activeoahutours.com` or `active oahu tours`.

## Step 6: Pull GA4 data

```bash
PROPERTY_ID="<discovered_property_id>"
curl -s -X POST "https://analyticsdata.googleapis.com/v1beta/properties/$PROPERTY_ID:runReport" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dateRanges": [{"startDate": "2026-03-21", "endDate": "2026-06-16"}],
    "dimensions": [{"name": "pagePath"}],
    "metrics": [{"name": "sessions"}, {"name": "engagementRate"}, {"name": "averageSessionDuration"}],
    "limit": 100
  }'
```

## GA4 reports to pull (priority order)

### Report 1: Top 20 pages by sessions (last 90 days)

- dimensions: pagePath, pageTitle
- metrics: sessions, totalUsers, engagementRate, avgSessionDuration, conversions
- Use case: validate GSC top pages ranking with actual engagement

### Report 2: Booking funnel (CRITICAL)

- Event flow: page_view → click_book_online → fh_widget_open → fh_widget_complete → purchase
- Use case: identify drop-off points in booking flow
- Need GA4 events set up correctly for this

### Report 3: Top 10 entry pages

- dimensions: pagePath
- metrics: sessions, bounceRate
- Use case: which pages retain users best

### Report 4: Acquisition by organic keyword (via GSC integration)

- dimensions: sessionDefaultChannelGroup, sessionSource
- metrics: sessions, conversions
- Use case: validate SEO is actually driving conversions

### Report 5: Hour-of-day traffic

- dimensions: hour
- metrics: sessions, conversions
- Use case: when to publish content, when to monitor

### Report 6: New vs returning users

- dimensions: newVsReturning
- metrics: sessions, conversions, revenue
- Use case: brand strength vs new acquisition

### Report 7: Top events

- dimensions: eventName
- metrics: eventCount, conversions
- Use case: what users actually click

### Report 8: User journey (path exploration)

- dimensions: pagePath
- metric: sessions
- sort by events
- Use case: most common navigation paths

## GA4 event setup recommendations (for AOT)

Recommended event taxonomy:

| Event | Trigger | Conversion value |
|---|---|---|
| `view_item` | Tour/rental page view | $0 |
| `select_content` | "Book Online" CTA click | $0 |
| `begin_checkout` | FH widget opens | $0 |
| `add_payment_info` | Payment step in FH | $0 |
| `purchase` | Booking confirmed | (booking value) |
| `generate_lead` | Email signup, phone call | $5 |
| `search` | Site search used | $0 |

Setup in GA4 admin → Events → Create event.

## GA4 conversion events to set up

For the AOT booking funnel to be tracked properly:

1. **`purchase`** — when booking completes (FareHarbor webhook → GA4 Measurement Protocol)
2. **`generate_lead`** — phone call tap or email submit
3. **`begin_checkout`** — when FH widget opens

These need FareHarbor's webhook integration OR manual GTM setup.

## Implementation status

| Step | Status | Blocker |
|---|---|---|
| 1. Enable Analytics API in GCP | pending | Michael action |
| 2. Generate auth URL | done | – |
| 3. Michael authorizes | pending | Michael action |
| 4. Kai exchanges code | ready to run | – |
| 5. Discover Property ID | ready | – |
| 6. Pull GA4 data | ready | – |

---

*Setup procedure documented by Kai on 2026-06-19.*


## Quick verification (once GA4 access granted)

```bash
TOKEN=$(jq -r .access_token /home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json)
PROPERTY="G-PRRRLMBR8Z"
# Convert GA4 Property ID to numeric form
PROP_NUM=$(echo "$PROPERTY" | tr -d 'G-')

# Quick test: top pages by sessions, last 30 days
curl -s -X POST "https://analyticsdata.googleapis.com/v1beta/properties/$PROP_NUM:runReport" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dateRanges": [{"startDate": "30daysAgo", "endDate": "yesterday"}],
    "dimensions": [{"name": "pagePath"}],
    "metrics": [{"name": "sessions"}, {"name": "totalUsers"}],
    "limit": 20
  }'
```

This is the first call to make once access is granted.

---

*Updated 2026-06-19 with discovered GA4 Property ID G-PRRRLMBR8Z.*
