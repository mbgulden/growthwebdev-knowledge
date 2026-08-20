# HDE legacy static light-theme bridge — 2026-07-17

Use this reference when HDE staging/production readiness asks require applying the cream/sage theme across Astro pages plus legacy static Human Design library pages copied from `docs/`.

## Durable pattern

- Treat the Astro layout theme and legacy `docs/**/*.html` pages as two separate surfaces.
- Legacy bridge CSS must be web-readable after build/sync. If the HTML has `<link rel="stylesheet" href="/hde-light-theme.css">` but the page still shows old navy/gold/white styling, check the CSS response directly with `curl -I https://staging.humandesignengine.com/hde-light-theme.css`; a `403 Forbidden` with file mode `600` means the theme is present but unreadable. Fix the source/build path with `chmod 644` and make the build script set copied legacy assets to `0644` so rsync/Cloudflare/nginx can serve them.
- For legacy pages copied by `scripts/route-complete-build.mjs`, add a single bridge stylesheet such as `/hde-light-theme.css` during postbuild instead of hand-editing every generated/static page.
- The bridge can override old navy/gold and purple/dark tokens at runtime while leaving legacy source HTML intact.
- Include the bridge globally from `src/layouts/Layout.astro` so first-class Astro pages and embedded modules share the same palette.
- Update self-contained modules separately when they inject their own CSS; HDE `public/widget.js` / `public/widget.src.js` had their own `BRAND` object and did not inherit page CSS.

## PWP route coverage pattern

When the user asks to scan “all gates/peripheral pages,” expand `.pwp/routes.json` beyond core pages with representative examples from each static class:

- `/human-design/gates/`
- one individual gate, e.g. `/human-design/gates/gate-1.html`
- one channel page, e.g. `/human-design/channels/1-8-inspiration.html`
- one type page, e.g. `/human-design/types/generator.html`
- one authority page, e.g. `/human-design/authorities/emotional.html`
- the free-reading/free-report route and buy-report route

This catches class-level theme regressions without screenshotting all 64 gates every run.

## Verification sequence

1. `npm run build` first; fix postbuild syntax before visual work.
2. If the visual change is intentional and screenshots fail only because the theme changed, run `npm run qa:update-screenshots`, then rerun `npm run pwp:verify`.
3. Use `npm run qa:a11y` as an active contrast/debug loop. Cream/sage changes commonly surface contrast issues in:
   - footer/logo/copy links,
   - widget labels and small optional text,
   - breadcrumb and inline links,
   - legacy highlight spans,
   - legacy hero blocks,
   - inline dark table/statistical sections.
4. Fix accessibility in source/bridge CSS, not by relaxing axe thresholds.
5. Run final `npm run pwp:verify` after the last edit and report exact counts.

## Deployment caveat

If deploying with Wrangler from a non-interactive shell, ensure the Cloudflare API token is exported before invoking Wrangler. Do not claim staging was deployed from local proof alone; local PWP passing means the artifact is ready to deploy, not that Cloudflare has received it.
