---
type: Standards
title: Astro/emdash header + footer canonical shell prep
description: Generated: 2026-07-11T22:46:20Z Source commit: `addf7acb2f983bb003c5e3637b92949839a440bf`
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/architecture/astro-emdash/header-footer/README.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Astro/emdash header + footer canonical shell prep

Generated: 2026-07-11T22:46:20Z  
Source commit: `addf7acb2f983bb003c5e3637b92949839a440bf`

This is the first low-risk preparation step for moving Active Oahu Tours toward Astro + emdash without rewriting content prematurely.

## Goal

Turn the repeated WordPress-export header/footer into canonical reusable shell modules that help, in order:

1. **Users** understand where they are, move by intent, and book without fighting the menu.
2. **Search engines** crawl stable, semantic navigation and LocalBusiness/contact signals.
3. **AI assistants** parse a canonical navigation graph instead of guessing from duplicated HTML.
4. **Booking conversion** stays one tap away without hijacking the navigation experience.

## Current inventory

| Area | Count |
|---|---:|
| HTML pages scanned | 306 |
| Pages with rendered header | 295 |
| Header structural variants | 220 |
| Pages with rendered footer | 295 |
| Footer structural variants | 214 |
| Homepage header links captured | 27 |
| Homepage footer links captured | 20 |

See `current-header-footer-inventory.json` for the preserved labels/hrefs and variant samples.

## Canon modules to create in Astro

```txt
src/components/shell/SiteShell.astro
src/components/shell/Header.astro
src/components/shell/PrimaryNav.astro
src/components/shell/BookNowButton.astro
src/components/shell/LanguageSwitch.astro
src/components/shell/Footer.astro
src/content/nav/aot-nav.ts or emdash nav collection
src/content/nav/aot-footer.ts or emdash footer collection
```

The contract is in `canonical-shell.contract.json`.

## Migration order

### Phase 1 — contract + inventory (this PR)

- Preserve current header/footer labels, hrefs, phone, logo destination, language switch, and FareHarbor booking config.
- Record the module/data contract before changing rendered output.
- Capture the variant count so later work can shrink duplication safely.

### Phase 2 — data extraction

- Convert the primary nav and footer links into typed nav/footer data.
- Add stable IDs and intent tags: `tour`, `rental`, `guide`, `support`, `booking`, `language`, `legal`.
- Add one-sentence `aiSummary` fields for high-level nav groups so `/llms.txt` and AI navigation can use the same graph.

### Phase 3 — static module prototype

- Build Astro `Header` and `Footer` modules from the data.
- Render to a sandbox route first, not production pages.
- Compare link labels/hrefs against this inventory.

### Phase 4 — page shell adoption

- Start with a small page cohort: homepage, one activity, one rental, one guide, one Japanese page.
- Only then expand to all content pages.
- Keep visual CSS parity with the current AOT shell until the content is fully preserved.

## Non-negotiables

- No content rewrite as part of shell migration.
- No booking URL/shortname changes without a dedicated booking-flow verifier.
- Parent nav anchors remain real links.
- Header/footer are accessible without JavaScript.
- `h1`-`h6` remain Open Sans Condensed Bold.
- Each migrated page has `header`, `main`, and `footer` landmarks.
- AI/search metadata derives from the same nav/footer source as the UI.

## Phase 2 completed — typed data + non-public prototype

The next slice added `prototype/`, including typed nav/footer/booking JSON, TypeScript interfaces, Astro component stubs, and a static non-public render proof. The verification target remains exact link-label/href parity before visual styling or page adoption.

## Phase 3 completed — schema + AI outputs

The next slice generated `SiteNavigationElement`, LocalBusiness/contact schema, a combined JSON-LD graph, and an `/llms.txt` navigation section from `prototype/src/content/nav/aot-shell-data.json`. Rendered UI remains unchanged.

## Phase 4 completed — sandbox route semantic proof

The next slice added a non-public sandbox route stub and deterministic rendered proof that consume the canonical shell data, generated JSON-LD schema, and `/llms.txt` navigation output together. Rendered production `site/` files remain unchanged.

## Next implementation slice

Create the first real Astro page cohort plan: homepage, one activity, one rental, one guide, and one Japanese page. Capture current metadata/schema/content/booking baselines before building any public replacement route.
