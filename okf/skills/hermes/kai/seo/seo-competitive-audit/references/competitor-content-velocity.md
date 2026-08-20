# Competitor Content Velocity Monitoring

## Purpose

Track how many new pages competitors publish per month and which topics they're targeting. Detect when they enter your uncontested territory early.

## Why It Matters

Competitors don't stay in their lane. KBA (kailuabeachadventures.com) was absent from Kaneohe Sandbar in May 2026, but by June they had a "Kayaking Kaneohe Bay | Sandbar - Chinaman's Hat" page driving 242 traffic. Early detection = counter-strategy time.

## Method

### One-Time Baseline

```python
# Run Ubersuggest domain_top_pages on your domain and top competitors
await call_mcp("domain_top_pages", {"domain": "competitor.com", "limit": 20})
```

Save the result as a JSON baseline. Each entry has: `title`, `url`, `traffic`, `keyword`.

### Weekly Check

Re-run the same query and compare against baseline:

1. **New entries** — pages that don't exist in the baseline. Flag them.
2. **Traffic jumps** — existing pages that gained significant traffic. Investigate why.
3. **Keyword shifts** — check if they're targeting keywords in YOUR uncontested territories.

### Territory Alerting

Define competitor territories and your territories:

**Your territories:**
- Chinaman's Hat / Kualoa keywords
- Kaneohe Sandbar keywords
- North Shore / Sharks Cove keywords
- Kahana River keywords

**Their territories:**
- Kailua Beach / Lanikai keywords
- Generic Oahu travel keywords

**Alert trigger:** Competitor publishes a page targeting ANY of your territory keywords.

### Output Format

```
=== Weekly Competitor Content Check ===
Date: 2026-06-03

Active Oahu Tours:
├── Total keywords: 1,345 (+12 from last week)
├── Traffic: 1,707 (+34)
└── Top new keyword: "chinamans hat kayak" (#1, ~210 vol)

KBA (kailuabeachadventures.com):
├── Total keywords: 2,416 (−5)
├── ⚠️ NEW: "Kayaking Kaneohe Bay | Sandbar - Chinaman's Hat" (242 traffic)
│   └── TERRITORY ALERT: This is in YOUR Kaneohe Sandbar territory!
└── Top pages unchanged: Lanikai guide (58K traffic)
```

### Automation (Cron)

Schedule weekly (Sunday 6AM):
- Pull `domain_overview` for your site + top 3 competitors
- Pull `domain_top_pages` for each
- Compare against saved baseline
- Alert if new pages detected in your territory
- Save as new baseline for next week

```python
# Cron spec
# Schedule: 0 6 * * 0 (Sundays 6AM)
# Tools: terminal, file
# Compare cached domain_top_pages JSON against fresh pull
```

## Real-World Findings (Active Oahu, June 2026)

- KBA published "Kayaking Kaneohe Bay | Sandbar - Chinaman's Hat" — 242 traffic, pushing into our uncontested territory
- KBA's top 20 pages include 7 informational articles we have zero equivalents of (beach guides with 58K traffic, how-to kayaking guides, wildlife guides)
- Surfnsea.com has DA 36 and blog content but ranks poorly on our keywords (#17 for sharks cove snorkeling)

## Files

- Full competitor baseline: `cron/output/seo-audit/20260602_075208_phase3_top_pages.json`
- KBA top pages analysis in GEO report: `cron/output/seo-audit/20260603_GEO_READINESS_REPORT.md`
