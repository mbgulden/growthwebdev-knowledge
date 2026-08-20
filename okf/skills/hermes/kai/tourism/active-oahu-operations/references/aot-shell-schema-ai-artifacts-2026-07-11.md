# AOT shell schema + AI artifacts pattern (2026-07-11)

Use this after the Astro/emdash shell prototype has typed canonical shell data under `okf/architecture/astro-emdash/header-footer/prototype/src/content/nav/aot-shell-data.json`.

## Goal

Prove that user-facing navigation, search-engine schema, and AI-readable navigation can all derive from the same canonical shell graph before migrating rendered pages.

## Outputs to generate

Place generated artifacts under:

```txt
okf/architecture/astro-emdash/header-footer/prototype/generated/
```

Recommended outputs:

- `schema/site-navigation.jsonld` — schema.org `ItemList` with `SiteNavigationElement` rows.
- `schema/local-business.jsonld` — `LocalBusiness`/tour business contact + booking action graph.
- `schema/combined-shell-schema.jsonld` — combined `@graph` for future injection.
- `llms/navigation-section.txt` — `/llms.txt` navigation section.
- `schema-ai-manifest.json` — source/output/count manifest.
- `scripts/generate-schema-ai.py` — deterministic generator.

## Generator expectations

- Load from `src/content/nav/aot-shell-data.json`; do not duplicate nav literals in the generator.
- Convert relative site hrefs to `https://activeoahutours.com/...`.
- Keep `tel:` and `mailto:` unchanged for contact rows, but exclude them from public `SiteNavigationElement` rows if appropriate.
- Preserve priority order: `users`, `search_engines`, `ai_assistants`, `booking_conversion`.
- Preserve FareHarbor config from shell data, especially shortname `activeoahutours`, fallback `simple`, and booking href.
- Include high-risk nav proof rows in assertions: `Activities & Tours`, `Kayak Rentals`, `Mokolii Kayak Rentals`, `Kailua Kayak Rentals`, `Book Online`, `Cancellation Policy`.
- `/llms.txt` section should include booking, primary nav, footer/contact nav, and AI routing notes. Keep the note that booking is a dedicated action and must not replace crawlable navigation links.

## Verification checklist

Use focused ad-hoc verification, not canonical-suite language:

1. `python3 -m py_compile prototype/scripts/generate-schema-ai.py`.
2. Run the generator from the repo root.
3. Parse every JSON-LD and manifest file with `json.load`.
4. Assert the manifest `sourceVersion` matches shell data version.
5. Assert `site-navigation.jsonld` is `@type: ItemList` and the row count matches the manifest.
6. Assert `local-business.jsonld` contains `LocalBusiness`, `https://activeoahutours.com/#localbusiness`, and a booking action URL derived from shell data.
7. Assert `combined-shell-schema.jsonld` is exactly `[site_nav, local_business]` in `@graph`.
8. Assert `/llms.txt` output contains booking, key rental rows, and the users → search → AI → booking priority note.
9. Assert generator determinism by running it twice and comparing generated outputs.
10. Assert only architecture artifact paths changed; no rendered `site/` output should change in this slice.

## Hermes verification guard refinement

When Hermes flags changed script/report paths after this work, create a fresh literal `/tmp/hermes-verify-*` script with `tempfile.mkstemp`, run it against the exact flagged paths, remove it, and report the exact output as ad-hoc verification. If the first verifier fails because the assertion is too brittle (for example Markdown backticks around a marker), fix the verifier expectation and rerun; summarize the final passing run plus the useful first-failure lesson. Do not call this full suite green.

## PR body notes

The PR body should state:

- rendered site files changed: none,
- schema navigation count,
- `/llms.txt` line count,
- booking shortname preserved,
- generator deterministic,
- verification was focused ad-hoc, not canonical suite green.
