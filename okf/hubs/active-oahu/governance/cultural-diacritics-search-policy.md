---
type: Standard
title: Cultural diacritics + search policy
description: Updated: 2026-07-12 Owner: Kai / Active Oahu Tours Applies to: Active Oahu Tours and future tourism sites in Hawaiʻi or any culture/language that uses diacritical marks.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/governance/cultural-diacritics-search-policy.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Cultural diacritics + search policy

Updated: 2026-07-12
Owner: Kai / Active Oahu Tours
Applies to: Active Oahu Tours and future tourism sites in Hawaiʻi or any culture/language that uses diacritical marks.

## Purpose

Use culturally correct place names without making the site harder to find, book, or operate.

For Hawaiʻi tourism pages, diacritics are a trust signal when used in visible, culturally meaningful copy. They should not be sprayed into operational strings where users, systems, domains, or URLs expect plain ASCII.

## Policy

### Use diacritics in visible cultural/place-name copy

Use correct forms when writing human-facing place names or culturally meaningful terms:

| Preferred visible form | Common search/plain form to also understand |
|---|---|
| `Oʻahu` | `Oahu` |
| `Hawaiʻi` | `Hawaii` |
| `Mokoliʻi` | `Mokolii`, `Chinaman's Hat` |
| `Kāneʻohe` | `Kaneohe` |

This applies especially to:

- body copy,
- headings where natural,
- guide content,
- captions,
- local/cultural context notes,
- schema text fields that mirror visible content.

### Preserve plain ASCII for operational and exact-match strings

Do **not** force diacritics into:

- domains and compact brand strings, e.g. `ActiveOahu.com`, `Active Oahu Tours`, `Active Oahu`,
- URL slugs,
- filenames and asset paths,
- analytics event names,
- CSS/JS identifiers,
- API/vendor identifiers,
- exact legal/business/entity names unless the official source uses marks,
- user-entered search phrases quoted as examples.

### Pair respectful spelling with tourist search behavior

For high-intent SEO pages, use both culturally correct and plain/search variants naturally:

- `Oʻahu kayak rentals in Kailua`
- `Kayak to Mokoliʻi, also known as Chinaman's Hat`
- `Kāneʻohe Bay sandbar tours`

Do not stuff variants. One clear common-name bridge is enough when the common tourist query differs from the correct place name.

## SEO guidance

Google generally normalizes accent/diacritic variants well, similar to `cafe`/`café`. Correct visible spelling does not make AOT invisible to unmarked searches such as `Oahu kayak rentals`.

Risk comes from applying diacritics to the wrong layer:

- bad: `ActiveOʻahu.com`,
- bad: changing `/oahu-kayak-rentals/` to a diacritic slug,
- bad: replacing every plain tourist search variant so common names disappear,
- good: `Oʻahu kayak rentals`, with common/plain variants still present naturally elsewhere.

## Review checklist

Before merging Hawaiian/cultural diacritic edits:

- [ ] Visible place-name copy uses correct marks where natural.
- [ ] Domain/brand strings like `ActiveOahu.com` remain unchanged.
- [ ] URL slugs, filenames, CSS/JS identifiers, analytics labels, and vendor IDs remain ASCII/stable.
- [ ] English adjective `Hawaiian` remains unmarked unless quoting a Hawaiian-language word.
- [ ] Common tourist names/search forms remain present where commercially useful.
- [ ] No malformed glued text appears, e.g. `Hawaiʻi[a-zA-Z]` or `OʻahuReady`.
- [ ] Hreflang/schema/meta still point to valid route pairs and visible content.
- [ ] PWP visual/audit flow triggers the cultural-diacritics conditional for Hawaiʻi or other diacritic-bearing cultures/languages.

## Conditional trigger rule

When a site is located in Hawaiʻi, serves Hawaiian place names, or already contains cultural/language diacritics, every PWP or similar visual/content QA pass must include a **Cultural Diacritics & Search Compatibility** section.

For non-Hawaiʻi sites, the same conditional applies if the site/culture/language uses marks such as accents, macrons, ʻokina, kahakō, ñ, ç, ü, or other orthographic marks that may differ from tourist/user search input.
