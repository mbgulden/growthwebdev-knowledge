# AOT Astro/emdash header/footer shell prep — 2026-07-11

## Trigger

Michael asked to begin moving Active Oahu Tours toward Astro + emdash methodically, preserving current content while establishing canonical reusable modules that help users, search engines, AI, and booking in that order. He specifically asked to start with the standardized header and footer.

## Durable pattern

Do **not** start by changing rendered pages. First create architecture artifacts that inventory the current exported shell and define the reusable module/data contract. This preserves the current site while creating a safe migration target.

Recommended artifact path:

```txt
okf/architecture/astro-emdash/header-footer/
  README.md
  canonical-shell.contract.json
  current-header-footer-inventory.json
  migration-checklist.md
```

Use a `feature/` branch because this is architecture/governance/report work, not deployable content.

## Inventory expectations

Scan current static HTML and capture:

- number of HTML pages scanned;
- pages with rendered header/footer;
- structural variant counts for header/footer;
- representative variant samples;
- homepage primary header links with labels/hrefs;
- homepage footer links with labels/hrefs;
- booking links and FareHarbor config.

Session reference numbers from 2026-07-11 were: 306 HTML pages scanned, 295 with header, 295 with footer, 220 header variants, 214 footer variants. These numbers are not fixed requirements; they are a sanity-check pattern for future runs.

## Contract priorities

Lock the shell priority order explicitly:

1. users
2. search engines
3. AI assistants
4. booking conversion

The shell components established in the contract were:

```txt
SiteShell
Header
PrimaryNav
BookNowButton
LanguageSwitch
Footer
```

Expected future source files/prototypes:

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

## Non-negotiables

- No content rewrite as part of shell migration.
- Preserve current labels, hrefs, phone, logo destination, language switch, footer links, and FareHarbor booking config.
- Parent nav anchors remain real links.
- Header/footer work without JavaScript.
- H1–H6 remain Open Sans Condensed Bold.
- Each migrated page has `header`, `main`, and `footer` landmarks.
- Search/AI metadata derives from the same nav/footer source as the rendered UI.
- Booking stays easy, but does not hijack navigation.

## Verification pattern

Use focused ad-hoc artifact verification, not canonical suite claims:

- `python3 -m json.tool` for JSON artifacts.
- Assert all required artifacts exist.
- Assert priority order is exactly users → search_engines → ai_assistants → booking_conversion.
- Assert FareHarbor shortname remains `activeoahutours`.
- Assert enough pages/links were inventoried to be meaningful.
- Assert only architecture artifact paths changed; no rendered `site/` files changed in this prep slice.
- PR checks still need to pass before merge.

## Next slice after contract

Extract typed nav/footer data from the inventory, then build a non-public Astro shell prototype that renders header/footer from that data. Verify exact link-label/href parity first, then visual parity.