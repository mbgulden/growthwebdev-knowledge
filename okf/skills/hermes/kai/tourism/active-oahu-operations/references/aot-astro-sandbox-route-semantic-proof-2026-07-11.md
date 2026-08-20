# AOT Astro sandbox route semantic proof — 2026-07-11

## Context

After the AOT Astro/emdash shell inventory, typed data prototype, and schema/AI generation slices, the next safe step is a **non-public sandbox route proof**. This proves the canonical shell data, generated JSON-LD, and `/llms.txt` navigation output can be consumed together before migrating any live route.

## Artifact location

Use:

```txt
okf/architecture/astro-emdash/header-footer/
```

Recommended files for this slice:

```txt
next-steps-execution-plan.md
prototype/src/pages/_sandbox/aot-shell.astro
prototype/rendered/sandbox-shell-route.html
prototype/scripts/render-sandbox-route.py
```

## Implementation pattern

1. Start from current `origin/main` in a clean `feature/` worktree.
2. Write a next-steps execution plan that covers:
   - sandbox semantic proof,
   - sandbox rendered QA,
   - first real Astro page cohort plan,
   - private cohort implementation,
   - production adoption gate.
3. Add a sandbox Astro route stub under `prototype/src/pages/_sandbox/` that imports:
   - `aot-shell-data.json`,
   - generated `site-navigation.jsonld`,
   - generated `local-business.jsonld`,
   - `navigation-section.txt?raw`.
4. Add a deterministic renderer script that writes `prototype/rendered/sandbox-shell-route.html` from the same artifacts. Use this until a real Astro build harness exists.
5. The rendered proof should be `noindex,nofollow`, include one `header`, one `main`, one `footer`, a skip link, Primary/Footer nav labels, `activeoahutours` booking marker, generated JSON-LD scripts, `/llms.txt` excerpt/digest, and H1-H6 Open Sans Condensed Bold CSS.
6. Do not touch rendered production `site/` output.

## Verification pattern

Run a fresh `/tmp/hermes-verify-*` ad-hoc verifier. Label it **focused ad-hoc sandbox-route verification, not canonical suite green**.

Checks:

- Renderer `py_compile` passes.
- Renderer executes successfully and is deterministic against current artifacts.
- Rendered HTML has exactly one `header`, one `main`, and one `footer`.
- Rendered HTML has `noindex,nofollow`, skip link, Primary/Footer nav labels, no duplicate IDs, no empty anchors, and no missing `href`s.
- JSON-LD script bodies parse and exactly match generated source artifacts.
- Schema navigation element count remains 46 unless the canonical shell data changes.
- LocalBusiness booking URL still derives from `aot-shell-data.json` and includes `activeoahutours`.
- `/llms.txt` digest in the route matches the actual generated file.
- Astro stub imports the intended shell data/schema/AI artifacts.
- Plan contains the first cohort routes: homepage, one activity, one rental, one guide, one Japanese page.
- `git diff --check` passes.
- Changed paths stay under `okf/architecture/astro-emdash/header-footer/`; fail if any `site/` path changes.

## Pitfalls

- Do **not** HTML-escape JSON-LD bodies inside `<script type="application/ld+json">`; script content must remain raw JSON, with only `</` escaped as `<\/` to avoid closing the script tag.
- Do not publish the sandbox route as a live route. Keep it in `okf/architecture/.../prototype/` until an Astro build harness and route gating exist.
- Do not confuse the static proof render with a full Astro build. It is a semantic artifact/verifier target, not canonical suite green.
- Keep H1-H6 font guard present in sandbox proof; Michael explicitly wants Open Sans Condensed Bold preserved.
