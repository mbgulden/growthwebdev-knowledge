# AOT cultural diacritics + search/PWP policy — 2026-07-12

## When this applies

Use this when writing, editing, auditing, or visually QA'ing Active Oahu Tours pages that include Hawaiian place names, Hawaiian-language terms, Japanese locale content, or other culture/language-specific diacritical marks.

Also use this for future tourism sites outside Hawaiʻi when the site's language/culture uses accents, macrons, ʻokina, kahakō, ñ, ç, ü, or similar marks that users may omit in search.

## Core doctrine

Use culturally correct spelling in visible, meaningful copy while preserving discoverability and operational stability.

For AOT:

- `Oʻahu`, `Hawaiʻi`, `Mokoliʻi`, and `Kāneʻohe` are appropriate in visible place-name copy.
- Plain/common forms such as `Oahu`, `Hawaii`, `Mokolii`, `Kaneohe`, and `Chinaman's Hat` remain useful as natural search/common-name bridges.
- Domain/brand strings such as `ActiveOahu.com`, `Active Oahu Tours`, and `Active Oahu` should stay plain unless an official brand source says otherwise.

## Do use diacritics in

- body copy;
- headings where natural;
- local/cultural context notes;
- guide captions;
- schema text fields that mirror visible copy;
- respectful explanations of Hawaiian place names.

## Do not force diacritics into

- domains and compact brand strings;
- URL slugs;
- filenames and asset paths;
- analytics event names;
- CSS/JS identifiers;
- API/vendor identifiers;
- exact legal/business names unless official source uses marks;
- quoted user search examples.

## SEO rule

Correct diacritics are SEO-safe when applied strategically. Google generally normalizes marked/unmarked variants, but AOT should keep natural common-name bridges on commercial pages.

Good examples:

- `Oʻahu kayak rentals in Kailua`
- `Kayak to Mokoliʻi, also known as Chinaman's Hat`
- `Kāneʻohe Bay sandbar tours`

Bad examples:

- `ActiveOʻahu.com`
- changing `/oahu-kayak-rentals/` to a marked slug;
- removing every common tourist search variant from a commercial page.

## PWP conditional trigger

During PWP or equivalent page QA, add a **Cultural Diacritics & Search Compatibility** section when any of these are true:

1. Site is in Hawaiʻi.
2. Page contains Hawaiian place names or terms.
3. Site language/culture uses marks users may omit in search.
4. Existing page copy already has diacritical marks.
5. Task changes place names, title/meta, schema, hreflang, or language switching.

The conditional should report:

```json
{
  "culturalDiacriticsConditional": {
    "triggered": true,
    "reasons": ["site_in_hawaii", "hawaiian_place_names_present"],
    "visibleCopyFindings": [],
    "operationalStringViolations": [],
    "searchBridgeFindings": [],
    "metaSchemaHreflangFindings": [],
    "status": "pass"
  }
}
```

## PWP pass/fail checks

Pass when:

- visible place-name copy uses correct marks where natural;
- plain/common variants remain where commercially useful;
- operational strings are preserved;
- no malformed glued words appear;
- URLs/schema/hreflang remain valid.

Fail when:

- operational strings mutate, e.g. `ActiveOʻahu.com`;
- URLs or identifiers are changed to marked variants without explicit approval;
- every common/tourist search bridge disappears from a commercial page;
- malformed terms appear, e.g. `Hawaiʻian`, `HawaiʻiReady`, `OʻahuReady`;
- hreflang/schema URLs become invalid.

## Repo artifacts

Mirror repo public-safe doctrine:

- `okf/governance/cultural-diacritics-search-policy.md`
- `okf/reports/golden-thread/pwp-cultural-diacritics-conditional-20260712.md`

## Verification pattern

For changes touching this doctrine, run a focused `/tmp/hermes-verify-*` ad-hoc verifier that asserts:

- OKF policy exists and includes the operational-preservation and PWP trigger rules;
- PWP conditional doc includes trigger/reason/output shape;
- skill reference exists and includes `ActiveOahu.com`, `Mokoliʻi`, and `Cultural Diacritics & Search Compatibility`;
- no private/vendor/customer-sensitive data was added;
- changed paths stay under allowed OKF public-safe or skill reference paths.
