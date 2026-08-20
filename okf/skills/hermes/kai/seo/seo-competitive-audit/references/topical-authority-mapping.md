# Topical Authority Mapping

## What It Is

A topical authority map groups all priority keywords into topic clusters, scores our coverage per cluster, and identifies gaps. It answers: "how much of this topic do we actually cover?"

## When to Build One

After a full competitive sweep (phases 1-6) when you have:
- Domain keywords list (our positions)
- Competitor top pages (what they rank for)
- Content strategy (planned pages)
- Site inventory (existing pages)

## Cluster Structure

Each cluster contains keywords grouped by geographic or topical entity:

```
KAILUA CLUSTER (8 keywords)
├── Kailua Beach Park — #13 (need dedicated guide)
├── Kailua Kayak Rental — #2 (good)
├── Lanikai Beach — not ranking (need page)
└── Kailua Beach Oahu — #13 (need better page)
```

## Coverage Scoring

Use the following rubric to score each cluster 0-100%:

| Score | Meaning | Criteria |
|:-----:|---------|----------|
| 0-20% | Minimal | No dedicated page exists for cluster head term |
| 20-40% | Weak | One page exists but ranks poorly (#10+) |
| 40-60% | Medium | Multiple pages but gaps remain in long-tail coverage |
| 60-80% | Strong | Most keywords covered, 1-2 terms need improvement |
| 80-100% | Owned | All keywords ranking top 5, KBA absent |

## How to Build (Step by Step)

### 1. Define Clusters
Group keywords by entity. Standard clusters for a tour/rental business:

1. **Kailua/Lanikai** — Kailua Beach, Lanikai Beach, Mokes, Popoia, Kailua kayak rental
2. **Kaneohe Bay** — Kaneohe Sandbar, Chinaman's Hat, Kualoa, Mokoli'i, Kualoa Park
3. **North Shore** — Sharks Cove, Pupukea, Waimea Bay, Electric Beach, Haleiwa
4. **Kahana/Windward** — Kahana River, Windward Oahu, Secret spots
5. **Rentals/Commercial** — SUP rental, Snorkel rental, Kayak rental, Beach gear, E-bike
6. **How-to/Informational** — Beginners guide, Safety, Turtles, Kayak techniques, Beach guides

### 2. Inventory Pages
For each cluster, list every existing page that covers keywords in that cluster.
Include: page path, title, current position keywords, traffic.

Source: `domain_keywords` output, site inventory (internal link graph).

### 3. Score Coverage
For each cluster:
- Count keywords where we have a page ranking top 10
- Count keywords where we have NO page or rank outside top 20
- Score = (covered ÷ total) × 100

### 4. Identify Gaps
For each missing keyword, note:
- Volume
- Our best position (or "not ranking")
- Who ranks #1 (competitor + DA)
- Whether KBA ranks (if yes, priority)

### 5. Prioritize Gaps
Rank missing pages by:
- **Squeeze play value** = volume × (1 - our position/20) — higher means bigger gap
- **Territory defense** = is KBA entering our space?
- **Ease of win** = what DA do we need to outrank?

## Output Format

The map document should have:

```
## Cluster: Kaneohe Bay — Coverage: 85% 🏆

| Keyword | Vol | Our Pos | Target | Traffic | SERP Features | Gap |
|---------|:---:|:-------:|:------:|:-------:|:-------------:|:---:|
| kaneohe sandbar kayak | 110 | #1 | #1 | 59 | PAA, Local | ✅ |
| chinamans hat kayak | 210 | #1 | #1 | — | AI Overview, PAA | ✅ |
| kualoa park kayak | 170 | — | #3 | — | — | ⬜ Create page |

**Missing pages:** 1 (Kualoa Park guide)
**Urgent:** None — KBA has no presence here
```

## What Drives Coverage Lift

| Action | Coverage Impact |
|--------|:--------------:|
| Create dedicated page for uncovered keyword | +15-25% per cluster |
| Add schema to existing page | +5-10% (quality signal) |
| Improve page from #10+ to #3-5 | +10-15% per keyword |
| Add internal links from related pages | +5% (link equity flow) |

## Data Sources

- Domain keywords: `domain_keywords(MY_SITE, "organic", 50)` — returns raw list
- Competitor gap: `domain_keywords(KBA, "organic", 50)` — find what they cover that we don't
- Site inventory: internal link graph output (page count, titles, positions)
- Content strategy: planned page list from strategy document

## Pitfalls

- Keyword overlap across clusters: Some keywords belong to multiple clusters (e.g., "kaneohe sandbar kayak" is both Kaneohe Bay AND Rentals). Assign to the primary cluster, cross-reference in notes.
- Volume estimates are Ubersuggest approximations — use for prioritization, not absolute projections.
- Traffic estimates for #1 position assume first-page CTR curves — real distribution depends on SERP features.
- KBA's absence from a keyword doesn't mean they won't enter it. Check `domain_top_pages` periodically (see competitor-velocity-monitoring).
