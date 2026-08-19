---
type: Standards
title: Active Oahu Astro/emdash next-steps execution plan
description: Move Active Oahu Tours toward Astro + emdash without breaking the live WordPress-exported site. The migration path stays methodical: prove the shell, schema, AI, and route semantics in a private sandbox before any produc
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/architecture/astro-emdash/header-footer/next-steps-execution-plan.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Astro/emdash next-steps execution plan

## Goal

Move Active Oahu Tours toward Astro + emdash without breaking the live WordPress-exported site. The migration path stays methodical: prove the shell, schema, AI, and route semantics in a private sandbox before any production page adoption.

## Guiding priority order

1. **Users** — accessible landmarks, crawlable/usable links, no JavaScript dependency for navigation.
2. **Search engines** — stable navigation/schema generated from the same source as the UI.
3. **AI assistants** — `/llms.txt` and route summaries generated from canonical shell data, not scraped guesses.
4. **Booking conversion** — FareHarbor stays intact and one-tap, but does not replace crawlable navigation.

## Current completed foundation

- Header/footer inventory and shell contract exist under `okf/architecture/astro-emdash/header-footer/`.
- Canonical typed shell data exists under `prototype/src/content/nav/`.
- Non-public Astro component stubs exist under `prototype/src/components/shell/`.
- Generated schema and AI outputs exist under `prototype/generated/`.
- No rendered `site/` files have been changed by the Astro prep slices.

## Execution phases from here

### Phase 4 — sandbox route semantic proof (this slice)

Build a private sandbox route/proof that consumes all existing shell artifacts together:

- canonical shell data,
- Astro shell component stubs,
- `SiteNavigationElement` JSON-LD,
- LocalBusiness JSON-LD,
- `/llms.txt` navigation section.

Acceptance checks:

- Route is clearly non-public/noindex.
- Route has exactly one `header`, one `main`, and one `footer` landmark.
- Route includes skip link and accessible nav labels.
- Route includes generated JSON-LD from the canonical generated files.
- Route references the `/llms.txt` navigation artifact and includes a digest/summary.
- Route preserves FareHarbor shortname `activeoahutours`.
- Route keeps `h1`-`h6` on Open Sans Condensed Bold.
- Route is artifact-only; no `site/` production output changes.

### Phase 5 — sandbox rendered QA

Run rendered checks against the sandbox proof:

- heading hierarchy,
- link count and critical link presence,
- JSON-LD parseability,
- no duplicate IDs,
- no empty anchors,
- no missing `href`s,
- no public-index markers,
- no drift between shell data and generated schema/AI outputs.

### Phase 6 — first real Astro page cohort plan

After the sandbox passes, create a cohort adoption plan for:

- homepage,
- one activity page,
- one rental page,
- one guide page,
- one Japanese page.

Acceptance checks before building:

- source route selected,
- content boundaries documented,
- current metadata/schema captured,
- booking path verified,
- Lighthouse baseline captured,
- rollback path documented.

### Phase 7 — first cohort implementation

Build the cohort in Astro behind a private/non-public output target first. Do not replace production URLs until rendered parity and conversion-path verification pass.

### Phase 8 — production adoption gate

Only after the cohort passes:

- visual parity screenshots,
- navigation parity,
- schema validation,
- booking launch verification,
- Lighthouse threshold review,
- Cloudflare preview verification.

## Current slice deliverable

This PR executes **Phase 4** by adding a sandbox Astro route stub plus a deterministic rendered proof generated from the canonical shell/schema/AI artifacts.
