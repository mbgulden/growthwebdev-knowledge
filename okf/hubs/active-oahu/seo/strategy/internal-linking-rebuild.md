---
type: Standard
title: Internal Linking Rebuild — GSC-Informed Hub & Spoke
description: Strategy for rebuilding AOT's internal link graph based on actual traffic patterns from GSC, not theoretical hub-and-spoke from GRO-795.
tags: [internal-linking, seo, hub-and-spoke, aot, site-architecture]
timestamp: 2026-06-19T16:15:00Z
linear_issue: null
git_path: okf/strategy/internal-linking-rebuild.md
status: current
resource: okf/hubs/active-oahu/seo/strategy/internal-linking-rebuild.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Internal Linking Rebuild — GSC-Informed Hub & Spoke

## Why internal linking matters for AOT

Internal links:
- Distribute page authority (PageRank) across the site
- Help Google understand site structure
- Pass contextual relevance (anchor text)
- Improve user navigation (longer sessions, more pages per session)
- Get less-authoritative pages indexed faster

## Current state (inferred from GSC)

AOT currently has 200 indexed pages with ~1,000 backlinks across them. Page authority distribution is likely:
- Homepage: high (200+ backlinks)
- Top revenue pages (SUP, Kailua kayak, Sharks Cove, Kanohe): medium-high
- Long-tail pages: low (orphaned)

**Orphan pages estimate:** 30-50% of indexed pages have <3 internal links.

## New site architecture (after 6 months)

```
HOMEPAGE
├── /tours/ (hub)
│   ├── Guided tours → /activities/* (existing + new)
│   │   ├── /activities/sharks-cove-self-guided-snorkel/ [P0]
│   │   ├── /activities/chinamans-hat-self-guided-oahu-kayak-tour/ [P0]
│   │   ├── /activities/kailua-bay-mokulua-island-self-guided-kayak-tour/ [P0]
│   │   ├── /activities/kahana-rainforest-river-oahu-kayak-tour/ [P0]
│   │   └── /activities/NEW/* (Month 1-3)
│   └── E-bike tours → /tours/e-bike-* (existing + new)
├── /rentals/ (hub)
│   ├── Kayak rentals → /rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/ [P0]
│   ├── SUP rentals → /rentals/oahu-stand-up-paddle-board-rentals-sup-hire/ [P0]
│   ├── Snorkel rentals → /rentals/oahu-snorkel-mask-and-fin-rentals/ [P1]
│   ├── Beach chairs → /rentals/oahu-beach-chair-rentals/ [P2]
│   └── Life vests + accessories → /rentals/* [P2]
├── /guides/ (NEW hub - critical)
│   ├── Location guides
│   │   ├── /guides/lanikai-beach/ [NEW - P0]
│   │   ├── /guides/kailua-beach-park/ [P0]
│   │   ├── /guides/waimanalo-beach/ [P0]
│   │   └── /guides/sea-turtles-on-oahu/ [NEW - P0]
│   ├── Topic guides
│   │   ├── /guides/best-beaches-windward-oahu/ [NEW - P0]
│   │   ├── /guides/best-snorkeling-on-oahu/ [NEW - P0]
│   │   ├── /guides/best-oahu-activities-for-families/ [NEW - P2]
│   │   └── /guides/beginner-kayak-tours-oahu/ [NEW - P1]
│   └── How-to guides
│       ├── /guides/how-to-snorkel-sharks-cove/ [P1]
│       └── /guides/kayaking-mokulua-islands-guide/ [P1]
├── /faq/ (NEW hub - critical for long-tail)
│   ├── /faq/[topic-slug]/ (30+ pages by Q3)
└── /near-me/ (NEW hub - voice search)
    ├── /near-me/kayak-rental-near-me/
    ├── /near-me/snorkel-rental-near-me/
    ├── /near-me/paddleboard-rental-near-me/
    └── /near-me/e-bike-rental-near-me/
└── /best/ (NEW hub - commercial intent)
    ├── /best/oahu-beaches/
    ├── /best/oahu-snorkeling/
    ├── /best/oahu-kayak-tours/
    └── /best/oahu-e-bike-tours/
```

## Anchor text rules

When linking from one AOT page to another:

### Varied anchor text

For the same target page, vary anchor text:
- "Kailua kayak rental" (exact match)
- "Kailua kayak tours" (close variant)
- "rent a kayak in Kailua" (natural)
- "Click here to book" (CTA-style)
- The page title itself (branded)
- Just the brand name (for homepage)

Avoid:
- ❌ Same exact anchor text 10+ times (Google sees as manipulative)
- ❌ Generic "click here" only (wastes anchor text relevance)
- ❌ Naked URLs (https://activeoahutours.com/...) — looks spammy

## Per-page linking rules

### Hub pages (tours, rentals, guides)

- Link DOWN to every spoke page (1x each)
- Link UP to homepage (1x in footer or hero)
- Link HORIZONTALLY to other hubs (1x in "Related sections")

### Spoke pages (tours, rentals, individual guides)

- Link UP to relevant hub (1x in breadcrumb)
- Link DOWN to sub-spokes if applicable
- Link HORIZONTALLY to 3-5 related spokes
- Link UP to homepage (1x in footer CTA)

### Revenue pages (bookable activities)

- Link UP to relevant guide (1x in "More info" section)
- Link HORIZONTALLY to 3-5 related activities ("Other tours you might like")
- Link to FAQ pages if relevant

## Internal link audit (per page)

For each top 20 page by GSC clicks:

1. **Inbound links:** count unique pages linking TO this page
2. **Outbound links:** count links going FROM this page
3. **Anchor text distribution:** are anchors varied?
4. **Orphan check:** does any page have <2 inbound?

Tools to use:
- Screaming Frog SEO Spider (free trial available)
- Google Search Console Internal Links report
- Sitebulb (paid, deeper analysis)

## Rebuild phases

### Phase 1 (Month 1): Quick wins

For each top 20 page by GSC clicks:
- Add 3-5 internal links to related pages
- Fix any broken internal links (from earlier audit)
- Add breadcrumb navigation
- Add "Related Tours" section with 3-5 links

### Phase 2 (Month 2): Hub pages

- Build `/guides/` hub with index linking to all guides
- Build `/tours/` and `/rentals/` hub if not already
- Add cross-hub navigation

### Phase 3 (Month 3): New content linking

- Every new page (FAQ, near-me, etc.) links back to hub + 3-5 related pages
- Every new guide links UP to /guides/ + DOWN to 3-5 related tours

## Success metrics

| Metric | Baseline | Target |
|---|---:|---:|
| Average inbound links per page | ~3 | 8-10 |
| Orphan pages (<3 inbound) | 30-50% | <5% |
| Click depth from homepage | 3+ | 1-2 for top pages |
| Internal links per revenue page | ~5 | 12-15 |

---

*Strategy authored by Kai on 2026-06-19.*
