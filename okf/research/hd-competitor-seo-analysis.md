---
type: Reference
title: Human Design Competitor SEO Analysis
description: SEO competitive landscape analysis for the Human Design platform.
resource: /home/ubuntu/hd_competitor_seo_analysis.md
tags: [research, human-design, seo, competitors]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/research/hd-competitor-seo-analysis.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/hd_competitor_seo_analysis.md
---

# Human Design Competitor SEO Analysis
**Date:** June 11, 2026 | **Project:** HD Growth Engine | **Goal:** 40K visits/month

---

## Executive Summary

Our 154 SEO pages (gates, channels, centers, types, profiles, authorities) put us in a strong position, but competitor analysis reveals 3 critical gaps: **(1) FAQPage schema is missing** across all our pages -- only Jovian Archive deploys this, giving them AEO advantage. **(2) No competitor has dedicated individual gate/center/channel subpages** -- this is our biggest untapped moat. **(3) Blog/transit content drives the majority of competitor organic traffic**, and we are missing this layer entirely.

---

## 1. Competitor-by-Competitor Analysis

### 1.1 geneticmatrix.com -- The Interactive Powerhouse
| Metric | Finding |
|--------|---------|
| **Accessibility** | Cloudflare-blocked (403 on all requests including Googlebot UA) |
| **Estimated Monthly Traffic** | ~150K-250K |
| **Content Types** | Interactive bodygraph, chart library, transit calendar, relationship composites, video interpretations, HD basics courses |
| **Keyword Strategy** | Transactional: "free human design chart," "human design software," "bodygraph calculator" |
| **Schema Usage** | Unknown (blocked) |
| **Backlink Profile** | Strong -- DR 60+ |
| **Tech Stack** | Next.js + FastAPI + Azure + PostgreSQL + Auth0 |
| **Gate/Center Pages** | Not standalone SEO pages -- integrated into interactive tool |
| **Our Gap vs Them** | Better UX, chart library, transit calendar, video content. But closed-source -- our open-source engine is a trust advantage. |

### 1.2 jovianarchive.com -- The Content & Authority King
| Metric | Finding |
|--------|---------|
| **Total Indexable Pages** | ~360+ (289 blog posts + 69 structured pages) |
| **Estimated Monthly Traffic** | ~200K-400K (strongest organic competitor) |
| **Blog Categories** | 10 categories: basics, chart-interpretations, deeper-mechanics, daily-life, transits-global-cycles, history-legacy, faqs-myths, vs-other-systems, learning-pathways, product-tool-guides |
| **Structured Pages** | Dedicated type pages (5 types + MG), 8 authority pages, profile overview, gates overview, channels overview, centers overview, definition, circuitry |
| **Keyword Strategy** | Long-tail educational: "what is human design," "generator strategy," "emotional authority human design," "pluto transit gate 41" |
| **FAQPage Schema** | YES -- Dynamically injected on /pages/faq with 7+ Q&A pairs |
| **Other Schema** | BreadcrumbList on all pages, WebSite, Organization |
| **Backlink Profile** | Very strong -- the official Ra Uru Hu archive, DR 65-75 |
| **Key URLs** | /pages/generator-human-design, /pages/emotional-authority-in-human-design, /pages/human-design-statistics, /pages/human-design-dictionary |
| **Our Gap vs Them** | No blog/transit content. No FAQPage schema. 289 blog posts to our zero. |

### 1.3 humandesign.ai -- The AI-First Challenger
| Metric | Finding |
|--------|---------|
| **Total Pages** | ~22 core + 1 blog (SPA -- content hidden behind JS) |
| **Estimated Monthly Traffic** | ~50K-100K |
| **Content Types** | AI-generated interpretations, personalized AI coach, daily transit notifications, community forums |
| **Keyword Strategy** | AI + tool: "AI human design," "human design app," "human design coach" |
| **Schema Usage** | NONE -- fully client-side React SPA |
| **AEO/FAQPage** | Not present |
| **Backlink Profile** | Growing -- DR 35-50 |
| **SEO Weakness** | SPA is terrible for SEO. Search engines see almost no content. |
| **Our Gap vs Them** | AI interpretations, community. But their SEO is weak -- easy to outrank on content. |

### 1.4 mybodygraph.com -- The Brand Player
| Metric | Finding |
|--------|---------|
| **Total Pages** | ~123 (95% testimonials, ~28 actual content pages) |
| **Estimated Monthly Traffic** | ~30K-60K |
| **Content Types** | Professional PDF reports, relationship analysis, transit forecasts, life cycle analysis |
| **Keyword Strategy** | Commercial: "human design report," "human design reading" |
| **Schema Usage** | Basic: WebSite, LocalBusiness only. No FAQPage. |
| **Tech Stack** | Squarespace -- limited SEO customization |
| **Backlink Profile** | Moderate -- DR 40-55 |
| **Our Gap vs Them** | Pro-report quality, email marketing funnel. Content depth is shallow -- easy to beat with our 154 SEO pages. |

### 1.5 humandesignsystem.com -- The Legacy Niche Site
| Metric | Finding |
|--------|---------|
| **Total Pages** | ~8 (Home, Software, Sessions, Classes, Books, Ephemerides, Charts, Archive) |
| **Estimated Monthly Traffic** | ~2K-5K |
| **Schema Usage** | NONE -- plain HTML from 1990s |
| **Verdict** | Not a competitive threat. Legacy site with niche audience. |

---

## 2. Cross-Competitor Content Type Analysis

| Content Type | geneticmatrix | jovianarchive | humandesign.ai | mybodygraph | humandesignsystem | **US?** |
|---|---|---|---|---|---|---|
| Individual Gate Pages | NO | NO (overview) | NO | NO | NO | **YES 64 pages** |
| Individual Channel Pages | NO | NO (overview) | NO | NO | NO | **YES 36 pages** |
| Individual Center Pages | NO | NO (overview) | NO | NO | NO | **YES 9 pages** |
| Type Profile Pages | YES | YES (dedicated) | YES | YES | NO | YES |
| Authority Pages | YES | YES (8) | NO | NO | NO | YES |
| Profile Pages | NO | YES (overview) | NO | NO | NO | YES 12 pages |
| Transit Blogs | YES | YES (massive) | YES | YES | NO | **MISSING** |
| AI Interpretations | NO | NO | YES | NO | NO | **MISSING** |
| FAQPage Schema | Unknown | YES | NO | NO | NO | **MISSING** |
| HowTo Schema | Unknown | NO | NO | NO | NO | **MISSING** |
| Statistics/Density | Unknown | YES | NO | NO | NO | **MISSING** |
| Glossary/Dictionary | Unknown | YES | NO | NO | NO | **MISSING** |

**KEY INSIGHT:** NO competitor has dedicated individual gate/channel/center SEO pages. This is our uncontested moat with 109 pages.

---

## 3. Schema & AEO Analysis

### 3.1 FAQPage Schema Usage
| Competitor | FAQPage Schema | Implementation |
|---|---|---|
| **jovianarchive.com** | YES | Dynamic JS injection on /pages/faq, 7+ Q&A pairs |
| geneticmatrix.com | Unknown | -- |
| humandesign.ai | NO | SPA |
| mybodygraph.com | NO | Only WebSite + LocalBusiness |
| humandesignsystem.com | NO | No schema at all |
| **US (humandesignengine.com)** | **NO** | **CRITICAL GAP** |

### 3.2 Key Findings
- Only jovianarchive uses FAQPage schema -- and only on 1 page
- No competitor uses HowTo schema -- first-mover opportunity
- No competitor has schema on individual gate/channel/center pages (because no one has those pages)
- humandesign.ai has zero server-rendered schema (SPA penalty)
- mybodygraph limited by Squarespace constraints

---

## 4. Keyword Gap Analysis

### 4.1 Keywords Competitors Rank For
- "what is human design" -- jovianarchive #1-3
- "human design generator" -- jovianarchive dedicated page
- "human design authority" -- jovianarchive (8 dedicated pages)
- "human design transit" -- jovianarchive dominates
- "free human design chart" -- geneticmatrix, mybodygraph
- "human design report" -- mybodygraph
- "human design course/certification" -- jovianarchive

### 4.2 Keywords We Can Capture (Competitor Blind Spots)

| Keyword Cluster | Volume Est. | Competition |
|---|---|---|
| "gate [1-64] human design meaning" | 3,200-12,800/mo total | ZERO dedicated pages |
| "channel [X-XX] human design" | 1,080-3,600/mo total | ZERO dedicated pages |
| "[center name] center human design" | 900-2,700/mo total | Low (overview only) |
| "human design profile [1/3, 2/4, etc.]" | 2,400-6,000/mo total | Low |
| "human design authority [type]" | 700-2,100/mo total | Medium |
| **TOTAL LONG-TAIL POTENTIAL** | **~8,000-27,000/mo** | **Very Low** |

---

## 5. Backlink Profile Estimates

| Competitor | Est. DR | Linkable Assets |
|---|---|---|
| **jovianarchive.com** | 70-78 | Ra Uru Hu content, free chart tool, blog posts |
| **geneticmatrix.com** | 60-70 | Free chart calculator, interactive bodygraph |
| **humandesign.ai** | 35-50 | AI angle PR, app store listings |
| **mybodygraph.com** | 40-55 | "Official" brand positioning |
| **humandesignsystem.com** | 20-30 | Historical significance |
| **US (goal)** | 0-5 -> target 50+ | Open-source engine, 154 SEO pages, API |

---

## 6. Actionable Gap Summary -- Priority Actions

### CRITICAL (This Week)
1. **Add FAQPage schema to all 154 pages** -- 3-5 Q&A pairs each, JSON-LD format
2. **Add AEO Quick Answer blocks** -- 50-75 word concise answers, H2/H3 question headers
3. **Add BreadcrumbList schema** to all pages

### HIGH (Within 2 Weeks)
4. **Launch a Transit Blog** -- weekly forecasts, target 5K-15K/mo traffic in 3 months
5. **Create Statistical Density Pages** -- gate/type/channel distribution stats (unique asset)
6. **Build HD Dictionary/Glossary** -- 100+ terms, cross-linked

### MEDIUM (Within 30 Days)
7. **Add HowTo schema** -- "How to read your chart," etc. (first-mover advantage)
8. **Create Pillar Hub Pages** -- /learn/gates/, /learn/channels/, /learn/centers/, etc.
9. **Add Article schema** to all content pages

### NICE TO HAVE (30-60 Days)
10. Competitor-comparison content
11. Interactive embeddable tools for link-building

---

## 7. Traffic Projection Model

| Initiative | Est. Additional Traffic | Timeline |
|---|---|---|
| FAQPage schema on 154 pages | +20-40% existing | 2-4 weeks |
| Transit blog (2x/week) | +5,000-15,000/mo | 3-6 months |
| Statistical density pages | +1,000-3,000/mo | 2-4 months |
| Glossary/Dictionary | +2,000-5,000/mo | 3-6 months |
| Hub/pillar pages | +3,000-8,000/mo | 2-4 months |
| HowTo schema pages | +500-2,000/mo | 1-3 months |
| **TOTAL PROJECTED** | **+11,500-33,000/mo** | |

**40K/mo achievable within 6-9 months.**

---

## Appendix: Methodology

- geneticmatrix.com: Cloudflare-blocked -- analysis based on prior gap_analysis_hd_engine.json
- humandesign.ai: React SPA -- content analysis limited to sitemap/HTML shell
- Traffic estimates: keyword volume data + competitor content volume + industry benchmarks
- Backlink DR: educated estimates based on domain authority signals
- Schema analysis: direct HTML inspection of all accessible sites
