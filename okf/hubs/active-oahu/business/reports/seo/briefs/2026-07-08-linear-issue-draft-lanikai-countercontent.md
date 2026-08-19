---
type: Operations
title: Linear Issue Draft — Lanikai Snorkel Fix + KBA Counter-Content
description: Linear API create attempt failed on 2026-07-08 because the workspace API quota was exhausted (`Rate limit exceeded. Only 2500 requests are allowed per 1 hour`). Use this draft when rate limit resets.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/reports/seo/briefs/2026-07-08-linear-issue-draft-lanikai-countercontent.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# Linear Issue Draft — Lanikai Snorkel Fix + KBA Counter-Content

Linear API create attempt failed on 2026-07-08 because the workspace API quota was exhausted (`Rate limit exceeded. Only 2500 requests are allowed per 1 hour`). Use this draft when rate limit resets.

## Title
Fix Lanikai snorkel mismatch and build KBA Kailua/Lanikai counter-content

## Project
Active Oahu Tours — Media Library & Content Engine

## Labels
- `agent:kai-content`
- `pipeline:content-seo`
- `agent:kai`

## Priority
High / P2

## Description

### Why now

After GSC + Ubersuggest re-auth, Kai analyzed KBA territory alerts for Kailua/Lanikai beach-day and rental intent. KBA is ranking/appearing with pages for Lanikai snorkeling, snorkel rentals, beach chair/umbrella rentals, and a Kailua/Lanikai day pass.

### Verified evidence

- Ubersuggest MCP: KBA `lanikai` page shows `lanikai beach snorkel` pos 2 / vol 720 / traffic 44; `snorkeling lanikai beach` pos 7 / vol 590 / traffic 13.
- Ubersuggest MCP: KBA `snorkel-rental-lanikai-oahu` shows 122 estimated traffic / 48 organic keywords.
- GSC API (`sc-domain:activeoahutours.com`, 2026-04-07 → 2026-07-06): `lanikai beach snorkeling` has 488 impressions / avg position 10.5 / CTR 0.4%.
- GSC API: AOT `activities/lanikai-beach-self-guided-snorkel/` has 911 impressions / avg position 10.9 / CTR 0.1%.
- Repo inspection: local page title says Lanikai, but headings/body include Sharks Cove / Pupukea content. This is the first fix.

### Private report / briefs

- PR merged: https://github.com/mbgulden/active-oahu-business/pull/2
- `okf/reports/seo/2026-07-08-kba-lanikai-kailua-countermove.md`
- `okf/reports/seo/briefs/2026-07-08-lanikai-kailua-countercontent-briefs.md`

### Implementation scope

1. Rewrite/fix `https://activeoahutours.com/activities/lanikai-beach-self-guided-snorkel/` so title, H1/H2s, body, schema, and CTA all align with Lanikai snorkeling.
2. Refresh or build the Kailua/Lanikai beach-day rental hub using existing `https://activeoahutours.com/beach-gear-rentals/` as the likely primary target.
3. Refresh chair/umbrella and snorkel rental pages with Windward/Kailua/Lanikai positioning and internal links.

### Acceptance criteria

- No Sharks Cove / Pupukea copy remains on the Lanikai snorkel page except as intentional comparison/internal links.
- Target GSC queries are naturally addressed: `lanikai beach snorkeling`, `lanikai snorkeling`, `lanikai beach snorkel`, `snorkel rentals kailua`.
- Page has direct booking CTA and local safety/E-E-A-T sections.
- Post-publish: submit sitemap / changed URL in GSC and track query/page movement for 28 days.
