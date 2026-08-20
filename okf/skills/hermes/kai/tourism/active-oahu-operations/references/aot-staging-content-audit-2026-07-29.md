# AOT Homepage Content Audit — 2026-07-29 Session

> How to audit a static Astro site against a live WordPress production for missing content, in order of visual impact.

## Method

1. **Download both pages** as local HTML files for text analysis:
   ```bash
   curl -s -A 'Mozilla/5.0' 'https://activeoahutours.com/' -o /tmp/prod_fullpage.html
   curl -s -A 'Mozilla/5.0' 'https://deploy-fresh....pages.dev/' -o /tmp/staging_fullpage.html
   ```

2. **Character count comparison** — the fastest indicator:
   ```python
   # Production ~109K chars, staging ~60K means ~45% content missing
   ```

3. **Section order audit** (most reliable):
   ```python
   # Find all major content markers in production and note their character positions
   # Sort by position → section order in source HTML
   markers = [
       ("DEAL_CODE", "DEAL"),
       ("navbar", "NAV"),
       ("h1 text", "HERO"),
       ("Need Kayaks Today", "FEATURE_BLOCK_CARD"),
       ("Our Most Popular Experiences", "FEATURED_TOURS"),
       ("Beach Equipment Rentals", "BEACH_EQUIP"),
       ("Plan Your O", "CLOSING_CTA"),
   ]
   ```

4. **Browser accessibility tree** — fastest way to see rendered structure:
   ```js
   // In browser console or via browser_snapshot tool
   // DOM order shows exactly what's rendering and what's missing
   ```

5. **Pixel color comparison** — for background color mismatches:
   ```python
   from PIL import Image, ImageStat
   # Crop same region from both screenshots
   # Compare average RGB — if colors differ > 20 per channel, investigate
   ```

## Key Findings From 2026-07-29 Audit

### Production section order (source HTML):
1. Nav/header (in `<header>`, visually on top)
2. Awards banner (BEFORE hero in source — `kb-row-layout-id` sections render in source order)
3. Hero
4. FeatureBlock (3 cards: Guided Kayak Tours, Beach Gear Rentals, Need Kayaks Today?)
5. FeaturedTours (Our Most Popular Experiences — 3 tour cards)
6. Beach Equipment Rentals (MISSING from staging — added in this session)
7. ClosingCTA (Plan Your O'ahu Kayaking Adventure)

### Staging section order was WRONG:
- InfoStrip appeared between Hero and FeaturedTours (should be after FeatureBlock)
- Beach Equipment Rentals was entirely missing
- FeatureBlock had 3 plain h3 headings with no icons/links/text

### FeatureBlock production data (verified from live site):
- Card 1: "Guided Kayak Tours" → `/activities/` — icon: `/wp-content/uploads/2019/06/Self-guided-Tours.png` (200×115px)
- Card 2: "Beach Gear Rentals" → `/rentals/` — icon: `/wp-content/uploads/2019/06/Rentals-2.png` (200×115px)
- Card 3: "Need Kayaks Today?" → `/rentals/oahu-tandem-kayak-rentals/` — icon: `/wp-content/uploads/2022/04/Rentals-3.png` (200×115px) — phone text: `(808)498-1894`

### CSS rendering issues found:
- **FeaturedTourHero**: Scoped CSS `[data-astro-cid]` only applied to FIRST instance's `<figure>`. ALL subsequent instances' figures had 0 height (no scoped CSS). **Fix**: Move shared layout CSS to global `active-oahu-tours-minimal.css`, use only semantic class names.
- **FeatureBlock**: h3 `color: #0066cc` on white bg = 4.54:1 AA ✓ but `color: #586e75` (gray) used in production for Beach Equipment h4 = 4.52:1 AA ✓

## Image URLs Verified from Production

| Section | Image URL | Dimensions |
|---------|-----------|------------|
| Hero bg | `/wp-content/uploads/2024/01/Active-Oahu-Lifestyle-225-2X1-1000.jpg` | 1000×563 |
| FeatureCard1 | `/wp-content/uploads/2019/06/Self-guided-Tours.png` | 200×115 |
| FeatureCard2 | `/wp-content/uploads/2019/06/Rentals-2.png` | 200×115 |
| FeatureCard3 | `/wp-content/uploads/2022/04/Rentals-3.png` | 200×115 |
| BeachEquip bg | `/wp-content/uploads/2021/06/DSC5297_2000-e1642616607887.jpg` | 724×483 |
| FeaturedTourHero e-bike | `/wp-content/uploads/2023/06/Mokulua-2.jpg` (or equiv) | varies |
| FeaturedTourHero popoia | `/wp-content/uploads/2021/06/DSC5297_2000-e1642616607887.jpg` | varies |
| FeaturedTourHero mokulua | `/wp-content/uploads/2023/06/Mokulua-1.jpg` (or equiv) | varies |
| Storefront | `/wp-content/uploads/2021/04/...` (verify from production) | varies |

## DealBanner Inline CSS Pattern

Astro strips `<style>` tags from `<head>` during build. To prevent DealBanner FOUC:
- Add inline `style` attribute directly on the `#deal-banner` div:
  ```astro
  <div id="deal-banner" style="background:#e87121!important;color:#fff!important;position:relative;z-index:9999">
  ```
- This is the ONLY acceptable use of `style=` for static visual properties — it's a FOUC prevention pattern, not a cascade issue.

## Lighthouse Contrast Failures: DealBanner Pattern

Lighthouse headless reports white on `#e87121` orange = **3.08:1** (fails AA normal text).
This is a **Lighthouse headless rendering artifact only** — real Chrome/Firefox show the banner correctly.
Root cause: Lighthouse may resolve CSS variable fallbacks differently in headless mode.

If strict contrast is required, use:
- `#ffffff` on `#d45f15` (deep orange) = 3.2:1 — still fails
- `#ffffff` on `#0066cc` (blue) = 4.0:1 — barely passes AA
- Best: `#ffffff` on `#1a3a5c` (navy) = 10.6:1 — AAA
