---
type: Operations
title: AOT Content Fact-Check Gates
description: **Owner:** Kai **Applies to:** Active Oahu Tours content, SEO/AEO copy, guide updates, tour pages, Linear executor work, and agent-generated reports that mention specific facts.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/ops/content-fact-check-gates.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# AOT Content Fact-Check Gates

**Owner:** Kai  
**Applies to:** Active Oahu Tours content, SEO/AEO copy, guide updates, tour pages, Linear executor work, and agent-generated reports that mention specific facts.

## Purpose

Active Oahu content must not ship obvious factual errors. Any copy that names a place, feature, route, product, price, duration, safety condition, person, image, or cultural/Hawaiian term must pass a fact-check gate before it is treated as done.

## When this gate is required

Run this gate before committing, opening/updating a PR, commenting “done,” or moving a Linear issue forward when the work mentions any of the following:

- **Places or alternate names:** Kailua, Lanikai, Kāneʻohe, Mokoliʻi / Chinaman’s Hat, Kahana, Sharks Cove, North Shore, launch points, beaches, islands, reefs, trails, bays.
- **Products/features:** kayak rentals, guided tours, e-bike adventures, stand-up paddleboards, snorkel gear, beach equipment, delivery, pickup, permits, route guidance.
- **Operational claims:** prices, durations, pickup location, launch point, availability, seasonality, vehicle requirements, route distance, required skill level.
- **Safety claims:** wind, tide, surf, reef, seasonal conditions, beginner suitability, route difficulty, landing rules, permit/access constraints.
- **Cultural/language claims:** Hawaiian place names, ʻokina, kahakō, island/region context, culturally sensitive explanations.
- **Imagery claims:** any image that implies a specific place, route, activity, product, or customer experience.

## Fact-check sequence

1. **Extract named facts** from the changed copy/report.
2. **Classify each fact** as place, product/feature, operational detail, safety claim, cultural/language term, or imagery claim.
3. **Verify each fact** against the strongest available source:
   - AOT canonical page/source for AOT offerings and operating details.
   - FareHarbor for bookable products, pricing, durations, and availability-sensitive details.
   - Official/authoritative public sources for geography, access, park/permit rules, safety, and place-name facts.
   - Synology_NAS / media metadata for image facts (see [`../assets/image-gps-verification.md`](../assets/image-gps-verification.md)).
4. **Correct obvious errors immediately.** Examples:
   - Use `Kāneʻohe` and `Mokoliʻi` in polished copy.
   - Use “Chinaman’s Hat” only as the common English alternate where it helps users recognize Mokoliʻi.
   - Do not claim AOT supports a product, pickup method, permit, route, or delivery option unless verified.
   - Do not imply a route is always safe; qualify wind, tide, surf, season, skill, permit, and launch-point details where relevant.
5. **If a fact cannot be verified**, remove it, soften it, or mark the issue blocked with the exact unknown. Do not invent specifics.
6. **Record the gate** in the PR/Linear comment.

## Required PR/Linear comment section

```markdown
## Fact-check gates

| Fact checked | Classification | Source / method | Result |
|---|---|---|---|
| Mokoliʻi / Chinaman’s Hat naming | Place / alternate name | AOT canonical source + official/public geography check | Corrected to “Mokoliʻi (Chinaman’s Hat)” |
| E-bike adventures | Product/feature | AOT site/FareHarbor source | Verified as supported |
| Wind/tide/safety language | Safety claim | AOT route guidance + public condition context | Qualified; no unconditional safety claim |
```

If no named facts were touched, say:

```markdown
## Fact-check gates
No named facts, product claims, location claims, operational claims, safety claims, or imagery claims were changed.
```

## Non-negotiables

- Do not leave “close enough” facts in AOT copy.
- Do not use generated or guessed place facts.
- Do not assume a feature exists because it sounds plausible for a tour company.
- Do not treat a spell-check pass as a fact-check pass.
- If a named fact matters to customer expectations, booking, safety, or cultural respect, verify it before shipping.
