---
name: active-oahu-operations
description: Operate Active Oahu Tours work queues, deployment/governance checks, PR reconciliation, and verified status reporting across Linear, GitHub, Cloudflare Pages, and the static mirror repo. Use when Michael asks what needs work on activeoahutours.com, asks for AOT prioritization, or when triaging AOT Linear/GitHub/deployment state.
tags:
  - active-oahu
  - tourism
  - linear
  - github
  - cloudflare-pages
  - triage
  - operations
---

# Active Oahu Operations

## When to use

Use this skill for **class-level Active Oahu Tours operations**, including:

- "What needs to be worked on for activeoahutours.com?"
- AOT Linear queue triage and prioritization.
- Reconciling stale Linear PR-review issues against live GitHub PR state.
- Checking whether production/mirror are responding from Cloudflare.
- Separating site stability/governance work from SEO/content/growth backlog.
- Reporting verified status across the AOT toolchain (Linear, GitHub, CF Pages, Ubersuggest, GA4).

## Communication contract (user preference, captured 2026-07-30)

For every AOT homepage / preview-URL task-completion message:

1. **Include the staging preview URL prominently** — currently `https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/`.
2. **Add a `Mirrored to latest commit: yes/no` note** so the user can tell at a glance whether the URL reflects the most recent push.
3. **If "no"**, flag the deploy-pipeline blocker (e.g., GH Actions billing error, CF build stuck, deploy hook misconfigured).

This is a hard rule, not a suggestion — Michael asked for it explicitly and asked it be carried forward to every future session.
- **Astro homepage development and CSS auditing.** See `references/astro-css-architecture.md` for the full Kadence CSS replacement pattern, glyphicon gotchas, and WCAG contrast safe-harbors for orange buttons.
- **Homepage content audit method:** See `references/aot-staging-content-audit-2026-07-29.md` for the content comparison technique against the live WordPress production site (character count, section order, pixel color comparison, browser accessibility tree audit).
- **PrimaryNav keyboard/a11y pattern:** See `references/aot-primary-nav-a11y-pattern-2026-07-28.md`.
- **Screenshot capture (wkhtmltoimage):** See `references/aot-screenshot-capture-wkhtmltoimage-2026-07-28.md`.
- **Button contrast safe harbor:** See `references/aot-button-contrast-safe-harbor-2026-07-28.md`.
- **Astro template/JSX parsing pitfalls:** See `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` — when `npm run build` fails with `Expected ">" but found "class"` inside a `.map()` callback, the fix is multiline + parens around the conditional JSX. Also covers the sneakier `class="...{feature.id}..."` template-literal interpolation bug (Pitfall #4) — silently broken HTML, no build error. Pitfall #5 (2026-07-30): the `patch` tool's `mode='replace'` and `mode='patch'` are different invocations; passing `old_string`/`new_string` while `mode='patch'` silently no-ops. Switch to `mode='replace'` (default) for single-file find-and-replace, or `write_file` for full rewrites.
- **Lighthouse audit fix recipes:** See `references/aot-lighthouse-audit-recipe-2026-07-29.md` — concrete recipes for the 7 audits that fire on AOT homepage PRs (`image-redundant-alt`, `target-size`, `lcp-lazy-loaded`, `errors-in-console` glyphicon 404s, `heading-order` regression guard, `render-blocking-resources` Google Fonts + FH SDK defer, and the duplicate-`<head>` bug from nested BaseLayout), plus the `/tmp/hermes-verify-*.py` script shape that catches the bugs Lighthouse doesn't see.
- **Nav CTA cluster + JSON patch pitfall:** See `references/aot-nav-cta-cluster-and-json-patch-pitfall-2026-07-29.md` — adding the Call + Book Now CTA cluster to `PrimaryNav.astro` (markup, CSS, data wiring, regression verification recipe), and the `patch --replace_all=true` pitfall that clobbered an unrelated JSON entry when a field name happened to repeat. Includes the regex verification false-positive / false-negative lessons.
- **Staging-vs-production structural diff recipe (2026-07-30):** See `references/aot-staging-vs-prod-structural-diff-2026-07-30.md` — the 5 structural signals (byte size, img dedup, bg-image count, heading diff, section ordering) that found all of Michael's reported issues in one pass, plus the production 75/25 "front-page-with-bg" + "front-page-packages" layout pattern and how to dedupe images by replacing with production's actual image choice rather than removing one. Companion script: `scripts/aot-staging-vs-prod-diff.py` (runs all 5 signals, prints a report ready to paste into the user-facing audit message).
- **Production-parity implementation playbook (2026-07-30):** See `references/aot-production-parity-implementation-playbook-2026-07-30.md` — companion to the audit recipe above; the 4-stage end-to-end workflow (audit → implement 2-col components → commit+push → byte-match live). Includes the Pattern A (75/25 bg-left + cards-right) and Pattern B (25/75 cards-left + bg-right) Astro component shapes, the `renderTextWithLinks` helper, the SHA-256 byte-match verification recipe, and the `patch` tool mode-confusion pitfall. Use when the audit returned non-zero signals and you actually need to fix the staging site end-to-end.
- **CF Pages build_config mismatch & direct-API deploy:** See `references/aot-cloudflare-pages-build-config-mismatch-direct-api-deploy-2026-07-30.md` — when a "succeeded" Cloudflare Pages deploy publishes the wrong file (e.g., `site/index.html` WP export instead of the Astro `dist/`), the fix is `PATCH /accounts/{id}/pages/projects/{name}` to update `build_config.build_command` + `destination_dir`, then `POST /deployments/{id}/retry` to trigger a fresh build. Includes project-name-vs-branch-alias-URL naming, multi-account token scoping (token vs. email+key sees different accounts), Wrangler 4.x's `CLOUDFLARE_API_TOKEN` requirement, `sha256sum` byte-for-byte verification (local `dist/index.html` vs. deployed URL), and the **retry rebuilds from GitHub HEAD, not your local dist** pitfall (must commit+push before retry, otherwise the retry builds the wrong commit).
- **CF Pages SPA fallback returns HTML for missing assets:** See `references/aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` — when `/wp-content/uploads/...` paths return HTTP 200 but `file downloaded.jpg` shows `HTML document`, CF Pages is serving `index.html` as the SPA fallback. Includes the file-type verification recipe (`aot-check-images.py`), the Astro `public/` bundling pattern that fixes the root cause, the CDN-cache-survivor pitfall (some images work until cache TTL expires), and the diagnostic ladder for "missing images" reports.
- **Hallucinated-commit failure mode (2026-07-31):** See `references/aot-hallucinated-commit-verification-2026-07-31.md` — never report a commit as pushed + deployed + verified when the source files were never modified. The build succeeds only because the old state is still being deployed. Detection recipe: `grep` the source file (not `dist/`) for the new symbols before claiming "done". Same class as `prismatic-evidence-handling` and `corrections-lead-with-recipe`: prove a change with a tool output, don't rely on memory of what was typed.
- **Gallery lightbox modal + full-size image derivation:** See `references/aot-gallery-lightbox-fullsize-derivation-2026-07-31.md` — the data-lightbox pattern, the URL derivation logic (`-115x115` thumbnail → `_lightbox/` full-size), the fallback chain when full-size 404s, and the focus-trap/ARIA dialog template.
- **CDN-served stale JS during/after deploy:** See `references/aot-cdn-stale-js-after-deploy-2026-07-31.md` — CF Pages may serve the prior version of bundled JS assets even after a fresh `git push` and `sha256sum` of `index.html` matches. Includes the cache-bust verification recipe (timestamped URL probes) and a stop-the-presses moment: when a user reports a feature still broken after deployment, the FIRST question is "is the deployed asset actually the new one?" not "did I miss a CSS rule?".
- **Browser-tool cache vs. CDN cache (2026-07-31):** See `references/aot-browser-tool-cache-vs-cdn-cache-2026-07-31.md` — companion to the CDN reference. Even after `curl` confirms fresh deploy, the `browser_navigate` tool may keep rendering the old DOM from its own disk cache (a different cache layer from the CDN). 6-layer diagnostic ladder (source → dist → CDN HTML → CDN JS → browser cache → DOM render) catches which layer is stale. Browser-tool cache-buster pattern: `await fetch(url, {cache: "no-store"})` from `browser_console`, or `browser_navigate` to a different URL first then back. Occurred twice in the same session (Round 7 lightbox + Round 9 header refinement) before it was tracked separately.
- **Header refinement: single-banner + nav flex + branding layout (2026-07-31):** See `references/aot-header-refinement-round-9-2026-07-31.md` — 4 pitfalls specific to header/nav production-parity: (1) duplicated semantic-role elements from prior rounds (two stacked banners), (2) `display: block` on a nav parent causes flex children to stack vertically even though each child is internally flex (138px nav when it should be 70px), (3) nav-link padding inflates nav height past production spec, (4) word-wrap defaults after CSS resets. Includes the per-element `getBoundingClientRect().height` measurement diagnostic that catches flex-vs-block bugs invisible to HTML/CSS/Lighthouse audits.
- **Header production-CSS extraction (Round 9b — 2026-07-31):** See `references/aot-production-header-css-extraction-round-9b-2026-07-31.md` — bypass the audit subagent and read production's actual `nav-fix.css` (`https://activeoahutours.com/wp-content/themes/activeoahu/css/nav-fix.css?v=16`, 18KB). Audit subagent reported wrong values (claimed phone was `#006699` blue, "Call or Text" missing); nav-fix.css has ground-truth: phone `#ff7f00`, `::before { content: "Call or Text" }`, lang switcher present, breadcrumb visible. Also covers minified-CSS escaping (`::before` → `:before`, `rgba()` → 8-digit hex), the `execute_code` Python fallback for `patch` `path required` failures, and the round's full production-spec CSS reference.
- **Hero image local bundling + minified-CSS verifier pattern (Round 10 — 2026-07-31):** See `references/aot-astro-css-minification-verifier-2026-07-31.md` — Astro's CSS minifier shortens `rgba(0,0,0,0.3)` → `#0000004d`, `#003366` → `#036`, `::before` → `:before`. Naive verification scripts that grep for the source-written form fail even when the rule is present. The minified-form allow-list pattern (ALLOWED dict with both source and minified forms) prevents false-fail verification. Companion script: `scripts/verify-hero.py` (re-runnable, 30-check Round 10 verifier with minified-form handling). The Round 10 hero itself: downloaded `Active-Oahu-Lifestyle-225-2X1-1000.jpg` (98KB JPEG) to `public/wp-content/uploads/2024/01/` so the image is bundled by Astro (Astro does not bundle absolute `/wp-content/...` URLs from external sources — see `references/aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` for the upstream bug). Also covered: the production hero uses inline `background-image` on the inner column (not a separate `.hero-bg` div) with a `::before` overlay (`opacity: 0.3; color: #000`) for text readability.
- **Modular primitives + design system for the Astro homepage (Round 12/13 — 2026-07-31):** See `references/aot-modular-primitives-design-system-2026-07-31.md` — the 3-layer pattern (design tokens → reusable primitives → adopt in components), the 5 primitives shipped (`Heading`, `BookingButton`, `Card`, `Section`, `PriceTag`), the BEM `aot-` prefix convention, and 5 pitfalls that bit during the same session: Astro doesn't support dynamic tag names (`<Tag>` syntax), CSS for unused primitives is tree-shaken from the bundle, `patch` regex collision can silently keep both old AND new CSS in the file, `BookingButton.useShortname` defaults matter for FH integration, and `patch` warns on stale-read can corrupt subsequent patches. Also captures the **hero text-shadow technique** (production uses `text-shadow: 1px 1px 21px #000` on H2 + transparent `::before` overlay — NOT a dark overlay — for white text on lifestyle photo contrast).
- **Hero font-size: production's `html { font-size: 62.5% }` + `clamp()` pattern (Round 14 — 2026-07-31):** See `references/aot-hero-font-size-root-clamp-pattern-2026-07-31.md` — when "hero text is way too big" is reported and your CSS matches production's source values, the missing piece is usually `<html> { font-size: 62.5% }` (production's classic "1rem = 10px" trick). With the root set, Kadence's `--global-kb-font-size-xxxl: clamp(2.75rem, 0.489rem + 7.065vw, 6rem)` resolves to 60px on desktop; without it, the same clamp resolves to 96px. Covers the 3-file coordinated change (tokens.css root + hero component clamp() + primitive `xxxl` size 5rem → 6rem), the diagnostic ladder (`getComputedStyle(document.documentElement).fontSize` first, then the h2's computed style), and the silent-regression pitfall: every other `rem` value on the site halves when the root changes.
- **Modular adoption recipes (Rounds 16-18 — 2026-07-31):** See `references/aot-modular-adoption-rounds-16-18-2026-07-31.md` — follow-on to R12/13. 6 new pitfalls: (A) **NEVER set `html { font-size: 62.5% }` globally to fix one hero** — Michael rejected this verbatim ("you made ALL the site text smaller in order to make the header text slightly smaller"). Use `[style*="font-size"]` attribute selector scoped to `.hero-banner` instead. (B) Vite barrel-import failure — `import { X } from "../primitives"` won't resolve `index.astro`; use direct file imports. (C) Card primitive hardcodes `<Heading size="lg">` (32px) for the title — for consumers needing smaller titles (e.g. FeaturedTours 1.1rem), add a `titleSize` prop. (D) Orphan global CSS with `!important` keeps bleeding into the new component — delete the orphan block from the global stylesheet, not just the new component. (E) `<Section>` defaults to `container={true}` (max-width 1100px); use `container={false}` for full-width sections (FeatureBlock, FeaturedTours). (F) BEM `__modifier` selectors in scoped CSS need `[data-astro-cid-*]` for them to match. Plus 5 worked recipes (Testimonial, FeatureBlock, FeaturedTourHero, FeaturedTours, verification script shape) and the file-impact summary showing -3 net lines but proper modular structure.
- **Modular adoption recipes (Rounds 19-20 — 2026-07-31):** See `references/aot-modular-adoption-rounds-19-20-2026-07-31.md` — BeachEquipment + MokuluaFeatureBlock + ClosingCTA + Awards + FooterExtras + DealBanner. 4 new pitfalls: (A) **Duplicate `:root` blocks silently override tokens** — when two CSS files declare `--aot-gray-600` with different values, the LATER one wins the cascade. Removed duplicate `:root` from `active-oahu-tours-minimal.css`; added legacy gray-100/400/600/900 values to `tokens.css`. (B) **Scoped CSS doesn't reach `<Section>`'s rendered DOM** — Astro scoping uses the Section's own `data-astro-cid-*`, not the parent's. When wrapping `<Section class="my-thing">`, use `<style is:global>` for the parent component's styles. (C) Card primitive `titleSize` prop + `<PriceTag>` migration (R18 fix). (D) **Heading primitive inline style beats parent scoped CSS** — same as R16-18 pitfall A, but worth restating: use `.hero-banner h2[style*="font-size"] { font-size: 60px !important; }` global rule. Verification: R19 35/35 PASS, R20 36/36 PASS.
- **`!important` audit + inline-style → CSS refactor (R21 — 2026-08-02):** See `references/aot-r21-important-and-inline-style-refactor-2026-08-02.md` — the 11 migrated-component selectors refactored from `!important` to specificity-raised patterns (element-prefix `section.foo` and doubled-class `.foo.foo`), the 5 inline `style="..."` values moved to scoped CSS via CSS custom property pattern (`--bg-image`, `--hero-bg-image`), the 5 legacy token aliases added to `tokens.css`, and the dead-code removal (`.info-strip`, `#deal-banner`). 5 new pitfalls: (P1) Section primitive's `[data-astro-cid-*]` selector wins over single-class overrides — use `section.foo` prefix. (P2) Inline dynamic bg-image pattern: `style="--bg-image: url(...)"` + `background-image: var(--bg-image)`. (P3) Minifier shortens hex (`.#003366` → `#036`) — pattern allow-list helps. (P4) Carry-forward from R17: orphan global `!important` keeps bleeding into migrated components — grep after every R-value refactor. (P5) "Fresh verification evidence" trap — re-run verification script per round, don't claim verified from prior script. Numbers: source `!important` 80→66 (-17%), bundle `!important` 115→59 (-49%), 23/23 verification PASS.

## Deployment / Transfer Readiness

When pushing Astro-emdash builds to staging (`deploy-fresh`):
- Always copy both `dist/index.html` AND `dist/_aot_assets/*.css` to the `site/` root
- The `_aot_assets/` directory is NOT auto-deployed by CF Pages unless it lives in `site/`
- CSS bundle filename changes on every rebuild (hash-based) — always copy the new one

## CSS Architecture

**Strategic direction (confirmed 2026-07-28): Kadence is being phased OUT.** All styling must be self-contained in the Astro project. Do not re-add external Kadence CSS links. The `src/styles/active-oahu-tours-minimal.css` is the single source of truth for all CSS.

**Key rule: no external Kadence/theme CSS links in Astro templates.** External hotlinks to `activeoahutours.com` CSS files cause double-injection by the Astro build, making Kadence `!important` rules win over Astro-scoped `!important`. All styling must live in scoped `<style>` blocks + `src/styles/active-oahu-tours-minimal.css`.

**Do NOT use `all: revert`** — it strips CSS custom property inheritance and causes all text to render black. Use explicit palette overrides instead.

**Final working pattern for AOT buttons:** White text on `#1a3a5c` background (10.6:1 WCAG AAA). This shares the hero/CTA section background color, is visually cohesive, and is not affected by Kadence's CSS variable cascade. See `references/astro-css-architecture.md` for full details including why orange buttons fail.

**Working button design system (2026-07-28 session):**
- Drop ALL `.btn-primary` from button HTML — it is Kadence's hook into the cascade
- Use AOT-native classes: `aot-book-now` (header nav), `aot-btn-hero-book` (hero), `aot-btn-phone` (closing CTA)
- Button colors: `#1a3a5c` background + `#ffffff` text = 10.6:1 AAA (passes everywhere)
- Hover: `#003366` background + `#ffffff` text

Key findings from the 2026-07-28 CSS sessions:
- **Remove `.btn-primary` from button HTML entirely** — it is Kadence's hook into the cascade. Use AOT-native classes: `aot-book-now`, `aot-btn-hero-book`, `aot-btn-phone`.
- **Astro scoping transforms `.hero-banner .child`** — `<section class="hero-banner">` is scoped as `section.hero-banner[data-astro-cid]`. A bare `.hero-banner` class selector doesn't exist. Use `:where(.hero-banner)` to work around this.
- **`has-text-color` adds a second specificity layer** — always include it in Kadence palette override selectors.
- **Glyphicon font-size is Kadence-controlled** — Kadence sets `.glyphicon { font-size: small !important }`. Always add `font-size: inherit !important`.
- **Source order wins even with `!important`** — Kadence's injected `<style>` blocks appear after the Astro bundle. When specificities match and both have `!important`, Kadence wins because it comes last. Removing `.btn-primary` from HTML is the only clean solution.

## Verification Commands

### Lighthouse on staging
```bash
npx lighthouse "https://deploy-fresh.active-oahu-tours-mirror.pages.dev/" \
  --only-categories=performance,accessibility,best-practices,seo \
  --output=json --output-path=/tmp/lh.json \
  --chrome-flags="--headless --no-sandbox" --quiet
```

### Staging-vs-production structural diff (the 5-signal audit)
```bash
# Live (fetches both URLs)
python3 scripts/aot-staging-vs-prod-diff.py \
  --prod-url https://activeoahutours.com/ \
  --staging-url https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/

# From saved HTML
python3 scripts/aot-staging-vs-prod-diff.py \
  --prod-html /tmp/prod.html \
  --staging-html /tmp/staging.html
```
Catches missing images, duplicate images, missing background images, missing content, and section-order drift in one pass. See `references/aot-staging-vs-prod-structural-diff-2026-07-30.md` for the recipe.

### Hero font-size / contrast verification (Round 14 — 2026-07-31)
```bash
python3 scripts/verify-hero.py
```
12-check verifier for the hero only: root `html { font-size: 62.5% }`, H1
clamp, H2 production clamp curve, lifestyle bg image bundled locally, overlay
`::before` with opacity 0.3, H1/H2 text-shadow values. Handles the
minified-CSS pitfall (e.g., `clamp(2.75rem, 0.489rem + 7.065vw, 6rem)` becomes
`clamp(2.75rem,.489rem+7.065vw,6rem)` in the bundle). Returns exit 1 with a
5-layer diagnostic ladder if hashes don't match. See
`references/aot-hero-font-size-root-clamp-pattern-2026-07-31.md`.

### CF Pages deploy check (content-aware, not just HTTP 200)
The branch preview URL can return `HTTP 200` while still serving a prior commit
(webhook lag, stale queue). Probe for a marker that only exists in the new commit:
```bash
branch=content-astro-homepage
url="https://${branch}.active-oahu-tours-mirror.pages.dev/"
marker="view-all-tours-link"   # pick something new in this PR
count=$(curl -sL -A "Mozilla/5.0" "$url" | grep -c "$marker")
[ "$count" -ge 1 ] && echo "DEPLOYED" || echo "STALE (HTTP 200 but old build)"
```
See `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` §"Cloudflare Pages deploy lag"
for the full diagnostic ladder.

### 6-layer deploy + browser-cache diagnostic (2026-07-31)
See `references/aot-browser-tool-cache-vs-cdn-cache-2026-07-31.md` for the full
ladder. Short version, in order: source → dist → CDN HTML → CDN sub-asset → browser
cache → DOM render. Run `sha256sum` + `grep` against each layer to find which one
is stale.

### Header layout diagnostic — height + children measurement
After every nav/header change, run from `browser_console`:
```javascript
var nav = document.querySelector(".aot-primary-nav");
return Array.from(nav.children).map(c => ({
  cls: c.className.split(" ")[0],
  h: Math.round(c.getBoundingClientRect().height),
  w: Math.round(c.getBoundingClientRect().width)
}));
```
If child widths == parent width AND both stack vertically → parent is missing
`display: flex`. See `references/aot-header-refinement-round-9-2026-07-31.md`.

### CF Pages deploy check
```bash
curl -s -A "Mozilla/5.0" "https://deploy-fresh.active-oahu-tours-mirror.pages.dev/" | wc -c
```

### CSS bundle check
```bash
# Get the bundle URL from built HTML
grep "_aot_assets" site/index.html
# Fetch and check it's live (200, not 404)
curl -sI "https://deploy-fresh.active-oahu-tours-mirror.pages.dev/_aot_assets/$(basename $(grep _aot_assets site/index.html | grep href | head -1 | sed 's/.*href="//;s/".*//'))"
```

### Inline style audit (must be zero)
```bash
grep -rn "style=" src/components/ --include="*.astro" | grep -v ".bak"
```

### Contrast audit (Python)
```python
import json
with open('/tmp/lh.json') as f:
    d = json.load(f)
cc = d['audits'].get('color-contrast', {})
items = cc.get('details', {}).get('items', [])
print(f'Contrast failures: {len(items)}')
for it in items:
    n = it.get('node', {})
    print(f"  {n.get('nodeLabel','?')} — {it.get('explanation','')[:200]}")
```

## Git Workflow

### Before opening a PR
1. Branch off `main` (never `staging` — that's Michael's in-progress branch)
2. Run `git diff --stat` and verify scope is what you intended
3. For bulk HTML edits, use HTMLParser-based scripts (never regex — AGY caught a high-severity regex bug in the first version of `add_main_landmark.py`)
4. Capture Lighthouse baseline BEFORE pushing if the change affects rendered output

### Before any push
- NEVER `git push --force` to shared branches (main, staging, deploy-fresh)
- `git push --force-with-lease` is OK only on your own private feature branch
- If work is lost to a bad push: use `git reflog` to find the lost commit, `git reset --hard <sha>` on local branch

### After pushing (PR + edge changes)
1. Wait for CF Pages auto-preview deploy (~75 seconds is the typical minimum; can run 5+ minutes if the queue is backed up)
2. Test on preview URL before claiming "done" — verify with a **content-aware probe**, not just `HTTP 200` (see Verification Commands above). The preview can serve a stale commit while still returning 200.
3. Post PR link in Linear with standard comment pattern (see `okf/ops-runbook/linear-integration.md`)

### Branch cleanup after merged PRs (2026-08-19)

When Michael says "do your cleanup on the branches you've been working on":

1. **Scope to MY branches.** `content/kai-*` + branches confirmed mine via `git log -1 --format='%an'`. Other agents' branches (Jules/AGY `feat/gro-*`, `fix/*`, `content/kba-*`, Fred/Ned `ned/GRO-*`, `feature/fred-*`) stay even if they look stale — ownership = deletion approval (governance: `branch-deletion-approval` micro-skill). Report what was left and why.
2. **Squash-merge false "UNMERGED".** `git merge-base --is-ancestor` / `git cherry` report `UNMERGED-COMMITS` for squash-merged branches (GitHub creates a new commit SHA on main, so the feature commits are not ancestors). This is the normal case here. The correct deletion proof is: (a) `gh pr view <n> --json state,mergedAt` → MERGED, AND (b) the branch's signature artifact exists on `origin/<default>` (`git show origin/main:okf/README.md | head -2` for retirement pointers). Ancestry checks alone both over-block and under-block.
3. **Branch still OPEN ≠ deletable.** A retirement branch whose PR is still OPEN (e.g. SEO PR #2 while its twin PRs #132/#6 merged) must be kept; delete only after merge + content verification.
4. **Dirty-checkout trap.** `git checkout main` can abort on untracked files that would be overwritten — but you don't need to switch to delete a branch you're not sitting on: `git branch -D <name>` works from any other checked-out branch. Only the currently-checked-out branch needs a switch first.
5. **Non-branch tidy:** `/tmp` temp clones (e.g. `/tmp/seo-scrub` from a filter-repo scrub) and `hermes-verify-*` scripts are safe to `rm -rf` as part of the same cleanup pass.

## Governance / Prismatic Engine

- `PRISMATIC_ENGINE.yaml` in the Astro worktree (`work/astro-homepage-work/`) is the effective config for pre-push hooks
- `governor: "fred"` means Fred must approve deploys to `deploy-fresh`
- Kai's lane must explicitly include `astro/` to own Astro content
- Use `git push --no-verify` only when Michael has authorized Kai's AOT permissions for that push
- **The pre-push hook evaluates the diff range, not just your commit's files** — a prior session's out-of-lane commit in your push range can block your push even when your own commit is in-lane. Diagnose and override pattern in `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` §"Prismatic Engine: lane-violation can hit without you editing the file".

## Worktree Locations

| Work | Path |
|------|------|
| Astro homepage | `/home/ubuntu/work/astro-homepage-work/` |
| Main mirror | `/home/ubuntu/work/active-oahu-tours-mirror/` |
| Prismatic Engine | `/home/ubuntu/.gemini/antigravity-cli/scratch/prismatic-engine/` |

## Business Data

**AOT OKF is centralized in the private hub (2026-08-19, Phase 1 — Michael's decision).** Canonical home for ALL AOT knowledge: `mbgulden/growthwebdev-knowledge` → `okf/hubs/active-oahu/` (hub PR #29; mirror retirement PR #132; business + SEO retirements pending).

| Section | Was |
|---|---|
| `okf/hubs/active-oahu/business/` | `mbgulden/active-oahu-business/okf` (compliance, vendors, FareHarbor, analytics, decision log) |
| `okf/hubs/active-oahu/seo/` | `mbgulden/aot-seo-knowledge/okf` (strategy, audits, GA4/GSC baselines, Ubersuggest) |
| `okf/hubs/active-oahu/{architecture,governance,reports,kai-reports,audits,verification}/` | `mbgulden/active-oahu-tours-mirror/okf` (public-safe doctrine) |

- **New AOT OKF goes to the hub, not to per-repo `okf/` dirs** (source repos become pointer stubs). Lane: kai owns `okf/hubs/` in the hub's PRISMATIC_ENGINE.yaml; branch prefix `content/`.
- **Secret still live in the source repos:** the aot-seo-knowledge docs contain a Google OAuth client secret that was redacted in the hub copy but NOT rotated — treat any reuse of those docs as a re-leak path until the OAuth client is rotated (follow-up, not yet done).
- Search via `mcp_okf_search("active oahu")` after the hub PR merges (per-profile MCP index staleness applies — reload/new session needed).
- Full session record + open follow-ups: `okf-mcp-hub` skill → `references/aot-hub-centralization-phase1-2026-08-19.md`.
- The public mirror repo does NOT contain FareHarbor API keys, Ubersuggest credentials, or analytics configs — those were in the private repos and now live in the private hub.
