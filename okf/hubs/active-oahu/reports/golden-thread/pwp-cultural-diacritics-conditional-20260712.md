---
type: Report
title: PWP conditional: Cultural diacritics & search compatibility
description: Updated: 2026-07-12 Owner: Kai / PWP visual-content QA
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/golden-thread/pwp-cultural-diacritics-conditional-20260712.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# PWP conditional: Cultural diacritics & search compatibility

Updated: 2026-07-12
Owner: Kai / PWP visual-content QA

## Trigger

Run this conditional module during PWP or equivalent page QA when **any** of the following are true:

1. The business/site is in Hawaiʻi.
2. The page contains Hawaiian place names or terms that may use ʻokina/kahakō.
3. The site language/culture uses diacritics or orthographic marks that users may omit in search.
4. Existing page copy already contains diacritical marks.
5. A content task changes place names, title/meta, schema, hreflang, or language-switching.

## Goal

Protect three things at the same time:

1. **Cultural respect** — spell place names correctly where it matters.
2. **Search discoverability** — keep plain/common tourist query forms present naturally.
3. **Operational stability** — do not mutate domains, URLs, IDs, vendor strings, analytics names, or brand strings.

## PWP checks to add

### 1. Site/culture detection

Record whether the conditional was triggered and why:

```json
{
  "culturalDiacriticsConditional": {
    "triggered": true,
    "reasons": ["site_in_hawaii", "hawaiian_place_names_present"]
  }
}
```

Recommended trigger terms for Hawaiʻi/AOT:

- `Oahu`, `Oʻahu`
- `Hawaii`, `Hawaiʻi`
- `Mokolii`, `Mokoliʻi`, `Chinaman's Hat`
- `Kaneohe`, `Kāneʻohe`
- `Kailua`, `Lanikai`, `Mokulua`

### 2. Respectful visible-copy check

For visible text only, flag likely missing preferred forms on pages that discuss the relevant place:

| Plain term | Preferred visible form |
|---|---|
| `Oahu` | `Oʻahu` |
| `Hawaii` as place name | `Hawaiʻi` |
| `Mokolii` | `Mokoliʻi` |
| `Kaneohe` | `Kāneʻohe` |

Do not auto-fail every plain occurrence. Some plain forms are useful as search/common-name bridges. Classify findings:

- `preferred_form_missing` — likely should use the marked form.
- `plain_search_bridge_present` — acceptable common/tourist variant.
- `operational_string_preserved` — should remain plain.

### 3. Operational preservation check

Fail the audit if cultural marks appear in operational strings where they do not belong:

- `ActiveOʻahu.com`
- URL slugs containing marked characters unless explicitly approved,
- image filenames with new marked characters,
- CSS/JS identifiers,
- analytics event names,
- FareHarbor/vendor IDs,
- schema URLs and route references.

### 4. Search compatibility check

For commercial pages, confirm at least one natural plain/common search bridge remains when marked forms dominate:

Examples:

- `Mokoliʻi, also known as Chinaman's Hat`
- `Oʻahu kayak rentals` plus natural page context or metadata still recognizable for `Oahu kayak rentals`
- `Kāneʻohe Bay` plus a natural page topic that still matches `Kaneohe Bay`

Do not require keyword stuffing. The check should protect against accidentally removing every common-name/search variant.

### 5. Meta/schema/hreflang sanity

When the page has title/meta/schema/hreflang:

- title/meta can use correct marks but should not remove important common-name bridges;
- JSON-LD text should mirror visible content;
- URLs in schema/hreflang remain ASCII/current and valid;
- language alternates must point to actual equivalent pages, not fake `/ja/` fallbacks.

### 6. Visual/screenshot note

If PWP produces screenshots, note any culturally sensitive place-name spelling visible in hero/H1/CTA areas. A visible screenshot can override pure text assumptions when the user says something reads wrong or looks weird.

## Suggested output shape

```json
{
  "culturalDiacriticsConditional": {
    "triggered": true,
    "reasons": ["site_in_hawaii"],
    "visibleCopyFindings": [],
    "operationalStringViolations": [],
    "searchBridgeFindings": [],
    "metaSchemaHreflangFindings": [],
    "status": "pass"
  }
}
```

## Pass/fail guidance

Pass when:

- correct forms are used in meaningful visible copy;
- plain/common variants remain where commercially useful;
- operational strings are preserved;
- no malformed glued words appear;
- URLs/schema/hreflang remain valid.

Fail when:

- operational strings are mutated, e.g. `ActiveOʻahu.com`;
- URLs or identifiers are changed to marked variants without explicit approval;
- all common tourist/search bridges are removed from a commercial page;
- malformed forms appear, e.g. `Hawaiʻian`, `HawaiʻiReady`, `OʻahuReady`;
- hreflang/schema URLs become invalid.

## AOT-specific notes

AOT should keep the diacritical pass. It is brand-positive and SEO-safe when applied strategically. The standing policy is:

> Spell Hawaiian place names correctly in visible content, preserve plain operational strings, and keep common tourist search bridges where they help booking intent.
