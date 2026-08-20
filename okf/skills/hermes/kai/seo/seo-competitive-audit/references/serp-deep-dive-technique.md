# SERP Deep Dive Technique — Analyzing Priority Keywords

After a full sweep identifies target keywords, run individual SERP analyses to understand exactly who to outrank and why. This technique turns raw position data into actionable content strategy.

## When to Use

After completing the full competitive sweep (phases 1-3) when you need to:
- Decide which keywords to target first
- Understand why competitors outrank you (authority gap vs content quality gap)
- Identify "breakthrough opportunities" — keywords where low-DA sites rank high
- Provide writers with specific competitor analysis for each page

## Methodology

### Step 1: Select Priority Keywords

Pick from each category:
- **High volume we already rank for** (position 2-9, volume >1,000)
- **Uncontested territory** (main competitor doesn't rank, we do)
- **Squeeze plays** (low-DA competitors ahead of us)

Limit to 9-12 keywords per deep dive. Each MCP session handles 3 calls max.

### Step 2: Run SERP Analysis

Use the standard MCP session pattern. Query `serp_analysis` with the keyword and limit=10.

### Step 3: Read the Response

The response has `serpEntries` — an array of results. Each entry:

| Field | What It Tells You |
|-------|------------------|
| `domain` | Who's on the page |
| `position` | Their rank |
| `clicks` | How many clicks they get (traffic proxy) |
| `domainAuthority` | DA of the ranking page |
| `type` | organic, local_pack, people_also_ask, knowledge_graph, ai_overview, map, short_videos, product_considerations, discussions_and_forums, images |

### Step 4: Identify Breakthrough Opportunities

The critical pattern: compare DA vs position vs clicks.

**Breakthrough opportunity = competitors with LOWER DA ranking ABOVE you**
This means their content quality is better, not their authority. A good content upgrade can leapfrog them without needing backlinks.

**Example:** "electric beach" (8,100 vol) — sites at DA 21-22 rank #3-4 with 4,361 and 1,011 clicks. Our site has DA 26 but ranks #9 with 139 clicks. This is a **content quality gap, not an authority gap** — a proper guide can jump to #3-5.

**False breakthrough = competitors with HIGHER DA ranking above you**
This requires DA growth, backlinks, or long-term authority building. Don't prioritize these.

### Step 5: Note SERP Features

Record what SERP features appear for each keyword:
- `ai_overview` — AI summary reduces organic CTR
- `local_pack` — Requires Google Business Profile, not just on-page SEO
- `people_also_ask` — Featured snippet opportunity with Q&A content
- `product_considerations` — Commercial intent signal
- `short_videos` / `images` — Visual content opportunity

### Step 6: Calculate Squeeze Play Value

For each keyword, estimate traffic gain from moving up:

```
clicks_at_target_position - our_current_clicks = estimated_gain
```

Use the `clicks` field from SERP entries above and below you as a proxy. Be realistic: moving #9 → #5-6 gains a few hundred clicks, not thousands.

### Step 7: Compile into a SERP Report

For each keyword, output:
```
## N. "[keyword]" (volume) — We're #X (Y clicks)

| Pos | Site | DA | Clicks | Notes |
|:---:|------|:--:|:------:|-------|
| 1 | competitor.com | XX | X,XXX | Why they win |
| X | us ✅ | XX | X | Current state |

**SERP Features:** (list)
**Squeeze:** (specific action + expected gain)
```

## Pitfalls

- **Position mismatch:** `domain_keywords` and `serp_analysis` may report different positions. `serp_analysis` is point-in-time; `domain_keywords` aggregates. Trust `serp_analysis` for current state, `domain_keywords` for trend.
- **NODOMAIN entries:** SERP features (local_pack, PAA, etc.) show domain=NODOMAIN. These are non-organic — note them but don't treat as competitors.
- **Maps in top spots:** Local results occupy positions 1-3 and can't be outranked by on-page SEO alone. Need GMB optimization.
- **Clicks are estimated:** The `clicks` field is a model estimate. Use for directional comparison only.
- **3 calls per session max:** Each MCP session supports 3-4 tool calls. Plan batches accordingly.

## Output Example

See `20260603_SERP_DEEP_DIVE.md` in the cron output for a worked 9-keyword analysis.
