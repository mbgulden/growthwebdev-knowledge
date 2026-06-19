---
type: Integration
title: Ubersuggest MCP — SEO Data via Model Context Protocol
description: OAuth-authenticated MCP server exposing 38 Ubersuggest SEO tools (domain_overview, serp_analysis, backlinks_overview, etc.) over streamable HTTP. Used by Active Oahu Tours competitive sweeps and KPI tracking.
resource: https://ubersuggest-mcp.neilpatelapi.com/mcp
tags: [mcp, seo, ubersuggest, neil-patel, oauth, pkce]
timestamp: 2026-06-19T11:15:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/ubersuggest-mcp.md
last_verified: 2026-06-19
verified_by: kai
status: current
auth_method: OAuth 2.0 + PKCE
oauth_client_id: ubersuggest-mcp
oauth_authorize_url: https://ubersuggest-mcp.neilpatelapi.com/authorize
oauth_token_url: https://ubersuggest-mcp.neilpatelapi.com/token
redirect_uri: https://ubersuggest-mcp.neilpatelapi.com/callback
scope: "profile domain keywords serp backlinks site_audit content"
account_email: michael@growthwebdev.com
tier: tier1
tier_label: Individual Lifetime ($290)
token_storage: /tmp/ubs_token
refresh_token_storage: /tmp/ubs_refresh
token_ttl_seconds: 172800
---

# Ubersuggest MCP — SEO Data via Model Context Protocol

## TL;DR

The Ubersuggest MCP server (`https://ubersuggest-mcp.neilpatelapi.com/mcp`)
exposes 38 SEO tools over a single OAuth-authenticated endpoint. The
connection is live for `michael@growthwebdev.com` on an Individual
Lifetime ($290) plan. After re-auth with the correct OAuth scope on
2026-06-19, `domain_overview` returns DA 26, 1,345 organic keywords,
1,354 backlinks for `activeoahutours.com` — matching the June 2
baseline.

**The single most important thing about this integration:** the OAuth
scope must be `profile domain keywords serp backlinks site_audit content`,
NOT the standard OIDC `openid email profile`. With the wrong scope, the
token validates but every data tool returns HTTP 403 "Insufficient scope".

## Connection

- **Endpoint:** `https://ubersuggest-mcp.neilpatelapi.com/mcp`
- **Auth method:** OAuth 2.0 with PKCE (S256)
- **Client ID:** `ubersuggest-mcp`
- **Redirect URI:** `https://ubersuggest-mcp.neilpatelapi.com/callback` (browser-handled, no localhost required)
- **Required scope:** `profile domain keywords serp backlinks site_audit content`
- **Login identity:** `michael@growthwebdev.com`

### Token storage

| Token | File | TTL | Notes |
|---|---|---|---|
| Access | `/tmp/ubs_token` | 2 days (172,800s) | Bearer token for `Authorization` header |
| Refresh | `/tmp/ubs_refresh` | Until used | Single-use; rotating on refresh |
| Full response archive | `/tmp/ubs_token_response.json` | — | Includes scope + expiry metadata |

### Token transport

Use `streamablehttp_client` (NOT `sse_client` — SSE returns 401):

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async with streamablehttp_client(
    "https://ubersuggest-mcp.neilpatelapi.com/mcp",
    headers=HEADERS,
) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # ... call tools
```

**Session timeout rule:** max 3–4 tool calls per session. Run each
phase of a sweep as a separate `asyncio.run()` call.

## Tool inventory

The MCP exposes 38 tools. Tier1 (Individual Lifetime) unlocks most
data tools but **not** `site_audit*`, `traffic_value`, or `project_*`
(those require tier2+).

### Always available

| Tool | Purpose |
|---|---|
| `auth_status` | Verify login + tier |
| `validate_site` | Check if domain is reachable (param: `site`, not `domain`) |
| `search_neilpatel_blog` | Search Neil Patel's blog content |

### Domain intelligence

| Tool | Tier1? | Notes |
|---|---|---|
| `domain_overview` | ✅ | Returns `organic`, `domainAuthority`, `organicKeywords`, `backlinks`, traffic trend |
| `domain_keywords` | ✅ | Returns **raw list** (not dict with `keywords` key) |
| `domain_top_pages` | ✅ | Response key is `topPages` |
| `domain_top_countries` | ✅ | Requires `lang_locs` array of locale IDs |
| `traffic_value` | ❌ 403 | Requires tier2+ |
| `page_overview` | ✅ | Single page metrics |
| `page_keywords` | ✅ | Keywords a specific page ranks for |
| `competitors` | ✅ | Returns `competitors` array with `domain`, `commonKeywordCount`, `gapKeywordCount` |

### Keyword research

| Tool | Tier1? | Notes |
|---|---|---|
| `keyword_overview` | ✅ | Volume, CPC, SEO difficulty, paid difficulty |
| `keyword_metrics` | ✅ | Search difficulty or intent |
| `match_keywords` | ✅ | Find keywords matching seed terms |
| `keyword_suggestions` | ⚠️ Input validation bug | Known broken — see Pitfalls |
| `google_suggestions` | ✅ | Requires `keywords` as **array** (not `keyword` string) |

### SERP analysis

| Tool | Tier1? | Notes |
|---|---|---|
| `serp_analysis` | ✅ | Response key is `serpEntries` (not `serpResults`) |
| `estimate_serp_clicks` | ✅ | Per-position CTR estimation |

### Backlinks

| Tool | Tier1? | Notes |
|---|---|---|
| `backlinks_overview` | ✅ | Total backlinks, ref domains, DA, follow/nofollow split |
| `backlinks` | ✅ | Individual backlinks list |
| `anchor_texts` | ✅ | Most common anchor texts |
| `linking_domains` | ✅ | Referring domains list |
| `backlink_opportunity` | ⚠️ Input validation bug | Known broken — see Pitfalls |

### Site audit (tier2+)

| Tool | Tier1? | Notes |
|---|---|---|
| `site_audit` | ❌ 403 | Tier2+ required |
| `site_audit_status` | ❌ 403 | Tier2+ required |
| `site_audit_results` | ❌ 403 | Tier2+ required |
| `site_audit_pages` | ❌ 403 | Tier2+ required |
| `pagespeed_audit` | ❌ 403 | Tier2+ required |

### Content & projects (tier2+)

| Tool | Tier1? | Notes |
|---|---|---|
| `content_ideas` | ❌ 403 | Tier2+ required |
| `page_shares` | ❌ 403 | Tier2+ required |
| `list_projects` | ❌ 403 | Tier2+ required |
| `get_project` | ❌ 403 | Tier2+ required |
| `project_position_info` | ❌ 403 | Tier2+ required |
| `seo_opportunities` | ❌ 403 | Tier2+ required |
| `create_project` | ❌ 403 | Tier2+ required |
| `add_project_keywords` | ❌ 403 | Tier2+ required |
| `add_project_competitors` | ❌ 403 | Tier2+ required |

### Locale lookup

| Tool | Tier1? | Notes |
|---|---|---|
| `location_suggest` | ✅ | Find loc IDs by name |
| `location_details` | ✅ | Resolve multiple loc IDs at once |

## Subscription tier mapping

Ubersuggest sells 3 plans, each available monthly or as a one-time
Lifetime purchase:

| Tier | Monthly | Lifetime | Tools unlocked |
|---|---|---|---|
| **Tier 1 — Individual** | $29/mo | $290 once | Most domain/keyword/SERP/backlink tools. **No** site_audit, traffic_value, projects, AI Search Visibility beyond baseline. |
| **Tier 2 — Business** | $99/mo | $490 once | Adds site_audit (5,000 pages/week), traffic_value, projects, AI Search Visibility (10/project monthly). |
| **Tier 3 — Enterprise / Agency** | $130/mo | $990 once | Adds site_audit (10,000 pages/week), AI Search Visibility (20/project weekly), up to 15 domains. |

**This account:** `michael@growthwebdev.com` owns Individual Lifetime.
MCP backend reports `tier1`. This is correct — Individual Lifetime
legitimately maps to tier1. The `tier1` label is NOT a misclassification.

**If you need site_audit or traffic_value:** upgrade to Business Lifetime
($490) at https://app.neilpatel.com/en/pricing.

## Re-auth procedure

### When to re-auth

- Token expired (2 days after issue on this account)
- Refresh token returns `invalid_grant`
- 502 errors from `/token` endpoint (Neil Patel backend issue — retry first)
- `auth_status` returns a non-tier1 label after scope change

### Full PKCE flow (copy-paste ready)

```bash
# Step 1 — Generate PKCE verifier + challenge
python3 << 'EOF'
import base64, hashlib, os, urllib.parse

verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()

with open('/tmp/ubs_pkce_verifier', 'w') as f:
    f.write(verifier)

params = {
    "response_type": "code",
    "client_id": "ubersuggest-mcp",
    "redirect_uri": "https://ubersuggest-mcp.neilpatelapi.com/callback",
    "scope": "profile domain keywords serp backlinks site_audit content",
    "code_challenge": challenge,
    "code_challenge_method": "S256",
    "access_type": "offline",
    "login_hint": "michael@growthwebdev.com",
    "prompt": "login",
}
print(f"https://ubersuggest-mcp.neilpatelapi.com/authorize?{urllib.parse.urlencode(params)}")
EOF

# Step 2 — User opens the URL on phone, logs in, approves,
#          browser redirects to /callback?code=XXXXX
#          Copy the FULL callback URL and paste back

# Step 3 — Exchange code for tokens (write to file directly to avoid shell truncation)
CODE="<paste the code value from the callback URL>"
VERIFIER=$(cat /tmp/ubs_pkce_verifier)
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=ubersuggest-mcp" \
  --data-urlencode "code_verifier=$VERIFIER" \
  --data-urlencode "redirect_uri=https://ubersuggest-mcp.neilpatelapi.com/callback" \
  -o /tmp/ubs_token_response.json

# Step 4 — Save tokens to canonical paths
python3 << 'EOF'
import json
d = json.load(open('/tmp/ubs_token_response.json'))
open('/tmp/ubs_token', 'w').write(d['access_token'])
open('/tmp/ubs_refresh', 'w').write(d['refresh_token'])
print(f"Saved. Scope: {d['scope']}, expires in {d['expires_in']}s")
EOF
```

### Refresh (proactive, before expiry)

```bash
REFRESH=$(cat /tmp/ubs_refresh)
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=ubersuggest-mcp" \
  -d "refresh_token=$REFRESH" \
  -o /tmp/ubs_token_response.json

# Then save the new access + refresh tokens
python3 -c "
import json
d = json.load(open('/tmp/ubs_token_response.json'))
open('/tmp/ubs_token', 'w').write(d['access_token'])
open('/tmp/ubs_refresh', 'w').write(d['refresh_token'])
"
```

## Known failure modes

### The OAuth-scope trap

**Symptom:** `auth_status` returns successfully but every data tool
returns `HTTP 403 /<tool>: Insufficient scope for this endpoint.`

**Cause:** Token was issued with the standard OIDC scope
(`openid email profile`) or any subset of the required scope segments.

**Fix:** Re-auth with the full scope:
`profile domain keywords serp backlinks site_audit content`.

**Why the SKILL docs are wrong:** The skill reference doc at
`~/.hermes/profiles/kai/skills/seo/seo-competitive-audit/references/ubs-token-refresh-pkce.md`
claims the correct scope is `openid email profile`. **This is incorrect.**
That doc was authored before the scope-segments-as-feature-flags behavior
was discovered on 2026-06-19. Patch pending (GRO ticket to track).

### Tier1 ceilings (correct 403s, not bugs)

These tools require tier2+ subscriptions and will return 403 even with
the correct scope. To unlock them, upgrade the subscription.

- `site_audit`, `site_audit_status`, `site_audit_results`, `site_audit_pages`
- `pagespeed_audit`
- `traffic_value`
- `content_ideas`, `page_shares`
- `list_projects`, `get_project`, `project_position_info`, `seo_opportunities`,
  `create_project`, `add_project_keywords`, `add_project_competitors`

### Known-broken tools (input validation bugs at MCP transport layer)

- `keyword_suggestions` — throws `MCP error -32602: Input validation error`
- `backlink_opportunity` — same transport-layer rejection

Workaround: skip these in sweeps. Use `google_suggestions` (with array
param) as a `keyword_suggestions` substitute when needed.

### Shell display truncation of JWTs

**Symptom:** `cat /tmp/ubs_token` shows `ubs_oa...9ytj` instead of the
real token.

**Cause:** JWTs contain literal `.` characters that bash/shell truncates
in display. The actual file content is correct — the issue is only in
shell output formatting.

**Fix:** Read tokens via Python, not bash. Or write tokens directly via
`curl -o` and read the file rather than the curl output.

### `validate_site` param naming

`validate_site` expects parameter `site` (string), NOT `domain`. Easy
to get wrong; the error message is helpful.

### Rate limiting

After ~15–20 rapid MCP calls within a few minutes, some tools start
returning empty responses or HTTP 429. Add 0.5–1s delays between phases,
or re-run failed phases after a brief pause.

## Baseline data captured

`domain_overview(activeoahutours.com)` — 2026-06-19:

- **Domain Authority:** 26
- **Organic keywords:** 1,345
- **Backlinks:** 1,354
- **Referring domains:** 453
- **Top positions (by traffic):**
  - #4 "stand up paddleboard rental" (vol 2,400, 803 traffic)
  - #1 "active oahu" (vol 720, 294 traffic)
  - #9 "electric beach" (vol 8,100, 139 traffic)
  - #3 "sharks cove snorkeling" (vol 3,600, 124 traffic)
  - #4 "kayak rentals on oahu" (vol 320, 107 traffic)

Compared to 2026-06-02 baseline:
- DA: 26 (unchanged)
- Organic keywords: 1,345 (unchanged)
- Backlinks: 1,373 → 1,354 (-19, within normal drift)
- Ref domains: 448 → 453 (+5)
- **Movement:** Sharks Cove moved from #9 to #3 (squeeze-play opportunity confirmed)

## Related Linear issues

- KPI tracker cron job `ce817dba90d3` — errored since 2026-06-15 due to
  token expiry. Should auto-resolve on next run (2026-06-22 04:00 UTC).
- Future: patch the SKILL.md scope docs.

## Companion scripts

The following scripts depend on this integration and live in
`~/.hermes/profiles/kai/scripts/`:

- `seo_full_sweep.py` — full 7-phase competitive audit
- `kpi_tracker.py` — weekly KPI rankings tracker (cron)
- `competitor_velocity.py` — competitor content velocity monitor (cron)

All three read `/tmp/ubs_token` and follow the streamablehttp_client
pattern documented in the
[seo-competitive-audit skill](../projects/prismatic-engine.md) (well,
via the skill, not via this index).

## Citations

- [Ubersuggest pricing](https://app.neilpatel.com/en/pricing)
- [Ubersuggest MCP docs](https://app.neilpatel.com) (see MCP section)
- [Behindrankings lifetime tier reference](https://behindrankings.com)
- [OKF spec v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
