# Location SEO Foundation — Fix → Research → Report → Dispatch

Use this pattern when a stakeholder identifies specific geographic locations
(e.g., "focus on Kailua, Lanikai, and Waimanalo") that need dedicated SEO
authority. This bridges raw SERP data through analysis into actionable
content tasks.

## Workflow

### Phase 1: Data Hygiene (Before Research)

Fix any factual errors about the locations BEFORE running research. Common
issues to check:

- **Business address mismatches** across pages. Search for old/incorrect
  address strings across the site and fix all instances before research begins.
- **Location name inconsistencies** (e.g., "Kailua" vs "Kailua, Oahu")
- **Outdated facility/amenity information** that contradicts official sources

### Phase 2: Targeted SERP Analysis

Rather than running a full 7-phase competitive sweep, focus on location-specific
queries:

1. **Build a keyword list** — 5-6 keywords per location:
   - `[location] beach oahu`
   - `[location] beach parking`
   - `[location] things to do`
   - `[location] beach swimming`
   - `[location] beach park`
   - `[location] kayak rental` (if relevant)
   
   Plus 3-4 cross-location keywords:
   - `best beaches [region] oahu`
   - `[location1] vs [location2]`
   - `[location1] [location2] [location3]`
   - `[region] coast beaches`

2. **Run serp_analysis** for every keyword:
   ```python
   r = await call_mcp("serp_analysis", {"keyword": kw, "limit": 10})
   ```

3. **Check domain_overview** for your site + top competitors:
   ```python
   r = await call_mcp("domain_overview", {"domain": domain})
   ```

### Phase 3: Analyze & Classify Results

For each keyword, classify the opportunity:

| Classification | Signal | Action |
|---------------|--------|--------|
| **Wide Open** | AOT absent + no strong competitor (DA < 30) at top 5 | New page, highest priority |
| **Striking Distance** | AOT ranks #2-5 + leader is beatable | Improve existing page, stronger internal links |
| **GEO Play** | AI Overview at position #1 | GEO optimization (FAQPage, HowTo schema, author byline) |
| **Defend** | AOT already ranks #1-3 | Maintain, add fresh content |
| **Hard Target** | High-DA authority sites dominate (TripAdvisor, Yelp) | Consider if worth the effort |

Key SERP features to note:
- `ai_overview` → GEO optimization needed (structured data, Q&A, author byline)
- `people_also_ask` → FAQPage schema opportunity
- `local_pack` → LocalBusiness schema needed with correct address
- `discussions_and_forums` (Reddit) → Content gap: real user questions not answered
- `knowledge_graph` → Strong local citation signals needed
- `top_sights` → Google's curated list — hard to crack but valuable

### Phase 4: Competitive Landscape Summary

Extract and present:

```
| Domain | DA | Monthly Traffic | Organic Keywords | Ref Domains |
|--------|----|-----------------|------------------|-------------|
| yoursite.com | 26 | 1,707 | 1,345 | 452 |
| competitor1.com | 32 | 154,950 | 2,416 | 687 |
```

Note each competitor's strength and weakness:
- **KBA pattern:** Broad authority but generic content, no local operator voice
- **Your edge:** Being a local operator with physical presence in the area

### Phase 5: Build the Report

Synthesize findings into a structured document with:
1. Executive Summary
2. Competitive Landscape
3. "Where We Rank" table (defend)
4. "Critical Gaps" by location (attack)
5. Key Insights for Content Strategy
6. Recommended Content Roadmap (phased)
7. Existing Content Assets inventory

### Phase 6: Dispatch to orchestrator via Linear

1. Save the report to a known path (e.g., `seo-audit/location_seo_report_for_orchestrator.md`)
2. Save raw SERP JSON at `seo-audit/<timestamp>_serp_locations.json`
3. Create a Linear parent epic titled: `EPIC: [Locations] Location SEO Foundation`
4. Create sub-tasks under it:

| Type | Title | Label |
|------|-------|-------|
| Research | `Orchestrator: Research & Content Strategy for [N]-Location SEO Foundation` | `agent:orchestrator` |
| Content | `Content: [Location 1] — [Specific Guide]` | (none) |
| Content | `Content: [Location 2] — [Specific Guide]` | (none) |
| ... | ... | ... |
| Schema | `GEO/Schema: Location Page Structured Data & AI Overview Optimization` | (none) |
| QA | `QA: Verify [N] Address/Data Fix — [details]` | (none) |

**Important:** The `agent:orchestrator` label requires a UUID, not the string name.
Look up the correct UUID first:
```graphql
query { teams { nodes { labels { nodes { id name } } } } }
```

### Phase 7: Feed orchestrator task with full context

The orchestrator task description should contain:
- The full SEO report (truncated to ~3000 chars in the description)
- Paths to raw SERP data files
- Key constraints (Waimanalo: no commercial delivery, no clear kayaks, etc.)
- Existing content assets inventory
- Priority content candidates (with rationale)
- Brand voice requirements
- Schema requirements per page type

## Pitfalls

- **Wrong google_suggestions param:** The MCP API expects `{"keywords": ["kw"]}`
  (array), not `{"keyword": "kw"}` (string). Documented correctly in the
  parent skill's tools table — don't copy from the old buggy docs.
- **Address mismatches spread silently:** Different pages may use different
  versions of the same address (e.g., "167 Hamakua Drive" vs "134B Hamakua Dr").
  Always do a `grep -r` sweep of the entire site before starting.
- **SERP NODOMAIN entries are SERP features, not competitors.** Skip them
  when counting competitors — they occupy SERP real estate but aren't
  clickable organic results.
- **Content creators need constraints upfront.** Document what the business
  CAN and CANNOT do at each location in the orchestrator research brief, not in the
  content tasks. The orchestrator incorporates constraints into outlines before Ella writes.
- **Epic issues in Linear can create at most ~8 sub-tasks without pagination
  limits.** If more content pages are needed, batch them into multiple epics
  or use the `parentId` field in the mutation.
