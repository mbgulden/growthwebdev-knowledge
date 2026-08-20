# Sentinel ITAD Astro Theme + EmDash Integration — 2026-07-09

## Context

Michael asked for the `sentinelitad.com` website styles to be codified so future agents know exactly how to build new pages, and so redesigns update the whole site instead of leaving old styles behind. He also explicitly corrected the visual direction: the public website must be a **light** theme overall. Dark backgrounds with white text are allowed only for modules, buttons, banners, and scoped sections — not the entire website.

## Durable workflow pattern

1. **Treat style corrections as theme rules, not one-off CSS edits**
   - When Michael says a website should be light/dark/cleaner/etc., encode that in the theme documentation and verifier.
   - For Sentinel: global body/header/cards/forms remain light; dark is scoped to `.dark`, primary CTAs, banners, and selected modules.

2. **Codify the theme in several synchronized places**
   - Current deployed CSS: `public/style.css`.
   - Astro CSS mirror: `src/styles/theme.css`.
   - Typed tokens: `src/theme/tokens.ts`.
   - Theme docs: `docs/theme/sentinel-theme.md`.
   - Redesign rules: `docs/theme/redesign-playbook.md`.
   - Verification helper: `scripts/verify-theme.py`.

3. **Create Astro-ready modules even before migration is complete**
   - Keep current static `public/` pages working.
   - Add `src/` as the future Astro/EmDash source of truth:
     - `src/layouts/BaseLayout.astro`
     - `src/components/SiteHeader.astro`
     - `Hero`, `WarningStrip`, `CardGrid`, `TrustPanel`, `ProcessTimeline`, `SplitSection`, `LeadCapture`
     - `src/content.config.ts`
     - `src/content/pages/*.json`
   - Expect Astro build to warn that `src/pages/index.astro` is skipped while `public/index.html` exists; during static-to-Astro transition this is acceptable if build exits 0 and static deploy still serves `public/`.

4. **Gate EmDash so static builds do not require CMS infrastructure**
   - Add `emdash` and `astro` dependencies.
   - Gate integration behind `ENABLE_EMDASH=true` in `astro.config.mjs`.
   - Default `npm run build` should work without D1/R2/Dynamic Workers configured.
   - Document local command:
     - `ENABLE_EMDASH=true EMDASH_SQLITE_URL=file:./.emdash/sentinelitad.db npm run dev`
   - Add `data-emdash-block` / `data-emdash-field` markers to standard modules to make edit boundaries explicit.

5. **Use canonical plus ad-hoc verification**
   - Once `package.json` exists, canonical verification is `npm run build`.
   - Add `npm run check:theme` for deterministic theme/module invariants.
   - Still run `/tmp/hermes-verify-*` ad-hoc verification when the system requests fresh changed-behavior evidence.
   - Good verifier coverage: theme docs present, light theme invariant, scoped dark modules, Astro routes/components/content schema, EmDash gating, JSON/HTML/XML parsing, `npm run check:theme`, `npm run build`, `git diff --check`, clean tree.

## Pitfalls observed

- Do not only edit `public/style.css` after a style correction; future agents need the rule in docs and verification.
- Do not turn EmDash on unconditionally before Cloudflare/D1/R2/auth are configured; it breaks ordinary static builds.
- Do not deploy `dist/` accidentally while current Cloudflare Pages deploy is still pointed at `public/`.
- Do not treat Astro’s `public/index.html` conflict warning as a failure during transition, but document it clearly.
- Do not create a narrow one-session website style note without linking it from the umbrella skill; future site work needs the reference.
