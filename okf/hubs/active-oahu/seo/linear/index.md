---
type: Index
title: Linear Tracking — AOT SEO Initiative
description: Tracking issue list for content production, audits, fixes, AGY dispatches — with status, priority, owner, and target dates for the 6-month initiative.
tags: [index, linear, tracking, aot, seo, project-management]
timestamp: 2026-06-19T14:45:00Z
linear_issue: null
git_path: okf/linear/index.md
status: current
linear_workspace: growthwebdev
linear_project_id: 5a9ea0d6-f6c1-42ee-adf6-f4dd59e9db9b (existing) or new "AOT-SEO" project
resource: okf/hubs/active-oahu/seo/linear/index.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Linear Tracking — AOT SEO Initiative

All work for the AOT SEO/GEO initiative is tracked in Linear under the **Growth Web Dev** workspace, project **AOT-SEO** (to be created).

## Linear project structure

| Project | Owner | Description |
|---|---|---|
| **AOT-SEO-CONTENT** | Ella | Content briefs, drafts, reviews, publishes |
| **AOT-SEO-TECH** | Kai-CSS | Schema, internal links, performance, deployments |
| **AOT-SEO-AGY-RESEARCH** | AGY | Ubersuggest sweeps, ATP, SERP analysis, AI Overview capture |
| **AOT-SEO-OUTREACH** | Michael | Backlink outreach, partnerships, PR |
| **AOT-SEO-CONVERSION** | Kai | CRO, GA4, booking funnel optimization |
| **AOT-SEO-PHOTOS** | Kai | Photo deployment, alt-text, image SEO |

## Issue tracking (created + pending)

### Tier 1 — Month 1-2 (high priority)

| Issue | Title | Owner | Status |
|---|---|---|---|
| GRO-2052 | Complete state-of-AOT baseline audit | Kai | ✅ Done (2026-06-19) |
| GRO-2053 | Re-auth Google OAuth with GSC + GA4 scopes | Kai + Michael | 🔴 Blocked (waiting for Michael) |
| GRO-2054 | Inject LocalBusiness + TouristTrip schema into top 5 revenue pages | Kai-CSS | Pending |
| GRO-2055 | Refresh Sharks Cove Snorkel page (push #3 → #2) | Ella + Kai | Pending |
| GRO-2056 | Create Snorkeling Oahu North Shore page (NEW — closes critical gap) | Ella + Kai | Pending |
| GRO-2057 | Refresh Oahu Paddleboard Rental page (push #7 → #3) | Ella + Kai | Pending |
| GRO-2058 | Refresh Lanikai Beach Kayak page (push #6 → #3) | Ella + Kai | Pending |
| GRO-2059 | Refresh Oahu E-Bike Rental page (push #6 → #3) | Ella + Kai | Pending |
| GRO-2060 | Refresh Mokulua Islands Kayak page (push #7 → #5) | Ella + Kai | Pending |
| GRO-2061 | Expand Waimanalo Beach Guide (GRO-795 priority #1) | Ella + Kai | Pending |
| GRO-2062 | Deploy photos from Synology to top 5 pages | Kai + Kai-CSS | Pending |
| GRO-2063 | Publish Lanikai Pillbox Hike Guide (NEW) | Ella + Kai | Pending |
| GRO-2064 | Publish Best Beaches Windward Oahu pillar page (NEW master) | Ella + Kai | Pending |
| GRO-2065 | Publish Lanikai vs Kailua Beach comparison (NEW) | Ella + Kai | Pending |
| GRO-2066 | Submit to 10 Hawaii business directories (backlinks) | Michael | Pending |
| GRO-2067 | Set up daily rank tracker cron job | Kai | Pending |
| GRO-2068 | Set up weekly digest cron job (Monday morning) | Kai | Pending |

### Tier 2 — Month 2-3

| Issue | Title | Owner |
|---|---|---|
| GRO-2070 | Publish Kailua Parking Guide | Ella + Kai |
| GRO-2071 | Publish Lanikai Parking Guide | Ella + Kai |
| GRO-2072 | Publish Things to Do in Kailua | Ella + Kai |
| GRO-2073 | Publish Things to Do in Waimanalo | Ella + Kai |
| GRO-2074 | Publish Waimanalo Swimming & Safety | Ella + Kai |
| GRO-2075 | Publish Best Things to Do in Kailua (blog) | Ella + Kai |
| GRO-2076 | Publish Complete Guide to Mokulua Islands Kayaking (blog) | Ella + Kai |
| GRO-2077 | Publish North Shore Oahu Snorkeling Guide (blog) | Ella + Kai |
| GRO-2078 | Publish Kaneohe Sandbar Self-Guided Kayak Tour (blog) | Ella + Kai |
| GRO-2079 | Refresh Chinaman's Hat page (push CTR) | Ella + Kai |
| GRO-2080 | Capture 4+ AI Overview citations | AGY + Kai |
| GRO-2081 | Capture 8+ Google PAA boxes | AGY + Kai |
| GRO-2082 | Set up A/B testing framework | Kai |
| GRO-2083 | First A/B test: SUP page H1 with pricing | Ella + Kai |

### Tier 3 — Month 4-6

(TBD — initialized after Tier 2 progress)

## Decision log

Decisions documented in `okf/decisions/`:
- `canonical-gdd-handling.md` — single source of truth for game design
- `image-pipeline.md` — Cloudflare Pages vs Cloudflare Images decision
- `automation-cadence.md` — daily/weekly/monthly cadence decisions
- `reporting-format.md` — markdown-first, JSON secondary, Telegram delivery

## Dependencies (which issues block others)

```
GRO-2053 (OAuth re-auth)
    └── blocks GRO-2054..2070 (need GA4/GSC data for validation)

GRO-2067 (Daily rank tracker)
    └── enables ongoing monitoring for GRO-2055..2060 (rank progress)

GRO-2062 (Photo deployment)
    └── enables higher conversion on all tour pages
```

## Workflow

1. **Kai creates issues** as work is identified (this file is the master inventory)
2. **Linear issues get labels:** `AOT-SEO-CONTENT`, `AOT-SEO-TECH`, etc.
3. **Issues get priorities:** P0 (Tier 1), P1 (Tier 2), P2 (Tier 3)
4. **Status:** Backlog → In Progress → In Review → Done
5. **Weekly digest (Monday)** reports open issues, blocked items, recent completions

## Filter views

- `is:open label:AOT-SEO-CONTENT priority:P0` — Tier 1 content briefs
- `is:open label:AOT-SEO-TECH` — Technical SEO work
- `is:open label:AOT-SEO-AGY-RESEARCH` — Research tasks
- `is:open label:AOT-SEO-OUTREACH` — Backlink outreach
- `is:blocked` — Anything blocked (e.g., waiting on Michael OAuth)

## Tracking conventions

- Each issue should have: title, description, acceptance criteria, due date, owner, labels, priority
- Commit messages should reference the Linear issue: `GRO-####: Fix broken link on Kailua beach page`
- PR descriptions should link to the Linear issue
- Status updates posted in Linear comments, not Slack/Telegram

## Open dependency: Michael

- **GRO-2053:** OAuth re-auth required (1 link click on phone). Without this, GA4 + GSC data is blocked, which limits our ability to validate content performance.
- **GRO-2066:** Business directory submissions require Michael's personal relationships (Yelp, Tripadvisor, Hawaii Tourism Authority).
