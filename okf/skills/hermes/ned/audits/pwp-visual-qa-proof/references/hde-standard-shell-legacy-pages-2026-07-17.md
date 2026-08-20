# HDE legacy pages: standard header/footer shell proof — 2026-07-17

## When this applies

Use this when HDE legacy/static pages under `docs/` or copied static HTML need to match the standard Astro website shell.

Covered route families from the session:

- `/human-design/profiles/` and sub-pages
- `/human-design/types/` and sub-pages
- `/human-design/centers/` and sub-pages
- `/human-design/channels/` and sub-pages
- `/human-design/gates/` and sub-pages
- `/hd-engine/free-tools/type-quiz.html`
- `/hd-engine/free-tools/gate-lookup.html`
- `/bodygraph.html`
- `/free-human-design-reading-generator/`

## Durable pattern

1. Treat Astro pages and legacy static HTML as different surfaces.
2. For Astro pages, add the shared `Nav` and `Footer` in the common layout, not per-page.
3. For legacy static HTML, inject a standard shell during `scripts/route-complete-build.mjs` postbuild normalization.
4. Make shell injection idempotent:
   - only remove an old `<nav>` when inserting the new standard header,
   - only remove an old `<footer>` when inserting the new standard footer,
   - if a page already has the standard shell but lacks the helper script, add only the script.
5. Keep standard shell CSS in `docs/hde-light-theme.css`; legacy pages need a CSS bridge because their inline styles can fight the standard site components.
6. Include representative index and sub-page routes in `.pwp/routes.json`; update required text to match the real page heading, not the SEO title.
7. Run `npm run build` after doc/source edits and `npm run pwp:verify` after route coverage changes.
8. Deploy both surfaces when staging uses VM static dist and Cloudflare Pages:
   - `rsync -a --delete --chmod=F644,D755 dist/ /home/ubuntu/work/hd-platform-staging/dist/`
   - map `CLOUDFLARE_PAGES_API_TOKEN` into `CLOUDFLARE_API_TOKEN` for Wrangler Pages deploy.

## A11y pitfalls found

- Injecting standard shell can expose legacy form controls to axe. Add accessible names for legacy `<select>` controls with static labels or a small postbuild helper script. Do not silence axe.
- Old free-tool badges/classes may keep weak sage-on-cream contrast (`#738675` on light backgrounds). Add explicit contrast overrides for classes such as `.quiz-badge`, `.page-badge`, `.tool-badge`, `.gc-name`, `.question-text`, and related chip/card classes.
- Footer/body links on legacy tools may fail `link-in-text-block`; enforce underlines and sufficient contrast in the bridge stylesheet.

## Verification recipe

Local:

```bash
npm run build
npm run pwp:verify
```

Focused live shell proof with Playwright should assert each listed route and representative sub-page has:

- HTTP 200,
- `<header>` present,
- `<footer>` present,
- standard header selector (`.hde-standard-header` or Astro `.nav-logo-text`),
- standard footer selector (`.hde-standard-footer` or Astro `.footer-logo`),
- standard nav links: Free Reading, Reports, Sanctuary, API, Learn, Coaching,
- standard footer groups: Start, Products, Learn.

Run the live check against all relevant bases when both VM staging and Cloudflare Pages are in play:

- `https://staging.humandesignengine.com`
- `https://deploy-fresh.hd-platform.pages.dev`
- direct deployment URL from Wrangler output

## Reporting

Report both the human-facing result and the proof:

- link to a representative route Michael can open,
- list covered route families,
- give `pwp:verify` counts,
- give live shell smoke result,
- include PR/deploy URL if created.
