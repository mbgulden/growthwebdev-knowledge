# HDE Astro/emdash standard-module migration proof — 2026-07-18

## Context

Michael asked to move HDE staging/dev onto one Astro/PWP emdash shell so header/footer changes are centralized instead of copied into each custom page. Production was explicitly out of scope until approval.

## Durable workflow lessons

1. **Treat shell ownership as a contract, not a visual preference.**
   - Astro pages should not each import/render `Nav` and `Footer` if `Layout.astro` owns the shell.
   - The regression test should assert exactly one direct `body > header.emdash-site-header` and one direct `body > footer.emdash-site-footer`.
   - Include homepage in the shell test; duplicate layout/page chrome appears there first.

2. **Legacy copied HTML needs build-time normalization.**
   - HDE still ships many copied `docs/**/*.html` pages via `route-complete-build.mjs`.
   - These are not Astro modules, so standardization has to happen in the postbuild copy/normalize stage.
   - Remove legacy `<nav>` and final `<footer>` blocks before injecting the canonical emdash shell.
   - Preserve page body content and route aliases; do not manually edit each copied output page.

3. **PWP route coverage must include representative generated/static families.**
   - Core Astro pages alone are not enough.
   - Include legal pages, checkout/success, homepage, docs, and representative legacy families such as gates, channels, types, authorities, profiles, and affiliate/report pages.

4. **A11y failures after theme normalization are useful fix lists.**
   - Do not lower axe thresholds.
   - Typical fixes: raise contrast on badges/tags, add focus semantics to scrollable code blocks, add labels/ARIA labels to legacy form controls during normalization.

5. **Fresh verification means after the last repo edit.**
   - If a report file or code path changes after `pwp:verify`, rerun at least `npm run build`; for shell/theme changes rerun full `npm run pwp:verify` when feasible.
   - Report the last command that actually ran after the final edit.

6. **AGY/Gemini image QA has two layers.**
   - `prismatic-engine visual-verify --grade --model gemini-3.1-flash-image-preview` may fall back to heuristic PASS if no visual grader endpoint is configured; label that as fallback, not true model judgment.
   - For true Gemini image judgment, send the captured screenshots to Gemini directly or through a configured grader and save the PASS/FAIL text as an artifact.
   - The AGY CLI model list may not expose `gemini-3.1-flash-image-preview` even when Gemini API does; do not pretend AGY used it if the CLI reports a different active model.

7. **Staging deployment proof has two surfaces.**
   - Cloudflare deploy preview proves the branch artifact.
   - `staging.humandesignengine.com` may be served from the VM runtime; if so, copy/sync the verified `dist/` into the staging runtime with a timestamped backup, then verify the live staging URL with cache-busting markers.

## Good final evidence shape

- PR/branch and staging preview URL.
- Live staging URL proof with cache-busting query.
- `npm run pwp:verify` counts: build, visual, a11y, flows, Lighthouse, links.
- Gemini image QA PASS/FAIL and whether it was true model grading or fallback.
- Production unchanged proof when work is staging-only.
- Runtime backup path if staging VM `dist/` was replaced.
