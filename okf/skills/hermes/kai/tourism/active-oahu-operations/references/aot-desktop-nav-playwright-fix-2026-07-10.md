# AOT desktop nav Playwright fix — 2026-07-10

## When this applies

Use this pattern when `activeoahutours.com` desktop navigation looks broken, top-level menu labels do not navigate, nested dropdowns are hard to reach, or nav links need full rendered verification rather than static HTML checks.

## Production symptoms found

A Playwright audit against production found:

- `#primary-menu` had 26 desktop nav links.
- Top-level parent menu labels such as Activities, Rentals, Adventure Guide, and Contact Us were intercepted by an inline desktop dropdown click handler using `e.preventDefault()`, so the labels toggled dropdowns instead of acting as real links.
- Nested dropdown behavior needed explicit hover-path verification.
- The Reviews nav item pointed at `/reviews/index.html`, while Cloudflare Pages `_redirects` included `/reviews/* /reviews/ 301`; this produced a `/reviews/` self-redirect loop.

## Durable fix pattern

1. Create a clean worktree from `origin/main` on a `content/` branch.
2. Run a production Playwright desktop audit before editing. Use a 1440×900 viewport and inspect every `#primary-menu` item.
3. Fix the behavior, not just the visual symptom:
   - Remove/avoid desktop JavaScript that calls `e.preventDefault()` for parent nav links.
   - Keep mobile hamburger behavior intact.
   - Let desktop dropdowns be controlled by CSS `:hover` and `:focus-within` so mouse and keyboard users can reveal them.
   - For nested dropdowns, verify by hovering through the full parent path.
4. Fix nav target redirects if the nav reveals route issues:
   - Normalize Review links from `/reviews/index.html` to `/reviews/`.
   - Remove broad self-looping redirect rules such as `/reviews/* /reviews/ 301` when they also match `/reviews/` itself.
   - Preserve explicit legacy review-slug redirects above the removed wildcard when possible.
5. Add a reusable Playwright regression script under `scripts/`, not a one-off `/tmp` script only. The script should:
   - Crawl `#primary-menu` recursively.
   - Hover each parent path before checking a submenu item.
   - Assert each link is visible, inside the viewport, topmost/clickable at center, HTTP 2xx/3xx, and click-navigates away from the homepage.
   - Write JSON evidence and screenshots to `/tmp`.
6. Store the plan/evidence artifact in a Kai-owned lane, e.g. `okf/reports/golden-thread/`, not top-level `reports/` if the pre-push lane guard rejects that path.
7. Open PR, wait for `drift-guard`, web governance, and Cloudflare Pages preview checks.
8. After merge, confirm Cloudflare Pages production deployed the merge commit, purge exact nav URLs on apex + www, then rerun the Playwright verifier against production.

## Verification checklist

Pre-PR/local:

```bash
python3 -m http.server 8780 --bind 127.0.0.1  # from site/
NODE_PATH=/tmp/aot-playwright/node_modules node scripts/verify_desktop_nav_playwright.js 'http://127.0.0.1:8780/' /tmp/aot-nav-local-after.json
```

Expected shape:

```json
{
  "totalLinks": 26,
  "failures": 0
}
```

Post-merge/production:

```bash
NODE_PATH=/tmp/aot-playwright/node_modules node scripts/verify_desktop_nav_playwright.js 'https://activeoahutours.com/' /tmp/aot-nav-prod-after.json
curl -sS -I -L --max-redirs 5 https://activeoahutours.com/reviews/
```

Expected:

- Production verifier reports `totalLinks: 26`, `failures: 0`.
- `/reviews/` returns HTTP 200 with no redirect loop.

## Ad-hoc verification guard lesson

If Hermes asks for fresh verification after code edits, create a focused temporary verifier at `/tmp/hermes-verify-*.py`, run it, and clean it up. For this class of work, assert:

- The reusable Playwright script exists and passes `node --check`.
- Any `/tmp` audit/PR-body scripts referenced by the session still parse or contain expected markers.
- The lane-safe report exists at `okf/reports/...`; any rejected old `reports/...` path is absent.
- The latest production Playwright JSON exists and reports `baseUrl=https://activeoahutours.com/`, `totalLinks=26`, `failures=0`.
- Representative nav items are present in the JSON: Activities & Tours, Rentals, Adventure Guide, Contact Us, Reviews, FAQ.
- `gh pr view <PR>` confirms merged.
- `/reviews/` returns HTTP 200.
- `git diff --check` passes.

Report this as focused ad-hoc verification, not a canonical suite green.

## Pitfalls

- Do not “fix” desktop parent links by removing dropdowns; parent links and dropdowns both need to work.
- Do not regress keyboard access; add `:focus-within` when relying on CSS dropdowns.
- Do not trust static link checks alone. A menu item can have a valid href but be hidden, covered, or blocked by JS.
- Do not leave a broad `_redirects` wildcard that redirects a path to itself.
- If the pre-push lane guard rejects `reports/...`, move the artifact to `okf/reports/...` or another Kai-owned lane rather than bypassing the hook.
- If Playwright cannot start because disk is full, free transient caches/artifacts and rerun verification; capture the cleanup as operational hygiene, not as a durable claim that Playwright is broken.
