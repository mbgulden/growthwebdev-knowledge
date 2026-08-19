---
type: Report
title: Active Oahu desktop navigation Playwright fix — 2026-07-10
description: Fix the `activeoahutours.com` desktop navigation by testing every desktop nav item with Playwright, then shipping a regression-safe solution.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/golden-thread/desktop-nav-playwright-fix-20260710.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu desktop navigation Playwright fix — 2026-07-10

## Goal

Fix the `activeoahutours.com` desktop navigation by testing every desktop nav item with Playwright, then shipping a regression-safe solution.

## Acceptance criteria

At desktop viewport `1440 x 900`:

1. Every top-level nav link is a real clickable link and navigates when clicked.
2. Every submenu item can be revealed with hover through its parent path.
3. Nested submenu items are visible, in viewport, and clickable when their parent path is hovered.
4. Keyboard focus can reveal dropdowns via `:focus-within`.
5. Every nav href returns HTTP 2xx/3xx with no redirect loop.
6. Reviews nav item serves a page instead of looping `/reviews/ -> /reviews/`.
7. Mobile hamburger behavior is not intentionally changed.

## Production findings before fix

Playwright production audit on `https://activeoahutours.com/?kai_nav_audit=desktop1` found:

- 26 total nav links under `#primary-menu`.
- Top-level parent links were intercepted by the desktop dropdown click handler, so parent labels such as Activities, Rentals, Adventure Guide, and Contact Us toggled menus instead of acting as normal links.
- Nested desktop submenu links required fragile JS state and were not reliably visible/clickable in a parent-only hover pass.
- `Reviews` pointed to `/reviews/index.html`, while Cloudflare Pages `_redirects` had a broad `/reviews/* /reviews/ 301` rule. That caused `/reviews/` and `/reviews/index.html` to redirect to `/reviews/` repeatedly.

## Solution shipped in this branch

- Removed the desktop parent-click dropdown handler from static HTML pages so parent menu labels remain normal links.
- Left mobile menu-toggle behavior intact.
- Hardened desktop dropdowns in `nav-fix.css` using CSS `:hover` and `:focus-within` so mouse and keyboard users can reveal first-level and nested submenus.
- Normalized duplicated nav Review links from `/reviews/index.html` to `/reviews/`.
- Removed the broad self-looping `_redirects` wildcard `/reviews/* /reviews/ 301`, while preserving the explicit legacy review-slug redirects already listed above it.
- Added `scripts/verify_desktop_nav_playwright.js`, a reusable Playwright regression verifier that crawls each nav item, hovers through parent paths, checks visibility/clickability, requests each link, and click-tests navigation.

## Local verification

Command:

```bash
python3 -m http.server 8780 --bind 127.0.0.1  # from site/
NODE_PATH=/tmp/aot-playwright/node_modules node scripts/verify_desktop_nav_playwright.js 'http://127.0.0.1:8780/' /tmp/aot-nav-local-after.json
```

Result:

```text
totalLinks: 26
failures: 0
```

Every nav item passed local Playwright verification, including:

- Activities & Tours
- All Tours
- Self Guided Tours
- Guided Tours
- Rentals
- All Rentals
- Kayak Rentals
- Mokolii Kayak Rentals
- Kailua Kayak Rentals
- Multi-Day Rentals
- Rental Partners
- Electric Bike Rentals
- Adventure Guide
- All Adventure Guides
- Get Your Kayak Rental for Chinaman’s Hat
- Lanikai Beach Guide
- Kailua Beach Guide
- How to Transport Kayaks
- Contact Us
- About
- Our Kailua Storefront
- Awards
- Guides
- Reviews
- Gallery
- FAQ

## Post-merge verification required

After merge and Cloudflare deploy:

1. Confirm Cloudflare Pages production deployed the merge commit.
2. Purge `/`, `/reviews/`, `/reviews/index.html`, and representative nav target URLs on apex + www.
3. Run the Playwright verifier against `https://activeoahutours.com/`.
4. Confirm `/reviews/` is HTTP 200 with no redirect loop.
5. Update Linear/PR with production evidence.
