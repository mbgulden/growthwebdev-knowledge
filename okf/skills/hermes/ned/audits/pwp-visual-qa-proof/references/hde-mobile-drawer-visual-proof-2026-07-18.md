# HDE mobile drawer visual proof — 2026-07-18

Session lesson: a passing build/PWP suite plus computed-style assertions can still miss human-visible mobile drawer defects. For HDE, the drawer had an apparent cream background mechanically, but semantic image QA still caught white menu text on a light drawer and page bleed-through/contrast problems.

## Durable workflow

1. Reproduce the exact user screenshot state first: mobile viewport, drawer/menu open, cache-busted staging URL.
2. Add deterministic assertions for the behavior that broke, not only generic shell checks:
   - drawer/open menu `background-color` is cream/sage;
   - `background-image`/overlay is present;
   - drawer height covers most of viewport (`>700px` at 390x844);
   - menu link `color` and `-webkit-text-fill-color` are dark (`rgb(47, 54, 49)` for HDE);
   - screenshot artifact is saved after opening the drawer.
3. Run the canonical suite after the final edit: `npm run pwp:verify`.
4. Run focused live staging browser verification against cache-busted URLs after syncing/deploying the verified `dist/`.
5. Send the final screenshots through Gemini image QA, not just heuristic screenshot capture. If Gemini returns FAIL, keep fixing even when computed styles look green.

## HDE-specific fixes that proved useful

- In Astro `Nav.astro`, make the mobile drawer full-height and opaque:
  - `height/min-height: calc(100dvh - 72px) !important`
  - cream/sage `background` + `background-image`
  - forced dark mobile `.nav-links a` color and text fill
- Add `body.drawer-open::before` as a fixed cream/sage backdrop for belt-and-suspenders opacity.
- In legacy bridge CSS, mirror the same drawer-open backdrop and nav link contrast so generated/copied HTML surfaces behave the same.
- For legacy self-contained widgets, normalize high-risk text inline during postbuild if old page CSS order can override the bridge stylesheet.

## Reporting caveat

If Gemini catches a visual defect after mechanical checks pass, report the Gemini finding plainly and continue. Do not call the work visually verified until the final screenshot state has both deterministic browser proof and semantic image review, or explicitly label the remaining image-review gap.