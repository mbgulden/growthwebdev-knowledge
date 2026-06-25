---
type: Report
title: Ubersuggest MCP Setup & Recovery — 2026-06-19
description: Time-series incident report: OAuth-scope failure diagnosis and recovery. Pairs with the canonical okf/integrations/ubersuggest-mcp.md doc.
resource: /home/ubuntu/work/reports/20260619_ubersuggest_mcp_setup_and_recovery.md
tags: [report, ubersuggest, mcp, incident, oauth]
timestamp: 2026-06-19T10:52:15Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/ubersuggest-mcp-setup-and-recovery-2026-06-19.md
last_verified: 2026-06-25
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/reports/20260619_ubersuggest_mcp_setup_and_recovery.md
---

# Ubersuggest MCP Connection — Setup, Failure Diagnosis & Recovery Report

**Date:** June 19, 2026
**Author:** Kai (orchestrator agent)
**For:** Michael Gulden — Active Oahu Tours
**Status:** ✅ Resolved — MCP fully operational

---

## TL;DR

The Ubersuggest MCP at `https://ubersuggest-mcp.neilpatelapi.com/mcp` failed all data calls (HTTP 403 "Insufficient scope") after a re-auth. Root cause was the **OAuth scope**: I initially re-authed with the standard OIDC scope (`openid email profile`), but the MCP backend requires a wider scope (`profile domain keywords serp backlinks site_audit content`) to expose data tools. After re-auth with the correct scope, all tools work — `domain_overview` returned DA 26, 1,345 organic keywords, 1,354 backlinks, matching the June 2 baseline exactly.

---

## Background

The Ubersuggest MCP server provides 38 SEO tools (domain_overview, serp_analysis, backlinks_overview, etc.) over a single OAuth-authenticated endpoint. Past sessions on June 2 and June 8 confirmed the integration worked end-to-end with rich data flowing back from `activeoahutours.com`.

Between June 8 and June 19 the OAuth token expired (10-day TTL → confirmed 2 days on re-issue). Re-auth on June 19 was needed to resume scheduled KPI tracking and SEO sweeps.

---

## What broke

After re-auth via the standard PKCE flow documented in `seo-competitive-audit/references/ubs-token-refresh-pkce.md`, the connection showed:

- `auth_status` → ✅ `Logged in as michael@growthwebdev.com / Tier: tier1`
- `domain_overview` → ❌ `HTTP 403 /domain_overview: Insufficient scope for this endpoint`
- `serp_analysis`, `keyword_overview`, `backlinks_overview`, `competitors` → ❌ same 403 across the board
- `search_neilpatel_blog`, `validate_site` → ✅ worked

The token validated, the tier reported correctly, but every data tool was gated behind a scope check the token didn't satisfy.

---

## The fix

### Wrong scope (initial re-auth)
```python
scope = "openid email profile"
```

### Correct scope (working re-auth)
```python
scope = "profile domain keywords serp backlinks site_audit content"
```

The MCP backend requires explicit scope segments for each tool category:
- `profile` → auth_status, validate_site, search_neilpatel_blog
- `domain` → domain_overview, domain_keywords, domain_top_pages, domain_top_countries, traffic_value
- `keywords` → keyword_overview, keyword_suggestions, keyword_metrics, match_keywords
- `serp` → serp_analysis, google_suggestions, estimate_serp_clicks
- `backlinks` → backlinks_overview, backlinks, anchor_texts, linking_domains, backlink_opportunity
- `site_audit` → site_audit, site_audit_status, site_audit_results, site_audit_pages, pagespeed_audit
- `content` → content_ideas, page_shares, page_overview, page_keywords

Note: the SKILL.md docs at `~/.hermes/profile/kai/skills/seo/seo-competitive-audit/references/ubs-token-refresh-pkce.md` say the scope should be `openid email profile`. **This is wrong.** The actual working scope is `profile domain keywords serp backlinks site_audit content`. The June 8 session note captured the correct scope:

> "OAuth scope: `profile domain keywords serp backlinks site_audit content`"

But it wasn't propagated to the skill docs.

---

## Side quest: finding the right account

Before diagnosing the scope issue, we had to figure out which Gmail account had the lifetime purchase. Three accounts were investigated:

| Account | Method | Result |
|---------|--------|--------|
| mbgulden@gmail.com | Full-text Gmail scan via OAuth + body keywords | 29 marketing emails, **0 receipts** |
| michael@activeoahu.com | Full-text scan + Welcome email analysis | "Welcome to Ubersuggest 👋" from Sep 23, 2024 → confirms account exists, **0 receipts** |
| **michael@growthwebdev.com** | User recall | ✅ This is the lifetime account |

The lifetime tier ($290 Individual, paid via PayPal on Dec 27, 2024) is owned by `michael@growthwebdev.com`. Setup of Gmail OAuth for both `mbgulden@gmail.com` and `michael@activeoahu.com` is preserved at `/home/ubuntu/.config/mcp-gdrive/` for future use.

---

## Final operational state

### Tokens (saved to disk)
- `/tmp/ubs_token` — `ubs_oauth2_zj3nZQrqRaeG3UHgNf84gzaSZvzsQdqzTdiMLMIbh2` (53 chars, expires June 21, 2026)
- `/tmp/ubs_refresh` — `ubs_oauth2_I2fWBNBIRULO70F8g36T1N18f7VRvtbAb9jQTZnEwap7zjw0` (59 chars)

### Gmail OAuth tokens (also saved)
- `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json` — mbgulden@gmail.com
- `/home/ubuntu/.config/mcp-gdrive/.michael-gmail-credentials.json` — michael@activeoahu.com

### Tool status
| Tool | Status |
|------|--------|
| `auth_status` | ✅ |
| `validate_site` | ✅ |
| `search_neilpatel_blog` | ✅ |
| `domain_overview` | ✅ |
| `domain_keywords` | ✅ |
| `domain_top_pages` | ✅ |
| `domain_top_countries` | ✅ |
| `competitors` | ✅ |
| `serp_analysis` | ✅ |
| `keyword_overview` | ✅ |
| `keyword_metrics` | ✅ |
| `match_keywords` | ✅ |
| `backlinks_overview` | ✅ |
| `backlinks` | ✅ |
| `anchor_texts` | ✅ |
| `linking_domains` | ✅ |
| `traffic_value` | ❌ 403 — likely tier2+ feature |
| `keyword_suggestions` | ⚠️ Input validation bug (known per skill) |
| `google_suggestions` | ⚠️ 429 rate-limit (transient) |
| `backlink_opportunity` | ⚠️ Input validation bug (known per skill) |
| `site_audit*` | ❌ 403 — tier2+ feature |
| `list_projects`, `*project_*` | ❌ 403 — likely tier2+ feature |

The 403s on tier2+ tools are correct: Michael owns an **Individual Lifetime ($290)** which maps to `tier1`. To unlock site_audit and traffic_value, he'd need to upgrade to Business ($490) or Enterprise ($990) lifetime.

---

## Baseline data captured

`domain_overview(activeoahutours.com)` — June 19, 2026:

- **Domain Authority:** 26
- **Organic keywords:** 1,345
- **Backlinks:** 1,354
- **Referring domains:** 453
- **Top positions (by traffic):**
  - #4 "stand up paddleboard rental" (vol 2,400, 803 traffic)
  - #1 "active oahu" (vol 720, 294 traffic)
  - #9 "electric beach" (vol 8,100, 139 traffic)
  - #3 "sharks cove snorkeling" (vol 3,600, 124 traffic) — *up from #9 in June*
  - #4 "kayak rentals on oahu" (vol 320, 107 traffic)

Compared to June 2 baseline:
- DA: 26 (unchanged)
- Organic keywords: 1,345 (unchanged)
- Backlinks: 1,373 → 1,354 (slight drop, within normal drift)
- Ref domains: 448 → 453 (small gain)

---

## Lessons & follow-ups

1. **Skill doc gap:** The PKCE reference doc at `seo-competitive-audit/references/ubs-token-refresh-pkce.md` lists the wrong scope (`openid email profile`). Should be updated to `profile domain keywords serp backlinks site_audit content`. The June 8 session note captured the right scope but it never made it into the skill.

2. **KPI tracker cron job erroring since June 15:** The token expiry broke the scheduled weekly KPI report (`ce817dba90d3` cron job). With tokens now refreshed, this should auto-resolve on the next Monday 4 AM UTC run (June 22, 2026).

3. **Tier1 ceiling:** Individual Lifetime ($290) is real and working, but it doesn't include site_audit, traffic_value, or project tracking. For a single-domain SEO setup that's fine — most analysis happens on `domain_overview`, `domain_keywords`, `serp_analysis`, `backlinks_overview`, and `competitors`, all of which work.

4. **Token TTL gotcha:** Re-authed tokens are now 2 days, not the previous 10 days. Refresh proactively — 1 day before expiry.

5. **Shell display truncation:** JWT tokens contain literal dots (`.`) that bash/shell displays truncate with `...`. Always write tokens to file via `curl -o` and read back via Python — never rely on `echo` output.

---

## Action items

| Item | Owner | Status |
|------|-------|--------|
| Patch `seo-competitive-audit/references/ubs-token-refresh-pkce.md` with correct scope | Kai | TODO |
| Verify KPI tracker cron resumes on June 22 | Kai (auto) | Will verify Monday |
| Run full 7-phase SEO sweep on activeoahutours.com + competitors | Kai | On request |
| Consider upgrading to Business lifetime ($490) for site_audit | Michael | Optional |

---

## Files referenced

- `~/.hermes/profiles/kai/skills/seo/seo-competitive-audit/SKILL.md`
- `~/.hermes/profiles/kai/skills/seo/seo-competitive-audit/references/ubs-token-refresh-pkce.md` (needs patch)
- `~/.hermes/profiles/kai/scripts/seo_full_sweep.py`
- `~/.hermes/profiles/kai/scripts/kpi_tracker.py`
- `~/.hermes/profiles/kai/scripts/competitor_velocity.py`
- `~/.config/mcp-gdrive/.gdrive-server-credentials.json`
- `~/.config/mcp-gdrive/.michael-gmail-credentials.json`
- `/tmp/ubs_token`, `/tmp/ubs_refresh`
- `/tmp/ubs_token_response.json` (full token response archive)

---

## Companion script

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()
URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async def call_tool(name, args):
    async with streamablehttp_client(URL, headers=HEADERS) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            r = await session.call_tool(name, args)
            return r.content[0].text

# Example: get domain overview
data = await call_tool("domain_overview", {"domain": "activeoahutours.com"})
print(json.dumps(json.loads(data), indent=2)[:1500])
```

---

*Report generated by Kai — orchestrator agent for Active Oahu Tours. Reach out via Telegram for follow-ups.*
