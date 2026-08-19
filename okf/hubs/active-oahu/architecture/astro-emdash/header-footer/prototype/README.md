---
type: Standards
title: Astro/emdash shell prototype — typed data slice
description: Generated: 2026-07-11T23:42:58Z Source commit: `6686a0340a961401c2415e614558f6e622259681`
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/architecture/astro-emdash/header-footer/prototype/README.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Astro/emdash shell prototype — typed data slice

Generated: 2026-07-11T23:42:58Z  
Source commit: `6686a0340a961401c2415e614558f6e622259681`

This prototype is intentionally **non-public** and does not change rendered site output. It proves the current Active Oahu header/footer can be represented as typed data before real Astro adoption.

## Files

- `src/content/nav/aot-shell-data.json` — canonical shell data source.
- `src/content/nav/aot-nav.json` — primary nav + utility links.
- `src/content/nav/aot-footer.json` — footer groups + business/contact data.
- `src/content/nav/aot-booking.json` — FareHarbor booking config.
- `src/types/shell.ts` — TypeScript data interfaces.
- `src/components/shell/*.astro` — non-public component prototype.
- `rendered/aot-shell-prototype.html` — static proof render generated from the same JSON.

## What is preserved

- Primary nav labels and hrefs from the current homepage header.
- Footer hrefs from the current homepage footer, including contact, social, gallery, company, and policy links.
- FareHarbor shortname: `activeoahutours`.
- Booking CTA label: `Book Online`.
- Phone and email contact paths.
- Intent tags for users/search/AI/booking: `tour`, `rental`, `guide`, `support`, `booking`, `language`, `contact`, `social`, `trust`.

## Why this matters

Astro should not inherit the current static export’s hundreds of header/footer variants. This data slice becomes the single source for:

1. rendered navigation,
2. `SiteNavigationElement`/LocalBusiness schema,
3. `/llms.txt` and AI navigation summaries,
4. booking CTA behavior.


## Generated schema + AI outputs

This slice adds search/AI artifacts generated from the same canonical shell data:

- `generated/schema/site-navigation.jsonld` — `SiteNavigationElement` graph.
- `generated/schema/local-business.jsonld` — LocalBusiness/contact/booking action graph.
- `generated/schema/combined-shell-schema.jsonld` — combined graph for future page injection.
- `generated/llms/navigation-section.txt` — `/llms.txt` navigation section.
- `generated/schema-ai-manifest.json` — source/output/count manifest.
- `scripts/generate-schema-ai.py` — reproducible generator.

The generated outputs preserve the same user/search/AI/booking priority order and the same FareHarbor shortname (`activeoahutours`) as the canonical shell data.

## Verification target

This slice must pass exact label/href parity against `current-header-footer-inventory.json` before visual styling or page adoption starts. The schema/AI outputs must also regenerate deterministically from `aot-shell-data.json`.

## Sandbox route semantic proof

This slice adds:

- `src/pages/_sandbox/aot-shell.astro` — non-public Astro route stub that imports shell data, generated JSON-LD, and `/llms.txt` output.
- `rendered/sandbox-shell-route.html` — deterministic static proof render for semantic/accessibility checks before an Astro build harness exists.
- `scripts/render-sandbox-route.py` — reproducible renderer for the sandbox proof.

The proof is `noindex,nofollow`, includes one `header`, one `main`, and one `footer`, embeds generated `SiteNavigationElement` and LocalBusiness JSON-LD, includes the `/llms.txt` excerpt/digest, preserves `activeoahutours`, and keeps `h1`-`h6` on Open Sans Condensed Bold.
