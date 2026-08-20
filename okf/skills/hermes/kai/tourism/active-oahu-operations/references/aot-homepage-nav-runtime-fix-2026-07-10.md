# AOT homepage nav contrast + runtime repair — 2026-07-10

## Trigger
Michael asked to fix `activeoahutours.com` because the desktop hovered/active nav contrast and homepage layout were visibly broken, and specifically asked to check logs/errors rather than only attach screenshots.

## Durable workflow

1. **Start from a clean branch off `origin/main`.** Do not continue from stale worktrees when production-facing layout is broken.
2. **Measure rendered contrast, not CSS intention.** Use Playwright against desktop hover state and compute contrast from `getComputedStyle()` foreground/background. In this run, top hover was fine (`8.84:1`) but submenu links rendered cream-on-white (`1.06:1`) because a later stylesheet overrode the submenu background.
3. **Treat console/page errors as layout blockers.** Browser console plus extracted inline scripts found first-party errors that affected homepage behavior:
   - empty `<script type="speculationrules"></script>` warnings;
   - broken lazyload snippet: `$("<img loading="lazy" />")` causing `missing ) after argument list`;
   - direct `})(jQuery, window, document);` call when jQuery may not be present;
   - duplicate mobile nav toggle handlers causing hamburger double-toggle closed;
   - malformed `</script></script>` closings;
   - malformed partner/banner snippets.
4. **Use broad static scans after fixing export-wide script patterns.** If the same broken static-export snippet appears across many generated HTML files, repair all matching pages, then run a site-wide executable inline-script syntax pass with `node --check` for every non-JSON, non-src inline script.
5. **Separate first-party from third-party noise.** FareHarbor may log `getGA4ClientIds ... destination` warnings in headless runs. Do not call the page broken if first-party `pageerror` is empty and only FareHarbor external warnings remain.
6. **After merge, verify production on the clean URL, not only cache-busted URLs.** Cache-busted production showed the deploy first, but the root URL still served stale HTML. Purge exact Cloudflare URLs (`/`, `/index.html`, `www /`, `www /index.html`) and re-check markers on `https://activeoahutours.com/`.

## Verification pattern

Minimum rendered checks:

- Desktop `1440px`: hover first top-level nav item, assert dropdown visible, compute top hover and submenu link contrast.
- Mobile `390px`: click `.menu-toggle`, assert `aria-expanded="true"`, menu visible, and top-level links visible.
- Homepage layout: assert hero grid renders and card columns have nonzero rects.
- Console: assert `pageErrors` is empty; list remaining warning sources separately.
- Static markers: confirm fresh stylesheet query/version and absence of the broken snippets above.

## Known-good results from this run

- Top hover contrast: `8.84:1`.
- Submenu contrast after fix: `8.35:1`.
- Production markers after cache purge: `nav-fix.css?v=12` present; passive nav note present; broken lazyload, empty speculation rules, and duplicate mobile toggle absent.
- Site-wide inline executable script check: `3,873` scripts checked, `0` syntax errors.

## Pitfalls

- Do not rely on screenshot existence as proof the nav works; the screenshot can show a visually broken state. Compute contrast and assert visibility/click state.
- Do not stop at cache-busted production verification. If `/` is still stale, purge exact URLs and verify the clean URL.
- Do not reintroduce desktop click handlers that `preventDefault()` on parent nav links; use CSS `:hover` / `:focus-within` for desktop dropdowns so parent links still navigate.
