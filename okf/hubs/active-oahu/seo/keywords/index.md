---
type: Index
title: Master Keyword Inventory
description: 101 keywords across 13 clusters mapping every AOT-targeted keyword to a target page with volume, intent, and current rank.
tags: [index, keywords, aot, seo, master-inventory]
timestamp: 2026-06-19T14:30:00Z
linear_issue: null
git_path: okf/keywords/index.md
status: current
resource: okf/hubs/active-oahu/seo/keywords/index.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Master Keyword Inventory

The canonical reference of every AOT-targeted keyword. Drives all content production, on-page optimization, and AI Overview capture work.

## Documents

| File | Purpose | Status |
|---|---|---|
| [master-inventory.md](./master-inventory.md) | 101 keywords × 13 clusters × target pages | current |
| [keyword-research-queue.md](./keyword-research-queue.md) | Future expansion: GSC data, competitor profiles, Japanese market, long-tail, image search, seasonal | empty |

## TL;DR

**101 keywords** organized into 13 thematic clusters. Every keyword maps to:
- **Cluster** (topic group — e.g., "Kailua Beach Hub", "Mokulua Islands", "E-Bike Tours")
- **Intent** (informational, commercial, transactional, navigational)
- **Volume** (Ubersuggest monthly search volume)
- **Current rank** (AOT's position, where measured in baseline)
- **Target page** (the AOT URL where this keyword should rank)

## Top-line numbers

| Metric | Value |
|---|---|
| Total keywords tracked | **101** |
| Total clusters | **13** |
| Striking-distance (rank 4-8) | **9 keywords with significant ROI** |
| Potential monthly visit gain (top 9 promoted to position 5) | **~142 visits/mo** |
| Owned positions (1-3) | **4 keywords** (kaneohe sandbar, chinamans hat, sharks cove, kailua kayak) |
| Critical gaps (AOT ranks nothing) | **1 keyword** (`snorkeling oahu north shore`) |

## Cluster summary

| # | Cluster | Keywords | Highest-volume keyword | Avg volume |
|---|---|---:|---|---:|
| 1 | Kailua Beach Hub | 11 | kailua beach (49,500/mo) | ~7,800 |
| 2 | Lanikai Beach Hub | 10 | lanikai beach (74,000/mo) | ~11,400 |
| 3 | Waimanalo Beach Hub | 6 | waimanalo beach (40,500/mo) | ~12,150 |
| 4 | Mokulua Islands | 6 | mokulua islands (24,000/mo) | ~4,300 |
| 5 | Chinaman's Hat | 8 | chinamans hat (22,000/mo) | ~7,400 |
| 6 | Kaneohe Sandbar | 7 | kaneohe bay sandbar (720/mo) — small but our #1 position | ~310 |
| 7 | Kahana Rainforest River | 6 | kahana bay beach park (590/mo) | ~370 |
| 8 | Sharks Cove (snorkel) | 10 | sharks cove (60,500/mo) | ~9,800 |
| 9 | Paddleboard (SUP) | 7 | stand up paddleboard rental (2,400/mo) | ~580 |
| 10 | E-Bike Tours | 7 | oahu e-bike rental (480/mo) | ~310 |
| 11 | Generic Oahu Beach Hub | 8 | best oahu beaches (4,400/mo) | ~1,180 |
| 12 | Snorkeling Rental | 5 | best snorkeling oahu hawaii (720/mo) | ~390 |
| 13 | Long-tail squeeze plays | 10 | kayak oahu (2,400/mo) | ~570 |

## Top 20 ROI priority keywords

These are the keywords where moving up 3 positions = biggest traffic gain. **Combined potential: ~142 visits/mo** if all 9 are promoted to position 5.

See master-inventory.md for the full list with targets and estimated gains.

## Usage patterns

### For Ella (content writer)
- Look up the cluster for the page you're writing
- Mention cluster keywords in: title/H1, ≥2 subheadings, meta description, URL slug, image alt text

### For Kai-CSS (technical SEO)
- Verify each target page has matching schema (LocalBusiness, TouristTrip, FAQPage, HowTo)
- Build internal links from cluster hub pages to spoke pages

### For Kai (analytics + automation)
- Track rank changes **per cluster**, not per keyword
- Weekly rank-check output groups results by cluster

### For AGY (research)
- Seed list for keyword expansion
- Identifies which clusters need more keyword coverage (currently <5 keywords)

## Limitations & future work

- **Volume data is Ubersuggest-based**, not Google. Once OAuth extended, replace with real GSC search volume data.
- **Current rank is from baseline June 19**, not continuously updated. Will refresh weekly via rank_tracker.py cron.
- **No Japanese market keywords** — separate inventory needed.
- **No voice-search patterns** ("near me", "open now", "for kids") — separate inventory needed.
