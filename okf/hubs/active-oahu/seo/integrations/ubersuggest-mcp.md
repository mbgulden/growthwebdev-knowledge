---
type: Reference
title: Ubersuggest MCP Integration
description: How the Ubersuggest MCP is configured and used for the AOT SEO initiative. Token storage, scope requirements, tool inventory, common patterns.
tags: [ubersuggest, mcp, integration, reference, seo]
timestamp: 2026-06-19T13:55:00Z
linear_issue: null
git_path: okf/integrations/ubersuggest-mcp.md
status: current
resource: okf/hubs/active-oahu/seo/integrations/ubersuggest-mcp.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Ubersuggest MCP Integration

## Connection

- **Endpoint:** `https://ubersuggest-mcp.neilpatelapi.com/mcp`
- **Auth method:** OAuth 2.0 with PKCE (S256)
- **Client ID:** `ubersuggest-mcp`
- **Redirect URI:** `https://ubersuggest-mcp.neilpatelapi.com/callback`
- **Required scope:** `profile domain keywords serp backlinks site_audit content`
- **Account:** `michael@growthwebdev.com` — **Individual Lifetime ($290)**
- **Tier reports:** `tier1` (confirmed)

## Token storage

| Token | File | TTL | Refresh |
|---|---|---|---|
| Access | `/tmp/ubs_token` | 2 days (172,800s) | Use refresh token |
| Refresh | `/tmp/ubs_refresh` | Until used (rotates on use) | Full PKCE re-auth |

## Tool inventory (38 total, tier1 unlocks most)

### Always-available (tier1+)
- `auth_status` — verify login + tier
- `validate_site` — check if domain is reachable (uses `site` param, not `domain`)
- `search_neilpatel_blog` — search Neil Patel's blog

### Domain intelligence (tier1)
- `domain_overview` — DA, traffic, backlinks, organic keywords
- `domain_keywords` — top 50 organic keywords for a domain (returns raw list)
- `domain_top_pages` — top 20 pages by traffic
- `domain_top_countries` — top countries (requires `lang_locs` array)
- `page_overview` — single page metrics
- `page_keywords` — keywords a specific page ranks for

### Keyword research (tier1)
- `keyword_overview` — volume, CPC, SEO difficulty, paid difficulty
- `keyword_metrics` — search difficulty or intent
- `match_keywords` — find keywords matching seed terms
- `google_suggestions` — Google autocomplete (requires `keywords` as **array**)

### SERP analysis (tier1)
- `serp_analysis` — top 10 results for a keyword (returns `serpEntries`)
- `estimate_serp_clicks` — per-position CTR estimation

### Backlinks (tier1)
- `backlinks_overview` — total, ref domains, follow/nofollow split
- `backlinks` — individual backlinks list
- `anchor_texts` — most common anchor texts
- `linking_domains` — referring domains list

### Site audit (tier2+ — 403 on tier1)
- `site_audit`, `site_audit_status`, `site_audit_results`, `site_audit_pages` — all 403 on tier1
- `pagespeed_audit` — 403 on tier1
- `traffic_value` — 403 on tier1

### Content & projects (tier2+ — 403 on tier1)
- `content_ideas`, `page_shares` — 403
- `list_projects`, `get_project`, `project_position_info`, `seo_opportunities` — 403
- `create_project`, `add_project_keywords`, `add_project_competitors` — 403

### Known-broken tools (work at transport but return empty/error)
- `keyword_suggestions` — input validation error in MCP, use `google_suggestions` instead
- `backlink_opportunity` — input validation error, may work with right schema

## Connection pattern

Always use `streamablehttp_client` (NEVER `sse_client`):

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()
MCP_URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
MCP_HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async def call(tool, args):
    async with streamablehttp_client(MCP_URL, headers=MCP_HEADERS) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            text = result.content[0].text if result.content else "{}"
            return json.loads(text)
```

**Session timeout rule:** 3-4 tool calls max per session before streamable HTTP connection times out. Run each phase as separate `asyncio.run()`.

## Refresh procedure

Token expires every 2 days on this account. Refresh before expiry:

```bash
REFRESH=$(cat /tmp/ubs_refresh)
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=ubersuggest-mcp" \
  -d "refresh_token=$REFRESH" \
  -o /tmp/ubs_refresh_response.json
```

Save new tokens:

```python
import json
d = json.load(open('/tmp/ubs_refresh_response.json'))
open('/tmp/ubs_token', 'w').write(d['access_token'])
open('/tmp/ubs_refresh', 'w').write(d['refresh_token'])
```

## Common patterns for AOT

```python
# Get domain overview for activeoahutours.com
overview = await call('domain_overview', {'domain': 'activeoahutours.com'})

# Get top 50 organic keywords
keywords = await call('domain_keywords', {'domain': 'activeoahutours.com', 'type': 'organic', 'limit': 50})

# Get SERP for priority keyword
serp = await call('serp_analysis', {'keyword': 'kailua kayak rental', 'limit': 10})
# Returns: { 'serpEntries': [{ 'domain': '...', 'position': N, 'type': 'organic'|'ai_overview'|'...', 'clicks': N }, ...] }

# Get Google suggestions for a seed
suggestions = await call('google_suggestions', {'keywords': ['kailua kayak']})
# IMPORTANT: 'keywords' must be an array, not 'keyword' string
```

## Pitfalls (verified)

- **Auth code is single-use.** If you exchange it and get an error, you need a fresh code.
- **JWTs contain `.` characters** that bash truncates to `...`. Always write tokens to file via `curl -o` and read via Python.
- **Mobile browser cache** can reissue the same code. Add `prompt=login` to bust cache.
- **`google_suggestions` requires array param** `{'keywords': [...]}`, not `{'keyword': '...'}`.
- **`keyword_suggestions` is buggy** — use `google_suggestions` as fallback.
- **`backlink_opportunity` has transport-layer validation errors** — may not work on tier1.

## See also

- `okf/integrations/google-oauth-extended.md` — for GSC + GA4 access
- `okf/audits/baseline-2026-06-19/run_baseline_audit.py` — example sweep script
- `okf/automation/scripts/rank_tracker.py` — daily tracking using SERP API
