# AOT Astro/emdash shell typed-data prototype — 2026-07-11

## Context

After creating the initial Astro/emdash header/footer inventory and shell contract, the next safe migration slice was **typed nav/footer/booking data plus a non-public prototype**. The goal was to prove the current AOT shell can be represented as canonical data before swapping any real rendered pages into Astro.

## Artifact location

Use this directory in the mirror repo:

```txt
okf/architecture/astro-emdash/header-footer/prototype/
```

Recommended files:

```txt
README.md
rendered/aot-shell-prototype.html
src/content/nav/aot-shell-data.json
src/content/nav/aot-nav.json
src/content/nav/aot-footer.json
src/content/nav/aot-booking.json
src/content/nav/aot-shell-data.ts
src/types/shell.ts
src/components/shell/SiteShell.astro
src/components/shell/Header.astro
src/components/shell/PrimaryNav.astro
src/components/shell/BookNowButton.astro
src/components/shell/Footer.astro
```

## Implementation pattern

1. Start from the already-merged inventory/contract under `okf/architecture/astro-emdash/header-footer/`.
2. Extract the homepage `#primary-menu` as the first canonical nav source.
3. Preserve current labels and hrefs exactly; put `English` language-switch utility outside `primaryNav`.
4. Extract footer hrefs and preserve the href multiset exactly. Empty image links may receive accessible labels in typed data, but keep `sourceText` so parity can still be checked against the inventory.
5. Preserve booking config:
   - FareHarbor shortname: `activeoahutours`
   - current header booking href
   - `fallback: simple`
   - analytics/event marker: `booking_click`
6. Add intent tags for future user/search/AI/booking outputs: `tour`, `rental`, `guide`, `support`, `booking`, `language`, `legal`, `contact`, `social`, `trust`.
7. Add `aiSummary` on nav/footer items so future `/llms.txt` and schema work can derive from the same graph.
8. Build Astro component stubs and a static `rendered/aot-shell-prototype.html`, but keep it non-public/noindex and do not change any `site/` rendered output.

## Verification pattern

Label this as **focused ad-hoc parity/artifact verification, not canonical suite green**.

Checks that should pass before PR:

- Required prototype files exist.
- All prototype JSON parses.
- `priorityOrder` is exactly `users → search_engines → ai_assistants → booking_conversion`.
- `primaryNav` + language utility has exact label/href parity with `current-header-footer-inventory.json`.
- Footer typed data has exact href multiset parity with the inventory; all non-empty source labels are preserved.
- `aot-nav.json`, `aot-footer.json`, and `aot-booking.json` match the canonical `aot-shell-data.json` splits.
- `bookingConfig.shortname === "activeoahutours"` and `analyticsEvent === "booking_click"`.
- Static proof render contains `header`, `main`, `footer`, `meta robots noindex`, and `data-booking-shortname="activeoahutours"`.
- `git diff --check` passes.
- Only `okf/architecture/astro-emdash/header-footer/` artifact paths changed; no rendered `site/` files changed.

## Pitfalls

- Intent inference order matters. Check social/contact/legal/support before broad text matching like `tour`, otherwise `facebook.com/activeoahutours` can be mislabeled as booking/tour because of the brand name.
- Do not collapse footer image links if the inventory has repeated gallery hrefs; preserve the href multiset first, then add better labels in typed data.
- Do not let the prototype become a production route. Keep it in `okf/architecture/.../prototype/` and noindex in the rendered proof.
- Do not begin visual polish before label/href parity passes.

## Next slice

Generate search/AI outputs from the same canonical data before UI adoption:

- `SiteNavigationElement` JSON-LD from `aot-shell-data.json`
- LocalBusiness/contact schema from business/footer data
- `/llms.txt` navigation section from `aiSummary` fields

The acceptance test is that rendered UI, schema, and AI-readable nav all derive from one canonical graph.
