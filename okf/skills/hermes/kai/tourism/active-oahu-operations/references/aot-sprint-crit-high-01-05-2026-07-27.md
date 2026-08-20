# AOT CRIT/HIGH Sprint Results — PR #104–#112 (2026-07-27)

All PRs merged to `origin/main` and deployed to `activeoahutours.com` via Cloudflare Pages.

| # | Task | PR | Status | Live |
|----|------|-----|--------|------|
| CRIT-01 | Booking calendar iframe (`/rentals/`) | [#104](https://github.com/mbgulden/active-oahu-tours-mirror/pull/104) | ✅ Merged | ✅ Live |
| CRIT-02 | Booking CTA `target=_blank` removed (267 links) | [#104](https://github.com/mbgulden/active-oahu-tours-mirror/pull/104) | ✅ Merged | ✅ Live |
| CRIT-03 | Heading H5→H3 hierarchy (898 tags, 134 files) | [#104](https://github.com/mbgulden/active-oahu-tours-mirror/pull/104) | ✅ Merged | ✅ Live |
| HIGH-01 | Schema `openingHoursSpecification` (Mon-Sat 8AM-5PM, Sun closed) | [#105](https://github.com/mbgulden/active-oahu-tours-mirror/pull/105) | ✅ Merged | ✅ Live |
| HIGH-02 | Descriptive alt text (88 files, 2 kebab-case alts replaced) | [#106](https://github.com/mbgulden/active-oahu-tours-mirror/pull/106) | ✅ Merged | ✅ Live |
| HIGH-03 | TripAdvisor trust badge above booking CTAs (162 pages) | [#107](https://github.com/mbgulden/active-oahu-tours-mirror/pull/107) | ✅ Merged | ✅ Live |
| HIGH-04 | `/adventure-guide/` → `/activities/` 301 redirect | [#108–#111](https://github.com/mbgulden/active-oahu-tours-mirror/pull/111) | ✅ Merged | ✅ Live |
| HIGH-05 | Meta keywords on 38 pages (homepage, rentals, 36 activity pages) | [#112](https://github.com/mbgulden/active-oahu-tours-mirror/pull/112) | ✅ Merged | ✅ Live |

## Key technical notes

### CRIT-01/02/03 — PR #104 (squash merge)
- **Calendar:** Replaced broken `aot-lazy-fh-calendar` div with direct `<iframe>` embed
- **CTAs:** Removed `target="_blank"` from 267 FareHarbor links across 33 tour pages
- **Headings:** H5→H3 with three-case logic (plain H5 + inline style, class H5, Kadence H5)

### HIGH-01 — PR #105
- Added `openingHoursSpecification` to TravelAgency schema in `site/index.html`
- Enhanced Organization schema in `site/_templates/head.html` with `foundingDate`, `telephone`, `address`

### HIGH-02 — PR #106
- Replaced `alt="kailua-lanikai-kayak-rental-mokes-oahu"` with descriptive alt
- Replaced `alt="mokolii-kayak-rentals-delivered"` with descriptive alt
- 88 files affected

### HIGH-03 — PR #107
- Injected TripAdvisor badge (4.8 stars, 356 reviews) above all "Book Online" buttons
- CSS scoped to `.tripadvisor-inline-badge`
- 162 badges across 161 pages

### HIGH-04 — PR #108–#111 (4 attempts)
- v1: Edited wrong `_redirects` (repo root instead of `site/`)
- v2: Placed redirect after 404 catch-all (never matched)
- v3: Added bare `/adventure-guide` redirect but CF Pages `/*` wildcard doesn't match bare paths
- **v4 (success):** Created `site/adventure-guide/index.html` with meta refresh + JS redirect; kept wildcard redirect in `_redirects` for subpaths

### HIGH-05 — PR #112
- 38 files: homepage (15 kw), rentals (14 kw), activities index (10 kw), 36 activity pages (5–12 kw each)
- Keywords chosen for commercial search intent: "Oahu kayak rental", "Mokulua Islands kayak tour", etc.
- Script handles both meta attribute orderings using `re.DOTALL`
