# AOT Staging-vs-Production Structural Diff — 2026-07-30 Session

> **Use this when:** the Astro homepage preview URL is up but Michael reports "missing background images", "duplicate images", "wonky layouts / empty gaps", or "missing content". This is the diagnostic recipe that found all five in one session.

## The five structural signals (run all five)

1. **HTML byte-size diff** — production 109 KB, staging 55 KB → ~50% smaller immediately flags missing content.
2. **`<img>` src dedup detection** — production has 0 duplicates; staging had 3 (Tripadvisor PNG in Hero AND Awards; `DSC5297_2000-e1642616607887.jpg` in Hero bg AND `FeaturedTourHero`; `Oahu-Kayaking-Tours_31-1-480x240.jpg` in two FeaturedTours cards).
3. **`background-image` URL count** — production has 6 unique bg-image references; staging had 1. Hero bg was the only one rendered; the 5 missing were: `DSC5297_2000-e1642616607887.jpg` (BeachEquip), `DSC5268_2000-650x433.jpg` (Daily card), `DSC5281_2000-650x433.jpg` (Multi-Day card), `Mokolii-from-above-view-1.jpg` (Mokulii block), `Oahu-Kayak-Tours_11_thumb-1-480x240.jpg` (Rainforest card), `Oahu-Kayaking-Tours_31-1-480x240.jpg` (Chinaman card).
4. **Heading order diff** — extract h1/h2/h3 in source order from both, diff the sets. Staging was missing "Testimonials" h2, "Popoia Kailua's Flat Island" h3, and had renamed the popular-tours h2 to appear after BeachEquipment (instead of before).
5. **Section ordering via source-position** — for production, the Kadence `<section class="container">` containing the H1 wraps everything until `</main>`. The h2/h3 markers inside it reveal the section order.

## Scripts that capture all five signals

The companion script `scripts/aot-staging-vs-prod-diff.py` (under this same skill) runs all five signals and prints a structured report. It expects two HTML files (production + staging) and a list of section IDs.

## Production's "2-column image card" pattern (the layout piece)

Production uses `<div class="front-page-with-bg" style="background-image:url(...)">` as the LEFT column (75% width, full-height bg image with text overlay). The RIGHT column is `<div class="col col-xs-3">` containing stacked `<div class="front-page-packages">` cards (each is an `<a>` with `style="background-image: url(...)"` containing `package-front-text` + `package-margins` headings).

Staging was rendering these as a flat 4-column grid of `<img>` tags instead of the 75/25 split + dark-overlay cards. The fix was rewriting `BeachEquipment.astro` to accept a `packages` prop and render a `front-page-with-bg` left column + 2 stacked cards right column, then creating a new `MokuluaFeatureBlock.astro` for the second production block (the inverse order — 25/75 with cards on the left).

CSS class signature for the layout pattern (worth preserving):
- `front-page-with-bg` — left column, bg-image + text overlay
- `col col-xs-9 feature-description` (or `feature-description-left`) — wraps the bg container
- `col col-xs-3` — wraps the stacked package cards
- `front-page-packages text-center` — individual card container
- `darken` — class on the card `<a>` that adds a `::before` overlay (rgba(0,0,0,0.45))
- `package-front-text` + `package-margins` + `activity-front-text` + `date-front-text` — typography layers

## Image dedup — root cause + fix pattern

The duplicate images came from two distinct design choices that share an image URL:

| Image | Hero/Awards uses | Also used in |
|---|---|---|
| `TC_transparent_BF-Logo_L_2024_RGB.png` | Hero (right column logo) + Awards section | — |
| `DSC5297_2000-e1642616607887.jpg` | Hero bg | `mokulua-kayak-adventure` FeaturedTourHero (inline img) |
| `Oahu-Kayaking-Tours_31-1-480x240.jpg` | FeaturedTours Chinaman card | FeaturedTours Kahana card |

Production solves this by using **3 different Tripadvisor images** (the wide SVG lockup for Hero, the 2024 BF PNG for Awards, the 2022 SVG for Awards). Staging had reused the BF PNG in both spots.

**Fix recipe:** when a duplicate `<img>` src appears in production, the production solution is always "use a different image". Don't de-duplicate by removing one — replace it with the production's actual choice. In this session:
- Hero Tripadvisor → `https://www.tripadvisor.com/img/cdsi/img2/branding/v2/Tripadvisor_lockup_horizontal_secondary_registered-18034-2.svg` (wide lockup, from production)
- Mokulua FeaturedTourHero → `DSC5281_2000-650x433.jpg` (smaller Kayaking image, from production)
- Kahana FeaturedTours card → `Oahu-Kayak-Tours_11_thumb-1-480x240.jpg` (Rainforest card image, from production)

## The 5 questions to answer before fixing

Before changing any code, dump these into the response so Michael can pick a fix strategy:

1. How many `<img>` URLs are missing on staging? (9 in this session)
2. How many `<img>` URLs are extra on staging? (1 in this session)
3. How many `background-image` URLs are missing? (5)
4. What's the section ordering diff? (which h2/h3 appear in prod but not staging, and vice versa)
5. What's the duplicate-image list?

If any of these is non-zero, the staging site is not production-parity and needs structural fixes, not just content patches.

## Production section order to mirror

This is the canonical order production uses (and what staging now matches):

```
Hero
  → Testimonial (centered "Great tour!" h2)
  → FeatureBlock (3 cards: Guided Kayak Tours / Beach Gear / Need Kayaks Today?)
  → FeaturedTourHero (e-bike Kau Kau)
  → FeaturedTourHero (Popoia Flat Island)
  → FeaturedTourHero (Mokulua Islands)
  → FeaturedTours (Our Most Popular Experiences — 3 tour cards)
  → BeachEquipment (75/25 split: bg-image left + Daily+Multi-Day cards right)
  → MokuluaFeatureBlock (25/75 split: Rainforest+Chinaman cards left + bg-image right)
  → ClosingCTA (Plan Your Oʻahu Kayaking Adventure)
  → Awards
```

Notice that the `RentalGrid` flat 4-column grid (Daily/Multi-Day/Self-Guided/Chinaman's Hat as plain list items) is **not** in production — that was a staging-invented section. It was kept in staging as a supplementary grid but doesn't appear on production's homepage. Worth confirming with Michael before deleting it.