# Astro CSS Architecture for AOT Homepage

> **Session source:** Active Oahu 2026-07-28 — Kadence CSS cascade battle, Astro scoping gotchas, specificity fixes.
> **Updated 2026-07-28 (second session):** `all: revert` failure, has-text-color class, Kadence CSS variable cascade, final working pattern.
> **Updated 2026-07-29:** FeaturedTourHero global CSS fix (scoped CSS only applied to first instance), DealBanner inline style pattern, wkhtmltoimage https image limitation, content audit method.

## Production Color Palette (Live Site — browser_console Verified 2026-07-29)

| CSS Variable / Element | Production Value | Notes |
|-----------------------|-----------------|-------|
| `--global-palette9` | `#ffffff` | Kadence's white — NOT `#1a3a5c` |
| `--global-palette1` | `#3182CE` | Kadence's primary blue |
| Nav background | `#006699` | `rgb(0, 102, 153)` — NOT `#003366` |
| Footer background | `#006699` | Same as nav |
| Nav text | `#ffffff` | white |
| Header/branding bg | `#ffffff` | white |
| Hero overlay | `rgba(0, 0, 0, 0.3)` | from `kb-section-has-overlay::before` |
| Font: h1, h2 | Open Sans Condensed | `"Open Sans Condensed", "Arial Narrow", Arial, sans-serif` |
| Font: body, nav | Open Sans | `"Open Sans", Arial, sans-serif` |

**Critical:** Kadence's `--global-palette9` IS `#ffffff`, NOT `#1a3a5c`. The dark hero appearance comes from the background image + `rgba(0,0,0,0.3)` overlay. This means `has-theme-palette9-background-color` sets `background: #ffffff`, NOT a dark color.

## The Fundamental Problem: Kadence Is Always In The Cascade

Even with zero `<link>` tags to `activeoahutours.com` CSS in BaseLayout, the live WordPress site injects its own `<style>` blocks directly into the page HTML. These rules are **always present** in the browser's cascade. Kadence's `!important` rules can beat Astro-scoped `!important` rules if selector specificity is lower — regardless of what we import.

### Do NOT Use `all: revert`

`all: revert !important` on `*, *::before, *::after` was tried and **rejected**. It strips CSS custom property (`--var`) inheritance — all text renders as black because `color: inherit` resolves to browser default black before the `:root` variables are applied.

**Lesson:** `all: revert` resets to user-agent defaults, not to CSS variable initial values. Use explicit overrides instead.

## Kadence's Selector Specificity Is Higher Than It Looks

Kadence's button rules:
```css
a.btn-primary { color: #fff !important; }                    /* (0,1,1,0) */
a.btn-primary .glyphicon { color: #fff !important; }          /* (0,1,1,1) */
```

When a button has `class="btn btn-small btn-primary aot-book-now"`:
- Kadence's `a.btn-primary` (0,1,1,0) beats `.aot-book-now` (0,1,0,0) **before `!important` is evaluated**
- This is why `color: #003366 !important` on `.aot-book-now` had zero effect

### Three Fix Options (in order of cleanliness)

**Option 1 — Remove `.btn-primary` from HTML (cleanest):**
```html
<!-- Before -->
<a class="btn btn-small btn-primary hero-book-btn" ...>
<!-- After -->
<a class="btn btn-small hero-book-btn" ...>
```
Do this in `HeroSection.astro` and `BookNowButton.astro`.

**Option 2 — Match Kadence's specificity:**
```css
a.btn-primary.aot-book-now { color: #003366 !important; }  /* (0,2,0,0) */
```
Source-order disadvantage: Kadence's injected `<style>` blocks come after the Astro bundle in rendered HTML.

**Option 3 — Raise specificity:**
```css
a.btn-primary.aot-book-now.hero-book-btn { color: #003366 !important; }  /* (0,3,0,0) */
```

**Recommendation:** Option 1. It is the only approach that doesn't require fighting the cascade.

## Kadence Palette Classes Add Specificity Layers

Kadence elements often carry compound classes like:
```html
<h3 class="kt-adv-heading2389_d8fad2-58 wp-block-kadence-advancedheading has-white-color has-text-color">
```

The `has-text-color` class adds another layer of specificity. A rule targeting `.has-white-color` (0,1,0,0) loses to `.has-theme-palette9-color.has-text-color` (0,2,0,0) even with `!important`.

**Rule:** Always include `has-text-color` in Kadence override selectors:
```css
.has-theme-palette9-color,
.has-theme-palette9-color.has-text-color { color: #1a3a5c !important; }
```

## Kadence CSS Variable Cascade: Why Orange Buttons Appeared Dark

This was the hardest bug of the session. Mathematically, `#003366` text on `#e87121` orange = **15.3:1 AAA**. Lighthouse consistently reported **4.09:1**.

**Root cause:** Kadence's `background: var(--global-palette9, #1a3a5c) !important` on section wrappers uses a CSS variable with a fallback. The variable `--global-palette9` was not defined in the static context, so the fallback `#1a3a5c` was used. When Lighthouse computed the button's background, it saw `#1a3a5c` (dark navy) — not `#e87121` (orange). The text `#003366` on `#1a3a5c` = **1.88:1** (fails).

**Confirmed behavior:** Kadence's `background-color: var(--global-palette9, #1a3a5c) !important` on `has-theme-palette9-background-color` was overriding the button's orange background through cascade interaction.

**Final working pattern:** Match Kadence's own palette. Use **white text on `#1a3a5c`** for buttons — this shares the section's background color, is visually cohesive, and achieves **10.6:1 WCAG AAA** regardless of what Kadence does to the wrapper:

```css
.aot-btn-hero-book, .aot-btn-phone, .aot-book-now {
  background-color: #1a3a5c !important;  /* matches section background */
  color: #ffffff !important;              /* 10.6:1 AAA */
}
.aot-btn-hero-book:hover, .aot-btn-phone:hover, .aot-book-now:hover {
  background-color: #003366 !important;
}
```

## Nav Text: Kadence `#99c2d6` Light Blue Cascade (2026-07-29)

The 4 contrast failures that persist are: `#99c2d6` (light blue) on `#006699` at 9.6pt (12.8px) = 3.28:1 (fails AA).

This is **nav dropdown/sub-nav text** that Kadence controls through its CSS variable `--global-palette4` (or similar). The browser console shows white `rgb(255,255,255)` but Lighthouse headless resolves a Kadence light blue `#99c2d6`.

**Workaround:** Add explicit high-specificity overrides for any nav element that might carry Kadence's palette classes:

```css
/* Force white on nav — overrides Kadence light blue palette */
.nav-item .nav-link,
.aot-primary-nav .nav-link,
.aot-primary-nav a,
.nav-link {
  color: #ffffff !important;
}
```

This is a **Lighthouse headless rendering quirk**, not a real browser issue. The real Chrome browser shows white nav text correctly.

## Hero Lifestyle Image (2026-07-29)

Production's hero has a background photo: `https://activeoahutours.com/wp-content/uploads/2024/01/Active-Oahu-Lifestyle-225-2X1-1000.jpg` (1000×563px, ~96KB).

To add it to the Astro HeroSection:

```astro
<!-- In HeroSection.astro <section> tag -->
<div class="hero-bg" style="background-image: url('https://activeoahutours.com/wp-content/uploads/2024/01/Active-Oahu-Lifestyle-225-2X1-1000.jpg');" aria-hidden="true"></div>

<!-- CSS -->
.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
}
/* Dark overlay for text readability — matches production kb-section-has-overlay */
.hero-section .kb-section-has-overlay > .kt-inside-inner-col::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 0;
}
/* Ensure all text sits above overlay */
.hero-section h1, .hero-section h2, .hero-section h3,
.hero-section p, .hero-section a { position: relative; z-index: 1; }
```

Production sets this via Kadence's JS runtime (adding `style="background-image: ..."` to `.kt-inside-inner-col`). We set it on a dedicated `.hero-bg` div with explicit overlay. Same visual result.

## Astro Scoping: `section.hero-banner` ≠ `.hero-banner`

Astro scopes `<section class="hero-banner">` as `section.hero-banner[data-astro-cid]`. A CSS rule written as `.hero-banner .child` compiles to `.hero-banner[data-astro-cid] .child[data-astro-cid]`. The bare `.hero-banner` class **does not exist** in compiled CSS.

**Diagnose:**
```bash
grep "hero-book-btn" dist/_aot_assets/*.css
```

**Fix options:**
- Use `:where(.hero-banner)` to neutralize the ancestor specificity requirement
- Match the full nesting chain: `.kt-inside-inner-col .hero-book-btn`
- Add a direct class on a parent element that carries the CID

## FeaturedTourHero: Scoped CSS Only Applies to First Instance (2026-07-29)

When a component is used multiple times on the same page, Astro generates **different scoped attributes** for each usage (`data-astro-cid-xxx`, `data-astro-cid-yyy`). A scoped CSS rule like:

```css
/* In FeaturedTourHero.astro <style> block */
figure { display: flex; }
```

...only compiles to `figure[data-astro-cid-xxx] { display: flex; }` — it does NOT apply to the second usage `data-astro-cid-yyy` because the attribute selector doesn't match.

**Impact:** All figures in the second and third `FeaturedTourHero` instances rendered with `display: block` (browser default), causing zero-height figures.

**Fix:** Move shared layout CSS to global `active-oahu-tours-minimal.css` using bare class selectors:

```css
.featured-tour-hero { display: flex !important; gap: 1.5rem !important; }
.featured-tour-hero figure { display: flex !important; flex-shrink: 0; }
```

Do NOT put layout-related CSS (display, flex, gap, padding) in Astro scoped `<style>` blocks when the component is used multiple times. Scoped CSS is fine for per-instance theming (colors, font sizes).

## Glyphicon Font-Size Is Kadence's Weakest Link

Kadence sets `.glyphicon { font-size: small !important }` which overrides `font-size: inherit`. Lighthouse audits each text node separately — glyphicon `<span>` measured at ~10px triggers normal-text threshold (4.5:1) instead of large-text (3:1).

**Fix:**
```css
.closing-cta .cta-phone .glyphicon {
  font-size: inherit !important;
  color: inherit;
}
```

## When `!important` Tie-Breaks Go Wrong

When two `!important` rules have equal specificity, **source order wins**. Kadence's injected `<style>` blocks appear after the Astro bundle in rendered HTML.

Confirmed: `a.btn-primary.hero-book-btn .glyphicon { color: #003366 !important }` (0,3,0,1) lost to Kadence's `a.btn-primary .glyphicon { color: #fff !important }` (0,2,1,1) because Kadence came later in the document.

**Ultimate fix:** Remove `.btn-primary` from button HTML. Kadence's rules only apply when their selectors match.

## WCAG Contrast Safe Harbors

| Text | Background | Ratio | AA Normal | AA Large | AAA |
|------|-----------|-------|-----------|----------|-----|
| `#ffffff` | `#e87121` orange | 3.08:1 | ❌ fail | ✅ pass | ❌ |
| `#003366` | `#e87121` orange | 4.09:1 | ✅ pass | ✅ pass | ❌ |
| `#003366` | `#1a3a5c` dark navy | 1.88:1 | ❌ fail | ❌ fail | ❌ |
| `#ffffff` | `#1a3a5c` dark navy | 10.6:1 | ✅ pass | ✅ pass | ✅ |
| `#003366` | `#fafafa` off-white | 11.4:1 | ✅ pass | ✅ pass | ✅ |
| `#ffffff` | `#0066cc` blue | 4.0:1 | ✅ pass | ✅ pass | ❌ |
| `#ffffff` | `#d45f15` deep orange | 3.2:1 | ❌ fail | ✅ pass | ❌ |

**Design rule:** For buttons that share a section background, white on `#1a3a5c` = 10.6:1 AAA. For standalone buttons on white/off-white backgrounds, `#003366` on `#e87121` = 4.09:1 AA (passes for 12pt+ bold). Never use white on orange (fails AA for normal text).

## AOT Button Class Naming Convention

Use AOT-native classes only. Never use Bootstrap/Kadence classes in button HTML:

| Old class (Kadence) | New class (AOT) | Where |
|---------------------|-----------------|-------|
| `btn btn-small btn-primary hero-book-btn` | `aot-btn-hero-book` | HeroSection.astro |
| `btn btn-small btn-primary aot-book-now` | `aot-book-now` | BookNowButton.astro |
| `cta-phone` | `aot-btn-phone` | ClosingCTA.astro |
| (any) `.btn-primary` | `aot-btn-secondary` or `aot-btn-primary` | FeaturedTours.astro |

Define all button styles in `active-oahu-tours-minimal.css` using these AOT-native classes.

## Minimal Structural CSS (what to keep)

### Kadence Row Layout
```css
.kb-row-layout-wrap { position: relative; border: 0 solid rgba(0,0,0,0); }
.kt-row-column-wrap {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--global-row-gutter-md, 2rem);
}
.kt-row-column-wrap.kt-has-2-columns { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.kt-row-column-wrap.kt-has-3-columns { grid-template-columns: repeat(3, minmax(0, 1fr)); }
@media (max-width: 767px) {
  .kt-row-column-wrap.kt-has-2-columns,
  .kt-row-column-wrap.kt-has-3-columns { grid-template-columns: 1fr; }
}
```

### Kadence Columns
```css
.wp-block-kadence-column { display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.kt-inside-inner-col { position: relative; transition: all .3s ease; display: flex; flex-direction: column; }
```

### Palette Classes (with !important)
```css
.has-theme-palette9-background-color { background-color: #1a3a5c !important; }
.has-theme-palette8-background-color { background-color: #f0f0f0 !important; }
.has-theme-palette1-background-color { background-color: #0066cc !important; }
.has-white-background-color { background-color: #ffffff !important; }
.has-theme-palette9-color,
.has-theme-palette9-color.has-text-color { color: #1a3a5c !important; }
.has-theme-palette8-color,
.has-theme-palette8-color.has-text-color { color: #333333 !important; }
.has-theme-palette4-color,
.has-theme-palette4-color.has-text-color { color: #ffffff !important; }
.has-theme-palette1-color,
.has-theme-palette1-color.has-text-color { color: #0066cc !important; }
.has-white-color,
.has-white-color.has-text-color { color: #ffffff !important; }
```

### Glyphicons
```css
@font-face {
  font-family: "Glyphicons Halflings";
  src: url("https://activeoahutours.com/wp-content/themes/activeoahu/fonts/glyphicons-halflings-regular.eot");
}
.glyphicon {
  position: relative; top: 1px; display: inline-block;
  font-family: "Glyphicons Halflings"; font-style: normal; font-weight: normal; line-height: 1;
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
  color: inherit !important;  /* override Kadence's #fff !important */
}
.glyphicon-earphone::before { content: "\e182"; }
.glyphicon-calendar::before { content: "\e109"; }
```

## CSS Variables for AOT Design System

Define in `:root` at top of `active-oahu-tours-minimal.css`:
```css
:root {
  --aot-navy:        #003366;   /* Dark navy — links, headings */
  --aot-navy-light:  #0066cc;   /* Mid blue — link hover, primary */
  --aot-orange:      #e87121;   /* Brand orange — CTA buttons */
  --aot-orange-dark: #d45f15;   /* Deep orange — button hover */
  --aot-white:       #ffffff;   /* White */
  --aot-off-white:   #fafafa;   /* Section backgrounds */
  --aot-light-gray:  #f5f5f5;   /* Alt section backgrounds */
  --aot-gray-100:    #e0e0e0;   /* Borders, dividers */
  --aot-gray-400:    #666666;   /* Muted text, captions */
  --aot-gray-600:    #555555;   /* Secondary body text */
  --aot-gray-900:    #333333;   /* Primary text, headings */
  --aot-text-light:  #c9ddee;   /* Light text on dark backgrounds */
  --aot-hero-bg:     #1a3a5c;   /* Hero banner background */
  --aot-skip-bg:     #0066cc;   /* Skip link background */
}
```

**Button-specific hardcoded values (not variables):** Use `#1a3a5c` and `#ffffff` for buttons (not CSS vars) because of Kadence's CSS variable cascade. The variables are for text, backgrounds, and borders — not for button foreground/background combinations.

## Inline Styles Rule

**Never use `style="..."` for static visual properties** — use scoped `<style>` blocks. Inline styles make CSS unauditable and create hidden cascade conflicts. Exception: one-off dynamic values like `style={"color: " + dynamicColor}`.

## File Naming

The CSS file was renamed `kadence-minimal.css` → `active-oahu-tours-minimal.css` on 2026-07-28 per Michael's direction. Always use `active-oahu-tours-minimal.css`.

## Deployment Checklist for CSS Changes

1. Copy both `dist/index.html` AND `dist/_aot_assets/*.css` to `site/` root
2. CSS bundle filename changes on every rebuild (hash-based) — always copy the new one
3. Commit all changes before pushing
4. Wait ~75 seconds for CF Pages to deploy
5. Verify: `curl -s "https://deploy-fresh...pages.dev/" | wc -c` should return new HTML size
6. Run Lighthouse — verify Accessibility ≥ 85, zero contrast failures
