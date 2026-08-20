---
name: cloudflare-security-event-check
category: devops
description: Guide for manually checking Cloudflare Security Events in the dashboard, especially for Pro plans.
---

Authoritative documentation: <https://developers.cloudflare.com/analytics/graphql-api/>

Support files:
- `references/cloudflare-credentials.md` — Active Oahu Tours Cloudflare account IDs, tokens, and API endpoints

This skill outlines the manual steps to investigate Cloudflare Security Events within the dashboard, particularly for accounts on the Pro plan where direct API access to full logs with Ray ID filtering might be limited.

## Goal
Identify triggered WAF or rate-limiting rules, and confirm bot exemptions for specific requests using Ray IDs and timestamps.

## Prerequisites
- Access to the Cloudflare dashboard for the target domain (`activeoahutours.com`).
- Specific audit timestamps and (if available) Ray IDs to investigate.

## Steps

1.  **Log in to Cloudflare:**
    *   Go to [https://dash.cloudflare.com/](https://dash.cloudflare.com/) and log in with your credentials.

2.  **Navigate to Security Events:**
    *   From the dashboard, select the target domain (`activeoahutours.com`).
    *   In the left-hand navigation menu, click on **Security** > **Events**.

3.  **Set Timeframe:**
    *   Use the date/time picker at the top right of the Security Events page.
    *   Select a **Custom Range** that encompasses the audit timestamps you are investigating. Be as precise as possible.

4.  **Filter by Ray ID (if available):**
    *   In the filters section (usually on the left or top of the events list), look for an option to filter by "Ray ID" or "Request ID".
    *   Enter the specific Ray ID(s) provided in the audit report.

5.  **Identify Triggered Rules:**
    *   Review the displayed security events. Pay attention to the "Action Taken" and "Rule ID/Description" columns.
    *   Note down the specific WAF rule(s) or rate-limit/challenge rule(s) that were triggered for the requests you are investigating.

6.  **Confirm Verified Bot Exemptions:**
    *   Examine the details of the triggered rules.
    *   Look for any explicit exemptions for "known bots," "verified bots," or specific User-Agents (like Googlebot, Bingbot). This might be configured directly within the rule settings or in a separate "WAF" or "Firewall Rules" section.
    *   Some general settings for bot management might also exist under **Security** > **Bots** (if available on the Pro plan).
## Reporting Findings

After completing these steps, provide the following information:

*   The **exact names/IDs of the triggered WAF or rate-limit rules.**
*   Details on **how verified bots (Googlebot/Bingbot) are handled** by these rules (exempt, challenged, blocked).
*   Any **screenshots** that clearly illustrate the triggered rules and bot exemption settings.

## API Access for Firewall Events (Programmatic)

### Authentication Methods

| Credential Type | Auth Headers | Used For |
|----------------|--------------|----------|
| Global API Key | `X-Auth-Email: <email>` + `X-Auth-Key: <key>` | Legacy REST API (v4) |
| API Token | `Authorization: Bearer <token>` | GraphQL API + modern REST |

**Critical:** The GraphQL API (`https://api.cloudflare.com/client/v4/graphql`) **requires an API Token**, not a Global API Key. Using Global API Key headers with Bearer auth will return `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}`.

### Existing API Tokens

List existing tokens (returns metadata only, not values):
```bash
curl -sS -X GET "https://api.cloudflare.com/client/v4/user/tokens" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  -H "Content-Type: application/json" | jq '.result[] | {id, name, status}'
```

**Token value is NEVER retrievable after creation** — Cloudflare does not return token values in API responses. If no pre-existing token with suitable permissions exists, you cannot retrieve its value programmatically.

**Search for tokens in environment and files:**
```bash
# Check env vars
env | grep -i "cloudflare\|cfut_\|cfat_"

# Search for token patterns in files (cfut_ = API token, cfat_ = older token)
grep -r "cfut_\|cfat_" ~/.hermes/profiles/ 2>/dev/null | head -10
grep -r "kf:" ~/.hermes/profiles/ 2>/dev/null | head -10  # OLD pattern

# Check .env files
grep -l "CLOUDFLARE.*TOKEN" ~/.hermes/profiles/*/.env 2>/dev/null
```

### Create API Token via API — NOT POSSIBLE with Global API Key alone

**CRITICAL CORRECTION:** You CANNOT create API tokens using only the Global API Key. The `POST /client/v4/user/tokens` endpoint requires a valid existing API token with `User Tokens: Edit` permissions as a Bearer token. The Global API Key only works with `X-Auth-Email` + `X-Auth-Key` headers for legacy REST endpoints, and cannot authenticate to the token creation API.

**Consequence:** If no pre-existing API token with `User Tokens: Edit` permissions exists, you cannot create one programmatically. Options:
1. Michael creates a token manually in the Cloudflare dashboard with the required permissions
2. Use the legacy REST API endpoints that support Global API Key authentication (limited — does not include GraphQL or Ray ID filtered logs)
3. For Pro plans, use manual dashboard with date/time filtering (Ray ID filtering is Enterprise-only)

**Pro plan limitation for log filtering:** Full filterable logs by Ray ID via API is an **Enterprise feature only**. Pro plans have limited log data accessible via dashboard, but programmatic Ray ID filtering is not available. For Pro plan investigations, use manual dashboard checks with timestamp-based filtering.

### IP Access Rules (Global API Key only)

```bash
curl -sS -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "query": "query ListFirewallEvents($zoneTag: string, $filter: FirewallEventsAdaptiveFilter_InputObject) { viewer { zones(filter: { zoneTag: $zoneTag }) { firewallEventsAdaptive( filter: $filter limit: 100 orderBy: [datetime_DESC] ) { action clientAsn clientCountryName clientIP clientRequestPath clientRequestQuery datetime source userAgent rayId } } } }",
    "variables": {
      "zoneTag": "$CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS",
      "filter": {"datetime_geq": "'$START_TIME'", "datetime_leq": "'$END_TIME'"}
    }
  }'
```

### IP Access Rules (Global API Key only)

```bash
# Create whitelist rule for IP bypass
curl -sS -X POST "https://api.cloudflare.com/client/v4/firewall/access_rules/rules" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "mode": "whitelist",
    "configuration": {"target": "ip", "value": "YOUR_IP"},
    "notes": "Temporary bypass for Hermes Agent"
  }' | jq '.result'

# Delete rule
curl -sS -X DELETE "https://api.cloudflare.com/client/v4/firewall/access_rules/rules/$RULE_ID" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY"
```

### Cloudflare Zone/Account IDs (Active Oahu Tours)

- Zone ID: `a8dc4f7db7ab9cea93c04ba315a7a7f7` (activeoahutours.com)
- Zone tag same as Zone ID for GraphQL queries
