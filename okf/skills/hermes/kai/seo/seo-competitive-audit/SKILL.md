---
name: seo-competitive-audit
description: >-
  Run comprehensive SEO competitive audits using Ubersuggest MCP. Pull domain
  overviews, keyword gaps, top pages, SERP analysis, and content suggestions
  for multiple competitors — all autonomously. Designed for overnight sweeps
  that deliver structured reports by morning. Use this skill for SEO-only
  work; pre-cutover deployment audits and WordPress-to-static migration
  prep live under the `wordpress-static-migration` umbrella.
triggers:
  - competitive audit or competitor audit or SEO sweep
  - Ubersuggest MCP research
  - keyword gap analysis or backlink opportunity
  - content topic expansion or SERP analysis
  - GEO or AI SEO or generative engine optimization
  - internal link audit or orphan page detection or content inventory
  - competitor content velocity or competitor monitoring
  - squeeze play or zero-click search analysis
  - overnight SEO report
  - deep corner creative audit (SEO-only mode — Jules/orchestrator audit patterns)
always-delegate: false
---

# SEO Competitive Audit — Autonomous Sweeps via Ubersuggest MCP

## Capability

Query Ubersuggest's full SEO dataset across multiple competitor domains in a
single autonomous run. Each phase opens its own MCP session to avoid connection
timeouts. Results are saved as structured JSON reports.

## Prerequisites

```bash
pip install --break-system-packages mcp
```

Token must be stored at `/tmp/ubs_token` (a plain Bearer token string, e.g.
`ubs_oauth2_...`). Refresh token lives at `/tmp/ubs_refresh`. Token expiry is ~10 days historically and **172800s / ~2 days on current re-auths**; refresh proactively using the stored refresh token (see
`references/ubs-token-refresh-pkce.md`). The canonical credential automation is the PWP provider in `prismatic-engine`: `python3 scripts/pwp credentials refresh ubersuggest` / `status ubersuggest --verify`, backed by `plugins/pwp/oauth_credentials.py` and documented in `plugins/pwp/docs/credential-providers.md`. The canonical scheduler automation is now PE-native crons, not Hermes: `seo.ubersuggest-token-refresh`, `seo.aot-weekly-rankings`, and `seo.aot-competitor-velocity` live in `prismatic/native_crons.py` and can be installed with `python3 scripts/install_native_crons.py`. See `references/pe-native-seo-cron-migration-2026-07-12.md` for the migration pattern, dashboard semantics, and verification checklist.

**Note:** The old REST API at `api.ubersuggest.com` no longer resolves
(NXDOMAIN). All queries go through the MCP endpoint below. A 502 error on
token validation means Neil Patel's auth backend had an issue — retry before
assuming the token is dead. A persistent 502 + `invalid_grant` on refresh means
a full PKCE re-auth is needed.

**Critical: OAuth scope must include the data-tool segments, not just `openid email profile`.** The working scope (verified June 2026) is:
```
profile domain keywords serp backlinks site_audit content
```
If you use only `openid email profile` or `profile`, the token validates but `domain_overview` and every other data tool returns HTTP 403 "Insufficient scope for this endpoint." The auth server **echoes back whatever scope you granted** in the response — a `scope: "profile"` response is a real signal that you only granted profile scope, not a quirk of the server. See `references/ubs-token-refresh-pkce.md` for the full "OAuth Scope Controls Tool Access" section. Also include `access_type=offline` to receive a refresh token for proactive renewal.

## Core MCP Session Pattern

Always use `streamablehttp_client` — never `sse_client` (SSE returns 401):

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()
URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async def call(tool, args):
    async with streamablehttp_client(URL, headers=HEADERS) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            text = result.content[0].text if result.content else "{}"
            return json.loads(text)
```

**IMPORTANT:** Wrap `json.loads()` in try/except. Some tools return empty or
non-JSON responses (see Pitfalls below).

## Available Tools & Key Response Keys

| Tool | Key Args | Response Key | Notes |
|------|----------|-------------|-------|
| `domain_overview` | `{"domain": "..."}` | `organic`, `domainAuthority`, `organicKeywords` | Also returns traffic trend in `domainTraffic` |
| `domain_keywords` | `{"domain": "...", "type": "organic", "limit": 50}` | **Raw list** (not a dict — `data` is a `list`, each item has `keyword`, `position`, `volume`, `traffic`) | Iterate with `for item in data:` not `data["keywords"]` |
| `domain_top_pages` | `{"domain": "...", "limit": 20}` | **`topPages`** (not `pages`) | |
| `serp_analysis` | `{"keyword": "...", "limit": 10}` | **`serpEntries`** (not `serpResults`) | Each entry has `domain`, `position`, `clicks`, `domainAuthority` |
| `competitors` | `{"domain": "..."}` | `competitors` array | Each has `domain`, `commonKeywordCount`, `gapKeywordCount` |
| `validate_site` | `{"site": "..."}` *(NOT `domain`)* | boolean | Quick domain check. MCP returns `Input validation error: path: ["site"], message: "Required"` if you pass `domain` — the parameter name is genuinely different from the other domain tools. |
| `auth_status` | `{}` | — | Returns **plain text** (not JSON): `"Logged in as X / Tier: Y"`. Don't try to `json.loads()` — read `r.content[0].text` directly. |
| `backlink_opportunity` | see below | — | **Known buggy** — see Pitfalls |
| `keyword_suggestions` | `{"keyword": "...", "limit": 20}` | — | **Known buggy** — see Pitfalls |
| `google_suggestions` | `{"keywords": ["..."]}` | — | **Requires `keywords` as an array** (not `keyword` string). Fallback if `keyword_suggestions` fails. |

**Not in the table above but available in the MCP:** `domain_top_countries`,
`traffic_value`, `page_overview`, `page_keywords`, `keyword_overview`,
`keyword_metrics`, `match_keywords`, `estimate_serp_clicks`, `backlinks_overview`,
`backlinks`, `anchor_texts`, `linking_domains`, `content_ideas`, `page_shares`,
`site_audit`, `site_audit_status`, `site_audit_results`, `site_audit_pages`,
`pagespeed_audit`, `list_projects`, `get_project`, `project_position_info`,
`seo_opportunities`, `create_project`, `add_project_keywords`,
`add_project_competitors`, `location_suggest`, `location_details`. **Which
ones work on a given account depends on tier — see
`references/ubersuggest-tier-feature-matrix.md` for the full grid.**

## Standard 7-Phase Sweep Pattern

```
Phase 1 — Domain Overviews:       domain_overview for your site + all competitors
Phase 2 — Keyword Gap Analysis:   domain_keywords for top competitors (limit=50)
Phase 3 — Top Pages:              domain_top_pages for top competitors (limit=20)
Phase 4 — Backlink Opportunity:   backlink_opportunity (⚠ may fail — skip if so)
Phase 5 — Keyword Suggestions:    keyword_suggestions OR google_suggestions (⚠ may fail)
Phase 6 — SERP Analysis:          serp_analysis for priority keywords (positions 2-4)
Phase 7 — Unknown Competitors:    domain_overview for unverified domains
```

### Connection Timeout Rule

Each MCP session supports **3-4 tool calls maximum** before the streamable HTTP
connection may timeout. Run each phase as a separate `asyncio.run()` call. Keep
the call count low per session.

### Report Output

Save each phase result as `<timestamp>_phase<N>_<name>.json`. Compile a final
markdown report with:
1. Competitive landscape table (traffic, DA, backlinks, ref domains)
2. Traffic trend (last 12 months)
3. Keyword battle map (us vs each competitor)
4. Keyword gap (what they rank for that we don't)
5. Top pages analysis (what content drives their traffic)
6. SERP breakdown for priority keywords
7. Content recommendations based on gaps

## Delegation & Parallel Work

When using delegate_task for browser-based QA work (page scans, visual checks):

- **Chunk by 10 pages max per subagent.** Browser navigation is stateful and slow — each page takes 2-3 seconds to load. 10 pages keeps a subagent under its iteration limit.
- **3 subagents max in parallel** (hard limit: `max_concurrent_children=3`).
- **Each subagent needs its own focus:** assign a logical cluster of pages (e.g., "all activity pages", "all rental pages", "root + about + FAQ pages") so results are easy to compare.
- **Browser subagents** need `toolsets: ["browser"]` — they cannot run terminal in the same session.
- **Terminal subagents** use `toolsets: ["terminal", "file"]` — faster, higher iteration limits.

## GEO / AI SEO Considerations  

### SERP Features to Track

When running `serp_analysis`, note these feature types in the response:
- `ai_overview` — Google's AI-generated answer (key for GEO optimization)
- `people_also_ask` — PAA boxes (featured snippet opportunity)
- `local_pack` — Google Maps results (LocalBusiness schema needed)
- `knowledge_graph` — Google's knowledge panel (structured data feeds this)
- `product_considerations` — Shopping/comparison results
- `short_videos` — Video carousel (YouTube content opportunity)
- `discussions_and_forums` — Reddit/forum results (content gap signal)
- `top_sights` — Travel/tourism feature

### GEO Optimization Checklist

For keywords that trigger `ai_overview`:
1. Structure pages with clear `<h2>What is [Topic]?</h2>` sections
2. Use HowTo schema for step-by-step instructions
3. Add FAQPage schema with realistic questions
4. Include author byline with credentials
5. Write in authoritative, first-person operator voice

### HowTo Schema (GEO Priority)

Most missing schema type. Template:
```json
{"@context":"https://schema.org","@type":"HowTo","name":"How to [Action]","step":[
  {"@type":"HowToStep","position":1,"name":"Step one","text":"Description"},
  {"@type":"HowToStep","position":2,"name":"Step two","text":"Description"}
]}
```

Full GEO reference: `references/geo-ai-seo-analysis.md`

## Pitfalls

- **Key format confusion:** `domain_keywords` returns a **raw list** (not a dict
  with a `keywords` key). Check `isinstance(data, list)` and iterate directly.
  `domain_top_pages` uses `topPages`. `serp_analysis` uses `serpEntries`.
  `domain_overview` response has `organicKeywords`. Always check the actual
  response type before processing.

- **Tools that fail at transport layer:** `backlink_opportunity`,
  `keyword_suggestions`, and `auth_status` throw `unhandled errors in a TaskGroup
  (1 sub-exception)` from `session.call_tool()` at the MCP transport layer —
  the server rejects the call before any response is returned. This is NOT a
  JSON parse error; the try/except must wrap the entire `call_mcp()` call (not
  just `json.loads()`). The `call_mcp()` helper in the sweep script already does
  this. Either:
  a. Skip these tools entirely (they almost never return data on free tier)
  b. `google_suggestions` — the docs here originally documented it with
     `{"keyword": "..."}` but the MCP API actually requires `{"keywords": ["..."]}`
     (array). If you're getting `MCP error -32602: Input validation error`
     with `expected: "array", received: "undefined"`, the fix is to pass
     an array: `{"keywords": [kw]}`. **Verified June 2026: even with the
     correct array parameter, `google_suggestions` returns an empty `data`
     list on tier1 (Individual Lifetime). The tool is exposed but doesn't
     return data at this tier.** If you need question/suggestion data,
     skip this tool entirely and either: (a) use a paid SERP API, (b) mine
     questions from existing GRO plans + keyword intent, or (c) check if
     tier2/tier3 unlocks the data.

- **Script divergence trap:** The sweep script exists in TWO places — the
  skill's copy at `skills/seo/seo-competitive-audit/scripts/seo_full_sweep.py`
  (correctly uses `google_suggestions`) and the profile's `scripts/` directory.
  If the profile copy diverges (uses `keyword_suggestions`), it will silently
  fail Phase 5 with transport exceptions. When running a sweep, verify which
  copy executed by checking the log output for the tool name called. Fix:
  `cp skills/seo/seo-competitive-audit/scripts/seo_full_sweep.py
  ~/.hermes/profiles/$PROFILE/scripts/seo_full_sweep.py`

- **Rate limiting:** After ~15-20 rapid MCP calls, some tools start returning
  empty responses. Add a small delay (0.5-1s) between sessions, or re-run phases
  that failed with fresh auth after a brief pause.

- **Token expiry:** The OAuth token expires after 10 days. Refresh proactively
  using the stored refresh token before running a sweep.

- **Paid tier gates depth, scope gates access — and tier1 ≠ "all tools."** There
  are three paid tiers, and they unlock different tool subsets even with the
  correct OAuth scope. tier1 (Individual Lifetime $290 / Monthly $29) unlocks
  most domain/keyword/SERP/backlink tools but **legitimately 403s on**:
  `site_audit`, `site_audit_status`, `site_audit_results`, `site_audit_pages`,
  `pagespeed_audit`, `traffic_value`, `content_ideas`, `page_shares`,
  `list_projects`, `get_project`, `project_position_info`, `seo_opportunities`,
  `create_project`, `add_project_keywords`, `add_project_competitors`. Those
  require tier2 (Business Lifetime $490) or tier3 (Enterprise Lifetime $990).
  See `references/ubersuggest-tier-feature-matrix.md` for the full tool × tier
  grid. **Diagnostic:** if `auth_status` shows tier1 AND `domain_overview`
  works AND the failing tool is in tier1's 403 list, the 403 is the tier
  ceiling — not a scope bug. **Don't waste cycles re-authing** — the token is
  fine, the account genuinely lacks the feature. Either upgrade or open a
  support ticket with purchase proof if you suspect a misclassification.

- **Scope, not tier, gates data tools (verified June 2026).** `auth_status` reports
  a tier label (`tier1`, `tier2`, `free`, etc.) but the label alone doesn't tell
  you whether data tools work. The actual gate is the **OAuth scope** in the
  token. With the working scope (`profile domain keywords serp backlinks
  site_audit content`), an account on `tier1` (Neil Patel's lowest paid tier —
  Individual Lifetime) **does** successfully call `domain_overview`,
  `keyword_overview`, `serp_analysis`, `competitors`, `backlinks_overview`, etc.
  Without the right scope, even a higher-tier account 403s. If `auth_status`
  shows the correct tier AND you used the correct scope AND data tools still
  403, then the account genuinely needs a tier bump via support@ubersuggest.com
  with purchase proof. The diagnostic: hit `auth_status` + `domain_overview`
  after every re-auth — both must succeed.

- **OAuth cached-session cache-buster (`prompt=login`):** If the user sends
  back a callback URL with the same `code=` value as a previous attempt, their
  phone browser is reusing a cached auth session. Add `&prompt=login` to the
  authorization URL to force a fresh login screen — this generates a brand-new
  code. If that still fails, ask the user to open the URL in incognito/private
  browsing mode on a different browser. (Same trick works for Google OAuth;
  applies broadly to any PKCE/OAuth flow on mobile where browser caching can
  reissue the same code.)

- **validate_site errors in batch:** When using `validate_site` inside the same
  session as `competitors` or other tools, it can cause session-level errors.
  Run it in its own session.

- **SERP NODOMAIN entries = SERP features, not sites:** `serp_analysis`
  responses include entries with `"domain": "NODOMAIN"` or `"url": "http://NODOMAIN"`.
  These represent Google SERP features — AI Overview, People Also Ask,
  Discussions and Forums, Top Sights, Knowledge Graph, Local Pack. Their
  `type` field tells you which feature. NODOMAIN entries have zero clicks — they
  occupy SERP real estate without being clickable organic results. When analyzing
  striking-distance opportunities, skip NODOMAIN entries and count only organic
  results from real domains.

- **Geo signal from NODOMAIN positions:** If a priority keyword has NODOMAIN
  features at positions 1-4 (especially AI Overview or People Also Ask), users
  satisfy their query without clicking through to any site. Traditional SEO
  position-improvement has diminishing returns here — GEO optimization
  (structured data, Q&A blocks, HowTo schema, author bylines) becomes the
  primary play for capturing visibility within those SERP features themselves.

- **Ubersuggest is for competitor intel. GSC is the source of truth for your own site.**
  Verified June 19, 2026 against activeoahutours.com. Ubersuggest's
  `domain_overview` reported monthly organic traffic of **1,345** for AOT.
  Google Search Console (the last 90 days) revealed the actual figure is
  **~452/month** — Ubersuggest overestimated by 3x. Other discrepancies:
  - Ubersuggest said Kanohe Sandbar was ranked #1; GSC showed position 5.2
  - Ubersuggest said SUP rentals was AOT's #1 traffic page; GSC showed
    Sharks Cove (589 clicks) was #1, SUP (96 clicks) was much further down
  - Ubersuggest reported 50 ranking keywords; GSC showed 1,000+ queries
  - Brand queries (`active oahu tours` at #1, 47% CTR) were completely
    invisible in Ubersuggest's data
  **Implication for the SEO workflow:** when planning content priorities for
  YOUR site, the per-page GSC data (clicks/impressions/CTR/position) is the
  source of truth. Ubersuggest is still useful for:
  - What competitors rank for that you don't (keyword gap analysis)
  - Estimating search volume for prioritization
  - Quick competitive landscape comparisons
  But for own-site performance, always pull GSC. The
  `templates/aot_seo_baseline_audit.py` script in this skill produces
  competitive intel from Ubersuggest — pair it with a GSC pull (covered in
  `google-api-setup` skill under webmasters scope) to get the full picture.

- **GitHub push via orchestrator token:** The orchestrator profile stores
  `GITHUB_PAT_KEY` in its `.env`. Use this for git pushes:
  ```bash
  TOKEN=$(grep '^GITHUB_PAT_KEY=' $HOME/.hermes/profiles/orchestrator/.env | cut -d= -f2)
  git remote set-url origin "https://user:${TOKEN}@github.com/user/repo.git"
  git push origin main
  ```

- **FormSubmit.co verification:** First form submission sends a verification
  email. User must click the confirmation link. Browser-based submission needed
  (curl blocked by Referer check). To trigger, use browser tools to fill and
  submit the form, or submit via `document.querySelector('form').submit()` in
  browser console.

- **CRO diagnosis: don't flag business model when the fix is copy.** A high-traffic page with 0% conversions may look like a structural problem (bad pricing, wrong location, broken model) when the actual issue is the copy failing to communicate the value proposition. The Sharks Cove case: page requires pickup at Kailua store to snorkel at North Shore. The orchestrator diagnosed this as a "geographical mismatch" and recommended changing the business model. The user corrected: the model is fine — guests get full-day gear, scenic windward drive, all-afternoon snorkeling, sunset, and after-hours return. The page just buries this story. **Rule:** Before recommending a business model change, verify the copy doesn't already have the right story told poorly. Frame the diagnosis as "copy doesn't communicate X" unless you can prove structural friction (pricing, logistics, availability).

## Scripts

The companion script at `scripts/seo_full_sweep.py` implements the full 7-phase
sweep. Copy it as a starting point and customize competitor targets and keyword
seeds.

For a single-domain baseline audit (the most common shape), prefer the
ready-to-customize template at `templates/aot_seo_baseline_audit.py` —
it runs Phases 1, 2, 3, 6, 7 (skipping the broken `keyword_suggestions`
and `backlink_opportunity`), saves timestamped JSON per phase, and is
the exact pattern used to build the AOT June 19 2026 baseline.

## Reference Files

- `references/kpi-tracking-workflow.md` — How to set up, debug, and maintain the
  weekly KPI rankings tracker cron job.
- `references/seo-action-plan-format.md` — Template for compiling raw sweep data
  into a structured SEO action plan.
- `references/serp-deep-dive-technique.md` — Targeted SERP analysis for
  breakthrough opportunities and squeeze-play values.
- `references/geo-ai-seo-analysis.md` — GEO/AI SEO analysis with HowTo schema template.
- `references/internal-link-graph-audit.md` — How to crawl a static site, build
  a link graph, identify orphan pages, and fix internal linking.
- `references/competitor-content-velocity.md` — Weekly competitor content monitoring.
- `references/topical-authority-mapping.md` — Keyword grouping into topic clusters.
- `references/structured-report-catalogue.md` — Template for organizing multiple
  related SEO reports into a structured directory with _index.md catalogue,
  naming conventions, dependency chains, and the "Questions Audit" meta-pattern.
  Use when creating 3+ related orchestrator tasks for the same site.
- `references/ubs-callback-url-pattern.md` — Ubersuggest OAuth callback URL pattern (alternative to OOB code display). User may receive a `/callback?code=...` URL instead of a bare code; how to extract and handle.
- `references/ubs-token-refresh-pkce.md` — Full PKCE OAuth flow for refreshing expired Ubersuggest tokens: authorization URL generation, code exchange, token refresh, and verification. Covers the 502 "Token validation failed" error pattern and the fact that `api.ubersuggest.com` (old REST API) no longer resolves. **Includes the JWT truncation pitfall — read before any token capture/exchange.**
- `references/pwp-ubersuggest-credential-provider-2026-07-12.md` — PWP credential-provider implementation for durable Ubersuggest refresh-token rotation: `scripts/pwp credentials refresh/status ubersuggest`, provider safety checks, repo-local plugin import pitfall under Hermes scheduler Python, cron bridge expectations, and focused verification commands.
- `references/pwp-pe-additive-plugin-integration-2026-07-12.md` — PWP as a first-class additive Prismatic Engine plugin: manifest capability contracts, PE-owned connection state, status/connect/disconnect/refresh API, Dashboard PWP tab, CLI integration commands, safe disconnect semantics, and focused verification checklist.
- `references/pe-native-seo-cron-migration-2026-07-12.md` — PE-native portable cron migration pattern for SEO automation: native cron registry IDs, dashboard pause/deactivate/delete semantics, managed crontab installer, import-shadowing pitfall, verification checklist, and next SEO tools to wire.
- `references/managed-seo-sites-ga4-crons-2026-07-12.md` — Managed SEO sites + GTM/GA4 cron onboarding: site registry scaffolding, GTM/dataLayer golden path, GSC/sitemap/GTM/dataLayer/GA4 setup audit workflow, GA4 conversion/revenue insights cron, booking-event requirements, native-cron metadata refresh pitfall, and verification checklist.
- `references/ubersuggest-mcp-mobile-reauth.md` — **Mobile-first 60-second re-auth checklist.** Use this only when the PWP refresh-token path is unavailable or returns `invalid_grant`; routine refresh should go through the PWP provider. Covers the three most-common failure modes in order, mobile-vs-Google-OAuth contrast, tier→plan mapping, and copy-paste blocks for verifier generation, safe token capture, and connection verification.
- `references/ubersuggest-tier-feature-matrix.md` — **Tool × tier grid (tier1/2/3/free) with the 60-second scope-vs-tier diagnostic. Read this whenever you see a 403 to determine if it's a scope bug or a tier ceiling.**
- `references/gsc-property-types.md` — **The `sc-domain:` vs `https://` trap that costs 30 minutes the first time you hit it.** Google Search Console has two property types for the same domain and they hold different data. URL-encode the colon. Default to `sc-domain:` for SEO work. Read this before any GSC API call.
- `references/gsc-ubersuggest-countercontent-workflow.md` — Pair Ubersuggest competitor territory alerts with GSC own-site query/page data, then produce evidence-backed Active Oahu counter-content briefs. Includes the `page_keywords` 405 fallback to `domain_keywords` + URL filtering and the rule to save Linear issue drafts when the Linear API is rate-limited.

> **Migration-prep references moved:** `pre-cutover-deployment-audit`, `dns-cutover-cloudflare`, `cloudflare-pages-deployment`, `cloudflare-pages-staging-workflow`, `static-form-replacement`, `linear-post-cutover-tasks`, `deep-corner-creative-audit`, `bulk-schema-injection`, `active-oahu-site-ops`, `site-scaffolding-template`, and `session-june-2026` now live under the `wordpress-static-migration` umbrella as `references/migrated-from-seo-*.md`. They describe cutover/migration prep rather than SEO audit work.