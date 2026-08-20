# Ubersuggest MCP — Tier × Tool Matrix

Distinguishes "scope bug" 403s (re-auth fixes) from "tier ceiling" 403s (need
upgrade or support ticket). Verified on `michael@growthwebdev.com` Individual
Lifetime account (tier1) on 2026-06-19.

## The 60-second diagnostic

After any re-auth or any 403:

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async def diagnose():
    async with streamablehttp_client(
        "https://ubersuggest-mcp.neilpatelapi.com/mcp", headers=HEADERS
    ) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            auth = await session.call_tool("auth_status", {})
            print(auth.content[0].text)
            dom = await session.call_tool("domain_overview", {"domain": "activeoahutours.com"})
            text = dom.content[0].text
            print("OK" if not text.startswith("Error") else f"FAIL: {text[:120]}")
asyncio.run(diagnose())
```

**Expected output on a healthy connection:**
```
Logged in as michael@growthwebdev.com
Tier: tier1
OK
```

**Failure mode 1 — auth shows tier1, `domain_overview` 403s:**
**Scope bug.** Re-auth with `scope = "profile domain keywords serp backlinks site_audit content"`.
See `references/ubs-token-refresh-pkce.md` → "OAuth Scope Controls Tool Access."

**Failure mode 2 — auth shows tier1, `domain_overview` works, but `site_audit` 403s:**
**Tier ceiling, not a bug.** tier1 legitimately doesn't include `site_audit*`,
`traffic_value`, `project_*`, `content_ideas`, `page_shares`. Either:
- Upgrade plan ($290 → $490 Business Lifetime), or
- Open a support ticket if you think you should already be on a higher tier.

**Failure mode 3 — auth shows "Tier: free":**
**Account has no paid subscription backing the requested scopes.** Either the
subscription lapsed or the wrong account is authenticated. Re-auth won't fix
this — only a paid subscription will.

## Full tool × tier matrix

Verified 2026-06-19. 38 total tools.

### Always available (any tier)

| Tool | Purpose |
|---|---|
| `auth_status` | Verify login + tier label |
| `validate_site` | Check if domain is reachable (`site` param, NOT `domain`) |
| `search_neilpatel_blog` | Search Neil Patel's blog |
| `location_suggest` | Find locale IDs by name |
| `location_details` | Resolve locale ID details |

### Tier 1 (Individual Lifetime $290 / Monthly $29)

All "always available" tools, plus:

| Tool | Notes |
|---|---|
| `domain_overview` | DA, organic keywords, backlinks, traffic trend |
| `domain_keywords` | Returns **raw list** |
| `domain_top_pages` | Response key is `topPages` |
| `domain_top_countries` | Requires `lang_locs` array |
| `competitors` | Returns `competitors` array |
| `page_overview` | Single page metrics |
| `page_keywords` | Page's ranking keywords |
| `serp_analysis` | Response key is `serpEntries` |
| `estimate_serp_clicks` | CTR estimation |
| `keyword_overview` | Volume, CPC, SD, PD |
| `keyword_metrics` | Difficulty or intent |
| `match_keywords` | Find keywords matching seeds |
| `google_suggestions` | Requires `keywords` array |
| `backlinks_overview` | Total + ref domains + DA |
| `backlinks` | Individual backlinks list |
| `anchor_texts` | Common anchor texts |
| `linking_domains` | Referring domains list |

### Tier 2 (Business Lifetime $490 / Monthly $99)

Everything in tier1, plus:

| Tool | Notes |
|---|---|
| `site_audit` | Start/restart site audit crawl (5,000 pages/week) |
| `site_audit_status` | Check audit progress |
| `site_audit_results` | Pages affected by an issue |
| `site_audit_pages` | All crawled URLs + status |
| `pagespeed_audit` | Core Web Vitals audit |
| `traffic_value` | Estimated USD traffic value |
| `content_ideas` | Top-performing content by shares/visits |
| `page_shares` | Social share counts for batch URLs |
| `list_projects` | List tracked projects |
| `get_project` | Project details + keywords |
| `project_position_info` | Rank tracking report |
| `seo_opportunities` | Improvement opportunities |
| `create_project` | Create new tracked project |
| `add_project_keywords` | Add keywords to project |
| `add_project_competitors` | Add competitors to project |

### Tier 3 (Enterprise Lifetime $990 / Monthly $130)

Everything in tier2, plus higher limits:
- 10,000 site_audit pages/week
- AI Search Visibility: 20/project weekly (vs tier2's 10/monthly, tier1's baseline AI)
- Up to 15 domains

## Tools that are broken regardless of tier

These have MCP transport-layer bugs and 32602 input validation errors
even when the tier and scope are correct:

- `keyword_suggestions` — `MCP error -32602: Input validation error`
- `backlink_opportunity` — same 32602 error

**Workaround:** use `google_suggestions` (with array param) as a substitute
for `keyword_suggestions`. For backlink gap analysis, no current substitute —
manual review of `competitors` data is the workaround.

## Subscription pricing snapshot (2026-06-19)

| Plan | Monthly | Lifetime | Tool unlock |
|---|---|---|---|
| Free | $0 | n/a | 3 tools (auth_status, validate_site, search_neilpatel_blog) |
| Individual (tier1) | $29/mo | $290 once | +18 data tools |
| Business (tier2) | $99/mo | $490 once | +13 advanced tools (site_audit, projects, content_ideas) |
| Enterprise (tier3) | $130/mo | $990 once | Higher limits + AI features |

Source: https://app.neilpatel.com/en/pricing (curated 2026-06-19).

## Related

- `references/ubs-token-refresh-pkce.md` — full PKCE re-auth flow + scope fix
- `references/ubs-callback-url-pattern.md` — callback URL extraction pattern
- Cross-link: `mbgulden/growthwebdev-knowledge/okf/integrations/ubersuggest-mcp.md`
  is the canonical org-level integration doc (this skill is the tactical layer)